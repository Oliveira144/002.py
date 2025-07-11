import streamlit as st
from collections import Counter

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
st.title("📊 FS Padrões Pro – Análise Completa por Bloco e Reescrita Camuflada")

# Botões de entrada
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🔴 Casa"):
        st.session_state.historico.append("C")
with col2:
    if st.button("🔵 Visitante"):
        st.session_state.historico.append("V")
with col3:
    if st.button("🟡 Empate"):
        st.session_state.historico.append("E")
with col4:
    if st.button("↩️ Desfazer") and st.session_state.historico:
        st.session_state.historico.pop()
with col5:
    if st.button("🧹 Limpar"):
        st.session_state.historico = []

# Codifica estrutura simbólica de uma lista (ex: ABA)
def codificar_estrutura(lista):
    mapa = {}
    codigo = []
    letra = 'A'
    for item in lista:
        if item not in mapa:
            mapa[item] = letra
            letra = chr(ord(letra) + 1)
        codigo.append(mapa[item])
    return "".join(codigo)

# Mostrar histórico em blocos de 27 jogadas (3 linhas de 9), mais recentes na Linha 1
def mostrar_blocos(historico):
    blocos = [historico[i:i+27] for i in range(0, len(historico), 27)]
    for idx, bloco in enumerate(reversed(blocos)):
        st.markdown(f"### 📦 Bloco {len(blocos) - idx} (mais recente acima)")
        for linha in range(3):
            ini = (2 - linha) * 9
            fim = ini + 9
            linha_jogadas = bloco[ini:fim]
            visual = " ".join(cores.get(x, x) for x in linha_jogadas)
            st.markdown(f"Linha {linha + 1}: {visual}")
    return blocos

# 🎯 Sugestão Inteligente de Próxima Jogada (baseada em reescrita)
st.divider()
st.markdown("## 🎯 Sugestão Inteligente de Próxima Jogada (baseada em reescrita)")

blocos = mostrar_blocos(st.session_state.historico) if st.session_state.historico else []
padrao_encontrado = False
proxima_cor = None

if len(blocos) >= 2:
    bloco_atual = blocos[-1]
    bloco_anterior = blocos[-2]

    for tamanho in range(4, 9):
        novo_trecho = bloco_atual[:tamanho]
        for i in range(len(bloco_anterior) - tamanho + 1):
            trecho_antigo = bloco_anterior[i:i+tamanho]

            if novo_trecho == trecho_antigo:
                proxima_cor = bloco_anterior[i + tamanho] if i + tamanho < len(bloco_anterior) else None
                padrao_encontrado = True
                st.success(f"🔁 Reescrita Exata detectada (tamanho {tamanho})")
                break

            estrutura_novo = codificar_estrutura(novo_trecho)
            estrutura_antigo = codificar_estrutura(trecho_antigo)
            if estrutura_novo == estrutura_antigo:
                proxima_cor = bloco_anterior[i + tamanho] if i + tamanho < len(bloco_anterior) else None
                padrao_encontrado = True
                st.info(f"🔄 Reescrita Estrutural detectada: `{estrutura_novo}`")
                break

            diffs = sum(1 for a, b in zip(novo_trecho, trecho_antigo) if a != b)
            if diffs <= 2:
                proxima_cor = bloco_anterior[i + tamanho] if i + tamanho < len(bloco_anterior) else None
                padrao_encontrado = True
                st.warning(f"⚠️ Reescrita com pequenas alterações detectada (diferença de {diffs})")
                break

        if padrao_encontrado:
            break

if padrao_encontrado and proxima_cor:
    st.markdown(f"### 👉 Próxima cor sugerida: **{cores[proxima_cor]}**")
else:
    st.info("Aguardando padrão confiável para sugerir próxima jogada.")

# 📊 Frequência de Padrões Estruturais
st.divider()
st.markdown("## 📊 Frequência de Padrões Estruturais (últimas jogadas)")

estruturas = []
h = st.session_state.historico
for i in range(len(h) - 2):
    trecho = h[i:i+3]
    estrutura = codificar_estrutura(trecho)
    estruturas.append(estrutura)

contagem = Counter(estruturas)
if contagem:
    for estrutura, qtd in contagem.most_common():
        st.markdown(f"🔹 `{estrutura}` → {qtd}x")
else:
    st.info("Ainda não há dados suficientes para mostrar padrões estruturais.")
