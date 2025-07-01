import streamlit as st
import pandas as pd
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
sheet = client.open("Dummy").worksheet("Output")
raw = sheet.get_all_values()

if len(raw) < 4:
    st.error("Data di sheet kurang dari 4 baris (header1, header2, header3, value).")
    st.stop()

header1 = raw[0]  # Level_1
header2 = raw[1]  # Level_2
header3 = raw[2]  # Level_3
values  = raw[3]  # Value

# === PARSING DATA KE DATAFRAME ===
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
    except:
        continue

df = pd.DataFrame(rows)

# === FUNGSI FORMAT RUPIAH ===
def format_rupiah(value):
    if value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f} T"
    elif value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} M"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f} Jt"
    else:
        return f"{value:,}".replace(",", ".")

# === BIKIN MERMAID SYNTAX ===
st.title("Diagram Pohon Dana (Mermaid.js dari Google Sheets)")

if df.empty:
    st.warning("Data kosong atau belum siap.")
else:
    mermaid = ["graph TD"]

    for _, row in df.iterrows():
        lv1 = row["Level_1"].replace(" ", "_")
        lv2 = row["Level_2"].replace(" ", "_")
        lv3 = row["Level_3"].replace(" ", "_")
        val_label = format_rupiah(row["Value"])

        # Buat node hierarki: Level_1 → Level_2 → Level_3
        mermaid.append(f'{lv1}["{row["Level_1"]}"] --> {lv2}["{row["Level_2"]}"]')
        mermaid.append(f'{lv2} --> {lv3}["{row["Level_3"]}<br>{val_label}"]')

    mermaid_code = "\n".join(mermaid)

    # === TAMPILKAN DI STREAMLIT ===
    st.markdown("```mermaid\n" + mermaid_code + "\n```")
    st.caption("Diagram akan otomatis mengikuti isi Google Sheets.")
