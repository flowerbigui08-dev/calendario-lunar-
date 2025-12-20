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
st.caption("🌑:Nueva | ✨:Celebra | 🌓:Crec | 🌕:Llena | 🌗:Meng")

# --- NUEVOS SELECTORES CON BOTONES +/- ---
col_m, col_a = st.columns(2)
with col_m:
    # Ahora el mes usa botones de + y - (valor del 1 al 12)
    mes = st.number_input("Mes", min_value=1, max_value=12, value=datetime.now(tz_sv).month)
with col_a:
    anio = st.number_input("Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)

if st.button('📅 Generar Calendario'):
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)))
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, ultimo_dia, 23, 59)))

    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}
    
    nombres_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    # Construcción de la Tabla Segura
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
                if dia in fases_dict:
                    f_tipo = fases_dict[dia][0]
                    if f_tipo != "CELEB": f_emoji = nombres_fases.get(f_tipo, "")
                    if f_tipo == 0:
                        f_h = fases_dict[dia][1]
                        t_s0 = ts.from_datetime(f_h.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(f_h.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), f_h.replace(hour=17, minute=45))
                        if f_h < atardecer: c_emoji = "✨"
                        elif dia < ultimo_dia: fases_dict[dia + 1] = ["CELEB", None]
                if dia in fases_dict and fases_dict[dia][0] == "CELEB": c_emoji = "✨"

                fila += f"<td><div class='n'>{dia}</div><div class='e'>{f_emoji}{c_emoji}</div></td>"
        fila += "</tr>"
        filas_html += fila

    # Diseño CSS para que se vea igual que el que te gustó
    html_final = f"""
    <style>
        table {{ width: 100%; border-collapse: collapse; table-layout: fixed; font-family: sans-serif; color: white; background-color: transparent; }}
        th {{ color: #888; font-size: 12px; padding-bottom: 5px; text-align: center; }}
        td {{ border: 1px solid #444; height: 65px; vertical-align: top; padding: 4px; position: relative; }}
        .n {{ font-size: 10px; color: #aaa; }}
        .e {{ font-size: 18px; text-align: center; margin-top: 5px; }}
    </style>
    <table>{header}{filas_html}</table>
    """
    
    components.html(html_final, height=500, scrolling=False)

st.sidebar.caption("v7.1 - SV Stepper Edition")
