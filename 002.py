import streamlit as st
from collections import defaultdict, Counter
import numpy as np

# Emojis para cada cor
cores = {
    "C": "🔴",  # Casa
    "V": "🔵",  # Visitante
    "E": "🟡",  # Empate
}

# Inicializa o histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

# Configuração da página
st.set_page_config(page_title="FS Padrões Pro", layout="centered")
st.title("📊 FS Padrões Pro - Sistema de Sugestões")

# Botões para entrada
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🔴 Casa"):
        st.session_state.historico.insert(0, "C")
with col2:
    if st.button("🔵 Visitante"):
        st.session_state.historico.insert(0, "V")
with col3:
    if st.button("🟡 Empate"):
        st.session_state.historico.insert(0, "E")
with col4:
    if st.button("↩️ Desfazer") and st.session_state.historico:
        st.session_state.historico.pop(0)
with col5:
    if st.button("🧹 Limpar"):
        st.session_state.historico = []

st.divider()

# Mostrar histórico em blocos de 27 (3 linhas de 9)
def mostrar_blocos(historico):
    blocos = [historico[i:i+27] for i in range(0, len(historico), 27)]
    for idx, bloco in enumerate(blocos):
        st.markdown(f"### 🧱 Ciclo {idx + 1}")
        for linha in range(3):
            ini = linha * 9
            fim = ini + 9
            if ini < len(bloco):
                linha_jogadas = bloco[ini:fim]
                visual = " ".join(cores.get(x, x) for x in linha_jogadas)
                st.markdown(visual)

st.markdown("## 📋 Histórico por blocos (cada 27 jogadas)")
if st.session_state.historico:
    mostrar_blocos(st.session_state.historico)
else:
    st.info("Nenhuma jogada ainda registrada.")

