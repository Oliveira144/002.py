import streamlit as st
from collections import defaultdict

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
st.title("📊 FS Padrões Pro – Detecção Inteligente de Padrões")

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
                
                # Destacar os últimos 3 elementos da primeira linha
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

# Função para detectar padrões de reescrita na primeira linha
def detectar_padrao_reescrita(historico):
    if len(historico) < 15:  # Mínimo de 1 linha completa + 6 jogadas
        return None
    
    # Extrair a primeira linha completa (9 jogadas)
    primeira_linha = historico[:9]
    
    # Coletar todas as linhas completas do histórico
    linhas_completas = []
    for i in range(0, len(historico), 9):
        if i + 9 <= len(historico):
            linha = historico[i:i+9]
            linhas_completas.append(linha)
    
    if len(linhas_completas) < 2:
        return None
    
    # Procurar padrões de reescrita
    padroes_detectados = []
    for idx, linha in enumerate(linhas_completas[1:]):
        # Verificar se a linha atual reescreve um padrão anterior
        if linha == primeira_linha:
            # Encontrar a próxima jogada após o padrão histórico
            posicao_padrao = (idx + 1) * 9
            if posicao_padrao < len(historico):
                proxima_jogada = historico[posicao_padrao]
                padroes_detectados.append(proxima_jogada)
    
    # Se encontrou padrões, retornar a sugestão mais frequente
    if padroes_detectados:
        contagem = defaultdict(int)
        for jogada in padroes_detectados:
            contagem[jogada] += 1
        
        # Ordenar por frequência
        sugestao = max(contagem, key=contagem.get)
        confianca = contagem[sugestao] / len(padroes_detectados)
        
        return {
            "padrao": primeira_linha,
            "ocorrencias": len(padroes_detectados),
            "sugestao": sugestao,
            "confianca": confianca,
            "historico": padroes_detectados
        }
    
    return None

# Análise de padrões
st.divider()
st.markdown("## 🔍 Análise de Reescrita na Primeira Linha")

resultado = detectar_padrao_reescrita(st.session_state.historico)

if resultado:
    # Mostrar detecção
    st.success(f"**🔁 Padrão Detectado!**")
    
    # Visualização do padrão
    padrao_visual = " ".join([cores.get(x, x) for x in resultado["padrao"]])
    st.markdown(f"- **Padrão na 1ª linha:** {padrao_visual}")
    st.markdown(f"- **Ocorrências históricas:** {resultado['ocorrencias']} vezes")
    
    # Sugestão única com justificativa
    st.divider()
    st.markdown(f"## 🎯 Sugestão: {cores.get(resultado['sugestao'])}")
    
    # Justificativa detalhada
    st.info("**Justificativa Técnica:**")
    st.write(f"- Após ocorrências anteriores deste mesmo padrão, a próxima jogada foi:")
    
    # Mostrar histórico de transições
    for i, jogada in enumerate(resultado["historico"]):
        st.write(f"  → Ocorrência {i+1}: {cores.get(jogada)}")
    
    st.write(f"- **Frequência de sugestão:** {resultado['confianca']*100:.1f}%")
    st.write("- A análise considera reescrita completa da primeira linha")
    
    # Explicação do comportamento
    st.divider()
    st.markdown("### 📊 Comportamento Típico:")
    st.write("1. Quando a primeira linha se repete completamente (reescrita)")
    st.write("2. O sistema sugere a jogada mais frequente após esse padrão")
    st.write("3. Padrões com mais ocorrências têm maior confiabilidade")
    
else:
    if len(st.session_state.historico) >= 15:
        st.warning("Nenhum padrão de reescrita detectado na primeira linha.")
        st.info("Dica: Continue registrando jogadas para aumentar a base de padrões históricos")
    else:
        st.info("Registre pelo menos 15 jogadas (1 linha completa + 6 jogadas) para ativar a análise")

st.divider()
st.markdown("### 🔬 Como Funciona a Detecção:")
st.write("1. **Foco na primeira linha completa:** Analisa os 9 elementos da linha atual")
st.write("2. **Busca reescrita completa:** Procura ocorrências idênticas no histórico")
st.write("3. **Analisa transições:** Examina a jogada imediatamente após cada ocorrência")
st.write("4. **Sugestão única:** Recomenda a jogada mais frequente após o padrão")
st.write("5. **Confiança estatística:** Calcula probabilidade com base em ocorrências históricas")
