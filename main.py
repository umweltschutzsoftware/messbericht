import streamlit as st
from data import *
from report import *
import pandas as pd

st.title('Messbericht')
st.markdown('Erzeugung eines Messberichts schalltechnischer Messungen mit den Messgeräten HBK 2255 und HBK 2245. Die Vorverarbeitung der Messdaten erfolgt mit der Software EnviroNoiseOffice. Die Daten werden als xlsx Datei importiert.')

# Excel Datei hochladen
uploaded_file = st.file_uploader("Dateien hochladen",type=['xlsm'])

if uploaded_file is not None:
         
    measuringprotocol = protocol(uploaded_file)
    markers = measuringprotocol.markers
    #metadata = konfiguration(uploaded_file).to_dict(orient='records')[0]

    #marker_names = st.multiselect("Marker:", markers)

    titel = st.text_input("Titel", "Schalltechnische Immissionsmessung bei der Musterfirma GmbH in Musterstadt")

    thema = st.text_input("Thema", "Immissionsmessung, Tagzeit, MP01")

    metadata = {}
    metadata["titel"] = titel
    metadata["thema"] = thema
    #metadata["marker_names"] = marker_names

    st.download_button(
        "Bericht herunterladen", 
        data=renderreport(measuringprotocol, metadata), 
        file_name="Messbericht.docx", 
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")