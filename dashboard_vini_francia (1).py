# DASHBOARD INTERATTIVA VINI DI FRANCIA (COMPLETA)

# 1. Installazione dei pacchetti:
# pip install streamlit pandas plotly geopandas

# 2. Salva come: dashboard_vini_francia.py

import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd

st.set_page_config(layout="wide")

# ---------- UPLOAD DATI PERSONALIZZATI ----------
st.sidebar.header("📁 Carica il tuo file CSV")
file = st.sidebar.file_uploader("Scegli un file con i tuoi vini", type="csv")

if file is not None:
    dati_vini = pd.read_csv(file)
else:
    dati_vini = pd.DataFrame({
        'Vino': ['Château Margaux', 'Chablis', 'Dom Pérignon', 'Côtes du Rhône', 'Sancerre'],
        'Tipo': ['Rosso', 'Bianco', 'Spumante', 'Rosso', 'Bianco'],
        'Vitigni': [
            'Cabernet Sauvignon, Merlot', 
            'Chardonnay', 
            'Chardonnay, Pinot Noir', 
            'Grenache, Syrah', 
            'Sauvignon Blanc'
        ],
        'Regione': ['Bordeaux', 'Bourgogne', 'Champagne', 'Rhône', 'Loire']
    })

# ---------- ESTRAZIONE VITIGNI SINGOLI ----------
dati_vini['Vitigni_List'] = dati_vini['Vitigni'].str.split(', ')
v_tutti = sorted(set([v for sublist in dati_vini['Vitigni_List'] for v in sublist]))

# ---------- SIDEBAR ----------
st.sidebar.title("🎯 Filtri Interattivi")
tipo_filtro = st.sidebar.multiselect("Tipo di Vino", options=dati_vini['Tipo'].unique(), default=dati_vini['Tipo'].unique())
regione_filtro = st.sidebar.multiselect("Regione", options=dati_vini['Regione'].unique(), default=dati_vini['Regione'].unique())
vitigno_filtro = st.sidebar.multiselect("Vitigno", options=v_tutti, default=v_tutti)

# ---------- FILTRAGGIO ----------
def contiene_vitigno(lista, selezione):
    return any(v in lista for v in selezione)

dati_filtrati = dati_vini[
    (dati_vini['Tipo'].isin(tipo_filtro)) &
    (dati_vini['Regione'].isin(regione_filtro)) &
    (dati_vini['Vitigni_List'].apply(lambda x: contiene_vitigno(x, vitigno_filtro)))
]

# ---------- GRAFICI ----------
st.title("🍷 Dashboard Interattiva - Vini di Francia")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribuzione per Tipo di Vino")
    fig1 = px.histogram(dati_filtrati, x='Tipo', color='Tipo')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📈 Numero di Vini per Regione")
    fig2 = px.histogram(dati_filtrati, x='Regione', color='Regione')
    st.plotly_chart(fig2, use_container_width=True)

# ---------- GRAFICO A TORTA ----------
st.subheader("🥧 Distribuzione Percentuale Tipi di Vino")
fig3 = px.pie(dati_filtrati, names='Tipo', title='Distribuzione dei Tipi di Vino')
st.plotly_chart(fig3, use_container_width=True)

# ---------- MAPPA REGIONI INTERATTIVA CON PLOTLY ----------
st.subheader("🗺️ Mappa delle Regioni Vinicole (interattiva e cliccabile)")

@st.cache_data
def carica_geojson():
    url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions/regions.geojson"
    gdf = gpd.read_file(url)
    return gdf

regioni_geo = carica_geojson()

# Conta i vini per regione nel geojson
regioni_geo['nome'] = regioni_geo['nom']
regioni_geo['Numero_Vini'] = regioni_geo['nome'].apply(lambda r: dati_filtrati['Regione'].str.contains(r, case=False).sum())

fig_map = px.choropleth(
    regioni_geo,
    geojson=regioni_geo.geometry,
    locations=regioni_geo.index,
    color='Numero_Vini',
    hover_name='nome',
    projection="mercator"
)
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# ---------- TABELLA ----------
st.subheader("📋 Tabella dei Vini Filtrati")
st.dataframe(dati_filtrati.drop(columns=['Vitigni_List']).reset_index(drop=True))
