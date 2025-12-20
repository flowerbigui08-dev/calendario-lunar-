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

# Leyenda compacta
st.markdown("🌑:Nueva | ✨:Celebra | 🌓:Crec | 🌕:Llena | 🌗:Meng")

# Selectores
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

    # Construcción de la tabla con ancho total
    # Usamos HTML para asegurar que el ancho sea 100% y las celdas iguales
    header = "<tr><th>Dom</th><th>Lun</th><th>Mar</th><th>Mié</th><th>Jue</th><th>Vie</th><th>Sáb</th></tr>"
    filas_html = ""

    cal = calendar.Calendar(firstweekday=6)
    for semana in cal.monthdayscalendar(anio, mes):
        fila = "<tr>"
        for dia in semana:
            if dia == 0:
                fila += "<td style='border:1px solid #444;'>&nbsp;</td>"
            else:
                f_emoji = "&nbsp;"
                c_emoji = "&nbsp;"
                
                if dia in fases_dict:
                    f_tipo = fases_dict[dia][0]
                    if f_tipo != "CELEB":
                        f_emoji = nombres_fases.get(f_tipo, "&nbsp;")
                    
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

                # Celda con tamaño uniforme y emojis centrados
                fila += f"""
                <td style='border:1px solid #444; text-align:center; width:14%; height:60px; vertical-align:top;'>
                    <span style='font-size:10px; color:#888;'>{dia}</span><br>
                    <span style='font-size:16px;'>{f_emoji}</span><br>
                    <span style='font-size:12px;'>{c_emoji}</span>
                </td>
                """
        fila += "</tr>"
        filas_html += fila

    # Renderizar la tabla final ocupando todo el ancho
    st.markdown(f"""
    <table style='width:100%; border-collapse:collapse; table-layout:fixed;'>
        {header}
        {filas_html}
    </table>
    """, unsafe_allow_html=True)

st.sidebar.caption("v5.0 - Final El Salvador")
