import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

st.set_page_config(page_title="Calendario Lunar", page_icon="🌙", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    /* Título Principal */
    .main-title { text-align: center; color: white; font-size: 38px; font-weight: bold; margin-bottom: 5px; }
    
    /* Etiquetas de Selección */
    .big-font {
        font-size: 22px !important; 
        font-weight: bold; 
        color: #FF8C00; 
        margin-top: 25px !important;
        margin-bottom: 12px !important;
        text-align: center;
    }
    
    /* Selector de Año */
    div[data-testid="stNumberInput"] { width: 160px !important; margin: 0 auto !important; }
    input { font-size: 24px !important; font-weight: bold !important; text-align: center !important; }

    /* Cuadrícula de Botones de Mes (Abreviados) */
    div[data-testid="stHorizontalBlock"] {
        justify-content: center !important;
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 10px !important;
        max-width: 400px !important;
        margin: 0 auto !important;
    }
    
    button[kind="secondary"] {
        border: 1.8px solid #FF8C00 !important;
        height: 48px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        color: white !important;
        background-color: transparent !important;
        border-radius: 10px !important;
        width: 100% !important;
    }

    /* Cuadros de Información Inferiores */
    .info-card { 
        border: 1px solid #444; 
        padding: 18px; 
        border-radius: 12px; 
        background-color: #1a1a1a; 
        margin: 15px auto !important;
        max-width: 500px;
    }
    .info-item { font-size: 18px; color: #ddd; margin-bottom: 10px; display: flex; align-items: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# Selector de Año
st.markdown('<p class="big-font">Selecciona el Año:</p>', unsafe_allow_html=True)
anio = st.number_input("", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year, label_visibility="collapsed")

# Selector de Mes (Abreviados para mejor diseño)
st.markdown('<p class="big-font">Selecciona el Mes:</p>', unsafe_allow_html=True)
meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
meses_abr = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

if 'mes_sel' not in st.session_state:
    st.session_state.mes_sel = datetime.now(tz_sv).month

# Dibujar botones en 4 filas de 3
for r in range(4):
    cols = st.columns(3)
    for c in range(3):
        idx = r * 3 + c
        if cols[c].button(meses_abr[idx], key=f"btn_{idx}"):
            st.session_state.mes_sel = idx + 1

mes = st.session_state.mes_sel

# --- CÁLCULOS ---
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
iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# Tabla HTML
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: fila += "<td></td>"
        else:
            icons, estilo_borde = "", ""
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB":
                    icons += iconos_fases.get(f_tipo, "")
                    if f_tipo == 0:
                        t_conj = fases_dict[dia][1]
                        info_utc = f"{t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M')} (UTC)"
                        info_sv = f"{t_conj.strftime('%d/%m/%y %I:%M %p')} (SV)"
                        t_s0, t_s1 = ts.from_datetime(t_conj.replace(hour=0, minute=0)), ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia: fases_dict[target_day] = ["CELEB", None]
            
            if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"
                estilo_borde = "style='border: 1.5px solid #FF8C00; border-radius: 6px;'"
            
            if dia in equi_dict and equi_dict[dia] == 0: icons += "🌸"
            fila += f"<td {estilo_borde}><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    filas_html += fila + "</tr>"

html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:28px; font-weight:bold; margin-bottom:15px; font-family:sans-serif;'>
    {meses_nombres[mes-1]} {anio}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; border-bottom: 1px solid #333; }}
    th {{ color: #FF4B4B; font-size: 17px; text-align: center; padding-bottom: 10px; font-family: sans-serif; }}
    td {{ border: 1px solid #333; height: 80px; vertical-align: top; padding: 6px; }}
    .n {{ font-size: 18px; font-weight: bold; font-family: sans-serif; }}
    .e {{ font-size: 32px; text-align: center; margin-top: 5px; line-height: 1; }}
</style>
<table>{header}{filas_html}</table>
"""
components.html(html_final, height=620)

# Leyendas Restauradas
st.markdown('<p class="big-font">Significado de Símbolos:</p>', unsafe_allow_html=True)
st.markdown(f"""
<div class="info-card">
    <div class="info-item"><span style="font-size:24px; margin-right:15px;">🌑</span> Luna Nueva (Conjunción)</div>
    <div class="info-item"><span style="font-size:24px; margin-right:15px;">🌘</span> Día de Celebración</div>
    <div class="info-item"><span style="font-size:24px; margin-right:15px;">🌸</span> Equinoccio de Primavera</div>
    <div class="info-item"><span style="font-size:24px; margin-right:15px;">🌕</span> Luna Llena</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Datos de la Conjunción:</p>', unsafe_allow_html=True)
st.markdown(f"""
<div class="info-card">
    <div class="info-item"><span style="font-size:24px; margin-right:15px;">🌎</span> {info_utc if info_utc else 'Sin datos'}</div>
    <div class="info-item"><span style="font-size:24px; margin-right:15px;">📍</span> {info_sv if info_sv else '-'}</div>
</div>
""", unsafe_allow_html=True)
