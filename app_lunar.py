import streamlit as st
from skyfield import api, almanac
from datetime import datetime

st.set_page_config(page_title="Mi Luna", page_icon="🌙")

st.title("🌙 Mi Calendario Lunar")

# Selector de fecha para ver otros días
st.subheader("Selecciona una fecha base")
fecha_elegida = st.date_input("¿Desde qué día quieres calcular?", datetime.now())

if st.button('✨ Ver lunas (Próximos 31 días)'):
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    
    # Rango basado en tu elección
    t0 = ts.utc(fecha_elegida.year, fecha_elegida.month, fecha_elegida.day)
    t1 = ts.utc(fecha_elegida.year, fecha_elegida.month, fecha_elegida.day + 31)

    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    lunas = {0: "🌑 Nueva", 1: "🌓 Creciente", 2: "🌕 Llena", 3: "🌗 Menguante"}

    st.write(f"### Fases en Horario UTC:")
    for ti, yi in zip(t, y):
        # Mostramos la fecha y hora UTC exacta
        st.success(f"*{lunas[yi]}* \n\n 📅 {ti.utc_strftime('%d/%m/%Y a las %H:%M UTC')}")

st.sidebar.info("App actualizada: Selector de fecha y UTC 🚀")
