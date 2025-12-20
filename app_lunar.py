import streamlit as st
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime, timedelta
import pytz
import calendar

# 1. Configuración de página
st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

# 2. Truco para que las columnas NO se desarmen en el celular
st.markdown("""
    <style>
    [data-testid="column"] {
        width: 14% !important;
        flex: 1 1 14% !important;
        min-width: 14% !important;
        text-align: center;
    }
    div[data-testid="stExpander"] { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Datos de El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)

st.title("🌙 Calendario Lunar SV")
st.caption("🌑:Nueva | ✨:Celebra | 🌓:Crec | 🌕:Llena | 🌗:Meng")

# 4. Selectores
col_m, col_a = st.columns(2)
with col_m:
    mes = st.selectbox("Mes", range(1, 13), index=datetime.now(tz_sv).month - 1)
with col_a:
    anio = st.number_input("Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)

if st.button('📅 Generar Calendario'):
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)))
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, ultimo_dia, 23, 59)))

    # Calcular fases
    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}
    
    nombres_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    # 5. Encabezados de días
    dias_nombres = ["D", "L", "M", "M", "J", "V", "S"]
    cols_h = st.columns(7)
    for i, d in enumerate(dias_nombres):
        cols_h[i].write(f"*{d}*")

    # 6. Dibujar días
    cal = calendar.Calendar(firstweekday=6)
    for semana in cal.monthdayscalendar(anio, mes):
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].write(" ")
            else:
                f_emoji = ""
                c_emoji = ""
                
                if dia in fases_dict:
                    f_tipo = fases_dict[dia][0]
                    if f_tipo != "CELEB":
                        f_emoji = nombres_fases.get(f_tipo, "")
                    
                    if f_tipo == 0: # Luna Nueva
                        f_h = fases_dict[dia][1]
                        t_s0 = ts.from_datetime(f_h.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(f_h.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), f_h.replace(hour=17, minute=45))
                        
                        if f_h < atardecer:
                            c_emoji = "✨"
                        elif dia < ultimo_dia:
                            fases_dict[dia + 1] = ["CELEB", None]

                if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                    c_emoji = "✨"

                # Mostrar el día en un cuadro limpio de Streamlit
                contenido = f"{dia}\n\n{f_emoji}{c_emoji}"
                cols[i].help(contenido) # Usamos 'help' porque crea un cuadrito muy pequeño y estético

st.sidebar.caption("v6.0 - El Salvador")
