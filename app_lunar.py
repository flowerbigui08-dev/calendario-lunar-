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

# TRUCO MAESTRO: CSS para obligar a que las 7 columnas NO se desarmen en vertical
st.markdown("""
    <style>
    /* Forza a que el contenedor de columnas sea siempre horizontal */
    [data-testid="column"] {
        width: calc(14.28% - 5px) !important;
        flex: 1 1 calc(14.28% - 5px) !important;
        min-width: calc(14.28% - 5px) !important;
        margin: 0 !important;
        padding: 1px !important;
    }
    /* Reduce espacios innecesarios */
    [data-testid="stVerticalBlock"] {
        gap: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 Calendario Lunar SV")

# Simbología súper resumida para ganar espacio
st.caption("🌑:Nueva | ✨:Celebra | 🌓:Crec | 🌕:Llena | 🌗:Meng")

# Selectores compactos
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

    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}
    
    nombres_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    # Dibujar encabezados (D, L, M, M, J, V, S)
    dias_semana = ["D", "L", "M", "M", "J", "V", "S"]
    cols_h = st.columns(7)
    for i, d in enumerate(dias_semana):
        cols_h[i].markdown(f"<p style='text-align:center; font-size:12px; margin:0;'><b>{d}</b></p>", unsafe_allow_html=True)

    # Dibujar los días
    cal = calendar.Calendar(firstweekday=6) 
    for semana in cal.monthdayscalendar(anio, mes):
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].write("")
            else:
                f_emoji = ""
                c_emoji = ""
                
                if dia in fases_dict:
                    f_tipo = fases_dict[dia][0]
                    if f_tipo != "CELEB":
                        f_emoji = nombres_fases.get(f_tipo, "")
                    
                    if f_tipo == 0: # Luna Nueva
                        f_h = fases_dict[dia][1]
                        # Cálculo de atardecer
                        t_s0 = ts.from_datetime(f_h.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(f_h.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), f_h.replace(hour=17, minute=45))
                        
                        if f_h < atardecer:
                            c_emoji = "✨"
                        elif dia < ultimo_dia:
                            if (dia + 1) not in fases_dict: fases_dict[dia+1] = ["CELEB", None]
                            else: c_emoji = "✨"

                if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                    c_emoji = "✨"

                # Cuadro de día compacto
                html_celda = f"""
                <div style='text-align:center; border:0.5px solid #555; border-radius:3px; padding:2px; min-height:45px;'>
                    <span style='font-size:11px; color:#ccc;'>{dia}</span><br>
                    <span style='font-size:14px;'>{f_emoji}</span><br>
                    <span style='font-size:11px;'>{c_emoji}</span>
                </div>
                """
                cols[i].markdown(html_celda, unsafe_allow_html=True)

st.sidebar.caption("v2.2 - El Salvador Fixed")
