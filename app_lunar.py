import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import calendar
import ephem

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Luna SV", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
hoy = datetime.now(tz_sv)

# Memoria de la App
if 'm_id' not in st.session_state:
    st.session_state.m_id = hoy.month

# Estilos CSS
st.markdown("""
    <style>
    .stButton>button { width:100%; height:55px; font-weight:bold; background:#1a1a1a; color:#eee; border:1px solid #444; }
    .stButton>button:hover { border-color:#FF8C00; color:#FF8C00; }
    .title { text-align:center; color:white; font-size:30px; font-weight:bold; }
    .label { color:#FF8C00; font-size:24px; font-weight:bold; text-align:center; margin:10px 0; }
    div[data-testid="stNumberInput"] label { display:none; }
    div[data-testid="stNumberInput"] { width:160px !important; margin:0 auto !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# Selector Año
st.markdown("<p class='label'>Año:</p>", unsafe_allow_html=True)
anio = st.number_input("Anio", min_value=2024, max_value=2030, value=2025)

# Selector Mes (Botones)
st.markdown("<p class='label'>Mes:</p>", unsafe_allow_html=True)
meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
cols = st.columns(4)
for i, m in enumerate(meses):
    with cols[i % 4]:
        if st.button(m, key=f"m{i}"):
            st.session_state.m_id = i + 1
            st.rerun()

m_sel = st.session_state.m_id

# --- LÓGICA LUNAR ---
d_inicio = datetime(anio, m_sel, 1)
n_m = ephem.next_new_moon(d_inicio)
dt_nm = n_m.datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)

# Calendario
cal = calendar.Calendar(firstweekday=6)
filas = ""
for semana in cal.monthdayscalendar(anio, m_sel):
    fila = "<tr>"
    for d in semana:
        if d == 0: fila += "<td></td>"
        else:
            txt, b_s = "", "border: 1px solid #333;"
            if d == dt_nm.day and dt_nm.month == m_sel:
                txt = "🌑"
                # Día de celebración (Lógica: si es antes de las 6pm es mañana, si no pasado)
                c_dia = d + 1 if dt_nm.hour < 18 else d + 2
                st.session_state.c_d = c_dia
            
            if 'c_d' in st.session_state and d == st.session_state.c_d:
                txt = "🌘"
                b_s = "border: 2px solid #FF8C00;"
            
            if d == hoy.day and m_sel == hoy.month and anio == hoy.year:
                b_s = "border: 2px solid #00FF7F; background:rgba(0,255,127,0.1);"
                
            fila += f"<td style='{b_s} height:75px; vertical-align:top; padding:5px;'><b>{d}</b><br><center style='font-size:28px;'>{txt}</center></td>"
    filas += fila + "</tr>"

html = f"""
<table style='width:100%; border-collapse:collapse; color:white; font-family:sans-serif;'>
    <tr style='color:#FF4B4B;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>
    {filas}
</table>
"""
components.html(html, height=500)
st.write(f"🌑 **Luna Nueva:** {dt_nm.strftime('%d/%m/%Y %I:%M %p')}")
