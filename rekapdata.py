import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import json

# === AUTH GOOGLE SHEETS DARI st.secrets ===
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

service_account_info = json.loads(st.secrets["gcp_service_account"])
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)

# === AMBIL DATA DARI SHEET ===
sheet = client.open("Dummy").worksheet("Output")  # Ganti dengan nama sheet kamu
raw = sheet.get_all_values()

# --- Pastikan sheet memiliki minimal 4 baris ---
if len(raw) < 4:
    st.error("Data di sheet kurang dari 4 baris (header1, header2, header3, value).")
    st.stop()

# Ambil baris-baris header dan nilai
header1 = raw[0]  # Level_1
header2 = raw[1]  # Level_2
header3 = raw[2]  # Level_3
values  = raw[3]  # Value

# === PARSING DATA ===
rows = []
for i in range(len(values)):
    h1 = header1[i].strip()
    h2 = header2[i].strip()
    h3 = header3[i].strip()
    val = values[i].replace(".", "").replace(",", "").strip()

    if not h1 or not h2 or not h3 or not val:
        continue

    try:
        val_int = int(val)
        rows.append({
            "Level_1": h1,
            "Level_2": h2,
            "Level_3": h3,
            "Value": val_int
        })
    except Exception as e:
        st.text(f"Kolom {i} skip karena error: {e}")
        continue

df = pd.DataFrame(rows)

def format_rupiah(value):
    if value >= 1_000_000_000_000:
        return f"Rp {value / 1_000_000_000_000:.1f}T"
    elif value >= 1_000_000_000:
        return f"Rp {value / 1_000_000_000:.1f}M"
    elif value >= 1_000_000:
        return f"Rp {value / 1_000_000:.1f}Jt"
    else:
        return f"Rp {value:,}".replace(",", ".")

df["Label"] = df.apply(
    lambda row: f'{row["Level_3"]}<br>{format_rupiah(row["Value"])}',
    axis=1
)

import plotly.graph_objects as go

# Buat kolom label gabungan biar tampil jelas
df["Label"] = df.apply(
    lambda row: f'{row["Level_3"]}<br>Rp {row["Value"]:,}'.replace(",", "."),
    axis=1
)

fig = px.sunburst(
    df,
    path=['Level_1', 'Level_2', 'Label'],  # gunakan Label di Level_3
    values='Value',
    color='Level_1',
    title="Struktur Dana Live Report (Live Data)",
)

# Tambahkan hovertemplate agar muncul detail saat mouse hover
fig.update_traces(
    hovertemplate='<b>%{label}</b><br>Nilai: Rp %{value:,}<extra></extra>',
)

fig.update_layout(
    height=900,
    margin=dict(t=50, l=0, r=0, b=0),
    uniformtext=dict(minsize=12, mode='hide')
)

# === STREAMLIT DASHBOARD ===
st.title("Distribusi Dana Live Report (Terhubung Google Sheets)")
st.write(f"Jumlah baris hasil parsing: {len(df)}")
st.dataframe(df)

# === SUNBURST CHART ===
if not df.empty:
    fig = px.sunburst(
        df,
        path=['Level_1', 'Level_2', 'Level_3'],
        values='Value',
        color='Level_1',
        title="Struktur Dana Live Report (Live Data)"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Data tidak ditemukan atau belum siap.")
