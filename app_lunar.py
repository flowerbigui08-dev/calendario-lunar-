import streamlit as st
from skyfield import api, almanac
from datetime import datetime

# Configuración de la App
st.set_page_config(page_title="Mi Luna", page_icon="🌙")

st.title("🌙 Mi Calendario Lunar")
st.write("Calculando las fases desde las estrellas...")

if st.button('✨ Ver lunas de este mes'):
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    hoy = datetime.now()
    t0 = ts.utc(hoy.year, hoy.month, hoy.day)
    t1 = ts.utc(hoy.year, hoy.month, hoy.day + 31)

    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    lunas = {0: "🌑 Luna Nueva", 1: "🌓 Creciente", 2: "🌕 Luna Llena", 3: "🌗 Menguante"}

    for ti, yi in zip(t, y):
        st.success(f"*{lunas[yi]}* \n\n 📅 {ti.utc_strftime('%d/%m/%Y')}")

st.sidebar.write("App lista para el celular 🚀")