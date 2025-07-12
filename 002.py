import streamlit as st
from collections import defaultdict
import numpy as np
from scipy import stats

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
st.title("📊 FS Padrões Pro – Sugestão com Máxima Confiança")

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
                
                # Destacar os últimos elementos da primeira linha
                if idx == 0 and linha == 0 and len(linha_jogadas) >= 6:
                    parte_inicial = " ".join(cores.get(x, x) for x in linha_jogadas[:-3])
                    parte_final = " ".join(f"**{cores.get(x, x)}**" for x in linha_jogadas[-3:])
                    st.markdown(f"{parte_inicial} {parte_final}")
                else:
                    st.markdown(visual)

st.markdown("## 📋 Histórico por blocos (cada 27 jogadas)")
if st.session_state.historico:
    mostrar_blocos(st.session_state.historico)
else:
    st.info("Nenhuma jogada ainda registrada.")

# Função para detectar padrões com alta confiança
def detectar_padrao_confiavel(historico, janela=5, min_ocorrencias=3):
    if len(historico) < janela + 9:
        return None
    
    primeira_linha = historico[:9]
    final_primeira_linha = primeira_linha[-janela:]
    
    padroes_cores = defaultdict(list)
    padroes_estrutura = defaultdict(list)
    
    for i in range(len(historico) - janela):
        segmento = historico[i:i+janela]
        proxima_jogada = historico[i+janela]
        
        chave_cores = "".join(segmento)
        padroes_cores[chave_cores].append(proxima_jogada)
        
        mapa = {}
        codigo = []
        letra = "A"
        for item in segmento:
            if item not in mapa:
                mapa[item] = letra
                letra = chr(ord(letra) + 1)
            codigo.append(mapa[item])
        chave_estrutura = "".join(codigo)
        padroes_estrutura[chave_estrutura].append(proxima_jogada)
    
    chave_atual_cores = "".join(final_primeira_linha)
    
    mapa_atual = {}
    codigo_atual = []
    letra = "A"
    for item in final_primeira_linha:
        if item not in mapa_atual:
            mapa_atual[item] = letra
            letra = chr(ord(letra) + 1)
        codigo_atual.append(mapa_atual[item])
    chave_atual_estrutura = "".join(codigo_atual)
    
    candidatos = []
    
    if chave_atual_cores in padroes_cores:
        ocorrencias = padroes_cores[chave_atual_cores]
        if len(ocorrencias) >= min_ocorrencias:
            contagem = defaultdict(int)
            for jogada in ocorrencias:
                contagem[jogada] += 1
            
            jogada_mais_comum = max(contagem, key=contagem.get)
            confianca = contagem[jogada_mais_comum] / len(ocorrencias)
            
            candidatos.append({
                "tipo": "Cores Exatas",
                "confianca": confianca,
                "ocorrencias": len(ocorrencias),
                "sugestao": jogada_mais_comum,
                "detalhes": ocorrencias,
                "padrao": final_primeira_linha
            })
    
    if chave_atual_estrutura in padroes_estrutura:
        ocorrencias = padroes_estrutura[chave_atual_estrutura]
        if len(ocorrencias) >= min_ocorrencias:
            contagem = defaultdict(int)
            for jogada in ocorrencias:
                contagem[jogada] += 1
            
            jogada_mais_comum = max(contagem, key=contagem.get)
            confianca = contagem[jogada_mais_comum] / len(ocorrencias)
            
            candidatos.append({
                "tipo": "Estrutura Simbólica",
                "confianca": confianca,
                "ocorrencias": len(ocorrencias),
                "sugestao": jogada_mais_comum,
                "detalhes": ocorrencias,
                "padrao": final_primeira_linha,
                "codigo": chave_atual_estrutura
            })
    
    if not candidatos:
        return None
    
    candidatos.sort(key=lambda x: (x['confianca'], x['ocorrencias']), reverse=True)
    return candidatos[0]

