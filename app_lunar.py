import streamlit as st
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime, timedelta
import pytz
import calendar

# Configuración de página
st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

# Zona horaria y ubicación (San Salvador)
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)

st.title("🌙 Calendario Lunar SV")

# --- SECCIÓN DE SIGNIFICADOS (LEYENDA) ---
with st.expander("ℹ️ Ver significado de emojis y reglas", expanded=False):
    st.markdown("""
    * 🌑 *Luna Nueva:* Conjunción astronómica.
    * ✨ *Celebración:* Inicio del mes (Primer atardecer tras la conjunción).
    * 🌓 *Creciente* | 🌕 *Llena* | 🌗 *Menguante*
    * 📍 Cálculos exactos para la puesta del sol en El Salvador.
    """)

# Selector de Mes y Año compacto
col_m, col_a, col_b = st.columns([2, 2, 2])
with col_m:
    mes = st.selectbox("Mes", range(1, 13), index=datetime.now(tz_sv).month - 1)
with col_a:
    anio = st.number_input("Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)
with col_b:
    st.write(" ") # Espacio estético
    btn = st.button('📅 Ver Calendario')

if btn:
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)))
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, ultimo_dia, 23, 59)))

    # Calcular fases
    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: (yi, ti.astimezone(tz_sv)) for ti, yi in zip(t_fases, y_fases)}
    
    nombres_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    # Crear la cuadrícula
    cal = calendar.Calendar(firstweekday=6) 
    dias_semana = ["DOM", "LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB"]
    
    # Encabezados
    cols_h = st.columns(7)
    for i, d in enumerate(dias_semana):
        cols_h[i].markdown(f"<p style='text-align:center; font-size:12px; color:gray;'><b>{d}</b></p>", unsafe_allow_html=True)

    # Días del mes
    for semana in cal.monthdayscalendar(anio, mes):
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].write(" ")
            else:
                contenido = f"<div style='text-align:center; border:1px solid #333; border-radius:5px; padding:2px;'><b>{dia}</b>"
                
                if dia in fases_dict:
                    f_tipo, f_hora = fases_dict[dia]
                    if f_tipo != "CELEB":
                        contenido += f"<br>{nombres_fases[f_tipo]}"
                    
                    if f_tipo == 0: # Luna Nueva
                        t_s0 = ts.from_datetime(f_hora.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(f_hora.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), f_hora.replace(hour=17, minute=45))
                        
                        if f_hora < atardecer:
                            contenido += "<br><span style='font-size:10px;'>✨</span>"
                        elif dia < ultimo_dia:
                            fases_dict[dia + 1] = ("CELEB", None)

                if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                    contenido += "<br><span style='font-size:10px;'>✨</span>"
                
                contenido += "</div>"
                cols[i].markdown(contenido, unsafe_allow_html=True)

st.sidebar.caption("v2.0 - Compacto para El Salvador")


