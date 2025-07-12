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
st.title("📊 FS Padrões Pro - Detector Universal de Padrões")

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
    
    for i in range(len(historico) - tamanho_padrao * 2 + 1):
        padrao = historico[i:i+tamanho_padrao]
        proximos = historico[i+tamanho_padrao:i+tamanho_padrao*2]
        
        if padrao == proximos:
            padroes.append({
                "inicio": i,
                "padrao": padrao,
                "repeticao": i + tamanho_padrao
            })
    
    return padroes

# Função para prever próxima jogada
def prever_proxima_jogada(historico, padroes_ciclicos):
    if not historico or not padroes_ciclicos:
        return None
    
    tamanho_ciclo = 27
    posicao_atual = len(historico) % tamanho_ciclo
    
    # Verificar se temos um padrão para esta posição
    for padrao in padroes_ciclicos:
        if padrao["posicao"] == posicao_atual:
            return padrao["cor"]
    
    return None

# Seção de análise de padrões
st.divider()
st.markdown("## 🔍 Análise de Padrões")

if st.session_state.historico:
    # 1. Padrões Cíclicos
    st.subheader("🔄 Padrões Cíclicos")
    padroes_ciclicos = detectar_padroes_ciclicos(st.session_state.historico)
    
    if padroes_ciclicos:
        st.success(f"Detectados {len(padroes_ciclicos)} padrões cíclicos!")
        
        # Tabela de padrões
        dados = []
        for p in padroes_ciclicos:
            dados.append({
                "Posição no Ciclo": p["posicao"] + 1,
                "Cor": cores.get(p["cor"]),
                "Frequência": f"{p['frequencia']*100:.1f}%",
                "Ocorrências": f"{p['ocorrencias']}/{p['total']}"
            })
        st.dataframe(dados)
        
        # Previsão para próxima jogada
        proxima = prever_proxima_jogada(st.session_state.historico, padroes_ciclicos)
        if proxima:
            st.markdown(f"### 🎯 Próxima Jogada Prevista: {cores.get(proxima)}")
            st.markdown(f"Baseada na posição {len(st.session_state.historico) % 27 + 1} do ciclo")
        else:
            st.info("Nenhuma previsão para a próxima jogada com base em padrões cíclicos")
    else:
        st.warning("Nenhum padrão cíclico significativo detectado")
        st.info("Adicione mais ciclos completos para melhor detecção")
    
    # 2. Sequências Consecutivas
    st.subheader("➰ Sequências Consecutivas")
    sequencias = detectar_sequencias(st.session_state.historico, min_tamanho=3)
    
    if sequencias:
        for seq in sequencias:
            st.markdown(f"- **{cores.get(seq['cor'])} repetido {seq['tamanho']} vezes** "
                        f"(posições {seq['inicio']+1} a {seq['fim']+1})")
    else:
        st.info("Nenhuma sequência longa detectada (mínimo 3 repetições)")
    
    # 3. Padrões de Repetição
    st.subheader("♻️ Padrões Repetidos")
    padroes_repetidos = detectar_padroes_repeticao(st.session_state.historico, tamanho_padrao=3)
    
    if padroes_repetidos:
        for padrao in padroes_repetidos:
            padrao_visual = " ".join(cores.get(p) for p in padrao["padrao"])
            st.markdown(f"- Padrão **{padrao_visual}** repetido "
                        f"(primeiro em {padrao['inicio']+1}-{padrao['inicio']+3}, "
                        f"depois em {padrao['repeticao']+1}-{padrao['repeticao']+3})")
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
st.write("1. **Padrões Cíclicos**: Detecta cores dominantes em posições específicas dos ciclos de 27 jogos")
st.write("2. **Sequências Consecutivas**: Identifica repetições de 3+ da mesma cor em sequência")
st.write("3. **Padrões Repetidos**: Encontra sequências idênticas que se repetem no histórico")
st.write("4. **Previsão**: Sugere próxima jogada baseada em padrões cíclicos detectados")
