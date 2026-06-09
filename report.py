import docx
from docxtpl import DocxTemplate, InlineImage
import io
import os
import pandas as pd
import numpy as np
from plot import *
from data import *

# Spalten, die energetisch gemittelt werden
METRIC_COLS = ['LAeq', 'LCeq', 'LAFmax', 'LAFTeq', 'LAeq_95']
# Spalten, die als t-Spalte (deutsches Komma) für die Anzeige formatiert werden
T_COLS = ['LAeq', 'LAFTeq', 'LAFmax', 'LCeq', 'K_I', 'LAeq_95']


def _komma(x):
    """Formatiere einen Pegel mit deutschem Komma und einer Nachkommastelle."""
    return f"{x:.1f}".replace(".", ",")


def _add_t_columns(df):
    """Ergänze die Anzeige-Spalten tLAeq, tLAFTeq, ... mit deutschem Komma."""
    for col in T_COLS:
        if col in df.columns:
            df['t' + col] = df[col].apply(_komma)
    return df


def _sort_summe(df):
    """Sortiere so, dass 'Gesamt' zuerst und 'Ohne Marker' an zweiter Stelle steht."""
    return pd.concat([
        df[df["Marker"] == "Gesamt"],
        df[df["Marker"] == "Ohne Marker"],
        df[~df["Marker"].isin(["Gesamt", "Ohne Marker"])]
    ], ignore_index=True)


def _format_summe(summarkerdf):
    """Ergänze K_I, sortiere und formatiere eine Summen-Tabelle für die Anzeige."""
    df = summarkerdf.copy()
    df["K_I"] = df["LAFTeq"] - df["LAeq"]
    df = _sort_summe(df)
    _add_t_columns(df)
    return df


def prepare_werte(p):
    """Bereite Details- und Summen-Tabelle einer Messung für das Template auf.

    Liefert (werte_dict, summedf). summedf (numerisch + formatiert, sortiert) wird
    zusätzlich für die Ergebnisermittlung (Maximalpegel) benötigt.
    """
    # Details: ohne "Gesamt" und "Ohne Marker"
    markerdf = p.markerdf[~p.markerdf["Marker"].isin(["Gesamt", "Ohne Marker"])].copy()
    markerdf["K_I"] = markerdf["LAFTeq"] - markerdf["LAeq"]
    _add_t_columns(markerdf)

    # Summen
    summedf = _format_summe(p.summarkerdf)

    werte = {
        "details": markerdf.to_dict(orient='records'),
        "summe": summedf.to_dict(orient='records'),
    }
    return werte, summedf


def _ergebnis_maximalpegel(summes, dateien):
    """Wähle die maßgebliche Messung: höchster Wert aus LAeq/LAFTeq (Marker 'Gesamt')."""
    best_idx, best_val = 0, None
    for i, sdf in enumerate(summes):
        g = sdf[sdf["Marker"] == "Gesamt"]
        if g.empty:
            continue
        val = max(float(g["LAeq"].iloc[0]), float(g["LAFTeq"].iloc[0]))
        if best_val is None or val > best_val:
            best_val, best_idx = val, i
    name = dateien[best_idx]["dateiname"] or f"Messung {best_idx + 1}"
    hinweis = (f"Maximalpegelverfahren: maßgebliche Messung „{name}“ "
               f"(höchster Pegel aus LAeq/LAFTeq: {_komma(best_val)} dB(A)).")
    return summes[best_idx], hinweis


def _ergebnis_mittelwert(protocols):
    """Energetische Mittelung der Pegel je Marker über alle Messungen."""
    allsum = pd.concat([p.summarkerdf for p in protocols], ignore_index=True)
    meandf = (
        allsum.groupby('Marker')[METRIC_COLS]
        .apply(lambda d: 10 * np.log10((10 ** (d / 10)).mean()))
        .reset_index()
    )
    ergsumme = _format_summe(meandf)
    hinweis = (f"Mittelwertverfahren: energetische Mittelung über {len(protocols)} "
               f"Messungen je Marker.")
    return ergsumme, hinweis


def renderreport(protocols, metadata):
    # Rückwärtskompatibel: einzelnes protocol als Liste behandeln
    if not isinstance(protocols, (list, tuple)):
        protocols = [protocols]

    report = io.BytesIO()
    # Nutze DocxTemplate um das Template zu laden
    doc = DocxTemplate("messergebnis_vorlage.docx")

    verfahren = metadata.get("verfahren", "Maximalpegel")

    info = {
        "titel": metadata.get("titel", ""),
        "thema": metadata.get("thema", ""),
        "beschreibung": metadata.get("beschreibung", ""),
        "mehrere": len(protocols) > 1,
        "ergebnis": {},
    }

    spektrum_marker = metadata.get("spektrum_marker", "Gesamt")

    tmpfiles = []
    dateien = []
    summes = []

    for p in protocols:
        laeqfile = plot_laeq(p)
        spektrumfile = plot_spektren(p.dfspektren(spektrum_marker))
        tmpfiles.extend([laeqfile, spektrumfile])

        werte, summedf = prepare_werte(p)
        summes.append(summedf)

        dateien.append({
            "dateiname": getattr(p, "dateiname", "") or "",
            "startzeit": p.info["startzeit"],
            "endzeit": p.info["endzeit"],
            "Kalibrierdatum": p.startdate,
            "pegelzeit": InlineImage(doc, laeqfile, width=docx.shared.Inches(6.17)),
            "spektrum": InlineImage(doc, spektrumfile, width=docx.shared.Inches(6.17)),
            "werte": werte,
        })

    info["dateien"] = dateien

    # Maßgebliches Ergebnis nur bei mehreren Dateien
    if info["mehrere"]:
        if "ittel" in verfahren:  # "Mittelwert ..."
            ergsumme, hinweis = _ergebnis_mittelwert(protocols)
        else:
            ergsumme, hinweis = _ergebnis_maximalpegel(summes, dateien)
        info["ergebnis"] = {
            "summe": ergsumme.to_dict(orient='records'),
            "hinweis": hinweis,
        }

    doc.render(info)

    # Fülle das Template mit den Daten aus dem Report
    doc.save(report)

    # Lösche die temporären Bilddateien
    for f in tmpfiles:
        if os.path.exists(f):
            os.remove(f)

    return report