# Função para detectar padrões cíclicos para todas as cores
def detectar_padroes_ciclicos(historico, tamanho_ciclo=27):
    if len(historico) < tamanho_ciclo:
        return []
    
    padroes = []
    
    # Para cada posição no ciclo
    for posicao in range(tamanho_ciclo):
        # Coletar todos os valores nesta posição cíclica
        valores = []
        for ciclo in range(len(historico) // tamanho_ciclo):
            idx = ciclo * tamanho_ciclo + posicao
            if idx < len(historico):
                valores.append(historico[idx])
        
        # Se temos valores suficientes para análise
        if len(valores) >= 5:
            contador = Counter(valores)
            cor_mais_comum, contagem = contador.most_common(1)[0]
            frequencia = contagem / len(valores)
            
            # Considerar padrão se frequência for alta
            if frequencia > 0.7:  # 70% de ocorrência
                padroes.append({
                    "posicao": posicao,
                    "cor": cor_mais_comum,
                    "frequencia": frequencia,
                    "ocorrencias": contagem,
                    "total": len(valores),
                    "valores": valores
                })
    
    return padroes

# Função para detectar sequências consecutivas
def detectar_sequencias(historico, min_tamanho=3):
    if not historico:
        return []
    
    sequencias = []
    sequencia_atual = []
    
    for i, resultado in enumerate(historico):
        if not sequencia_atual or resultado == sequencia_atual[-1]:
            sequencia_atual.append(resultado)
        else:
            if len(sequencia_atual) >= min_tamanho:
                sequencias.append({
                    "cor": sequencia_atual[0],
                    "inicio": i - len(sequencia_atual),
                    "fim": i - 1,
                    "tamanho": len(sequencia_atual)
                })
            sequencia_atual = [resultado]
    
    # Verificar última sequência
    if len(sequencia_atual) >= min_tamanho:
        sequencias.append({
            "cor": sequencia_atual[0],
            "inicio": len(historico) - len(sequencia_atual),
            "fim": len(historico) - 1,
            "tamanho": len(sequencia_atual)
        })
    
    return sequencias

# Função para detectar padrões de repetição
def detectar_padroes_repeticao(historico, tamanho_padrao=3):
    padroes = []
    
    if len(historico) < tamanho_padrao * 2:
        return padroes
    
    # Procurar padrões repetidos em todo o histórico
    for i in range(len(historico) - tamanho_padrao * 2 + 1):
        padrao = historico[i:i+tamanho_padrao]
        
        # Verificar se o padrão se repete posteriormente
        for j in range(i + tamanho_padrao, len(historico) - tamanho_padrao + 1):
            if historico[j:j+tamanho_padrao] == padrao:
                padroes.append({
                    "inicio": i,
                    "repeticao": j,
                    "padrao": padrao,
                    "tamanho": tamanho_padrao
                })
    
    return padroes

# Função para gerar sugestões com base nos padrões detectados
def gerar_sugestoes(historico, padroes_ciclicos, sequencias, padroes_repetidos):
    sugestoes = []
    
    # 1. Sugestões baseadas em sequências consecutivas
    if sequencias:
        # Verificar sequências ativas (que terminam no último elemento)
        sequencias_ativas = [s for s in sequencias if s["fim"] == len(historico)-1]
        
        for seq in sequencias_ativas:
            # Se a sequência tem 3 elementos, sugerir continuar
            if seq["tamanho"] == 3:
                sugestoes.append({
                    "tipo": "Sequência Ativa",
                    "cor": seq["cor"],
                    "confianca": 0.7,
                    "motivo": f"Sequência de 3 {cores.get(seq['cor']} consecutivos"
                })
            # Se a sequência é maior, sugerir oposto
            elif seq["tamanho"] >= 4:
                cores_opostas = {"C": "V", "V": "C", "E": "C"}  # Simplificado
                cor_oposta = cores_opostas.get(seq["cor"], "C")
                sugestoes.append({
                    "tipo": "Quebra de Sequência",
                    "cor": cor_oposta,
                    "confianca": 0.8,
                    "motivo": f"Sequência longa de {seq['tamanho']} {cores.get(seq['cor'])} pode quebrar"
                })
    
    # 2. Sugestões baseadas em padrões cíclicos
    if padroes_ciclicos and historico:
        tamanho_ciclo = 27
        posicao_atual = len(historico) % tamanho_ciclo
        
        for padrao in padroes_ciclicos:
            if padrao["posicao"] == posicao_atual:
                sugestoes.append({
                    "tipo": "Padrão Cíclico",
                    "cor": padrao["cor"],
                    "confianca": padrao["frequencia"],
                    "motivo": f"Padrão histórico na posição {posicao_atual+1} do ciclo"
                })
    
    # 3. Sugestões baseadas em padrões repetidos
    if padroes_repetidos:
        # Encontrar o padrão repetido mais recente
        padrao_recente = max(padroes_repetidos, key=lambda x: x["repeticao"], default=None)
        
        if padrao_recente:
            # Posição após o padrão repetido
            pos_apos_padrao = padrao_recente["repeticao"] + padrao_recente["tamanho"]
            
            if pos_apos_padrao < len(historico):
                # O que aconteceu após o padrão na primeira ocorrência?
                resultado_apos = historico[padrao_recente["inicio"] + padrao_recente["tamanho"]]
                sugestoes.append({
                    "tipo": "Padrão Repetido",
                    "cor": resultado_apos,
                    "confianca": 0.75,
                    "motivo": f"Padrão {' '.join(cores.get(p) for p in padrao_recente['padrao'])} se repetiu"
                })
    
    # 4. Sugestão baseada na tendência geral (se não houver outros padrões)
    if not sugestoes and historico:
        contador = Counter(historico)
        cor_mais_comum = contador.most_common(1)[0][0]
        sugestoes.append({
            "tipo": "Tendência Geral",
            "cor": cor_mais_comum,
            "confianca": contador[cor_mais_comum] / len(historico),
            "motivo": f"Cor mais frequente no histórico"
        })
    
    return sugestoes

# Seção de sugestões
st.divider()
st.markdown("## 💡 Sugestões de Entrada")

if st.session_state.historico:
    # Detectar padrões
    padroes_ciclicos = detectar_padroes_ciclicos(st.session_state.historico)
    sequencias = detectar_sequencias(st.session_state.historico, min_tamanho=3)
    padroes_repetidos = detectar_padroes_repeticao(st.session_state.historico, tamanho_padrao=3)
    
    # Gerar sugestões
    sugestoes = gerar_sugestoes(
        st.session_state.historico, 
        padroes_ciclicos, 
        sequencias, 
        padroes_repetidos
    )
    
    if sugestoes:
        # Ordenar por confiança
        sugestoes.sort(key=lambda x: x['confianca'], reverse=True)
        
        # Mostrar sugestão principal
        principal = sugestoes[0]
        st.success(f"**🎯 SUGESTÃO PRINCIPAL: {cores.get(principal['cor'])}**")
        st.markdown(f"**Tipo:** {principal['tipo']} | **Confiança:** {principal['confianca']*100:.0f}%")
        st.markdown(f"**Motivo:** {principal['motivo']}")
        
        # Mostrar outras sugestões
        if len(sugestoes) > 1:
            st.markdown("### 🔍 Outras Sugestões")
            for i, sug in enumerate(sugestoes[1:]):
                st.info(f"**{i+2}. {cores.get(sug['cor'])}**: {sug['tipo']} (Confiança: {sug['confianca']*100:.0f}%)")
                st.caption(f"{sug['motivo']}")
    else:
        st.warning("Nenhuma sugestão gerada com base nos padrões atuais")
        st.info("Adicione mais dados para melhorar a detecção de padrões")
else:
    st.info("Adicione dados para gerar sugestões")

# Seção de análise de padrões
st.divider()
st.markdown("## 🔍 Análise de Padrões")

if st.session_state.historico:
    # 1. Padrões Cíclicos
    st.subheader("🔄 Padrões Cíclicos")
    if padroes_ciclicos:
        dados = []
        for p in padroes_ciclicos:
            dados.append({
                "Posição no Ciclo": p["posicao"] + 1,
                "Cor": cores.get(p["cor"]),
                "Frequência": f"{p['frequencia']*100:.1f}%",
                "Ocorrências": f"{p['ocorrencias']}/{p['total']}"
            })
        st.dataframe(dados)
    else:
        st.warning("Nenhum padrão cíclico significativo detectado")
        st.info("Adicione mais ciclos completos para melhor detecção")
    
    # 2. Sequências Consecutivas
    st.subheader("➰ Sequências Consecutivas")
    if sequencias:
        for seq in sequencias:
            st.markdown(f"- **{cores.get(seq['cor'])} repetido {seq['tamanho']} vezes** "
                        f"(posições {seq['inicio']+1} a {seq['fim']+1})")
    else:
        st.info("Nenhuma sequência longa detectada (mínimo 3 repetições)")
    
    # 3. Padrões de Repetição
    st.subheader("♻️ Padrões Repetidos")
    if padroes_repetidos:
        for padrao in padroes_repetidos:
            padrao_visual = " ".join(cores.get(p) for p in padrao["padrao"])
            st.markdown(f"- Padrão **{padrao_visual}** repetido "
                        f"(primeiro em {padrao['inicio']+1}-{padrao['inicio']+padrao['tamanho']}, "
                        f"depois em {padrao['repeticao']+1}-{padrao['repeticao']+padrao['tamanho']})")
    else:
        st.info("Nenhum padrão repetido detectado")
else:
    st.info("Adicione dados para começar a análise")

# Seção de resumo estatístico
st.divider()
st.markdown("## 📊 Resumo Estatístico")

if st.session_state.historico:
    total = len(st.session_state.historico)
    contagem = Counter(st.session_state.historico)
    
    cols = st.columns(3)
    cols[0].metric("🔴 Casa", f"{contagem['C']} ({contagem['C']/total*100:.1f}%)")
    cols[1].metric("🔵 Visitante", f"{contagem['V']} ({contagem['V']/total*100:.1f}%)")
    cols[2].metric("🟡 Empate", f"{contagem['E']} ({contagem['E']/total*100:.1f}%)")
    
    # Distribuição em gráfico
    st.bar_chart({
        "Casa": [contagem['C']],
        "Visitante": [contagem['V']],
        "Empate": [contagem['E']]
    })
else:
    st.info("Nenhum dado disponível para análise estatística")

st.divider()
st.markdown("### ⚙️ Como Funciona:")
st.write("1. **Sugestões Inteligentes**: Gera recomendações com base em padrões detectados")
st.write("2. **Múltiplas Estratégias**: Usa sequências, padrões cíclicos e repetições")
st.write("3. **Níveis de Confiança**: Mostra o grau de confiança para cada sugestão")
st.write("4. **Transparência Total**: Exibe todos os padrões detectados para verificação")