# Função para detectar padrões cíclicos
def detectar_padroes_ciclicos(historico, tamanho_ciclo=27):
    if len(historico) < tamanho_ciclo * 2:
        return None
    
    mapeamento = {"C": 0, "V": 1, "E": 2}
    try:
        historico_numerico = np.array([mapeamento[j] for j in historico])
    except KeyError:
        st.error("Erro: Histórico contém valores inválidos. Use apenas 'C', 'V' ou 'E'.")
        return None
    
    padroes_significativos = []
    
    for posicao in range(tamanho_ciclo):
        valores = []
        for ciclo in range(len(historico) // tamanho_ciclo):
            idx = ciclo * tamanho_ciclo + posicao
            if idx < len(historico_numerico):
                valores.append(historico_numerico[idx])
        
        if len(valores) < 2:
            continue
            
        contagens = np.bincount(valores, minlength=3)
        total = len(valores)
        
        if np.count_nonzero(contagens) < 2:
            continue
        
        try:
            chi2, p_valor = stats.chisquare(contagens)
        except ValueError:
            continue
        
        if total >= 10 and p_valor < 0.05:
            cor_dominante = np.argmax(contagens)
            frequencia = contagens[cor_dominante] / total
            
            if frequencia > 0.6:
                padroes_significativos.append({
                    "posicao_ciclo": posicao,
                    "cor": list(mapeamento.keys())[list(mapeamento.values()).index(cor_dominante)],
                    "frequencia": frequencia,
                    "ocorrencias": total,
                    "p_valor": p_valor
                })
    
    return padroes_significativos

# Função para prever próximos ciclos
def prever_proximos_ciclos(historico, padroes, tamanho_ciclo=27, ciclos_prever=3):
    previsoes = []
    
    posicao_atual = len(historico) % tamanho_ciclo
    
    for ciclo in range(1, ciclos_prever + 1):
        previsao_ciclo = []
        
        for posicao in range(tamanho_ciclo):
            padrao_encontrado = None
            for p in padroes:
                if p["posicao_ciclo"] == posicao:
                    padrao_encontrado = p
                    break
            
            if padrao_encontrado:
                previsao_ciclo.append(padrao_encontrado["cor"])
            else:
                previsao_ciclo.append("?")
        
        previsoes.append(previsao_ciclo)
    
    return previsoes

# Análise de padrões curtos
st.divider()
st.markdown("## 🔍 Análise de Padrões com Alta Confiança")

col1, col2 = st.columns(2)
with col1:
    janela_padrao = st.slider("Tamanho do Padrão", 3, 7, 5)
with col2:
    min_ocorrencias = st.slider("Mínimo de Ocorrências", 2, 10, 3)

resultado = detectar_padrao_confiavel(st.session_state.historico, 
                                     janela=janela_padrao,
                                     min_ocorrencias=min_ocorrencias)

if resultado:
    st.success(f"**🎯 SUGESTÃO: {cores.get(resultado['sugestao'])}**")
    st.markdown(f"**Confiança:** {resultado['confianca']*100:.1f}%")
    
    st.divider()
    st.markdown("### 🔍 Detalhes do Padrão Detectado")
    
    padrao_visual = " ".join([cores.get(x, x) for x in resultado["padrao"]])
    st.markdown(f"- **Padrão analisado:** {padrao_visual}")
    st.markdown(f"- **Tipo de análise:** {resultado['tipo']}")
    
    if resultado['tipo'] == "Estrutura Simbólica":
        st.markdown(f"- **Estrutura codificada:** `{resultado['codigo']}`")
    
    st.markdown(f"- **Ocorrências históricas:** {resultado['ocorrencias']}")
    
    st.divider()
    st.markdown("### 📊 Estatísticas Históricas")
    
    contagem = defaultdict(int)
    for jogada in resultado["detalhes"]:
        contagem[jogada] += 1
    
    total = len(resultado["detalhes"])
    st.write(f"Após este padrão, as próximas jogadas foram:")
    
    for jogada, count in contagem.items():
        percentual = count / total * 100
        st.progress(percentual/100, text=f"{cores.get(jogada)}: {count} vezes ({percentual:.1f}%)")
    
    st.caption(f"Total de ocorrências analisadas: {total}")
    
    st.divider()
    st.markdown("### 💡 Por que esta sugestão?")
    st.write(f"1. Padrão detectado com **{resultado['ocorrencias']} ocorrências** históricas")
    st.write(f"2. **{cores.get(resultado['sugestao'])}** foi a jogada mais frequente após este padrão")
    st.write(f"3. Taxa de acerto histórica: **{resultado['confianca']*100:.1f}%**")
    
else:
    if len(st.session_state.historico) >= 9 + janela_padrao:
        st.warning("Nenhum padrão confiável detectado")
    else:
        st.info(f"Registre pelo menos {9+janela_padrao} jogadas para ativar a análise")

# Nova seção para análise cíclica
st.divider()
st.markdown("## 🔄 Análise de Padrões Cíclicos")

if len(st.session_state.historico) >= 54:
    padroes_ciclicos = detectar_padroes_ciclicos(st.session_state.historico)
    
    if padroes_ciclicos:
        st.success(f"**🎯 PADRÕES CÍCLICOS DETECTADOS: {len(padroes_ciclicos)} posições significativas**")
        
        st.markdown("### 📈 Padrões por Posição no Ciclo")
        dados_tabela = []
        for padrao in padroes_ciclicos:
            dados_tabela.append({
                "Posição": padrao["posicao_ciclo"] + 1,
                "Cor": cores.get(padrao["cor"]),
                "Frequência": f"{padrao['frequencia']*100:.1f}%",
                "Ocorrências": padrao["ocorrencias"],
                "Confiança Estatística": f"{(1-padrao['p_valor'])*100:.1f}%"
            })
        st.dataframe(dados_tabela)
        
        st.markdown("### 🔮 Previsão para Próximos Ciclos")
        previsoes = prever_proximos_ciclos(st.session_state.historico, padroes_ciclicos)
        
        for i, ciclo_previsao in enumerate(previsoes):
            st.markdown(f"#### Ciclo {len(st.session_state.historico)//27 + i + 1} (Previsão)")
            
            for linha in range(3):
                ini = linha * 9
                fim = ini + 9
                linha_jogadas = ciclo_previsao[ini:fim]
                visual = " ".join([cores.get(x, x) if x != "?" else "❓" for x in linha_jogadas])
                st.markdown(visual)
            
            azuis_previstos = sum(1 for x in ciclo_previsao if x == "V")
            st.metric(label="🔵 Azuis Previstos", value=azuis_previstos)
    else:
        st.warning("Nenhum padrão cíclico estatisticamente significativo encontrado")
else:
    st.info("Registre pelo menos 2 ciclos completos (54 jogos) para ativar análise cíclica")

st.divider()
st.markdown("### ⚙️ Como Funciona:")
st.write("1. **Análise de curto prazo:** Padrões nos últimos jogos da primeira linha")
st.write("2. **Análise cíclica:** Padrões recorrentes em posições fixas dos ciclos de 27 jogos")
st.write("3. **Sugestões únicas:** Recomendações com base em evidências estatísticas")
st.write("4. **Transparência:** Mostra toda a base de dados por trás das previsões")
