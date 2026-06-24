import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard de Infrequência", layout="wide")
st.title("📊 Monitoramento de Faltas Escolares 2026")

# 1. CONEXÃO COM O GOOGLE PLANILHAS
SHEET_ID = "1m9A-P5xR05fZPpQMlzSsr9efnpBDAuDPlujLIGenjts"
# Link corrigido apontando para a aba em maiúsculo
url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=PAINEL DE MONITORAMENTO"

@st.cache_data(ttl=300) # Atualiza os dados a cada 5 minutos
def load_data():
    df = pd.read_csv(url)
    
    # Tratamento da coluna de Data usando o nome real da sua planilha
    # Se você preferir usar a coluna B, troque 'Carimbo de data/hora' por 'Data' abaixo
    df['Carimbo de data e hora'] = pd.to_datetime(df['Carimbo de data e hora'], errors='coerce')
    df['Dia da Semana'] = df['Carimbo de data e hora'].dt.strftime('%A')
    
    # Tradução dos dias
    dias_pt = {
        'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 
        'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira'
    }
    df['Dia da Semana'] = df['Dia da Semana'].map(dias_pt)
    
    # Força a coluna de faltas a ser número
    df['Total Faltas Diárias'] = pd.to_numeric(df['Total Faltas Diárias'], errors='coerce').fillna(0)
    return df

    
    turnos = ["Todos"] + list(df['Turno'].dropna().unique())
    turno_selecionada = st.sidebar.selectbox("Selecione o Turno", turnos)

    # Filtrando os dados na tela
    df_filtrado = df.copy()
    if escola_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Escola'] == escola_selecionada]
    if turno_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Turno'] == turno_selecionada]

    # CARD PRINCIPAL
    total_faltas = int(df_filtrado['Total Faltas Diárias'].sum())
    st.metric(label="Total de Faltas no Período", value=f"{total_faltas:,}")

    # GRÁFICOS
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🗓️ Faltas por Dia da Semana")
        ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira']
        df_dias = df_filtrado.groupby('Dia da Semana')['Total Faltas Diárias'].sum().reindex(ordem_dias).reset_index()
        fig_dia = px.bar(df_dias, x='Dia da Semana', y='Total Faltas Diárias', template="plotly_white", color_discrete_sequence=['#4F46E5'])
        st.plotly_chart(fig_dia, use_container_width=True)

    with col2:
        st.subheader("⏳ Faltas por Turno")
        df_turno = df_filtrado.groupby('Turno')['Total Faltas Diárias'].sum().reset_index()
        fig_turno = px.pie(df_turno, values='Total Faltas Diárias', names='Turno', hole=0.4)
        st.plotly_chart(fig_turno, use_container_width=True)

    # TABELA DE ANO / SÉRIE
    st.subheader("🎒 Total de Faltas por Ano/Série")
    # Altere os nomes das colunas abaixo se na sua planilha estiver diferente!
    colunas_series = ['Berçário', 'Maternal', '1º Ano', '2º Ano', '3º Ano', '4º Ano', '5º Ano', '6º Ano', '7º Ano', '8º Ano', '9º Ano']
    colunas_existentes = [col for col in colunas_series if col in df_filtrado.columns]
    
    if colunas_existentes:
        df_series = df_filtrado.groupby('Escola')[colunas_existentes].sum()
        st.dataframe(df_series, use_container_width=True)
    else:
        st.warning("Colunas de séries não detectadas. Verifique os nomes na planilha.")

except Exception as e:
    st.error(f"Erro na conexão de dados: {e}")
