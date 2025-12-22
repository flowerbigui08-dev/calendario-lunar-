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

# --- ESTILOS CSS REFORZADOS ---
st.markdown("""
    <style>
    /* FORZAR TAMAÑO DE ETIQUETAS */
    .stNumberInput label, .stSelectbox label, .section-label {
        font-size: 28px !important; 
        color: #FF8C00 !important;
        font-weight: bold !important;
        text-align: center !important;
        display: block !important;
    }
    
    /* Título principal */
    .main-title { text-align: center; color: white; font-size: 32px; font-weight: bold; }

    /* Ajuste del selector de año */
    div[data-testid="stNumberInput"] { width: 200px !important; margin: 0 auto !important; }
    input { font-size: 28px !important; font-weight: bold !important; text-align: center !important; }

    /* Ajuste del selector de mes */
    div[data-testid="stSelectbox"] { width: 250px !important; margin: 0 auto !important; }
    div[data-baseweb="select"] { font-size: 22px !important; font-weight: bold !important; }

    /* Cuadros de Leyenda */
    .info-card {
        border: 1.5px solid #444;
        border-radius: 15px;
        background-color: #1a1a1a;
        padding: 20px;
        margin: 15px auto;
        max-width: 450px;
    }
    .info-item { font-size: 19px; color: #eee; margin-bottom: 12px; display: flex; align-items: center; }
    .emoji-span { font-size: 26px; margin-right: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selector de Año (Ahora con etiqueta forzada)
anio = st.number_input("Año:", min_value=2024, max_value=2030, value=hoy_sv.year)

# 2. Selector de Mes (Cambiado a Selectbox para asegurar que el calendario cambie)
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Buscamos el índice del mes actual para que aparezca por defecto
indice_mes_actual = hoy_sv.month - 1
mes_nombre = st.selectbox("Mes:", meses_completos, index=indice_mes_actual)
mes_seleccionado = meses_completos.index(mes_nombre) + 1

# --- CÁLCULOS ASTRONÓMICOS ---
ts = api.load.timescale()
eph = api.load('de421.bsp')
t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_seleccionado, 1)))
ultimo_dia = calendar.monthrange(anio, mes_seleccionado)[1]
t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_seleccionado, ultimo_dia, 23, 59)))

t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}
t_equi, y_equi = almanac.find_discrete(t0, t1, almanac.seasons(eph))
equi_dict = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_equi, y_equi)}

info_utc, info_sv = "", ""
iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# Construir tabla
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes_seleccionado):
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
                        info_utc = t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M')
                        info_sv = t_conj.strftime('%d/%m/%y %I:%M %p')
                        t_s0, t_s1 = ts.from_datetime(t_conj.replace(hour=0, minute=0)), ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target_day = dia + 1 if t_conj < atardecer else dia + 2
                        if target_day <= ultimo_dia: fases_dict[target_day] = ["CELEB", None]
            
            # Estilo de bordes refinados
            if dia == hoy_sv.day and mes_seleccionado == hoy_sv.month and anio == hoy_sv.year:
                b_style = "border: 1.2px solid #00FF7F; background-color: rgba(0, 255, 127, 0.08);"
            elif dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"
                b_style = "border: 1.2px solid #FF8C00;"
            
            if dia in equi_dict and equi_dict[dia] == 0: icons += "🌸"
            
            fila += f"<td class='day-cell' style='{b_style}' onclick='seleccionarDia(this)'><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    filas_html += fila + "</tr>"

# Render de Tabla
html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:28px; font-weight:bold; margin-bottom:15px; font-family:sans-serif;'>
    {mes_nombre} {anio}
</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; }}
    th {{ color: #FF4B4B; font-size: 16px; text-align: center; padding-bottom: 10px; }}
    .day-cell {{ border: 1px solid #333; height: 85px; vertical-align: top; padding: 6px; box-sizing: border-box; transition: background 0.3s; }}
    .n {{ font-size: 19px; font-weight: bold; font-family: sans-serif; }}
    .e {{ font-size: 32px; text-align: center; margin-top: 5px; }}
    .selected-day {{ background-color: #333 !important; }}
</style>
<table>{header}{filas_html}</table>
<script>
function seleccionarDia(elemento) {{
    var celdas = document.getElementsByClassName('day-cell');
    for (var i = 0; i < celdas.length; i++) {{ celdas[i].classList.remove('selected-day'); }}
    elemento.classList.add('selected-day');
}}
</script>
"""
components.html(html_final, height=560)

# 3. Leyendas
st.markdown(f"""
<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:20px; text-align:center;">Simbología:</div>
    <div class="info-item"><span style="width:18px; height:18px; border:1.2px solid #00FF7F; display:inline-block; margin-right:15px; border-radius:3px;"></span> Día Actual (Hoy)</div>
    <div class="info-item"><span class="emoji-span">🌑</span> Luna Nueva</div>
    <div class="info-item"><span class="emoji-span">🌘</span> Día de Celebración</div>
    <div class="info-item"><span class="emoji-span">🌸</span> Primavera</div>
    <div class="info-item"><span class="emoji-span">🌕</span> Luna Llena</div>
</div>
""", unsafe_allow_html=True)
