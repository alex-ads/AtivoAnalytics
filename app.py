import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Desempenho de Ativos")

ticker = st.text_input("Digite o ticker do primeiro ativo (por exemplo, BTC-USD ou USD):")
ticker2 = st.text_input("Digite o ticker do segundo ativo, caso queira comparar")
genre = st.radio("Selecione o Período:", ["1D", "5D", "1M", "3M", "6M", "1Y", "5Y", "10Y", "MAX"], index=None, horizontal=True)

# Verifique se um ticker foi fornecido
if ticker:
    # Baixe os dados do ticker
    df_ticket = yf.download(ticker, period=genre)

    # Verifique se o DataFrame não está vazio
    if not df_ticket.empty:
        # Renomeie as colunas do DataFrame
        df_ticket = df_ticket.rename(columns={'Adj Close': 'y'}).reset_index()
        df_ticket = df_ticket.rename(columns={'Date': 'ds'})

        # Crie um DataFrame com os dados do ticker
        df = df_ticket[["ds", "y"]]

        # Verifique se um segundo ticker foi fornecido
        if ticker2:
            # Baixe os dados do segundo ticker
            df_ticket2 = yf.download(ticker2, period=genre)

            # Verifique se o DataFrame do segundo ticker não está vazio
            if not df_ticket2.empty:
                # Renomeie as colunas do DataFrame do segundo ticker
                df_ticket2 = df_ticket2.rename(columns={'Adj Close': 'y2'}).reset_index()
                df_ticket2 = df_ticket2.rename(columns={'Date': 'ds'})

                # Crie um DataFrame com os dados do segundo ticker
                df2 = df_ticket2[["ds", "y2"]]

                # Mescle os dados dos dois ativos
                df = pd.merge(df, df2, on='ds', how='outer')

        # Crie o gráfico com os dados dos dois ativos, se existirem
        if 'y2' in df.columns:
            fig_date = px.line(df, x="ds", y=["y", "y2"])
        else:
            fig_date = px.line(df, x="ds", y="y")

        # Exiba o gráfico
        st.plotly_chart(fig_date, use_container_width=True)
    else:
        # Exiba uma mensagem de aviso se o DataFrame estiver vazio
        st.warning(f"Nenhum dado disponível para o ticker {ticker} no período selecionado.")