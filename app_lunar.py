import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import calendar
import ephem

# Configuración
st.set_page_config(page_title="Calendario Lunar SV", layout="wide")

# Datos SV
tz_sv = pytz.timezone('America/El_Salvador')
hoy = datetime.now(tz_sv)

# Memoria de Mes y Año
if 'm_id' not in st.session_state:
    st.session_state.m_id = hoy.month
if 'anio_id' not in st.session_state:
    st.session_state.anio_id = hoy.year

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    div[data-testid="stNumberInput"] label { display: none !important; }
    .title { text-align: center; color: white; font-size: 32px; font-weight: bold; margin-bottom: 20px; }
    .label { font-size: 26px !important; color: #FF8C00 !important; font-weight: bold !important; text-align: center; margin-top: 15px; }
    div[data-testid="stNumberInput"] { width: 180px !important; margin: 0 auto !important; }
    input { font-size: 26px !important; font-weight: bold !important; text-align: center !important; }
    
    /* Botones de Meses */
    div.stButton > button {
        width: 100%; height: 50px !important; font-size: 18px !important;
        font-weight: bold !important; background-color: #1a1a1a !important;
        border: 1px solid #444 !important; color: #eee !important;
    }
    .stButton>button:hover { border-color: #FF8C00 !important; color: #FF8C00 !important; }
    
    .card { border: 1.5px solid #444; border-radius: 12px; background: #1a1a1a; padding: 15px; margin-top: 20px; }
    .item { font-size: 18px; color: #eee; margin-bottom: 8px; display: flex; align-items: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selector de Año
st.markdown("<p class='label'>Año:</p>", unsafe_allow_html=True)
anio = st.number_input("Año", min_value=2024, max_value=2030, value=st.session_state.anio_id)

# 2. Selector de Mes
st.markdown("<p class='label'>Selecciona el Mes:</p>", unsafe_allow_html=True)
meses_n = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_f = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

cols = st.columns(4)
for idx, m_nombre in enumerate(meses_n):
    with cols[idx % 4]:
        if st.button(m_nombre, key=f"btn_{idx}"):
            st.session_state.m_id = idx + 1
            st.rerun()

mes_sel = st.session_state.m_id
nombre_mes = meses_f[mes_sel-1]

# --- LÓGICA LUNAR RÁPIDA ---
def calcular_luna(a, m):
    d_inicio = datetime(a, m, 1)
    u_dia = calendar.monthrange(a, m)[1]
    fases = {}
    
    # Próxima Luna Nueva
    n_m = ephem.next_new_moon(d_inicio)
    dt_nm = n_m.datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)
    
    # Próxima Luna Llena
    f_m = ephem.next_full_moon(d_inicio)
    dt_fm = f_m.datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)
    
    if dt_nm.month == m and dt_nm.year == a:
        fases[dt_nm.day] = "🌑"
        # Celebración (si es antes de las 6pm, es mañana; si es después, pasado mañana)
        c_dia = dt_nm.day + 1 if dt_nm.hour < 18 else dt_nm.day + 2
        if c_dia <= u_dia: fases[c_dia] = "🌘"
    
    if dt_fm.month == m and dt_fm.year == a:
        fases[dt_fm.day] = "🌕"
        
    return fases, dt_nm

luna_map, fecha_nueva = calcular_luna(anio, mes_sel)

# --- TABLA HTML ---
filas = ""
for sem in calendar.Calendar(firstweekday=6).monthdayscalendar(anio, mes_sel):
    f_h = "<tr>"
    for d in sem:
        if d == 0: f_h += "<td></td>"
        else:
            ic, b_s = "", ""
            if d in luna_map:
                ic = luna_map[d]
                if ic == "🌘": b_s = "border: 1.5px solid #FF8C00;"
            
            if d == hoy.day and mes_sel == hoy.month and anio == hoy.year:
                b_s = "border: 1.5px solid #00FF7F; background: rgba(0,255,127,0.1);"
            
            f_h += f"<td style='{b_s}'><div class='n'>{d}</div><div class='e'>{ic}</div></td>"
    filas += f_h + "</tr>"

html = f"""
<div style='text-align:center; color:#FF8C00; font-size:26px; font-weight:bold; margin-bottom:10px;'>{nombre_mes} {anio}</div>
<style>
    table {{ width:100%; border-collapse:collapse; color:white; table-layout:fixed; }}
    th {{ color:#FF4B4B; font-size:14px; padding-bottom:5px; }}
    td {{ border:1px solid #333; height:80px; vertical-align:top; padding:5px; }}
    .n {{ font-size:18px; font-weight:bold; }}
    .e {{ font-size:30px; text-align:center; }}
</style>
<table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas}</table>
"""
components.html(html, height=520)

# Información final
st.markdown(f"""
<div class="card">
    <div style="color:#FF8C00; font-weight:bold; font-size:20px; margin-bottom:10px;">Simbología:</div>
    <div class="item">🟢 <b>Hoy:</b> {hoy.strftime('%d/%m/%y')}</div>
    <div class="item">🌑 <b>Luna Nueva:</b> {fecha_nueva.strftime('%d/%m %I:%M %p')} (SV)</div>
    <div class="item">🌘 <b>Día de Celebración</b> (Naranja)</div>
</div>
""", unsafe_allow_html=True)
