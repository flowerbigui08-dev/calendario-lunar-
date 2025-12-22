import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import calendar
import ephem

# Configuración básica
st.set_page_config(page_title="Luna SV", layout="wide")

# Memoria de la app
if 'm_id' not in st.session_state:
    st.session_state.m_id = datetime.now(pytz.timezone('America/El_Salvador')).month

# Estilos básicos
st.markdown("""
    <style>
    .stButton>button { width:100%; height:50px; font-weight:bold; margin-bottom:5px; }
    .label { color: #FF8C00; font-size: 24px; font-weight: bold; text-align: center; }
    div[data-testid="stNumberInput"] label { display: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 Calendario Lunar")

# Selector de Año
st.markdown("<p class='label'>Año</p>", unsafe_allow_html=True)
anio = st.number_input("", min_value=2024, max_value=2030, value=2025)

# Selector de Mes
st.markdown("<p class='label'>Selecciona Mes</p>", unsafe_allow_html=True)
meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
cols = st.columns(4)
for i, m in enumerate(meses):
    with cols[i % 4]:
        if st.button(m, key=f"m{i}"):
            st.session_state.m_id = i + 1
            st.rerun()

# Lógica Lunar Simple
m_sel = st.session_state.m_id
tz = pytz.timezone('America/El_Salvador')
fecha_base = ephem.Date(datetime(anio, m_sel, 1))
proxima_nueva = ephem.next_new_moon(fecha_base).datetime().replace(tzinfo=pytz.utc).astimezone(tz)

# Construir Calendario HTML
cal = calendar.Calendar(firstweekday=6)
filas = ""
for semana in cal.monthdayscalendar(anio, m_sel):
    fila = "<tr>"
    for dia in semana:
        if dia == 0:
            fila += "<td></td>"
        else:
            txt = ""
            estilo = ""
            if dia == proxima_nueva.day and proxima_nueva.month == m_sel:
                txt = "🌑"
                # Día de celebración (Lógica simple)
                celeb = dia + 1 if proxima_nueva.hour < 18 else dia + 2
                st.session_state.dia_c = celeb
            
            # Dibujar celebración si toca
            if 'dia_c' in st.session_state and dia == st.session_state.dia_c:
                txt = "🌘"
                estilo = "border: 2px solid #FF8C00;"

            fila += f"<td style='{estilo} border: 1px solid #444; height:70px; vertical-align:top;'><b>{dia}</b><br><center style='font-size:25px;'>{txt}</center></td>"
    filas += fila + "</tr>"

html = f"""
<table style='width:100%; border-collapse:collapse; color:white; font-family:sans-serif;'>
    <tr style='color:#FF4B4B;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>
    {filas}
</table>
"""
components.html(html, height=500)

st.write(f"🌑 **Luna Nueva:** {proxima_nueva.strftime('%d/%m/%Y %I:%M %p')}")
