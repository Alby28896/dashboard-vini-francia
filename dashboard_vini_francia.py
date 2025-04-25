# DASHBOARD INTERATTIVA VINI DI FRANCIA (COMPLETA)

# 1. Installazione dei pacchetti:
# pip install streamlit pandas plotly folium streamlit-folium

# 2. Salva come: dashboard_vini_francia.py

import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

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

# ---------- COORDINATE REGIONI ----------
regioni_coord = {
    'Bordeaux': [44.837789, -0.57918],
    'Champagne': [49.256, 4.031],
    'Bourgogne': [47.0524, 4.3837],
    'Alsace': [48.3182, 7.4416],
    'Loire': [47.7516, 0.334],
    'Provence': [43.9352, 6.0679],
    'Rhône': [44.9334, 4.8924],
    'Languedoc-Roussillon': [43.6119, 3.8777],
    'Corsica': [42.0396, 9.0129]
}

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

# ---------- MAPPA INTERATTIVA ----------
st.subheader("🗺️ Mappa delle Regioni Vinicole")
mappa = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
for index, row in dati_filtrati.iterrows():
    regione = row['Regione']
    if regione in regioni_coord:
        coord = regioni_coord[regione]
        popup_text = f"<b>{row['Vino']}</b><br>Tipo: {row['Tipo']}<br>Vitigni: {row['Vitigni']}"
        folium.Marker(location=coord, popup=popup_text).add_to(mappa)
folium_static(mappa)

# ---------- TABELLA ----------
st.subheader("📋 Tabella dei Vini Filtrati")
st.dataframe(dati_filtrati.drop(columns=['Vitigni_List']).reset_index(drop=True))
