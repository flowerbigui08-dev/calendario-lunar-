import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# Configuración básica
st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

# --- TRUCO PARA FORZAR BOTONES EN FILAS (MÓVIL) ---
st.markdown("""
    <style>
    div[data-testid="column"] {
        display: flex;
        justify-content: center;
        min-width: 45px !important;
        padding: 2px !important;
    }
    .stButton>button {
        width: 100%;
        padding: 5px 2px;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)

st.title("🌙 Calendario Lunar SV")

# --- 1. BOTONERA DE MESES (FORZADA EN 2 FILAS DE 6) ---
st.write("Selecciona el Mes:")
meses_abreviados = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

if 'mes_sel' not in st.session_state:
    st.session_state.mes_sel = datetime.now(tz_sv).month

# Fila 1
c1, c2, c3, c4, c5, c6 = st.columns(6)
filas = [c1, c2, c3, c4, c5, c6]
for i in range(6):
    if filas[i].button(meses_abreviados[i], key=f"m_{i+1}"):
        st.session_state.mes_sel = i + 1

# Fila 2
c7, c8, c9, c10, c11, c12 = st.columns(6)
filas2 = [c7, c8, c9, c10, c11, c12]
for i in range(6, 12):
    if filas2[i-6].button(meses_abreviados[i], key=f"m_{i+1}"):
        st.session_state.mes_sel = i + 1

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

info_utc = ""
info_sv = ""
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
            clase_especial = ""
            
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB": 
                    f_emoji = nombres_fases.get(f_tipo, "")
                    if f_tipo == 0: # Luna Nueva
                        t_conj = fases_dict[dia][1]
                        info_utc = f"Luna Nueva (UTC): {t_conj.astimezone(pytz.utc).strftime('%d/%m/%Y %H:%M')}"
                        info_sv = f"Luna Nueva (SV): {t_conj.strftime('%d/%m/%Y %I:%M %p')}"
                        
                        t_s0 = ts.from_datetime(t_conj.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia:
                            fases_dict[target_day] = ["CELEB", None]

            if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                c_emoji = "✨"
                clase_especial = "celeb-day"

            fila += f"<td class='{clase_especial}'><div class='n'>{dia}</div><div class='e'>{f_emoji}{c_emoji}</div></td>"
    fila += "</tr>"
    filas_html += fila

# HTML con el Triángulo Dorado
html_final = f"""
<div style='text-align:center; color:#FFD700; font-size:22px; font-weight:bold; margin-bottom:10px; font-family:sans-serif;'>
    {meses_nombres[mes-1]} {anio}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; font-family: sans-serif; color: white; }}
    th {{ color: #aaa; font-size: 13px; padding-bottom: 5px; text-align: center; }}
    td {{ border: 1px solid #444; height: 70px; vertical-align: top; padding: 5px; position: relative; }}
    .n {{ font-size: 16px; color: #ffffff; font-weight: bold; }}
    .e {{ font-size: 20px; text-align: center; margin-top: 5px; }}
    .celeb-day::after {{
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 0;
        height: 0;
        border-style: solid;
        border-width: 0 18px 18px 0;
        border-color: transparent #FFD700 transparent transparent;
    }}
</style>
<table>{header}{filas_html}</table>
"""

components.html(html_final, height=540, scrolling=False)

# --- 3. INFORMACIÓN TÉCNICA (LIMPIA Y SIN CURSIVAS) ---
if info_utc:
    st.markdown(f"""
    <div style="border: 1px solid #444; padding: 10px; border-radius: 5px; background-color: #1e1e1e; font-family: sans-serif;">
        <span style="color: #aaa; font-size: 14px;">◼ {info_utc}</span><br>
        <span style="color: #aaa; font-size: 14px;">◼ {info_sv}</span>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.caption("v11.0 - Grid & Clean Style")
