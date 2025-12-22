import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)

st.title("🌙 Calendario Lunar SV")

# --- 1. SELECTOR DE AÑO ---
anio = st.number_input("Selecciona el Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)

# --- 2. BOTONERA DE MESES (FORZADO TOTAL) ---
meses_abr = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
if 'mes_sel' not in st.session_state:
    st.session_state.mes_sel = datetime.now(tz_sv).month

st.write("Selecciona el Mes:")

# Truco para que Streamlit detecte el cambio de mes desde HTML
import extra_streamlit_components as stx # Si no lo tienes, usaremos botones estándar con CSS forzado

# Usaremos columnas pero con un CSS que NO permite que se bajen
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 3px !important;
    }
    [data-testid="column"] {
        width: 16% !important;
        min-width: 0px !important;
        flex: 1 1 0% !important;
    }
    button[kind="secondary"] {
        border: 0.5px solid #FF8C00 !important; /* Línea más delgada */
        padding: 0px !important;
        height: 40px !important;
        font-size: 12px !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

c1 = st.columns(6)
for i in range(6):
    if c1[i].button(meses_abr[i], key=f"m{i+1}"): st.session_state.mes_sel = i + 1

c2 = st.columns(6)
for i in range(6, 12):
    if c2[i-6].button(meses_abr[i], key=f"m{i+1}"): st.session_state.mes_sel = i + 1

mes = st.session_state.mes_sel

# --- LÓGICA ---
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
meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Tabla HTML
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: fila += "<td></td>"
        else:
            icons = ""
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB": 
                    icons += nombres_fases.get(f_tipo, "")
                    if f_tipo == 0: 
                        t_conj = fases_dict[dia][1]
                        info_utc = f"UTC: {t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M')}"
                        info_sv = f"SV: {t_conj.strftime('%d/%m/%y %I:%M%p')}"
                        t_s0 = ts.from_datetime(t_conj.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, 45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia: fases_dict[target_day] = ["CELEB", None]
            
            if dia in fases_dict and fases_dict[dia][0] == "CELEB": icons += "🌘" # Nuevo brillo
            if dia in equi_dict and equi_dict[dia] == 0: icons += "🌸"
            fila += f"<td><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    filas_html += fila + "</tr>"

# Calendario con Mes Naranja
html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:24px; font-weight:bold; margin-bottom:10px; font-family:sans-serif;'>
    {meses_nombres[mes-1]} {anio}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; }}
    td {{ border: 1px solid #444; height: 75px; vertical-align: top; padding: 4px; }}
    .n {{ font-size: 16px; font-weight: bold; }}
    .e {{ font-size: 28px; text-align: center; margin-top: 5px; }}
    th {{ color: #888; font-size: 12px; text-align: center; }}
</style>
<table>{header}{filas_html}</table>
"""
components.html(html_final, height=520)

# --- 3. PIE DE PÁGINA COMPACTO ---
st.markdown(f"""
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-family: sans-serif;">
    <div style="border: 1px solid #444; padding: 8px; border-radius: 5px; font-size: 11px; color: #aaa;">
        🌑 Nueva | 🌘 Celeb.<br>🌸 Equi. | 🌕 Llena
    </div>
    <div style="border: 1px solid #444; padding: 8px; border-radius: 5px; font-size: 11px; color: #aaa;">
        ◼ {info_utc if info_utc else 'Sin datos'}<br>◼ {info_sv if info_sv else '-'}
    </div>
</div>
""", unsafe_allow_html=True)
