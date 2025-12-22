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
hoy_sv = datetime.now(tz_sv)

# --- ESTILOS CSS DEFINITIVOS ---
st.markdown("""
    <style>
    /* Ocultar etiquetas originales pequeñas */
    div[data-testid="stNumberInput"] label { display: none !important; }
    
    /* Crear etiquetas GRANDES personalizadas */
    .custom-label {
        font-size: 28px !important; 
        color: #FF8C00 !important;
        font-weight: bold !important;
        text-align: center;
        margin-bottom: 5px;
        margin-top: 15px;
    }
    
    .main-title { text-align: center; color: white; font-size: 32px; font-weight: bold; margin-bottom: 20px; }

    /* Centrar selectores */
    div[data-testid="stNumberInput"] { width: 180px !important; margin: 0 auto !important; }
    input { font-size: 26px !important; font-weight: bold !important; text-align: center !important; color: white !important; }

    /* Barra de Meses */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px !important;
        background-color: #1a1a1a;
        border-radius: 8px;
        color: #eee;
        font-size: 20px !important; 
        font-weight: bold;
        padding: 0 15px !important;
    }
    .stTabs [aria-selected="true"] { border: 1.5px solid #FF8C00 !important; color: #FF8C00 !important; }

    /* Leyendas y Tarjetas */
    .info-card {
        border: 1.2px solid #444;
        border-radius: 15px;
        background-color: #1a1a1a;
        padding: 15px;
        margin: 10px auto;
        max-width: 450px;
    }
    .info-item { font-size: 18px; color: #eee; margin-bottom: 10px; display: flex; align-items: center; }
    .emoji-span { font-size: 24px; margin-right: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selector de Año con etiqueta manual grande
st.markdown("<p class='custom-label'>Año:</p>", unsafe_allow_html=True)
anio = st.number_input("Anio_Hidden", min_value=2024, max_value=2030, value=hoy_sv.year)

# 2. Selector de Mes con Tabs
st.markdown("<p class='custom-label'>Mes:</p>", unsafe_allow_html=True)
meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Detectar mes por defecto
default_tab = hoy_sv.month - 1
tabs = st.tabs(meses_nombres)

mes_sel = 1
for i, tab in enumerate(tabs):
    with tab:
        mes_sel = i + 1
        nombre_mes_visual = meses_completos[i]

# --- CÁLCULOS (Usando mes_sel) ---
ts = api.load.timescale()
eph = api.load('de421.bsp')
t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_sel, 1)))
ultimo_dia = calendar.monthrange(anio, mes_sel)[1]
t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_sel, ultimo_dia, 23, 59)))

t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}

info_utc, info_sv = "---", "---"
iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# Construir tabla
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes_sel):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: fila += "<td></td>"
        else:
            icons, b_style = "", ""
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                icons += iconos_fases.get(f_tipo, "")
                if f_tipo == 0: # LUNA NUEVA
                    t_conj = fases_dict[dia][1]
                    info_utc = t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M')
                    info_sv = t_conj.strftime('%d/%m/%y %I:%M %p')
                    # Cálculo de celebración
                    t_s0, t_s1 = ts.from_datetime(t_conj.replace(hour=0, minute=0)), ts.from_datetime(t_conj.replace(hour=23, minute=59))
                    t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                    atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                    target = dia + 1 if t_conj < atardecer else dia + 2
                    if target <= ultimo_dia: fases_dict[target] = ["CELEB", None]
            
            # Bordes finos 1.2px
            if dia == hoy_sv.day and mes_sel == hoy_sv.month and anio == hoy_sv.year:
                b_style = "border: 1.2px solid #00FF7F; background-color: rgba(0, 255, 127, 0.1);"
            elif dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"
                b_style = "border: 1.2px solid #FF8C00;"
            
            fila += f"<td class='day-cell' style='{b_style}' onclick='selD(this)'><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    filas_html += fila + "</tr>"

# Render de Tabla
html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:26px; font-weight:bold; margin-bottom:10px;'>{nombre_mes_visual} {anio}</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; font-family: sans-serif; }}
    th {{ color: #FF4B4B; font-size: 15px; padding-bottom: 8px; }}
    td {{ border: 1px solid #333; height: 80px; vertical-align: top; padding: 5px; box-sizing: border-box; }}
    .n {{ font-size: 18px; font-weight: bold; }}
    .e {{ font-size: 30px; text-align: center; margin-top: 4px; }}
    .selected-day {{ background-color: #333 !important; }}
</style>
<table>{header}{filas_html}</table>
<script>
function selD(e) {{
    var cs = document.getElementsByClassName('day-cell');
    for (var i=0; i<cs.length; i++) {{ cs[i].classList.remove('selected-day'); }}
    e.classList.add('selected-day');
}}
</script>
"""
components.html(html_final, height=520)

# 3. LEYENDAS Y DATOS (Recuperados)
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:18px;">Simbología:</div>
        <div class="info-item"><span style="width:15px; height:15px; border:1.2px solid #00FF7F; display:inline-block; margin-right:10px;"></span> Hoy</div>
        <div class="info-item"><span class="emoji-span">🌑</span> Luna Nueva</div>
        <div class="info-item"><span class="emoji-span">🌘</span> Celebración</div>
        <div class="info-item"><span class="emoji-span">🌕</span> Luna Llena</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:18px;">Conjunción:</div>
        <div class="info-item"><span class="emoji-span">🌎</span> {info_utc} (UTC)</div>
        <div class="info-item"><span class="emoji-span">📍</span> {info_sv} (SV)</div>
    </div>
    """, unsafe_allow_html=True)
