import pandas as pd

def dfprotokoll(stfile):
    df = pd.read_excel(stfile, sheet_name='BB-Protokoll')
    df['Startuhrzeit'] = pd.to_datetime(df['Startzeit'], dayfirst=True).dt.time.astype(str)
    df['Enduhrzeit'] = pd.to_datetime(df['Endzeitpunkt'], dayfirst=True).dt.time.astype(str)
    return df

def dfmarker(stfile):
    df = pd.read_excel(stfile, sheet_name='Marker')
    df['Startuhrzeit'] = pd.to_datetime(df['Startzeit'], dayfirst=True).dt.time.astype(str)
    df['Enduhrzeit'] = pd.to_datetime(df['Endzeitpunkt'], dayfirst=True).dt.time.astype(str)
    return df

def dfkonfiguration(stfile):
    df = pd.read_excel(stfile, sheet_name='Konfiguration')
    # Benenne Positions-URL in PositionsURL um
    df = df.rename(columns={"Positions-URL": "PositionsURL"})
    return df

def allmarkers(markerdf):
    return markerdf[markerdf.Messung == 'Summe']["Marker"].unique()


def checkfile(stfile):
    # Überprüfe ob die Excel Tabelle die benötigten Tabellenblätter enthält
    try:
        protokoll = dfprotokoll(stfile)
        marker = dfmarker(stfile)
        konfiguration = dfkonfiguration(stfile)
    except:
        return False
    
    # Überprüfe ob die Spalten Startzeit und Endzeitpunkt in der Tabelle data_frame enthalten sind
    if 'Startzeit' not in protokoll.columns or 'Endzeitpunkt' not in protokoll.columns:
        return False
    
    # Überprüfe ob die Spalten Startzeit und Endzeitpunkt sowie Messung und Marker in der Tabelle marker enthalten sind
    if 'Startzeit' not in marker.columns or 'Endzeitpunkt' not in marker.columns or 'Messung' not in marker.columns or 'Marker' not in marker.columns:
        return False
    
    return True

def perparemarker(markerdf):
    # Entferne alle Spalten in denen die Spalte Messung nicht den Wert Summe hat
    markerdf = markerdf[markerdf.Messung == 'Summe']
    markerdf["K_I"] = markerdf["LAFTeq"] - markerdf["LAeq"]
    return markerdf

def perpareinfo(protokolldf):
    starttime = pd.to_datetime(protokolldf['Startzeit'], dayfirst=True).min()
    endtime = pd.to_datetime(protokolldf['Endzeitpunkt'], dayfirst=True).max()
    # Duration in Hours, minutes and seconds
    duration = endtime - starttime
    duration_hours = duration.seconds // 3600
    duration_minutes = (duration.seconds % 3600) // 60
    duration_seconds = duration.seconds % 60
    duration = f"{duration_hours} Stunden, {duration_minutes} Minuten, {duration_seconds} Sekunden"
    instrument = protokolldf['Instrument'].unique()[0]
  
    return {
        "dauer": duration,
        "startzeit": starttime.strftime('%d.%m.%Y %H:%M:%S'),
        "endzeit": endtime.strftime('%d.%m.%Y %H:%M:%S'),
        "messgerät": instrument
    }
