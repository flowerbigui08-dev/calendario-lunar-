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

# --- ESTILOS CSS REFORZADOS ---
st.markdown("""
    <style>
    .main-title { text-align: center; color: white; font-size: 32px; font-weight: bold; margin-bottom: 20px; }
    
    /* Etiquetas de Año y Mes más grandes */
    .stNumberInput label, .stRadio label {
        font-size: 24px !important;
        color: #FF8C00 !important;
        font-weight: bold !important;
        display: block;
        text-align: center;
    }

    /* Tamaño de letra dentro del selector de año */
    input { font-size: 26px !important; font-weight: bold !important; text-align: center !important; }

    /* Tamaño de letra de los meses (Radio Button) */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        font-size: 20px !important;
        justify-content: center;
    }
    
    div[data-testid="stRadio"] label {
        font-size: 20px !important;
        padding: 10px !important;
    }

    /* Cuadros de información (Una línea por emoji) */
    .info-card {
        border: 1.5px solid #444;
        border-radius: 15px;
        background-color: #1a1a1a;
        padding: 20px;
        margin: 15px auto;
        max-width: 450px;
    }
    .info-item { 
        font-size: 19px; 
        color: #eee; 
        margin-bottom: 12px; 
        display: flex; 
        align-items: center; 
    }
    .emoji-span { font-size: 26px; margin-right: 15px; }

    /* Centrar selectores */
    div[data-testid="stNumberInput"] { width: 180px !important; margin: 0 auto !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selector de Año (Sin que salte teclado al inicio)
anio = st.number_input("Selecciona el Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)

# 2. Selector de Mes (Radio Button para evitar el teclado)
meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_nombre = st.radio("Selecciona el Mes", meses_nombres, index=datetime.now(tz_sv).month - 1, horizontal=True)
mes = meses_nombres.index(mes_nombre) + 1

# --- CÁLCULOS ASTRONÓMICOS ---
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
iconos_cal = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

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
                    icons += iconos_cal.get(f_tipo, "")
                    if f_tipo == 0:
                        t_conj = fases_dict[dia][1]
                        info_utc = t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M') + " (UTC)"
                        info_sv = t_conj.strftime('%d/%m/%y %I:%M %p') + " (SV)"
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

# HTML del Calendario
html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:24px; font-weight:bold; margin-bottom:10px;'>
    {mes_nombre} {anio}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; }}
    th {{ color: #FF4B4B; font-size: 16px; text-align: center; padding-bottom: 8px; }}
    td {{ border: 1px solid #333; height: 75px; vertical-align: top; padding: 5px; box-sizing: border-box; }}
    .n {{ font-size: 18px; font-weight: bold; }}
    .e {{ font-size: 28px; text-align: center; margin-top: 4px; }}
</style>
<table>{header}{filas_html}</table>
"""
components.html(html_final, height=500)

# 3. Cuadros de Leyenda (Línea por emoji y letras grandes)
st.markdown(f"""
<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:20px; text-align:center;">Significado:</div>
    <div class="info-item"><span class="emoji-span">🌑</span> Luna Nueva (Conjunción)</div>
    <div class="info-item"><span class="emoji-span">🌘</span> Día de Celebración</div>
    <div class="info-item"><span class="emoji-span">🌸</span> Equinoccio de Primavera</div>
    <div class="info-item"><span class="emoji-span">🌕</span> Luna Llena</div>
</div>

<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:20px; text-align:center;">Datos de la Conjunción:</div>
    <div class="info-item"><span class="emoji-span">🌎</span> {info_utc if info_utc else '---'}</div>
    <div class="info-item"><span class="emoji-span">📍</span> {info_sv if info_sv else '---'}</div>
</div>
""", unsafe_allow_html=True)
