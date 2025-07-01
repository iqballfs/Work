import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === AUTH GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("reportbmn.json", scope)
client = gspread.authorize(creds)

# === AMBIL DATA DARI SHEET ===
sheet = client.open("Dummy").worksheet("Output")  # Ganti dengan nama sheet kamu
raw = sheet.get_all_values()

header1 = raw[0]  # Level_1
header2 = raw[1]  # Level_2
values  = raw[2]  # Nilai (hasil formula)

rows = []
last_major = ""
for i in range(len(values)):
    h1 = header1[i].strip()
    h2 = header2[i].strip()
    val = values[i].replace(".", "").replace(",", "").strip()

    if h1 != "":
        last_major = h1

    if h2 == "" or val == "":
        continue

    try:
        val_int = int(val)
        rows.append({
            "Level_1": last_major,
            "Level_2": h1 if h1 != last_major else h2,  # fallback kalau tidak ada Level_2
            "Level_3": h2,
            "Value": val_int
        })
    except:
        continue

df = pd.DataFrame(rows)

# === STREAMLIT DASHBOARD ===
st.title("Distribusi Dana Live Report (Terhubung Google Sheets)")
st.dataframe(df)

# Sunburst chart
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
