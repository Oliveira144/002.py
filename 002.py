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
st.title("📊 FS Padrões Pro – Análise Dinâmica de Transições")

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

# Função para analisar transições entre linhas
def analisar_transicoes(historico):
    if len(historico) < 15:  # Mínimo de 1 linha completa + 6 jogadas
        return None
    
    # Coletar todas as linhas completas
    linhas_completas = []
    for i in range(0, len(historico), 9):
        if i + 9 <= len(historico):
            linha = historico[i:i+9]
            linhas_completas.append(linha)
    
    if len(linhas_completas) < 2:
        return None
    
    # Foco no final da primeira linha (últimas 3-5 jogadas)
    primeira_linha = linhas_completas[0]
    final_primeira_linha = primeira_linha[-3:]
    
    # Verificar transição para segunda linha
    segunda_linha = historico[9:12]  # Primeiros 3 elementos da segunda linha
    
    # Procurar padrões históricos semelhantes
    padroes_detectados = []
    for idx, linha in enumerate(linhas_completas[1:]):
        # Verificar final de linha histórica
        final_linha_historica = linha[-3:]
        
        # Comparar padrão do final da linha
        if final_linha_historica == final_primeira_linha:
            # Verificar o que aconteceu após esse padrão (transição)
            proximo_bloco_idx = (idx + 1) * 9 + 6  # Posição após o padrão
            if proximo_bloco_idx + 3 < len(historico):
                transicao_historica = historico[proximo_bloco_idx:proximo_bloco_idx+3]
                
                # Calcular estatísticas de transição
                contagem = {"C": 0, "V": 0, "E": 0}
                for item in transicao_historica:
                    contagem[item] += 1
                
                padroes_detectados.append({
                    "padrao_final": final_linha_historica,
                    "transicao": transicao_historica,
                    "contagem": contagem,
                    "posicao_historica": proximo_bloco_idx
                })
    
    # Se encontrou padrões, determinar sugestão mais provável
    if padroes_detectados:
        # Contagem agregada de todas as transições históricas
        contagem_agregada = {"C": 0, "V": 0, "E": 0}
        total_padroes = len(padroes_detectados)
        
        for padrao in padroes_detectados:
            for cor, count in padrao["contagem"].items():
                contagem_agregada[cor] += count
        
        # Determinar sugestão mais frequente
        sugestao = max(contagem_agregada, key=contagem_agregada.get)
        confianca = contagem_agregada[sugestao] / (total_padroes * 3)
        
        return {
            "final_primeira_linha": final_primeira_linha,
            "transicao_atual": segunda_linha,
            "padroes_similares": len(padroes_detectados),
            "sugestao": sugestao,
            "confianca": confianca,
            "contagem_agregada": contagem_agregada,
            "historico_transicoes": [p["transicao"] for p in padroes_detectados]
        }
    
    return None

# Análise de transições
st.divider()
st.markdown("## 🔄 Análise de Transição Entre Linhas")

resultado = analisar_transicoes(st.session_state.historico)

if resultado:
    # Mostrar detecção
    st.success(f"**🔍 Padrão Detectado no Final da Primeira Linha!**")
    
    # Visualização do padrão
    padrao_final = " ".join([cores.get(x, x) for x in resultado["final_primeira_linha"]])
    st.markdown(f"- **Padrão no final da 1ª linha:** {padrao_final}")
    
    # Visualização da transição atual
    if resultado["transicao_atual"]:
        transicao_atual = " ".join([cores.get(x, x) for x in resultado["transicao_atual"]])
        st.markdown(f"- **Transição atual (2ª linha):** {transicao_atual}")
    
    # Sugestão única com justificativa
    st.divider()
    st.markdown(f"## 🎯 Sugestão: {cores.get(resultado['sugestao']}")
    
    # Justificativa detalhada
    st.info("**Justificativa Técnica:**")
    st.write(f"- Padrão detectado **{resultado['padroes_similares']} vezes** no histórico")
    st.write(f"- Após este padrão, as transições foram:")
    
    # Mostrar transições históricas
    for i, trans in enumerate(resultado["historico_transicoes"]):
        visual = " ".join([cores.get(x, x) for x in trans])
        st.write(f"  → Ciclo {i+1}: {visual}")
    
    st.write(f"- **Distribuição estatística:**")
    for cor, count in resultado["contagem_agregada"].items():
        st.write(f"  - {cores.get(cor)}: {count} ocorrências ({count/(resultado['padroes_similares']*3)*100:.1f}%)")
    
    st.write(f"- **Nível de confiança:** {resultado['confianca']*100:.1f}%")
    
    # Explicação do comportamento
    st.divider()
    st.markdown("### 📊 Comportamento Típico Deste Padrão:")
    st.write("1. O padrão no final da primeira linha indica uma **tendência de ruptura**")
    st.write("2. A transição para a segunda linha geralmente **mantém ou inverte** o fluxo")
    st.write("3. A sugestão considera a resposta estatística mais comum após este padrão")
    
else:
    if len(st.session_state.historico) >= 15:
        st.warning("Nenhum padrão recorrente detectado no final da primeira linha. Continue registrando jogadas.")
    else:
        st.info("Registre pelo menos 15 jogadas (1 linha completa + 6 jogadas) para ativar a análise")

st.divider()
st.markdown("### 🔬 Como Funciona a Análise:")
st.write("1. **Foco no final da 1ª linha:** Analisa os últimos 3 elementos da linha atual")
st.write("2. **Detecta padrões de reescrita:** Busca ocorrências históricas com mesmo padrão final")
st.write("3. **Analisa transições:** Examina como o sistema se comportou após esses padrões")
st.write("4. **Sugestão única:** Recomenda a jogada com maior probabilidade estatística")
st.write("5. **Comportamento dinâmico:** Considera tanto repetições quanto mudanças de padrão")
