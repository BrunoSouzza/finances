import streamlit as st
import pandas as pd
from services.SupabaseClient import SupabaseClient

st.set_page_config(page_title="Apartment", layout="wide")
st.subheader("\U0001F3E0 Apartment")

supabase = SupabaseClient(
    base_url=st.secrets["supabase"]["url"],
    api_key=st.secrets["supabase"]["key"]
)

df = supabase.get("apartment")

total = df["value"].sum() if not df.empty else 0.0
paid = df.loc[df["status"] == True, "value"].sum() if not df.empty else 0.0
saldo = total - paid

if not df.empty:
    df["expired_at"] = pd.to_datetime(df["expired_at"], errors='coerce')
    df = df.sort_values(by="expired_at")
    df["formatted_value"] = df["value"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
    df_display = df[["expired_at", "formatted_value", "installment", "status"]].copy()
    df_display["expired_at"] = df_display["expired_at"].dt.strftime("%d/%m/%Y")
else:
    df_display = pd.DataFrame(columns=["expired_at", "formatted_value", "installment", "status"])

row_height = 37
st.dataframe(df_display, use_container_width=True, hide_index=True, height=max(120, len(df_display) * row_height))

st.divider()

st.subheader("Pré Entrega")
col1, col2, col3 = st.columns(3)
col1.metric("Total Geral", f"R$ {total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), "100%", delta_color="off", border=True)
col2.metric("Total Pago", f"R$ {paid:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), f"{(paid / total * 100):.2f}%".replace(".", ",") if total else "0%", border=True)
col3.metric("Total Pendente", f"R$ {saldo:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), f"{(saldo / total * 100):.2f}%".replace(".", ",") if total else "0%", delta_color="inverse", border=True)

st.divider()

st.subheader("Pós Entrega")
col4, col5, col6 = st.columns(3)
valor_total, total_pago = 503000, 96000
saldo_restante = valor_total - total_pago
col4.metric("Valor Total", f"R$ {valor_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), "100%", delta_color="off", border=True)
col5.metric("Total Pago", f"R$ {total_pago:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), f"{(total_pago / valor_total * 100):.2f}%", border=True)
col6.metric("Saldo Restante", f"R$ {saldo_restante:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), f"{(saldo_restante / valor_total * 100):.2f}%", delta_color="inverse", border=True)

st.divider()
st.subheader("\u270F\ufe0f Editar Registro")

if not df.empty:
    for _, row in df.iterrows():
        with st.expander(f"{row['expired_at'].strftime('%d/%m/%Y')} | Parcela {row['installment']}"):
            with st.form(f"form_edit_{row['id']}"):
                new_value = st.number_input("Valor", value=float(row["value"]), step=100.0, format="%.2f")
                new_installment = st.text_input("Parcela", value=str(row["installment"]))
                new_status = st.selectbox("Status", [True, False], index=0 if row["status"] else 1)

                if st.form_submit_button("Atualizar"):
                    result = supabase.patch("apartment", row["id"], {
                        "value": new_value,
                        "installment": new_installment,
                        "status": new_status
                    })
                    if result.status_code == 200:
                        st.success("Registro atualizado com sucesso.")
                        st.rerun()
                    else:
                        st.error("Erro ao atualizar registro.")