import streamlit as st
from data import *
from report import *
import pandas as pd

st.title('Messbericht')
st.markdown('Erzeugung eines Messberichts schalltechnischer Messungen mit den Messgeräten NOR145. Die Vorverarbeitung der Messdaten erfolgt mit der Software NorReview. Die Daten werden als xlsm Datei importiert.')

# Mehrere Dateien hochladen?
mehrere = st.checkbox("Mehrere Dateien hochladen")

if mehrere:
    uploaded_files = st.file_uploader(
        "Dateien hochladen", type=['xlsm'], accept_multiple_files=True)
    verfahren = st.radio(
        "Verfahren zur Ermittlung des maßgeblichen Ergebnisses",
        ["Maximalpegel", "Mittelwert (energetisch)"])
else:
    single_file = st.file_uploader("Datei hochladen", type=['xlsm'])
    uploaded_files = [single_file] if single_file is not None else []
    verfahren = "Maximalpegel"

if uploaded_files:

    protocols = []
    for f in uploaded_files:
        p = protocol(f)
        p.dateiname = f.name
        protocols.append(p)

    titel = st.text_input("Titel", "Schalltechnische Immissionsmessung bei der Musterfirma GmbH in Musterstadt")

    thema = st.text_input("Thema", "Immissionsmessung, Tagzeit, MP01")

    beschreibung = st.text_area("Beschreibung", "Die Messung wurde durchgeführt, um die Schallimmissionen der Musterfirma GmbH zu überprüfen. Die Messung fand am 01.01.2023 statt. Die Wetterbedingungen waren optimal für die Messung.")

    others = sorted({m for p in protocols for m in p.markers}
                    - {"Gesamt", "Ohne Marker"})
    marker_optionen = ["Gesamt", "Ohne Marker"] + others
    spektrum_marker = st.selectbox("Marker für Spektrum", marker_optionen)

    filename = st.text_input("Dateiname", "Messbericht.docx")

    metadata = {}
    metadata["titel"] = titel
    metadata["thema"] = thema
    metadata["beschreibung"] = beschreibung
    metadata["verfahren"] = verfahren
    metadata["spektrum_marker"] = spektrum_marker

    st.download_button(
        "Bericht herunterladen",
        data=renderreport(protocols, metadata),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")