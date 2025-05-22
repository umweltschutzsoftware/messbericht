import docx
from docxtpl import DocxTemplate, InlineImage
import io
from plot import *
from data import *
import os

def renderreport(p, metadata):
    report = io.BytesIO()
    # Nutze DocxTemplate um das Template zu laden
    doc = DocxTemplate("messergebnis_vorlage.docx")

    laeqfile = plot_laeq(p)

    metadata["Kalibrierdatum"] = p.startdate
    info = p.info
    # Füge jedes item der metadaten als eigenes item in info hinzu
    for key, value in metadata.items():
        info[key] = value

    markerdf = p.markerdf
    summarkerdf = p.summarkerdf

    markerdf = markerdf[~markerdf["Marker"].isin(["Gesamt", "Ohne Marker"])]
    

    # Ergänze die Spalte K_I in markerdf
    markerdf["K_I"] = markerdf["LAFTeq"] - markerdf["LAeq"]
    summarkerdf["K_I"] = summarkerdf["LAFTeq"] - summarkerdf["LAeq"]
    # Sortiere summarkerdf so, dass "Gesamt" immer zuerst und "Ohne Marker" immer an zweiter Stelle steht
    summarkerdf = pd.concat([
        summarkerdf[summarkerdf["Marker"] == "Gesamt"],
        summarkerdf[summarkerdf["Marker"] == "Ohne Marker"],
        summarkerdf[~summarkerdf["Marker"].isin(["Gesamt", "Ohne Marker"])]
    ], ignore_index=True)
    # Ergänze die Spalte Zeit in markerdf
    #markerdf = markerdf.rename(columns={"Verstrichene Zeit": "Zeit"})


    # Ergänze die Spalten tLAeq, tLAFTeq, tLAFmax und tK_I
    # Diese beinhaltne den Wert der jeweiligen Spalte ohne t
    # Formatiere den Wert getrennt mit komma, auf eine nachkommastelle gerundet
    markerdf["tLAeq"] = markerdf["LAeq"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    markerdf["tLAFTeq"] = markerdf["LAFTeq"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    markerdf["tLAFmax"] = markerdf["LAFmax"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    markerdf["tLCeq"] = markerdf["LCeq"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    markerdf["tK_I"] = markerdf["K_I"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    markerdf["tLAeq_95"] = markerdf["LAeq_95"].apply(lambda x: f"{x:.1f}".replace(".", ","))

    summarkerdf["tLAeq"] = summarkerdf["LAeq"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    summarkerdf["tLAFTeq"] = summarkerdf["LAFTeq"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    summarkerdf["tLAFmax"] = summarkerdf["LAFmax"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    summarkerdf["tLCeq"] = summarkerdf["LCeq"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    summarkerdf["tK_I"] = summarkerdf["K_I"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    summarkerdf["tLAeq_95"] = summarkerdf["LAeq_95"].apply(lambda x: f"{x:.1f}".replace(".", ","))



    # Lese alle Zeilen aus dem Marker df, die nicht den Wert Summe in der Spalte Messung haben
    #detailsmarkerdf = markerdf[markerdf.Messung != 'Summe']
    # Berücksichtigte nur die Zeilen, in denen ein marker_name aus marker_names vorkommt
    #detailsmarkerdf = detailsmarkerdf[detailsmarkerdf.Marker.isin(marker_names)]
    

    #summemarkerdf = markerdf[markerdf.Messung == 'Summe']
    #summemarkerdf = summemarkerdf[summemarkerdf.Marker.isin(marker_names)]

    info["werte"] = {}
    info["werte"]["details"] = markerdf.to_dict(orient='records')
    info["werte"]["summe"] = summarkerdf.to_dict(orient='records')
    info["spektren"] = []

    #spektrenfile = plot_spektren(spektrendf)
    #info["spektren"].append({
    #        "name": "Gesamt",
    #        "bild": InlineImage(doc, spektrenfile, width=docx.shared.Inches(6.17))
    #    })


    info['pegelzeit'] = InlineImage(doc, laeqfile, width=docx.shared.Inches(6.17))

    doc.render(info)

    
    # Fülle das Template mit den Daten aus dem Report
    doc.save(report)

    # Lösche die laeqfile
    os.remove(laeqfile)
    #os.remove(spektrenfile)

    return report