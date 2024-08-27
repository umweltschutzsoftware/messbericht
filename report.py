import docx
from docxtpl import DocxTemplate, InlineImage
import io
from plot import *
from data import *
import os

def renderreport(protokolldf, markerdf, metadata):
    report = io.BytesIO()
    # Nutze DocxTemplate um das Template zu laden
    doc = DocxTemplate("messergebnis_vorlage.docx")

    laeqfile = plot_laeq(protokolldf, markerdf)

    info = perpareinfo(protokolldf)
    # Füge jedes item der metadaten als eigenes item in info hinzu
    for key, value in metadata.items():
        info[key] = value

    marker_names = metadata["marker_names"]

    # Ergänze die Spalte K_I in markerdf
    markerdf["K_I"] = markerdf["LAFTeq"] - markerdf["LAeq"]
    markerdf = markerdf.rename(columns={"Verstrichene Zeit": "Zeit"})


    # Ergänze die Spalten tLAeq, tLAFTeq, tLAFmax und tK_I
    # Diese beinhaltne den Wert der jeweiligen Spalte ohne t
    # Formatiere den Wert getrennt mit komma, auf eine nachkommastelle gerundet
    markerdf["tLAeq"] = markerdf["LAeq"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    markerdf["tLAFTeq"] = markerdf["LAFTeq"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    markerdf["tLAFmax"] = markerdf["LAFmax"].apply(lambda x: f"{x:.1f}".replace(".", ","))
    markerdf["tK_I"] = markerdf["K_I"].apply(lambda x: f"{x:.1f}".replace(".", ","))

    # Lese alle Zeilen aus dem Marker df, die nicht den Wert Summe in der Spalte Messung haben
    detailsmarkerdf = markerdf[markerdf.Messung != 'Summe']
    # Berücksichtigte nur die Zeilen, in denen ein marker_name aus marker_names vorkommt
    detailsmarkerdf = detailsmarkerdf[detailsmarkerdf.Marker.isin(marker_names)]
    

    summemarkerdf = markerdf[markerdf.Messung == 'Summe']
    summemarkerdf = summemarkerdf[summemarkerdf.Marker.isin(marker_names)]

    info["werte"] = {}
    info["werte"]["details"] = detailsmarkerdf.to_dict(orient='records')
    info["werte"]["summe"] = summemarkerdf.to_dict(orient='records')

    info["spektren"] = []
    spektrenfiles = []
    for marker_name in marker_names:
        spektrenfile = plot_spektren(markerdf, marker_name)
        spektrenfiles.append(spektrenfile)
        info["spektren"].append({
            "name": marker_name,
            "bild": InlineImage(doc, spektrenfile, width=docx.shared.Inches(6.17))
        })


    info['pegelzeit'] = InlineImage(doc, laeqfile, width=docx.shared.Inches(6.17))

    doc.render(info)

    
    # Fülle das Template mit den Daten aus dem Report
    doc.save(report)

    # Lösche die laeqfile
    os.remove(laeqfile)
    for spektrenfile in spektrenfiles:
        os.remove(spektrenfile)

    return report