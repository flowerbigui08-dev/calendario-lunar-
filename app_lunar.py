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

st.title("📅 Calendario Lunar El Salvador")
st.write("Semanas iniciando en *Domingo*")

# Selector de Mes y Año
col1, col2 = st.columns(2)
with col1:
    mes = st.selectbox("Selecciona el Mes", range(1, 13), index=datetime.now(tz_sv).month - 1)
with col2:
    anio = st.number_input("Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)

if st.button('📅 Ver mi Calendario'):
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    
    # Rango del mes
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)))
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, ultimo_dia, 23, 59)))

    # Calcular fases
    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: (yi, ti.astimezone(tz_sv)) for ti, yi in zip(t_fases, y_fases)}
    
    nombres_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    # Crear la cuadrícula estilo Calendario (Iniciando en Domingo)
    cal = calendar.Calendar(firstweekday=6) 
    dias_semana = ["DOM", "LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB"]
    
    # Encabezados de los días
    cols_header = st.columns(7)
    for i, dia_nom in enumerate(dias_semana):
        cols_header[i].markdown(f"<p style='text-align:center;'><b>{dia_nom}</b></p>", unsafe_allow_html=True)

    # Filas de días
    for semana in cal.monthdayscalendar(anio, mes):
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].write("") # Espacio vacío para días fuera del mes
            else:
                texto_dia = f"### {dia}"
                fase_info = ""
                
                # Revisar si hay fase este día
                if dia in fases_dict:
                    fase_tipo, hora_fase = fases_dict[dia]
                    if fase_tipo != "PROX_CELEB":
                        fase_info = f"\n\n {nombres_fases[fase_tipo]} {hora_fase.strftime('%I:%M %p')}"
                    
                    if fase_tipo == 0: # Si es Luna Nueva
                        # Calcular atardecer
                        t_s0 = ts.from_datetime(hora_fase.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(hora_fase.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), hora_fase.replace(hour=17, minute=45))
                        
                        if hora_fase < atardecer:
                            fase_info += "\n\n ✨ CELEBRACIÓN"
                        else:
                            # Marcar el día siguiente para celebración
                            if dia < ultimo_dia:
                                fases_dict[dia + 1] = ("PROX_CELEB", None)

                # Si el día fue marcado por la conjunción de ayer tarde
                if dia in fases_dict and fases_dict[dia][0] == "PROX_CELEB":
                    fase_info += "\n\n ✨ CELEBRACIÓN"

                # Mostrar el cuadro del día
                with cols[i]:
                    st.info(f"{texto_dia}{fase_info}")

st.sidebar.markdown("---")
st.sidebar.caption("📍 Localizado para El Salvador")

