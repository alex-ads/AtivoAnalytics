import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configuração da página
st.set_page_config(layout="wide")
st.title("Ativo Analytics - Criptomoedas")

# Input do usuário
ticker1 = st.text_input("Digite o ticker do primeiro ativo (exemplo: bitcoin, ethereum, solana):").lower()
ticker2 = st.text_input("Digite o ticker do segundo ativo, caso queira comparar").lower()
periodo = st.radio("Selecione o Período:", ["1", "7", "30", "90", "180", "365", "max"], index=2, horizontal=True)

def baixar_dados(ticker, dias):
    """Baixa dados históricos de uma criptomoeda da API do CoinGecko."""
    url = f"https://api.coingecko.com/api/v3/coins/{ticker}/market_chart?vs_currency=usd&days={dias}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['prices'], columns=['ds', 'y'])
        df['ds'] = pd.to_datetime(df['ds'], unit='ms')
        df['volume'] = [v[1] for v in data['total_volumes']]
        return df
    else:
        return None

col1, col2, col3 = st.columns([2, 1, 1])

# Verifica se o primeiro ticker foi inserido
if ticker1:
    df1 = baixar_dados(ticker1, periodo)
    if df1 is not None:
        preco_inicial = df1['y'].iloc[0]
        preco_final = df1['y'].iloc[-1]
        retorno = preco_final - preco_inicial
        
        if ticker2:
            df2 = baixar_dados(ticker2, periodo)
            if df2 is not None:
                df2.rename(columns={'y': 'y2'}, inplace=True)
                df = pd.merge(df1, df2, on='ds', how='outer')
                fig_lin = px.line(df, x='ds', y=['y', 'y2'], title=f"{ticker1.upper()} vs {ticker2.upper()}")
            else:
                st.warning(f"Não foi possível obter dados para {ticker2}.")
                fig_lin = px.line(df1, x='ds', y='y', title=f"Preço de {ticker1.upper()}")
        else:
            fig_lin = px.line(df1, x='ds', y='y', title=f"Preço de {ticker1.upper()}")

        col1.plotly_chart(fig_lin, use_container_width=True)

        # Gráfico de volume
        fig_vol = px.bar(df1, x='ds', y='volume', title=f"Volume de Negociação - {ticker1.upper()}")
        col2.plotly_chart(fig_vol, use_container_width=True)

        # Gráfico de retorno
        df_retorno = pd.DataFrame({'Métrica': ['Preço Inicial', 'Preço Final', 'Retorno'], 'Valor': [preco_inicial, preco_final, retorno]})
        fig_bar = px.bar(df_retorno, x="Métrica", y="Valor", title="Retorno do Ativo")
        fig_bar.add_annotation(x='Preço Inicial', y=preco_inicial, text=f"$ {preco_inicial:.2f}")
        fig_bar.add_annotation(x='Preço Final', y=preco_final, text=f"$ {preco_final:.2f}")
        fig_bar.add_annotation(x='Retorno', y=retorno, text=f"$ {retorno:.2f}")
        col3.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning(f"Não foi possível obter dados para {ticker1}.")
