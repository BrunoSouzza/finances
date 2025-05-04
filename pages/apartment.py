import streamlit as st
import requests
import pandas as pd

# Configurações da página
st.set_page_config(page_title="Apartment", layout="wide")
st.title("🏠 Apartment")

API_KEY = st.secrets["supabase"]["key"]
SUPABASE_URL = f"{st.secrets['supabase']['url']}/apartment"

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Buscar dados da Supabase
response = requests.get(SUPABASE_URL, headers=HEADERS)
if response.status_code == 200:
    df = pd.DataFrame(response.json())
else:
    st.error("Erro ao buscar dados.")
    df = pd.DataFrame()

# Tratamento e ordenação
if not df.empty:
    total = df["value"].sum()
    sum = df.loc[df["status"] == True, "value"].sum()
    saldo = total - sum

    if "expired_at" in df.columns:
        df["expired_at"] = pd.to_datetime(df["expired_at"], format='mixed')
        df = df.sort_values(by="expired_at")

    if "value" in df.columns:
        df["formatted_value"] = df["value"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

    df_display = df.copy()
    df_display["expired_at"] = df_display["expired_at"].dt.strftime("%d/%m/%Y")
    df_display = df_display[["expired_at", "formatted_value", "installment", "status"]]
else:    
    total = 0.0
    saldo = 1000.0
    df_display = pd.DataFrame(columns=["expired_at", "value", "installment", "status"])

# Exibir tabela com altura dinâmica
row_height = 37
min_height = 120
dynamic_height = max(min_height, len(df_display) * row_height)

st.dataframe(df_display, use_container_width=True, hide_index=True, height=dynamic_height)

st.divider()

# Métricas
st.subheader("Pré Entrega")
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Geral",
    f"R$ {total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
    "100%",
    delta_color="inverse",
    border=True
)

col2.metric(
    "Total Pago",
    f"R$ {sum:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
    f"{(sum / total) * 100:.2f}%".replace(".", ","),
    delta_color="normal",
    border=True
)

col3.metric(
    "Total Pendente",
    f"R$ {saldo:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
    f"{(saldo / total) * 100:.2f}%".replace(".", ","),
    delta_color="normal",
    border=True
)

st.subheader("Pós Entrega")
col4, col5, col6 = st.columns(3)

valor_total = 503000
total_pago = 96000
saldo_restante = valor_total - total_pago

col4.metric("Valor Total", f"R$ {valor_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), "100%", delta_color="inverse", border=True)
col5.metric("Total Pago", f"R$ {total_pago:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), f"{(total_pago / valor_total) * 100:.2f}%", delta_color="normal", border=True)
col6.metric("Saldo Restante", f"R$ {saldo_restante:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), f"{(saldo_restante / valor_total) * 100:.2f}%", delta_color="normal", border=True)


st.divider()
st.subheader("✏️ Editar Registro")

# Formulário de edição
if not df.empty:
    for index, row in df.iterrows():
        with st.expander(f"{row['expired_at'].strftime('%d/%m/%Y')} | Parcela {row['installment']}"):
            with st.form(f"form_edit_{row['id']}"):
                new_value = st.number_input("Valor", value=float(row["value"]), step=100.0)
                new_installment = st.text_input("Parcela", value=str(row["installment"]))
                new_status = st.selectbox("Status", [True, False], index=0 if row["status"] else 1)

                submitted = st.form_submit_button("Atualizar")
                if submitted:
                    payload = {
                        "value": new_value,
                        "installment": new_installment,
                        "status": new_status
                    }

                    update_url = f"{SUPABASE_URL}?id=eq.{row['id']}"
                    patch_response = requests.patch(update_url, headers=HEADERS, json=payload)

                    if patch_response.status_code == 200:
                        st.success("Registro atualizado com sucesso.")
                        st.rerun()
                    else:
                        st.error("Erro ao atualizar registro.")
