import streamlit as st
from data import *
from report import *
import pandas as pd

@st.cache_data
def protokoll(uploaded_file):
    return dfprotokoll(uploaded_file)

@st.cache_data
def marker(uploaded_file):
    return dfmarker(uploaded_file)

@st.cache_data
def konfiguration(uploaded_file):
    return dfkonfiguration(uploaded_file)

@st.cache_data
def check(uploaded_file):
    return checkfile(uploaded_file)

st.title('Messbericht')
st.markdown('Erzeugung eines Messberichts schalltechnischer Messungen mit den Messgeräten HBK 2255 und HBK 2245. Die Vorverarbeitung der Messdaten erfolgt mit der Software EnviroNoiseOffice. Die Daten werden als xlsx Datei importiert.')

# Excel Datei hochladen
uploaded_file = st.file_uploader("Dateien hochladen",type=['xlsx'])

if uploaded_file is not None:
    if check(uploaded_file):
        
        protokolldf = protokoll(uploaded_file)
        markerdf = marker(uploaded_file)
        metadata = konfiguration(uploaded_file).to_dict(orient='records')[0]

        marker_names = st.multiselect("Marker:", allmarkers(markerdf))

        titel = st.text_input("Titel", "Schalltechnische Immissionsmessung bei der Musterfirma GmbH in Musterstadt")

        thema = st.text_input("Thema", "Immissionsmessung, Tagzeit, MP01")

        metadata["titel"] = titel
        metadata["thema"] = thema
        metadata["marker_names"] = marker_names

        st.download_button(
            "Bericht herunterladen", 
            data=renderreport(protokolldf, markerdf, metadata), 
            file_name="Messbericht.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        

    else:
        st.error("Die Datei enthält nicht die notwendigen Tabellenblätter oder Spalten. Bitte überprüfen Sie die Datei und laden Sie eine korrekte Datei hoch.")