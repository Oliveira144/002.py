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
st.title("📊 FS Padrões Pro – Detecção Avançada de Padrões")

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

# Função para detectar padrões complexos
def detectar_padroes_complexos(historico, janela=5):
    if len(historico) < janela + 9:  # Mínimo de 1 linha completa + janela
        return None
    
    # Extrair a primeira linha completa e o início da segunda
    primeira_linha = historico[:9]
    
    # Padrões a serem detectados
    padroes = {
        "cores": defaultdict(list),
        "estrutura": defaultdict(list)
    }
    
    # Analisar todo o histórico
    for i in range(len(historico) - janela):
        segmento = historico[i:i+janela]
        
        # Verificar padrão de cores
        chave_cores = "".join(segmento)
        if i+janela < len(historico):
            proxima_jogada = historico[i+janela]
            padroes["cores"][chave_cores].append(proxima_jogada)
        
        # Verificar padrão estrutural
        mapa = {}
        codigo = []
        letra = "A"
        for item in segmento:
            if item not in mapa:
                mapa[item] = letra
                letra = chr(ord(letra) + 1)
            codigo.append(mapa[item])
        chave_estrutura = "".join(codigo)
        if i+janela < len(historico):
            padroes["estrutura"][chave_estrutura].append(proxima_jogada)
    
    # Verificar padrão atual no final da primeira linha
    final_primeira_linha = primeira_linha[-janela:]
    chave_atual_cores = "".join(final_primeira_linha)
    
    # Gerar chave estrutural para o padrão atual
    mapa_atual = {}
    codigo_atual = []
    letra = "A"
    for item in final_primeira_linha:
        if item not in mapa_atual:
            mapa_atual[item] = letra
            letra = chr(ord(letra) + 1)
        codigo_atual.append(mapa_atual[item])
    chave_atual_estrutura = "".join(codigo_atual)
    
    # Resultados encontrados
    resultados = []
    
    # Padrão de cores exatas
    if chave_atual_cores in padroes["cores"]:
        ocorrencias = padroes["cores"][chave_atual_cores]
        contagem = defaultdict(int)
        for jogada in ocorrencias:
            contagem[jogada] += 1
        
        sugestao = max(contagem, key=contagem.get)
        confianca = contagem[sugestao] / len(ocorrencias)
        
        resultados.append({
            "tipo": "Cores Exatas",
            "padrao": final_primeira_linha,
            "ocorrencias": len(ocorrencias),
            "sugestao": sugestao,
            "confianca": confianca,
            "detalhes": ocorrencias
        })
    
    # Padrão estrutural
    if chave_atual_estrutura in padroes["estrutura"]:
        ocorrencias = padroes["estrutura"][chave_atual_estrutura]
        contagem = defaultdict(int)
        for jogada in ocorrencias:
            contagem[jogada] += 1
        
        sugestao = max(contagem, key=contagem.get)
        confianca = contagem[sugestao] / len(ocorrencias)
        
        resultados.append({
            "tipo": "Estrutura Simbólica",
            "padrao": final_primeira_linha,
            "codigo": chave_atual_estrutura,
            "ocorrencias": len(ocorrencias),
            "sugestao": sugestao,
            "confianca": confianca,
            "detalhes": ocorrencias
        })
    
    return resultados if resultados else None

# Análise de padrões complexos
st.divider()
st.markdown("## 🔍 Análise Avançada de Padrões")

# Parâmetro ajustável para tamanho do padrão
janela_padrao = st.slider("Tamanho do Padrão para Análise", 3, 7, 5, help="Número de jogadas no final da primeira linha a serem consideradas")

resultados = detectar_padroes_complexos(st.session_state.historico, janela=janela_padrao)

if resultados:
    # Mostrar todas as detecções
    for resultado in resultados:
        st.success(f"**🔍 Padrão Detectado! ({resultado['tipo']})**")
        
        # Visualização do padrão
        padrao_visual = " ".join([cores.get(x, x) for x in resultado["padrao"]])
        st.markdown(f"- **Padrão analisado:** {padrao_visual}")
        
        if "codigo" in resultado:
            st.markdown(f"- **Estrutura codificada:** `{resultado['codigo']}`")
        
        st.markdown(f"- **Ocorrências históricas:** {resultado['ocorrencias']} vezes")
        
        # Sugestão
        st.divider()
        st.markdown(f"## 🎯 Sugestão: {cores.get(resultado['sugestao'])}")
        st.markdown(f"**Confiança:** {resultado['confianca']*100:.1f}%")
        
        # Justificativa detalhada
        st.info("**Justificativa Técnica:**")
        st.write(f"- Após este padrão, as próximas jogadas foram:")
        
        # Agrupar ocorrências por tipo
        contagem_detalhada = defaultdict(int)
        for jogada in resultado["detalhes"]:
            contagem_detalhada[jogada] += 1
        
        for jogada, count in contagem_detalhada.items():
            percentual = count / len(resultado["detalhes"]) * 100
            st.write(f"  - {cores.get(jogada)}: {count} vezes ({percentual:.1f}%)")
        
        st.write(f"- Total de ocorrências analisadas: {len(resultado['detalhes'])}")  # CORREÇÃO AQUI
        
        # Espaçamento entre padrões
        st.write("")
        st.write("---")
        st.write("")
    
else:
    if len(st.session_state.historico) >= 14:  # 9 + 5
        st.warning("Nenhum padrão recorrente detectado no final da primeira linha.")
        st.info("Dica: Tente ajustar o tamanho do padrão ou continue registrando jogadas")
    else:
        st.info(f"Registre pelo menos {9+janela_padrao} jogadas para ativar a análise")

st.divider()
st.markdown("### 🔬 Como Funciona a Detecção Avançada:")
st.write("1. **Análise de cores exatas:** Detecta sequências idênticas de cores")
st.write("2. **Análise estrutural:** Detecta padrões de repetição independente das cores específicas (ex: ABA, ABC, etc)")
st.write("3. **Janela ajustável:** Permite focar em diferentes tamanhos de padrão")
st.write("4. **Estatística robusta:** Sugere a jogada mais frequente após padrões similares")
st.write("5. **Transparência:** Mostra todas as ocorrências históricas usadas na análise")
