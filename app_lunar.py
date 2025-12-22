import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# 1. CONFIGURACIÓN Y CACHÉ (Para que cargue rápido)
st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

@st.cache_resource
def cargar_datos_astronomicos():
    # Carga los archivos pesados una sola vez y los guarda en memoria
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    return ts, eph

ts, eph = cargar_datos_astronomicos()

# Variables de tiempo y lugar
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

# Estado de la sesión para el mes
if 'mes_id' not in st.session_state:
    st.session_state.mes_id = hoy_sv.month - 1

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    div[data-testid="stNumberInput"] label { display: none !important; }
    .custom-label {
        font-size: 28px !important; color: #FF8C00 !important;
        font-weight: bold !important; text-align: center; margin: 15px 0 5px 0;
    }
    .main-title { text-align: center; color: white; font-size: 34px; font-weight: bold; }
    div[data-testid="stNumberInput"] { width: 180px !important; margin: 0 auto !important; }
    input { font-size: 28px !important; font-weight: bold !important; text-align: center !important; }

    /* Botones de Meses */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 65px !important; background-color: #1a1a1a;
        border-radius: 10px; color: #eee; font-size: 22px !important; 
        font-weight: bold; padding: 0 15px !important; border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] { border: 2px solid #FF8C00 !important; color: #FF8C00 !important; }

    .info-card {
        border: 1.5px solid #444; border-radius: 15px;
        background-color: #1a1a1a; padding: 15px; margin: 10px auto; max-width: 500px;
    }
    .info-item { font-size: 19px; color: #eee; margin-bottom: 10px; display: flex; align-items: center; }
    .emoji-span { font-size: 26px; margin-right: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selector de Año
st.markdown("<p class='custom-label'>Año:</p>", unsafe_allow_html=True)
anio = st.number_input("Año_Hid", min_value=2024, max_value=2030, value=hoy_sv.year)

# 2. Selector de Mes
st.markdown("<p class='custom-label'>Mes:</p>", unsafe_allow_html=True)
meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

tabs = st.tabs(meses_nombres)
mes_actual_idx = st.session_state.mes_id

# Detectar cambio de pestaña de forma eficiente
for i, tab in enumerate(tabs):
    with tab:
        if st.session_state.mes_id != i:
            st.session_state.mes_id = i
            st.rerun()
        nombre_mes_visual = meses_completos[i]

# --- CÁLCULOS OPTIMIZADOS ---
mes_sel = st.session_state.mes_id + 1
t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_sel, 1)))
ult_dia = calendar.monthrange(anio, mes_sel)[1]
t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_sel, ult_dia, 23, 59)))

f_ev, f_ty = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
datos_luna = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(f_ev, f_ty)}

res_utc, res_sv = "---", "---"
iconos = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# Generar Tabla
filas_html = ""
for semana in calendar.Calendar(firstweekday=6).monthdayscalendar(anio, mes_sel):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: fila += "<td></td>"
        else:
            txt_i, b_style = "", ""
            if dia in datos_luna:
                tipo = datos_luna[dia][0]
                txt_i = iconos.get(tipo, "")
                if tipo == 0: # Luna Nueva
                    t_c = datos_luna[dia][1]
                    res_utc = t_c.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M')
                    res_sv = t_c.strftime('%d/%m/%y %I:%M %p')
                    # Cálculo celebración simplificado para velocidad
                    t_s0, t_s1 = ts.from_datetime(t_c.replace(hour=0, minute=0)), ts.from_datetime(t_c.replace(hour=23, minute=59))
                    t_sol, y_sol = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                    atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_sol, y_sol) if yi == 0), t_c.replace(hour=17, minute=45))
                    target = dia + 1 if t_c < atardecer else dia + 2
                    if target <= ult_dia: datos_luna[target] = ["CELEB", None]

            if dia == hoy_sv.day and mes_sel == hoy_sv.month and anio == hoy_sv.year:
                b_style = "border: 2px solid #00FF7F; background-color: rgba(0, 255, 127, 0.1);"
            elif dia in datos_luna and datos_luna[dia][0] == "CELEB":
                txt_i = "🌘"
                b_style = "border: 2px solid #FF8C00;"
            
            fila += f"<td><div class='n'>{dia}</div><div class='e'>{txt_i}</div></td>"
    filas_html += fila + "</tr>"

# Render
html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:30px; font-weight:bold; margin-bottom:10px;'>{nombre_mes_visual} {anio}</div>
<style>
    table {{ width: 100%; border-collapse: collapse; color: white; table-layout: fixed; }}
    th {{ color: #FF4B4B; padding-bottom: 5px; font-size: 16px; }}
    td {{ border: 1px solid #333; height: 85px; vertical-align: top; padding: 5px; }}
    .n {{ font-size: 20px; font-weight: bold; }}
    .e {{ font-size: 34px; text-align: center; }}
</style>
<table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>
"""
components.html(html_final, height=580)

# Leyendas
st.markdown(f"""
<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:20px;">Simbología y Datos:</div>
    <div class="info-item"><span style="width:18px; height:18px; border:2px solid #00FF7F; display:inline-block; margin-right:12px;"></span> Hoy</div>
    <div class="info-item"><span class="emoji-span">🌑</span> Luna Nueva: {res_sv} (SV)</div>
    <div class="info-item"><span class="emoji-span">🌘</span> Día de Celebración</div>
    <div class="info-item"><span class="emoji-span">🌕</span> Luna Llena</div>
</div>
""", unsafe_allow_html=True)
