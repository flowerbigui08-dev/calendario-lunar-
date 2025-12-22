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

# --- 1. SELECTOR DE AÑO ---
anio = st.number_input("Selecciona el Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)

# --- 2. BOTONERA DE MESES (NUEVO DISEÑO UNIFORME) ---
meses_abr = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
if 'mes_sel' not in st.session_state:
    st.session_state.mes_sel = datetime.now(tz_sv).month

st.write("Selecciona el Mes:")

# CSS MAESTRO: Forzar botones iguales, emojis grandes y color de mes
st.markdown("""
    <style>
    /* Forzar 6 columnas reales en móvil */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 4px !important;
        justify-content: center !important;
    }
    div[data-testid="column"] {
        flex: 1 0 15% !important; /* Esto obliga a que quepan 6 */
        min-width: 50px !important;
    }
    button[kind="secondary"] {
        height: 42px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        border: 1px solid #FFD700 !important;
        color: white !important;
        background-color: #1a1a1a !important;
    }
    /* Estilo para los cuadros de abajo para que no se estiren */
    .footer-box {
        border: 1px solid #444;
        padding: 8px;
        border-radius: 5px;
        background-color: #1e1e1e;
        font-family: sans-serif;
        font-size: 12px;
        color: #aaa;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Botones de meses
cols = st.columns(6)
for i in range(12):
    with cols[i % 6]:
        if st.button(meses_abr[i], key=f"btn_{i+1}", use_container_width=True):
            st.session_state.mes_sel = i + 1

mes = st.session_state.mes_sel

# --- LÓGICA DE CÁLCULO ---
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
            icons = ""
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB": 
                    icons += nombres_fases.get(f_tipo, "")
                    if f_tipo == 0: 
                        t_conj = fases_dict[dia][1]
                        info_utc = f"UTC: {t_conj.astimezone(pytz.utc).strftime('%d/%m/%Y %H:%M')}"
                        info_sv = f"SV: {t_conj.strftime('%d/%m/%Y %I:%M %p')}"
                        t_s0 = ts.from_datetime(t_conj.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia:
                            fases_dict[target_day] = ["CELEB", None]
            
            if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "✨"
            if dia in equi_dict and equi_dict[dia] == 0:
                icons += "🌸"

            fila += f"<td><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    fila += "</tr>"
    filas_html += fila

# HTML con el Mes en Color Luna Llena
html_final = f"""
<div style='text-align:center; color:#FFD700; font-size:24px; font-weight:bold; margin-bottom:10px; font-family:sans-serif; text-shadow: 1px 1px 2px #000;'>
    {meses_nombres[mes-1]} {anio}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; font-family: sans-serif; color: white; }}
    th {{ color: #aaa; font-size: 13px; padding-bottom: 5px; text-align: center; }}
    td {{ border: 1px solid #444; height: 78px; vertical-align: top; padding: 5px; }}
    .n {{ font-size: 17px; color: #ffffff; font-weight: bold; }}
    .e {{ font-size: 28px; text-align: center; margin-top: 5px; line-height: 1.1; }}
</style>
<table>{header}{filas_html}</table>
"""
components.html(html_final, height=560, scrolling=False)

# --- 3. LEYENDA Y DATOS TÉCNICOS MEJORADOS ---
st.write("Leyenda y Conjunción:")
c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""<div class="footer-box">
    🌑 Conjunción | ✨ Celebración<br>
    🌸 Equinoccio | 🌕 Luna Llena
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="footer-box">
    ◼ {info_utc if info_utc else 'Sin datos'}<br>
    ◼ {info_sv if info_sv else '-'}
    </div>""", unsafe_allow_html=True)

st.sidebar.caption("v16.0 - Golden Moon Edition")
