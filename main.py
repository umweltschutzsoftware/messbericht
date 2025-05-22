import streamlit as st
from data import *
from report import *
import pandas as pd

st.title('Messbericht')
st.markdown('Erzeugung eines Messberichts schalltechnischer Messungen mit den Messgeräten NOR145. Die Vorverarbeitung der Messdaten erfolgt mit der Software NorReview. Die Daten werden als xlsm Datei importiert.')

# Excel Datei hochladen
uploaded_file = st.file_uploader("Dateien hochladen",type=['xlsm'])

if uploaded_file is not None:
         
    measuringprotocol = protocol(uploaded_file)
    markers = measuringprotocol.markers
    #metadata = konfiguration(uploaded_file).to_dict(orient='records')[0]

    #marker_names = st.multiselect("Marker:", markers)

    titel = st.text_input("Titel", "Schalltechnische Immissionsmessung bei der Musterfirma GmbH in Musterstadt")

    thema = st.text_input("Thema", "Immissionsmessung, Tagzeit, MP01")

    beschreibung = st.text_area("Beschreibung", "Die Messung wurde durchgeführt, um die Schallimmissionen der Musterfirma GmbH zu überprüfen. Die Messung fand am 01.01.2023 statt. Die Wetterbedingungen waren optimal für die Messung.")

    filename = st.text_input("Dateiname", "Messbericht.docx")

    metadata = {}
    metadata["titel"] = titel
    metadata["thema"] = thema
    metadata["beschreibung"] = beschreibung
    #metadata["marker_names"] = marker_names

    st.download_button(
        "Bericht herunterladen", 
        data=renderreport(measuringprotocol, metadata), 
        file_name=filename, 
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")