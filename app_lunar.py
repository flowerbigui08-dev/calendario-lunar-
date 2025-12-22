import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# Configuración inicial
st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)

# --- ESTILOS CSS REFINADOS PARA MÓVIL ---
st.markdown("""
    <style>
    /* Título Principal */
    .main-title { text-align: center; color: white; font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    
    /* Etiquetas de Año y Mes */
    .stNumberInput label, .section-label {
        font-size: 22px !important;
        color: #FF8C00 !important;
        font-weight: bold !important;
        text-align: center;
        display: block;
        margin-bottom: 10px !important;
    }

    /* Input de año grande y centrado */
    div[data-testid="stNumberInput"] { width: 160px !important; margin: 0 auto !important; }
    input { font-size: 26px !important; font-weight: bold !important; text-align: center !important; height: 50px !important; }

    /* Estilo para las Pestañas (Tabs) - Ordenadas y sin teclado */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: flex-start;
        overflow-x: auto; /* Permite deslizar los meses en móvil */
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 8px 16px;
        color: #aaa;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #FF8C00 !important;
        border-bottom-color: #FF8C00 !important;
    }

    /* Cuadros de información (Leyendas) */
    .info-card {
        border: 1.5px solid #444;
        border-radius: 15px;
        background-color: #1a1a1a;
        padding: 20px;
        margin: 15px auto;
        max-width: 450px;
    }
    .info-item { 
        font-size: 19px; 
        color: #eee; 
        margin-bottom: 12px; 
        display: flex; 
        align-items: center; 
    }
    .emoji-span { font-size: 26px; margin-right: 15px; }

    /* Eliminar espacios excesivos de Streamlit */
    .block-container { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selector de Año
anio = st.number_input("Año", min_value=2024, max_value=2030, value=datetime.now(tz_sv).year)

# 2. Selector de Mes con Pestañas (Evita el teclado y ordena el diseño)
st.markdown("<p class='section-label'>Selecciona el Mes:</p>", unsafe_allow_html=True)
meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Esto crea una fila de pestañas que se puede deslizar en el móvil
tabs = st.tabs(meses_nombres)
mes = 1
for i, tab in enumerate(tabs):
    if i == datetime.now(tz_sv).month - 1: # Pre-selección del mes actual (opcional)
        pass 
    with tab:
        mes = i + 1
        # El nombre del mes que saldrá arriba del calendario con las llamas
        mes_visual = f"🔥 {meses_completos[i]} 🔥"

# --- CÁLCULOS ASTRONÓMICOS ---
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

# Construir tabla del calendario
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: fila += "<td></td>"
        else:
            icons, b_style = "", ""
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB":
                    icons += iconos_fases.get(f_tipo, "")
                    if f_tipo == 0:
                        t_conj = fases_dict[dia][1]
                        info_utc = t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M') + " (UTC)"
                        info_sv = t_conj.strftime('%d/%m/%y %I:%M %p') + " (SV)"
                        t_s0, t_s1 = ts.from_datetime(t_conj.replace(hour=0, minute=0)), ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia: fases_dict[target_day] = ["CELEB", None]
            
            if dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"
                b_style = "style='border: 1.5px solid #FF8C00; border-radius: 8px;'"
            
            if dia in equi_dict and equi_dict[dia] == 0: icons += "🌸"
            fila += f"<td {b_style}><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    filas_html += fila + "</tr>"

# HTML del Calendario
html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:26px; font-weight:bold; margin-bottom:15px; font-family:sans-serif;'>
    {mes_visual}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; }}
    th {{ color: #FF4B4B; font-size: 16px; text-align: center; padding-bottom: 10px; }}
    td {{ border: 1px solid #333; height: 80px; vertical-align: top; padding: 6px; box-sizing: border-box; }}
    .n {{ font-size: 18px; font-weight: bold; font-family: sans-serif; }}
    .e {{ font-size: 30px; text-align: center; margin-top: 5px; }}
</style>
<table>{header}{filas_html}</table>
"""
components.html(html_final, height=520)

# 3. Cuadros de Leyenda (Diseño Clásico Renovado)
st.markdown(f"""
<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:20px; text-align:center;">Significado:</div>
    <div class="info-item"><span class="emoji-span">🌑</span> Luna Nueva (Conjunción)</div>
    <div class="info-item"><span class="emoji-span">🌘</span> Día de Celebración</div>
    <div class="info-item"><span class="emoji-span">🌸</span> Equinoccio de Primavera</div>
    <div class="info-item"><span class="emoji-span">🌕</span> Luna Llena</div>
</div>

<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:20px; text-align:center;">Datos de la Conjunción:</div>
    <div class="info-item"><span class="emoji-span">🌎</span> {info_utc if info_utc else '---'}</div>
    <div class="info-item"><span class="emoji-span">📍</span> {info_sv if info_sv else '---'}</div>
</div>
""", unsafe_allow_html=True)
