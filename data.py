import pandas as pd
import numpy as np

class protocol:
    def __init__(self, stfile):
        self.stfile = stfile
        self.protocoldf = self.dfprocotol()
        self.markers = self.uniquemarkers()
        self.info = self.prepareinfo()
        self.starttime = self.info["startzeit"]
        self.endtime = self.info["endzeit"]
        self.startdate = self.info["startdate"]

        self.markerdf = self.dfmarker()

        self.summarkerdf = (
            self.markerdf.groupby('Marker')[['LAeq', 'LCeq', 'LAFmax', 'LAFTeq', 'LAeq_95']]
            .apply(lambda df: 10 * np.log10((10 ** (df / 10)).mean()))
            .reset_index()
        )
        # Calculate total time for all markers except "Gesamt" and "Ohne Marker"
        other_times = pd.to_timedelta(self.markerdf.loc[~self.markerdf['Marker'].isin(['Gesamt', 'Ohne Marker']), 'Zeit']).sum()
        # Get the original "Ohne Marker" time as timedelta
        ohne_marker_idx = self.markerdf[self.markerdf['Marker'] == 'Ohne Marker'].index[0]
        ohne_marker_time = pd.to_timedelta(self.markerdf.at[ohne_marker_idx, 'Zeit'])
        # Subtract and update the "Ohne Marker" time
        new_ohne_marker_time = ohne_marker_time - other_times
        # Format back to %H:%M:%S
        self.markerdf.at[ohne_marker_idx, 'Zeit'] = str(new_ohne_marker_time).split(' ')[-1]


    def dfprocotol(self):
        # A:E = Zeitstempel/LAeq/LAFmax/LCeq/Markers, F:AJ = Lfeq-Terzspektrum (31 Bänder)
        df = pd.read_excel(self.stfile, sheet_name='Profile', skiprows=1, usecols="A:AJ")
        df = df.rename(columns={
            df.columns[0]: "Zeitstempel", df.columns[1]: "LAeq",
            df.columns[2]: "LAFmax", df.columns[3]: "LCeq", df.columns[4]: "Markers"})
        df['Markers'] = df['Markers'].str.replace('Battery;', '', regex=False)
        df['Markers'] = df['Markers'].str.replace('Stop;', '', regex=False)
        df['Markers'] = df['Markers'].str.replace('Audio-recording;', '', regex=False)
        df['Markers'] = df['Markers'].str.replace('Event0;', '', regex=False)

        # Calculate the LAFTeq
        # Calculate LAFTeq: LAFmax over rolling 5-row (5s) intervals
        df['LAFTeq'] = df['LAFmax'].rolling(window=5, min_periods=1).max()

        # Add a column Stunden with only hours and minutes
        df['Startuhrzeit'] = pd.to_datetime(df['Zeitstempel']).dt.strftime('%H:%M:%S')


        return df
    
    def prepareinfo(self):
        starttime = pd.to_datetime(self.protocoldf['Zeitstempel'], dayfirst=True).min()
        endtime = pd.to_datetime(self.protocoldf['Zeitstempel'], dayfirst=True).max()
        # Duration in Hours, minutes and seconds
        duration = endtime - starttime
        duration_hours = duration.seconds // 3600
        duration_minutes = (duration.seconds % 3600) // 60
        duration_seconds = duration.seconds % 60
        return {
            "dauer": duration,
            "startzeit": starttime.strftime('%d.%m.%Y %H:%M:%S'),
            "endzeit": endtime.strftime('%d.%m.%Y %H:%M:%S'),
            "startdate": starttime.strftime('%d.%m.%Y'),}
    
    def uniquemarkers(self):
        markers = set()
        markers.add('Gesamt')
        markers.add('Ohne Marker')
        for marker_str in self.protocoldf["Markers"].dropna():
            for marker in marker_str.split(";"):
                marker = marker.strip()
                if marker:
                    markers.add(marker)
        return list(markers)
    
    def dfmarker(self):
        # Create a DataFrame for intervals with logarithmic means for LAeq, LAFmax, and LCeq
        markers_data = []
        intervals = []
        in_interval = False
        start_time = None

        global_starttime = self.protocoldf["Zeitstempel"].min()
        global_endtime = self.protocoldf["Zeitstempel"].max()
        df = self.protocoldf.copy()

        intervals.append((global_starttime, global_endtime, 'Gesamt'))
        intervals.append((global_starttime, global_endtime, 'Ohne Marker'))

        for idx, row in df.iterrows():
            marker = row['Markers'].strip()
            if marker != '':
                if not in_interval:
                    start_time = row['Zeitstempel']
                    interval_marker = marker.replace(';', '')
                    in_interval = True
                end_time = row['Zeitstempel']
            else:
                if in_interval:
                    intervals.append((start_time, end_time, interval_marker))
                    in_interval = False

        # If the last row is part of an interval, close it
        if in_interval:
            intervals.append((start_time, end_time, interval_marker))

        for start, end, marker in intervals:
            if marker != 'Ohne Marker':
                mask = (df['Zeitstempel'] >= start) & (df['Zeitstempel'] <= end)
            else:
                mask = (df['Zeitstempel'] >= start) & (df['Zeitstempel'] <= end) & (df['Markers'] == '')
            start_time = pd.to_datetime(start, dayfirst=True)
            end_time = pd.to_datetime(end, dayfirst=True)
            # calculte the time difference in hours, minutes and seconds
            time_diff = end_time - start_time
            hours = time_diff.seconds // 3600
            minutes = (time_diff.seconds % 3600) // 60
            seconds = time_diff.seconds % 60
            # Format the time difference as a string
            time_diff_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            row = {'Startzeit': start, 'Endzeit': end, 'Marker': marker, 'Startuhrzeit': start_time.strftime('%H:%M:%S'), 'Enduhrzeit': end_time.strftime('%H:%M:%S'), 'Zeit': time_diff_str}
            for col in ['LAeq', 'LAFmax', 'LCeq', 'LAFTeq', "LAeq_95"]:
                if col== "LAeq_95":
                    values = df.loc[mask, 'LAeq'].values
                else:
                    values = df.loc[mask, col].values
                if col == 'LAFmax':
                    if len(values) > 0:
                        max_value = values.max()
                    else:
                        max_value = np.nan
                    row[f'{col}'] = max_value
                elif col == 'LAeq_95':
                    if len(values) > 0:
                        row[f'{col}'] = np.quantile(values, 0.05)
                else:
                    if len(values) > 0:
                        linear = 10 ** (values / 10)
                        log_mean = 10 * np.log10(linear.mean())
                    else:
                        log_mean = np.nan
                    row[f'{col}'] = log_mean

            markers_data.append(row)

        markersdf = pd.DataFrame(markers_data)
        return markersdf
    
    def dfspektren(self, marker="Gesamt"):
        # Lfeq-Terzspektrum je Marker: energetischer Mittelwert der Lfeq-Bänder
        # über die zum Marker gehörenden Zeilen des Profils.
        df = self.protocoldf
        band_cols = [c for c in df.columns if str(c).startswith("Lfeq ")]
        if marker == "Gesamt":
            mask = pd.Series(True, index=df.index)
        elif marker == "Ohne Marker":
            mask = df["Markers"].str.strip() == ""
        else:
            mask = df["Markers"].apply(
                lambda s: marker in [m.strip() for m in str(s).split(";") if m.strip()])
        vals = df.loc[mask, band_cols]
        if len(vals) == 0 and marker != "Gesamt":      # Marker in dieser Datei nicht vorhanden
            vals = df[band_cols]                        # Fallback: Gesamt
        leq = 10 * np.log10((10 ** (vals / 10)).mean())
        spektren = leq.to_frame("dB")
        spektren.index = [c.replace("Lfeq ", "").replace(" [dB]", "").replace(" ", "")
                          for c in band_cols]            # -> "20Hz","31,5Hz","1,25kHz","20kHz"
        spektren.index.name = "Frequenz"
        return spektren