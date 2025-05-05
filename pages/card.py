import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from services.SupabaseClient import SupabaseClient

st.set_page_config(page_title="Cartões de Crédito", layout="wide")
st.subheader("💳 Gerenciamento de Compras no Cartão")

client = SupabaseClient(
    base_url=st.secrets["supabase"]["url"],
    api_key=st.secrets["supabase"]["key"]
)

df = client.get("card")

if not df.empty:
    df["data_compra"] = pd.to_datetime(df["data_compra"]).dt.date
    df["mes_fatura"] = pd.to_datetime(df["mes_fatura"]).dt.strftime("%Y-%m")

    hoje = datetime.today().replace(day=1)
    meses_range = pd.date_range(hoje - relativedelta(months=6), hoje + relativedelta(months=6), freq="MS").strftime("%Y-%m").tolist()

    with st.sidebar:
        cartoes = ["Todos"] + sorted(df["cartao"].unique())
        filtro_cartao = st.selectbox("Filtrar por Cartão", cartoes)

        meses_disponiveis = sorted(set(df["mes_fatura"].unique()) & set(meses_range), reverse=True)
        filtro_mes = st.selectbox("Filtrar por Mês da Fatura", ["Todos"] + meses_disponiveis)

    if filtro_cartao != "Todos":
        df = df[df["cartao"] == filtro_cartao]

    if filtro_mes != "Todos":
        df = df[df["mes_fatura"] == filtro_mes]

    st.dataframe(df.drop(columns=["id"]), use_container_width=True)

# Formulário de cadastro
st.subheader("Nova Compra")
with st.form("form_nova_compra"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cartao = st.selectbox("Cartão", ["Bradesco American", "C6", "Inter", "MercadoPago", "Santander  Visa", "Santander Visa Cash", "Santander Master"])
    with col2:
        data_compra = st.date_input("Data da Compra", datetime.today())
    with col3:
        mes_fatura = st.date_input("Mês da Fatura", datetime.today())
    with col4:
        valor = st.number_input("Valor", step=0.01)
    
    descricao = st.text_input("Descrição")        
    
    parcelado = st.checkbox("Parcelado")
    
    col5, col6 = st.columns(2)
    with col5:
        parcela = st.number_input("Parcela Atual", min_value=0, step=1)
    with col6:
        total_parcela = st.number_input("Total Parcelas", min_value=0, step=1)
    
    col7, col8 = st.columns(2)
    with col7:
        fixo = st.checkbox("Fixo")
    with col8:
        previsto = st.checkbox("Previsto")

    submit = st.form_submit_button("Cadastrar")
    if submit:
        if not descricao.strip():
            st.warning("⚠️ A descrição é obrigatória.")
        else:
            payload = {
                "cartao": cartao,
                "data_compra": data_compra.isoformat(),
                "mes_fatura": mes_fatura.strftime("%Y-%m-%d"),
                "descricao": descricao,
                "parcelado": parcelado,
                "parcela": parcela,
                "total_parcela": total_parcela,
                "valor": valor,
                "fixo": fixo,
                "previsto": previsto
            }
            try:
                client.post("card", payload)                            
                st.success("✅ Cadastrada com sucesso!")
                st.rerun()                
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")
