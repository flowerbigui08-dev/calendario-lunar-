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

# --- TRUCO DE DISEÑO PARA CELULARES ---
# Este código obliga a que siempre haya 7 columnas, incluso en vertical
st.markdown("""
    <style>
    .calendario-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 2px;
        width: 100%;
        text-align: center;
    }
    .dia-caja {
        border: 1px solid #444;
        border-radius: 4px;
        padding: 4px 1px;
        min-height: 55px;
        background-color: #1a1a1a;
    }
    .dia-nombre {
        font-size: 10px;
        font-weight: bold;
        color: #888;
        margin-bottom: 4px;
    }
    .numero-dia {
        font-size: 12px;
        display: block;
    }
    .emoji-fase {
        font-size: 16px;
        display: block;
        margin: 2px 0;
    }
    .emoji-celeb {
        font-size: 12px;
        display: block;
        color: #ffd700;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 Calendario Lunar SV")

# Leyenda rápida
st.caption("🌑=Nueva | ✨=Celebración | 🌕=Llena")

# Selectores
col_m, col_a = st.columns(2)
with col_m:
    mes = st.selectbox("Mes", range(1, 13), index=datetime.now(tz_sv).month - 1)
with col_a:
    anio = st.number_input("Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)

if st.button('📅 Mostrar Calendario'):
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)))
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, ultimo_dia, 23, 59)))

    # Calcular fases
    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}
    
    nombres_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    # --- DIBUJAR CALENDARIO ---
    # Encabezados
    dias_nombres = ["D", "L", "M", "M", "J", "V", "S"]
    header_html = "".join([f"<div class='dia-nombre'>{d}</div>" for d in dias_nombres])
    
    # Días del mes
    cal_html = ""
    cal = calendar.Calendar(firstweekday=6)
    
    for semana in cal.monthdayscalendar(anio, mes):
        for dia in semana:
            if dia == 0:
                cal_html += "<div style='border:none;'></div>"
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

                cal_html += f"""
                <div class='dia-caja'>
                    <span class='numero-dia'>{dia}</span>
                    <span class='emoji-fase'>{f_emoji}</span>
                    <span class='emoji-celeb'>{c_emoji}</span>
                </div>
                """
    
    # Mostrar todo el bloque junto
    st.markdown(f"<div class='calendario-grid'>{header_html}{cal_html}</div>", unsafe_allow_html=True)

st.sidebar.caption("v3.0 - El Salvador Ultra-Compact")
