import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# Configuración inicial
st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)

# --- ESTILOS CSS REFINADOS ---
st.markdown("""
    <style>
    .main-title { text-align: center; color: white; font-size: 30px; font-weight: bold; margin-bottom: 0px; }
    .big-font {
        font-size: 18px !important; 
        font-weight: bold; 
        color: #FF8C00; 
        margin-top: 15px !important;
        margin-bottom: 5px !important;
        text-align: center;
    }
    
    /* BOTONES DE MES MÁS PEQUEÑOS */
    button[kind="secondary"] {
        border: 1.2px solid #FF8C00 !important;
        border-radius: 8px !important;
        height: 32px !important; /* Altura reducida */
        font-size: 14px !important; /* Letra más pequeña */
        font-weight: normal !important;
        padding: 0px !important;
        margin-bottom: -10px !important;
    }

    /* Ajuste de columnas para que no se separen tanto */
    [data-testid="stHorizontalBlock"] {
        gap: 5px !important;
        margin: 0 auto !important;
        max-width: 350px !important;
    }

    /* Cuadros de abajo */
    .info-card { 
        border: 1px solid #444; 
        padding: 12px; 
        border-radius: 10px; 
        background-color: #1a1a1a; 
        margin: 8px auto !important;
        max-width: 400px;
    }
    .info-item { font-size: 15px; color: #ddd; margin-bottom: 5px; display: flex; align-items: center; }

    /* Centrar input de año */
    div[data-testid="stNumberInput"] { width: 120px !important; margin: 0 auto !important; }
    input { font-size: 20px !important; font-weight: bold !important; text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selector de Año
st.markdown('<p class="big-font">Año:</p>', unsafe_allow_html=True)
anio = st.number_input("", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year, label_visibility="collapsed")

# 2. Selector de Mes
st.markdown('<p class="big-font">Mes:</p>', unsafe_allow_html=True)
meses_abr = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

if 'mes_sel' not in st.session_state:
    st.session_state.mes_sel = datetime.now(tz_sv).month

# Dibujar botones compactos
for i in range(0, 12, 3):
    cols = st.columns(3)
    for j in range(3):
        idx = i + j
        if idx < 12:
            if cols[j].button(meses_abr[idx], key=f"m_{idx}", use_container_width=True):
                st.session_state.mes_sel = idx + 1

mes = st.session_state.mes_sel

# --- CÁLCULOS ---
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
iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# Construir tabla
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: fila += "<td></td>"
        else:
            icons, b_style = "", ""
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB":
                    icons += iconos_fases.get(f_tipo, "")
                    if f_tipo == 0:
                        t_conj = fases_dict[dia][1]
                        info_utc = f"{t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M')} (UTC)"
                        info_sv = f"{t_conj.strftime('%d/%m/%y %I:%M %p')} (SV)"
                        t_s0, t_s1 = ts.from_datetime(t_conj.replace(hour=0, minute=0)), ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia: fases_dict[target_day] = ["CELEB", None]
            
            if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"
                b_style = "style='border: 1.5px solid #FF8C00; border-radius: 6px;'"
            
            if dia in equi_dict and equi_dict[dia] == 0: icons += "🌸"
            fila += f"<td {b_style}><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    filas_html += fila + "</tr>"

# Render de Tabla
html_cal = f"""
<div style='text-align:center; color:#FF8C00; font-size:22px; font-weight:bold; margin-bottom:8px; font-family:sans-serif;'>
    {meses_nombres[mes-1]} {anio}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; border-bottom: 1px solid #333; }}
    th {{ color: #FF4B4B; font-size: 14px; text-align: center; padding-bottom: 5px; font-family: sans-serif; }}
    td {{ border: 1px solid #333; height: 65px; vertical-align: top; padding: 4px; box-sizing: border-box; }}
    .n {{ font-size: 15px; font-weight: bold; font-family: sans-serif; }}
    .e {{ font-size: 24px; text-align: center; margin-top: 2px; line-height: 1; }}
</style>
<table>{header}{filas_html}</table>
"""
components.html(html_cal, height=460)

# 3. Leyendas
st.markdown('<p class="big-font" style="margin-top:0px !important;">Significado:</p>', unsafe_allow_html=True)
st.markdown(f"""
<div class="info-card">
    <div class="info-item">🌑 Nueva | 🌘 Celebración</div>
    <div class="info-item">🌸 Equinoccio | 🌕 Luna Llena</div>
</div>
<div class="info-card">
    <div class="info-item">🌎 {info_utc if info_utc else '---'}</div>
    <div class="info-item">📍 {info_sv if info_sv else '---'}</div>
</div>
""", unsafe_allow_html=True)
