import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Ativo Analytics")

ticker1 = st.text_input("Digite o ticker do primeiro ativo (por exemplo, BTC-USD):")
ticker2 = st.text_input("Digite o ticker do segundo ativo, caso queira comparar")
genre = st.radio("Selecione o Período:", ["1D", "5D", "1M", "3M", "6M", "1Y", "5Y", "10Y", "MAX"], index=None, horizontal=True)

preco_inicial = None
preco_final = None
retorno = None

def baixar(t, p):
    df_ticket = yf.download(t, period=p)
    return df_ticket

col1= st.columns(1)
col2, col3= st.columns(2)

# Verifique se um ticker foi fornecido
if ticker1:
    # Baixe os dados do ticker
    df_ticket = baixar(ticker1, genre)

    # Verifique se o DataFrame não está vazio
    if not df_ticket.empty:
        # Renomeie as colunas do DataFrame
        df_ticket = df_ticket.rename(columns={'Adj Close': 'y'}).reset_index()
        df_ticket = df_ticket.rename(columns={'Date': 'ds'})

        # Crie um DataFrame com os dados do ticker
        df = df_ticket[["ds", "y", "Volume", "Open", "Close"]]

        # Verifique se um segundo ticker foi fornecido
        if ticker2:
            # Baixe os dados do segundo ticker
            df_ticket2 = baixar(ticker2, genre)
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
            fig_lin = px.line(df, x="ds", y=["y", "y2"], title=ticker1.upper()+ " | " +ticker2.upper())
        else:
            fig_lin = px.line(df, x="ds", y="y", title=ticker1.upper())
    else:
        # Exiba uma mensagem de aviso se o DataFrame estiver vazio
        st.warning(f"Nenhum dado disponível para o ticker {ticker1} no período selecionado.")
    
    # Exiba o gráfico
    col1[0].plotly_chart(fig_lin, use_container_width=True)

    fig_bar = px.bar(df, x="ds", y="Volume", title="Volume de Negociação " + ticker1.upper())
    col2.plotly_chart(fig_bar, use_container_width=True)  


if ticker1:
    # Defina o período selecionado
    data_inicio = df_ticket['ds'].min()
    data_fim = df_ticket['ds'].max()

    # Obtenha os dados do ativo
    df_ticket = df_ticket.loc[df_ticket['ds'].between(data_inicio, data_fim)]

    # Calcule o preço inicial e o preço final
    preco_inicial = df_ticket['Open'].iloc[0]
    preco_final = df_ticket['Close'].iloc[-1]

    # Calcule o retorno do ativo
    retorno = preco_final - preco_inicial
    df = pd.DataFrame({'Metrica': ['Preço Inicial', 'Preço Final', 'Retorno'], 'Valor': [preco_inicial, preco_final, retorno]})
    
    # Apresente os resultados
    fig_bar1 = px.bar(df, x="Metrica", y="Valor", title="Retorno de acordo com o período ")
    fig_bar1.add_annotation(x='Preço Inicial', y=preco_inicial, text=f"$ {preco_inicial:.2f}")
    fig_bar1.add_annotation(x='Preço Final', y=preco_final, text=f"$ {preco_final:.2f}")
    fig_bar1.add_annotation(x='Retorno', y=retorno, text=f"$ {retorno:.2f}")

    col3.plotly_chart(fig_bar1, use_container_width=True)