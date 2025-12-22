import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# 1. OPTIMIZACIÓN DE CARGA (Para que no se quede en gris)
st.set_page_config(page_title="Calendario Lunar SV", layout="wide")

@st.cache_resource
def load_astro_data():
    # Esto solo se ejecuta una vez y se guarda en memoria para siempre
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    return ts, eph

try:
    ts, eph = load_astro_data()
except:
    # Si falla la carga pesada, usamos una alternativa ligera
    ts = api.load.timescale()
    eph = api.load('de421.bsp')

# Configuración Regional
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy = datetime.now(tz_sv)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    div[data-testid="stNumberInput"] label { display: none !important; }
    .title { text-align: center; color: white; font-size: 32px; font-weight: bold; margin-bottom: 20px; }
    .label { font-size: 26px !important; color: #FF8C00 !important; font-weight: bold !important; text-align: center; margin-top: 15px; }
    
    /* Input de Año */
    div[data-testid="stNumberInput"] { width: 180px !important; margin: 0 auto !important; }
    input { font-size: 26px !important; text-align: center !important; font-weight: bold !important; }

    /* Botones de Meses */
    div.stButton > button {
        width: 100%; height: 60px !important; font-size: 20px !important;
        font-weight: bold !important; background-color: #1a1a1a !important;
        border: 1px solid #444 !important; color: #eee !important;
    }
    div.stButton > button:active { border-color: #FF8C00 !important; color: #FF8C00 !important; }
    
    .card { border: 1.5px solid #444; border-radius: 12px; background: #1a1a1a; padding: 15px; margin: 10px 0; }
    .item { font-size: 18px; color: #eee; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selector de Año
st.markdown("<p class='label'>Año:</p>", unsafe_allow_html=True)
anio = st.number_input("Anio", min_value=2024, max_value=2030, value=hoy.year)

# 2. Selector de Mes (Cambiamos Tabs por Columnas para evitar el error de carga)
st.markdown("<p class='label'>Mes:</p>", unsafe_allow_html=True)
meses_n = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_f = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Usamos Session State para que no se pierda el mes
if 'm_id' not in st.session_state:
    st.session_state.m_id = hoy.month

cols = st.columns(6)
for idx, m_nombre in enumerate(meses_n):
    with cols[idx % 6]:
        if st.button(m_nombre, key=f"btn_{idx}"):
            st.session_state.m_id = idx + 1

mes_sel = st.session_state.m_id
nombre_mes = meses_f[mes_sel-1]

# --- CÁLCULOS ---
t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_sel, 1)))
u_dia = calendar.monthrange(anio, mes_sel)[1]
t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_sel, u_dia, 23, 59)))

f_ev, f_ty = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
luna_map = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(f_ev, f_ty)}

info_v = {"sv": "---", "utc": "---"}
icons = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# Dibujar Tabla
filas = ""
for sem in calendar.Calendar(firstweekday=6).monthdayscalendar(anio, mes_sel):
    f_html = "<tr>"
    for d in sem:
        if d == 0: f_html += "<td></td>"
        else:
            ic, st_d = "", ""
            if d in luna_map:
                tp = luna_map[d][0]
                ic = icons.get(tp, "")
                if tp == 0: # Luna Nueva
                    t_conj = luna_map[d][1]
                    info_v["utc"] = t_conj.astimezone(pytz.utc).strftime('%d/%m %H:%M')
                    info_v["sv"] = t_conj.strftime('%d/%m %I:%M %p')
                    # Cálculo celebración
                    t_s0 = ts.from_datetime(t_conj.replace(hour=0, minute=0))
                    t_s1 = ts.from_datetime(t_conj.replace(hour=23, minute=59))
                    t_sol, y_sol = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                    atard = next((ti.astimezone(tz_sv) for ti, yi in zip(t_sol, y_sol) if yi == 0), t_conj.replace(hour=17, minute=45))
                    targ = d + 1 if t_conj < atard else d + 2
                    if targ <= u_dia: luna_map[targ] = ["CELEB", None]
            
            if d == hoy.day and mes_sel == hoy.month and anio == hoy.year:
                st_d = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1);"
            elif d in luna_map and luna_map[d][0] == "CELEB":
                ic = "🌘"
                st_d = "border: 2px solid #FF8C00;"
            
            f_html += f"<td style='{st_d}'><div class='n'>{d}</div><div class='e'>{ic}</div></td>"
    filas += f_html + "</tr>"

# Render Calendario
html = f"""
<div style='text-align:center; color:#FF8C00; font-size:28px; font-weight:bold; margin-bottom:10px;'>{nombre_mes} {anio}</div>
<style>
    table {{ width:100%; border-collapse:collapse; color:white; table-layout:fixed; }}
    th {{ color:#FF4B4B; font-size:16px; padding-bottom:10px; }}
    td {{ border:1px solid #333; height:85px; vertical-align:top; padding:5px; }}
    .n {{ font-size:19px; font-weight:bold; }}
    .e {{ font-size:32px; text-align:center; }}
</style>
<table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas}</table>
"""
components.html(html, height=580)

# Información inferior
st.markdown(f"""
<div class="card">
    <div style="color:#FF8C00; font-weight:bold; font-size:20px; margin-bottom:10px;">Información:</div>
    <div class="item">🟢 <b>Hoy:</b> {hoy.strftime('%d/%m/%Y')}</div>
    <div class="item">🌑 <b>Nueva:</b> {info_v['sv']} (SV)</div>
    <div class="item">🌘 <b>Celebración:</b> Al día siguiente</div>
</div>
""", unsafe_allow_html=True)
