import os
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_KEY = st.secrets["supabase"]["key"]
SUPABASE_URL = f"{st.secrets['supabase']['url']}/expenses_daily"

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.set_page_config(page_title="Bruno Souza", layout="wide")
st.subheader("📊 Gastos - Denecessários")

# --- Formulário para nova despesa ---
st.markdown("<small>Por favor preencha todoas os campos.</small>", unsafe_allow_html=True)

with st.form("form_novo_item"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        date = st.date_input("Data *")
    with col2:
        description = st.text_input("Descrição  *")
    with col3:
        amount = st.number_input("Total *", step=0.01, format="%.2f")
    with col4:
        payment_type = st.selectbox("Tipo Pagamento *", ["", "credit", "debit"], index=0)

    submitted = st.form_submit_button("Salvar")

    # Validação
    if submitted:
        if not description or amount == 0 or not payment_type:
            st.warning("⚠️ Por favor preencha todoas os campos")
        else:
            payload = {
                "created_at": date.isoformat(),
                "description": description,
                "value": amount,
                "payment_type": payment_type
            }
            post_response = requests.post(SUPABASE_URL, headers=HEADERS, json=payload)

            if post_response.status_code in [200, 201]:
                st.success("✅ Expense added successfully!")
                st.cache_data.clear()  # Limpa cache para novo GET
                st.rerun()
            else:
                st.error(f"Error adding: {post_response.text}")

st.divider()

col_f1, col_f2 = st.columns(2)
meses = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

with col_f1:
    mes_selecionado = st.selectbox("Mês", options=list(meses.keys()), format_func=lambda x: meses[x], index=datetime.now().month - 1)
with col_f2:
    ano_selecionado = st.selectbox("Ano", options=list(range(2024, datetime.now().year + 1)), index=1)

# --- Buscar dados existentes ---
@st.cache_data
def get_data(mes, ano):
    data_inicio = f"{ano}-{mes:02d}-01"
    if mes == 12:
        data_fim = f"{ano + 1}-01-01"
    else:
        data_fim = f"{ano}-{mes + 1:02d}-01"

    params = {
    "and": f"(created_at.gte.{data_inicio},created_at.lt.{data_fim})"
    }
    
    response = requests.get(SUPABASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Erro ao buscar dados.")
        return pd.DataFrame()
    
df = get_data(mes_selecionado, ano_selecionado)

# Verificação se o DataFrame está vazio
if df.empty:
    total = 0.0
    saldo = 1000.0
    df_display = pd.DataFrame(columns=["created_at", "description", "value", "payment_type"])
else:
    total = df["value"].sum()
    limite = 1000
    saldo = limite - total

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], format='mixed').dt.strftime("%d/%m/%Y")

    if "value" in df.columns:
        df["value"] = df["value"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

    df_display = df.drop(columns=["id"]) if "id" in df.columns else df

st.dataframe(df_display, use_container_width=True, hide_index=True)
st.divider()

col1, col2, col3 = st.columns(3)

# Definindo o limite como 1000 (fora do bloco condicional para evitar erro)
limite = 1000

col1.metric("Limite Total", f"R$ {limite:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), "%", delta_color="off", border=True)
col2.metric("Total Gasto", f"R$ {total:,.2f}".replace(",", "v").replace(".", ",").replace("v", ","), f"{(total / limite) * 100:.2f}%".replace(".", ",") if limite else "0%", border=True)
col3.metric("Saldo Total", f"R$ {saldo:,.2f}".replace(",", "v").replace(".", ",").replace("v", ","), f"{(saldo / limite) * 100:.2f}%".replace(".", ",") if limite else "0%", border=True)

