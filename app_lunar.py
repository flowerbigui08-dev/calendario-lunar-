import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

st.set_page_config(page_title="Calendario Lunar", page_icon="🌙", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)

# --- TÍTULO PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 20px;'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# --- 1. SELECTOR DE AÑO (CENTRADO) ---
st.markdown("""
    <style>
    .big-font {
        font-size:22px !important; 
        font-weight: bold; 
        color: #FF8C00; 
        margin-top: 25px !important;
        margin-bottom: 12px !important;
        text-align: center;
    }
    div[data-testid="stNumberInput"] {
        width: 180px !important;
        margin: 0 auto !important;
    }
    input {font-size: 24px !important; font-weight: bold !important; text-align: center !important;}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="big-font">Selecciona el Año:</p>', unsafe_allow_html=True)
anio = st.number_input("", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year, label_visibility="collapsed")

# --- 2. BOTONERA DE MESES (NOMBRES COMPLETOS Y CENTRADO) ---
st.markdown('<p class="big-font" style="margin-top:35px !important;">Selecciona el Mes:</p>', unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Forzar centrado de la cuadrícula de botones */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 10px !important;
        max-width: 600px !important; /* Un poco más ancho para los nombres largos */
        margin: 0 auto !important;
        padding: 0 10px !important;
    }
    button[kind="secondary"] {
        border: 1px solid #FF8C00 !important;
        height: 55px !important;
        font-size: 14px !important; /* Ajuste para que quepa 'Septiembre' */
        font-weight: bold !important;
        color: white !important;
        background-color: transparent !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
    .info-card { 
        border: 1px solid #444; 
        padding: 15px; 
        border-radius: 8px; 
        background-color: #1a1a1a; 
        margin-top: 15px !important;
    }
    .info-item { font-size: 18px; color: #ddd; margin-bottom: 10px; display: flex; align-items: center; font-family: sans-serif; }
    .emoji-big { font-size: 24px; margin-right: 12px; }
    </style>
    """, unsafe_allow_html=True)

# Lista de meses completos
meses_nombres_lista = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

if 'mes_sel' not in st.session_state:
    st.session_state.mes_sel = datetime.now(tz_sv).month

# Dibujar botones en 3 filas de 4
for r in range(3):
    cols = st.columns(4)
    for c in range(4):
        idx = r * 4 + c
        if cols[c].button(meses_nombres_lista[idx], key=f"m_{idx+1}"):
            st.session_state.mes_sel = idx + 1

mes = st.session_state.mes_sel

# --- LÓGICA DE CÁLCULO ---
ts = api.load.timescale()
eph = api.load('de421.bsp')
t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)))
ultimo_dia = calendar.monthrange(anio, mes)[1]
t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, ultimo_dia, 23, 59)))

t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}
t_equi, y_equi = almanac.find_discrete(t0, t1, almanac.seasons(eph))
equi_dict = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_equi, y_equi)}

info_utc, info_sv = "", ""
nombres_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# CABECERA DEL CALENDARIO
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: fila += "<td></td>"
        else:
            icons, estilo_celda = "", ""
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB": 
                    icons += nombres_fases.get(f_tipo, "")
                    if f_tipo == 0: 
                        t_conj = fases_dict[dia][1]
                        info_utc = f"{t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M')} (UTC)"
                        info_sv = f"{t_conj.strftime('%d/%m/%y %I:%M %p')} (SV)"
                        t_s0, t_s1 = ts.from_datetime(t_conj.replace(hour=0, minute=0)), ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia: fases_dict[target_day] = ["CELEB",
