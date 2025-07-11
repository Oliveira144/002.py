import streamlit as st

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
st.title("📊 FS Padrões Pro – Análise de Colunas e Blocos")

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
            linha_jogadas = bloco[ini:fim]
            visual = " ".join(cores.get(x, x) for x in linha_jogadas)
            st.markdown(visual)

st.markdown("## 📋 Histórico por blocos (cada 27 jogadas)")
if st.session_state.historico:
    mostrar_blocos(st.session_state.historico)
else:
    st.info("Nenhuma jogada ainda registrada.")

# Codifica uma coluna (lista de 3 jogadas) para estrutura simbólica (ex: ABA)
def codificar_coluna(col):
    mapa = {}
    codigo = []
    letra = "A"
    for cor in col:
        if cor not in mapa:
            mapa[cor] = letra
            letra = chr(ord(letra) + 1)
        codigo.append(mapa[cor])
    return "".join(codigo)

# Gera colunas deslizantes (ex: [0:3], [1:4], [2:5]...)
def gerar_colunas_deslizantes(historico):
    colunas = []
    for i in range(len(historico) - 2):
        col = historico[i:i+3]
        colunas.append(col)
    return colunas

# Detecta reescrita entre colunas
colunas = gerar_colunas_deslizantes(st.session_state.historico)
reescrita_detectada = None

if len(colunas) >= 2:
    atual = colunas[0]
    cod_atual = codificar_coluna(atual)
    for i in range(1, len(colunas)):
        if codificar_coluna(colunas[i]) == cod_atual:
            reescrita_detectada = {
                "indice": i,
                "estrutura": cod_atual,
                "coluna_antiga": colunas[i],
                "coluna_nova": atual,
                "sugerida": st.session_state.historico[i - 1] if i - 1 >= 0 else None
            }
            break

st.divider()
st.markdown("## 🔍 Análise de Reescrita Estrutural (colunas deslizantes)")

if reescrita_detectada:
    st.success(f"Coluna 1 reescreve coluna {reescrita_detectada['indice'] + 1} com estrutura '{reescrita_detectada['estrutura']}'")
    st.write("🔹 Coluna antiga:", " ".join(cores[c] for c in reescrita_detectada["coluna_antiga"]))
    st.write("🔹 Coluna atual:", " ".join(cores[c] for c in reescrita_detectada["coluna_nova"]))

    if reescrita_detectada["sugerida"]:
        st.markdown("### 🧠 Sugestão de próxima jogada")
        st.info(f"Próxima cor sugerida: {cores[reescrita_detectada['sugerida']]}")
else:
    st.warning("Nenhuma reescrita detectada ainda. Aguarde formação de colunas (mínimo 3 jogadas).")
