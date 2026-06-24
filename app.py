import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard de Infrequência", layout="wide")
st.title("📊 Monitoramento de Faltas Escolares 2026")

# 1. CONEXÃO COM O GOOGLE PLANILHAS
SHEET_ID = "1m9A-P5xR05fZPpQMlzSsr9efnpBDAuDPlujLIGenjts"
url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respostas"

@st.cache_data(ttl=60) # Atualiza os dados a cada 1 minuto para testes rápidos
def load_data():
    df = pd.read_csv(url)
    
    # Tratamento da coluna de Data usando o Carimbo de data e hora
    df['Carimbo de data e hora'] = pd.to_datetime(df['Carimbo de data e hora'], errors='coerce')
    df['Dia da Semana'] = df['Carimbo de data e hora'].dt.strftime('%A')
    
    # Tradução dos dias para o gráfico
    dias_pt = {
        'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 
        'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira',
        'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    df['Dia da Semana'] = df['Dia da Semana'].map(dias_pt)
    
    # Força a coluna correta de faltas totais a ser numérica
    df['Total Faltas Diaria'] = pd.to_numeric(df['Total Faltas Diaria'], errors='coerce').fillna(0)
    
    return df

try:
    df = load_data()

    # 2. FILTROS LATERAIS (SIDEBAR)
    st.sidebar.header("Filtros de Análise")
    
    escolas = ["Todas"] + list(df['Escola'].dropna().unique())
    escola_selecionada = st.sidebar.selectbox("Selecione a Escola", escolas)
    
    turnos = ["Todos"] + list(df['Turno'].dropna().unique())
    turno_selecionada = st.sidebar.selectbox("Selecione o Turno", turnos)

    etapas = ["Todas"] + list(df['Etapa'].dropna().unique())
    etapa_selecionada = st.sidebar.selectbox("Selecione a Etapa de Ensino", etapas)

    # Aplicando os filtros escolhidos pelo usuário
    df_filtrado = df.copy()
    if escola_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Escola'] == escola_selecionada]
    if turno_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Turno'] == turno_selecionada]
    if etapa_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Etapa'] == etapa_selecionada]

    # 3. INDICADOR PRINCIPAL
    total_faltas = int(df_filtrado['Total Faltas Diaria'].sum())
    st.metric(label="Total de Faltas no Período Selecionado", value=f"{total_faltas:,}")

    # 4. GRÁFICOS PRINCIPAIS
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🗓️ Faltas por Dia da Semana")
        ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira']
        df_dias = df_filtrado.groupby('Dia da Semana')['Total Faltas Diaria'].sum().reindex(ordem_dias).reset_index()
        fig_dia = px.bar(df_dias, x='Dia da Semana', y='Total Faltas Diaria', template="plotly_white", color_discrete_sequence=['#4F46E5'])
        st.plotly_chart(fig_dia, use_container_width=True)

    with col2:
        st.subheader("⏳ Faltas por Turno")
        df_turno = df_filtrado.groupby('Turno')['Total Faltas Diaria'].sum().reset_index()
        fig_turno = px.pie(df_turno, values='Total Faltas Diaria', names='Turno', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_turno, use_container_width=True)

    # 5. TABELA MATRICIAL POR SÉRIE (ANO / ETAPA)
    st.subheader("🎒 Detalhamento de Faltas por Ano / Série")
    
    # Lista exata das colunas de séries
    colunas_series = [
        'Berçário', 'Maternal I', 'Maternal II', '1º Período', '2º Período', 
        '1º Ano', '2º Ano', '3º Ano', '4º Ano', '5º Ano', '6º Ano', '7º Ano', '8º Ano', '9º Ano', 'EJA'
    ]
    
    for col in colunas_series:
        if col in df_filtrado.columns:
            df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0)

    colunas_existentes = [col for col in colunas_series if col in df_filtrado.columns]
    
    if colunas_existentes:
        df_series = df_filtrado.groupby('Escola')[colunas_existentes].sum()
        st.dataframe(df_series, use_container_width=True)
    else:
        st.warning("Colunas de séries não detectadas. Verifique a estrutura da planilha.")

except Exception as e:
    st.error(f"Erro ao processar dados da planilha: {e}")
