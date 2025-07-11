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
    if len(historico) < janela + 9:  # Mínimo de 1 linha completa + janela
        return None
    
    # Extrair a primeira linha completa
    primeira_linha = historico[:9]
    final_primeira_linha = primeira_linha[-janela:]
    
    # Estruturas para análise
    padroes_cores = defaultdict(list)
    padroes_estrutura = defaultdict(list)
    
    # Analisar todo o histórico
    for i in range(len(historico) - janela):
        segmento = historico[i:i+janela]
        proxima_jogada = historico[i+janela]
        
        # Padrão de cores exatas
        chave_cores = "".join(segmento)
        padroes_cores[chave_cores].append(proxima_jogada)
        
        # Padrão estrutural
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
    
    # Gerar chaves para o padrão atual
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
    
    # Resultados candidatos
    candidatos = []
    
    # Verificar padrão de cores
    if chave_atual_cores in padroes_cores:
        ocorrencias = padroes_cores[chave_atual_cores]
        if len(ocorrencias) >= min_ocorrencias:
            contagem = defaultdict(int)
            for jogada in ocorrencias:
                contagem[jogada] += 1
            
            # Calcular taxa de acerto
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
    
    # Verificar padrão estrutural
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
    
    # Selecionar o candidato com maior confiança
    if not candidatos:
        return None
    
    # Ordenar por confiança e depois por ocorrências
    candidatos.sort(key=lambda x: (x['confianca'], x['ocorrencias']), reverse=True)
    return candidatos[0]  # Retornar apenas o melhor candidato

# Análise de padrões
st.divider()
st.markdown("## 🔍 Análise de Padrões com Alta Confiança")

# Parâmetros ajustáveis
col1, col2 = st.columns(2)
with col1:
    janela_padrao = st.slider("Tamanho do Padrão", 3, 7, 5, 
                             help="Número de jogadas no final da primeira linha a serem analisadas")
with col2:
    min_ocorrencias = st.slider("Mínimo de Ocorrências", 2, 10, 3, 
                               help="Número mínimo de ocorrências históricas para considerar um padrão")

resultado = detectar_padrao_confiavel(st.session_state.historico, 
                                     janela=janela_padrao,
                                     min_ocorrencias=min_ocorrencias)

if resultado:
    # Mostrar apenas a melhor sugestão
    st.success(f"**🎯 SUGESTÃO: {cores.get(resultado['sugestao'])}**")
    
    # Detalhes do padrão
    st.markdown(f"**Confiança:** {resultado['confianca']*100:.1f}%")
    
    st.divider()
    st.markdown("### 🔍 Detalhes do Padrão Detectado")
    
    padrao_visual = " ".join([cores.get(x, x) for x in resultado["padrao"]])
    st.markdown(f"- **Padrão analisado:** {padrao_visual}")
    st.markdown(f"- **Tipo de análise:** {resultado['tipo']}")
    
    if resultado['tipo'] == "Estrutura Simbólica":
        st.markdown(f"- **Estrutura codificada:** `{resultado['codigo']}`")
    
    st.markdown(f"- **Ocorrências históricas:** {resultado['ocorrencias']}")
    
    # Distribuição estatística
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
    
    # Explicação da sugestão
    st.divider()
    st.markdown("### 💡 Por que esta sugestão?")
    st.write(f"1. Padrão detectado com **{resultado['ocorrencias']} ocorrências** históricas")
    st.write(f"2. **{cores.get(resultado['sugestao'])}** foi a jogada mais frequente após este padrão")
    st.write(f"3. Taxa de acerto histórica: **{resultado['confianca']*100:.1f}%**")
    
else:
    if len(st.session_state.historico) >= 9 + janela_padrao:
        st.warning("Nenhum padrão confiável detectado")
        st.info("Dicas para melhor detecção:")
        st.write("- Aumente o número de jogadas registradas")
        st.write("- Reduza o tamanho do padrão ou o mínimo de ocorrências")
        st.write("- Verifique se há padrões consistentes no histórico")
    else:
        st.info(f"Registre pelo menos {9+janela_padrao} jogadas para ativar a análise")

st.divider()
st.markdown("### ⚙️ Como Funciona:")
st.write("1. **Foco no final da 1ª linha:** Analisa os últimos N elementos")
st.write("2. **Exigência de confiabilidade:** Padrões com poucas ocorrências são ignorados")
st.write("3. **Sugestão única:** Mostra apenas a recomendação mais confiável")
st.write("4. **Transparência:** Exibe toda a base estatística por trás da sugestão")
