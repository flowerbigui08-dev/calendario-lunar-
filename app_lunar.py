import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import pytz
import calendar
import ephem  # Librería ligera que no requiere descargas pesadas

# 1. CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="Calendario Lunar SV", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
hoy = datetime.now(tz_sv)

# Estado de la sesión para el mes
if 'm_id' not in st.session_state:
    st.session_state.m_id = hoy.month
if 'anio_id' not in st.session_state:
    st.session_state.anio_id = hoy.year

# --- ESTILOS CSS REFORZADOS ---
st.markdown("""
    <style>
    div[data-testid="stNumberInput"] label { display: none !important; }
    .title { text-align: center; color: white; font-size: 30px; font-weight: bold; }
    .label { font-size: 24px !important; color: #FF8C00 !important; font-weight: bold !important; text-align: center; margin-top: 10px; }
    
    /* Botones de Meses Gigantes */
    div.stButton > button {
        width: 100%; height: 55px !important; font-size: 18px !important;
        font-weight: bold !important; background-color: #1a1a1a !important;
        border: 1px solid #444 !important; color: #eee !important;
        margin-bottom: 5px;
    }
    /* Estilo para el botón seleccionado */
    .st-emotion-cache-199v05y { border: 2px solid #FF8C00 !important; }

    .card { border: 1.5px solid #444; border-radius: 12px; background: #1a1a1a; padding: 15px; margin-top: 15px; }
    .item { font-size: 18px; color: #eee; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>🌙 Calendario Lunar SV</h1>", unsafe_allow_html=True)

# 1. Selector de Año
st.markdown("<p class='label'>Año:</p>", unsafe_allow_html=True)
anio = st.number_input("Año", min_value=2024, max_value=2030, value=st.session_state.anio_id)

# 2. Selector de Mes (Botones)
st.markdown("<p class='label'>Selecciona el Mes:</p>", unsafe_allow_html=True)
meses_n = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_f = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

cols = st.columns(4) # 4 columnas para que los botones sean grandes en celular
for idx, m_nombre in enumerate(meses_n):
    with cols[idx % 4]:
        if st.button(m_nombre, key=f"m_{idx}"):
            st.session_state.m_id = idx + 1
            st.rerun()

mes_sel = st.session_state.m_id
nombre_mes = meses_f[mes_sel-1]

# --- LÓGICA ASTRONÓMICA (EPHEM - ULTRA RÁPIDA) ---
def obtener_fases(a, m):
    primer_dia = datetime(a, m, 1)
    ultimo_dia = calendar.monthrange(a, m)[1]
    fecha_busqueda = ephem.Date(primer_dia)
    
    fases = {}
    # Buscar Luna Nueva
    nn = ephem.next_new_moon(fecha_busqueda)
    ln = ephem.next_full_moon(fecha_busqueda)
    
    # Convertir a hora de SV
    dt_nn = nn.datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)
    dt_ln = ln.datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)
    
    if dt_nn.month == m and dt_nn.year == a:
        fases[dt_nn.day] = ("🌑", dt_nn)
        # Calcular día de celebración
        # El Salvador Atardecer aprox 17:45
        atardecer = dt_nn.replace(hour=17, minute=45)
        dia_celeb = dt_nn.day + 1 if dt_nn < atardecer else dt_nn.day + 2
        if dia_celeb <= ultimo_dia:
            fases[dia_celeb] = ("🌘", None)
            
    if dt_ln.month == m and dt_ln.year == a:
        fases[dt_ln.day] = ("🌕", dt_ln)
        
    return fases, dt_nn

luna_map, fecha_nueva = obtener_fases(anio, mes_sel)

# Dibujar Tabla
filas = ""
for sem in calendar.Calendar(firstweekday=6).monthdayscalendar(anio, mes_sel):
    f_html = "<tr>"
    for d in sem:
        if d == 0: f_html += "<td></td>"
        else:
            ic, st_d = "", ""
            if d in luna_map:
                ic = luna_map[d][0]
                if ic == "🌘": st_d = "border: 2px solid #FF8C00;"
            
            if d == hoy.day and mes_sel == hoy.month and anio == hoy.year:
                st_d = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1);"
            
            f_html += f"<td style='{st_d}'><div class='n'>{d}</div><div class='e'>{ic}</div></td>"
    filas += f_html + "</tr>"

# Render Calendario
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

# Panel de información
if fecha_nueva.month == mes_sel:
    txt_nueva = fecha_nueva.strftime('%d/%m/%Y %I:%M %p')
else:
    txt_nueva = "No este mes"

st.markdown(f"""
<div class="card">
    <div style="color:#FF8C00; font-weight:bold; font-size:18px; margin-bottom:8px;">Detalles:</div>
    <div class="item">🌑 <b>Luna Nueva:</b> {txt_nueva}</div>
    <div class="item">🌘 <b>Celebración:</b> Marcada en Naranja</div>
    <div class="item">🟢 <b>Hoy es:</b> {hoy.strftime('%d/%m/%Y')}</div>
</div>
""", unsafe_allow_html=True)
