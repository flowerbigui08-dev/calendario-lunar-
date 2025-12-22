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

st.title("🌙 Calendario Lunar SV")

# --- 1. BOTONERA DE MESES ---
st.write("Selecciona el Mes:")
mes_cols = st.columns(12)
if 'mes_sel' not in st.session_state:
    st.session_state.mes_sel = datetime.now(tz_sv).month

for i in range(1, 13):
    if mes_cols[i-1].button(str(i), key=f"m_{i}"):
        st.session_state.mes_sel = i

# --- 2. SELECTOR DE AÑO ---
anio = st.number_input("Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)
mes = st.session_state.mes_sel

# --- LÓGICA DE CÁLCULO ---
ts = api.load.timescale()
eph = api.load('de421.bsp')
t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)))
ultimo_dia = calendar.monthrange(anio, mes)[1]
t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, ultimo_dia, 23, 59)))

t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}

# Guardar info de conjunción para el pie de página
info_conjuncion = ""
nombres_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}
meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Construcción de la Tabla
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes):
    fila = "<tr>"
    for dia in semana:
        if dia == 0:
            fila += "<td></td>"
        else:
            f_emoji = ""
            c_emoji = ""
            estilo_celda = ""
            
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB": 
                    f_emoji = nombres_fases.get(f_tipo, "")
                    if f_tipo == 0: # Luna Nueva (Conjunción)
                        t_conj = fases_dict[dia][1]
                        info_conjuncion = f"Luna Nueva: {t_conj.strftime('%d/%m/%Y')} | SV: {t_conj.strftime('%I:%M %p')} | UTC: {t_conj.astimezone(pytz.utc).strftime('%H:%M')}"
                        
                        # Regla de celebración
                        t_s0 = ts.from_datetime(t_conj.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia:
                            fases_dict[target_day] = ["CELEB", None]

            if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                c_emoji = "✨"
                estilo_celda = "background-color: rgba(30, 60, 100, 0.4);" # Azul sutil

            fila += f"<td style='{estilo_celda}'><div class='n'>{dia}</div><div class='e'>{f_emoji}{c_emoji}</div></td>"
    fila += "</tr>"
    filas_html += fila

# HTML Final
html_final = f"""
<div style='text-align:center; color:#FFD700; font-size:24px; font-weight:bold; margin-bottom:10px; font-family:sans-serif;'>
    {meses_nombres[mes-1]} {anio}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; font-family: sans-serif; color: white; }}
    th {{ color: #aaa; font-size: 14px; padding-bottom: 8px; text-align: center; }}
    td {{ border: 1px solid #555; height: 75px; vertical-align: top; padding: 6px; }}
    .n {{ font-size: 16px; color: #ffffff; font-weight: bold; }}
    .e {{ font-size: 22px; text-align: center; margin-top: 8px; }}
</style>
<table>{header}{filas_html}</table>
"""

components.html(html_final, height=550, scrolling=False)

# Pie de página con datos técnicos
if info_conjuncion:
    st.info(info_conjuncion)

st.sidebar.caption("v9.0 - Edición Automática")
