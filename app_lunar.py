import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# Configuración básica
st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)

# --- ESTILOS LIMPIOS ---
st.markdown("""
    <style>
    .main-title { text-align: center; color: white; font-size: 26px; font-weight: bold; margin-bottom: 10px; }
    .section-label { color: #FF8C00; font-weight: bold; text-align: center; margin-top: 10px; font-size: 16px; }
    
    /* Centrar selectores */
    div[data-testid="stSelectbox"], div[data-testid="stNumberInput"] {
        max-width: 250px;
        margin: 0 auto !important;
    }

    /* Estilo para los cuadros de información de abajo */
    .info-card {
        border: 1px solid #444;
        border-radius: 10px;
        background-color: #1a1a1a;
        padding: 12px;
        margin: 10px auto;
        max-width: 400px;
    }
    .info-text { font-size: 14px; color: #ddd; margin-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selectores Simples (Año y Mes)
col_a, col_b = st.columns(2)
with col_a:
    anio = st.number_input("Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)
with col_b:
    meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_nombre = st.selectbox("Mes", meses_nombres, index=datetime.now(tz_sv).month - 1)
    mes = meses_nombres.index(mes_nombre) + 1

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
iconos_cal = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# Construir tabla HTML
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
                        # Lógica celebración
                        t_s0, t_s1 = ts.from_datetime(t_conj.replace(hour=0, minute=0)), ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia: fases_dict[target_day] = ["CELEB", None]
            
            if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"
                b_style = "style='border: 1px solid #FF8C00; border-radius: 5px;'"
            
            if dia in equi_dict and equi_dict[dia] == 0: icons += "🌸"
            fila += f"<td {b_style}><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    filas_html += fila + "</tr>"

# Render de Tabla
html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:20px; font-weight:bold; margin-bottom:8px;'>
    {mes_nombre} {anio}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; }}
    th {{ color: #FF4B4B; font-size: 14px; text-align: center; padding-bottom: 5px; }}
    td {{ border: 1px solid #333; height: 60px; vertical-align: top; padding: 4px; box-sizing: border-box; }}
    .n {{ font-size: 15px; font-weight: bold; }}
    .e {{ font-size: 22px; text-align: center; margin-top: 2px; }}
</style>
<table>{header}{filas_html}</table>
"""
components.html(html_final, height=420)

# 3. Cuadros de Leyenda
st.markdown(f"""
<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:5px;">Simbología:</div>
    <div class="info-text">🌑 Nueva | 🌘 Celebración</div>
    <div class="info-text">🌸 Equinoccio | 🌕 Llena</div>
</div>
<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:5px;">Datos Conjunción:</div>
    <div class="info-text">🌎 {info_utc if info_utc else '---'}</div>
    <div class="info-text">📍 {info_sv if info_sv else '---'}</div>
</div>
""", unsafe_allow_html=True)
