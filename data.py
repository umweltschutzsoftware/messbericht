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
        self.spektrendf = self.dfspektren()

        self.summarkerdf = (
            self.markerdf.groupby('Marker')[['LAeq', 'LCeq', 'LAFmax', 'LAFTeq']]
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
        df = pd.read_excel(self.stfile, sheet_name='Profile', skiprows=1, usecols="A:E", names=["Zeitstempel", "LAeq", "LAFmax", "LCeq", "Markers"])
        df['Markers'] = df['Markers'].str.replace('Battery;', '', regex=False)
        df['Markers'] = df['Markers'].str.replace('Stop;', '', regex=False)

        # Calculate the LAFTeq
        # Calculate LAFTeq: mean of LAFmax over rolling 5-row (5s) intervals
        df['LAFTeq'] = df['LAFmax'].rolling(window=5, min_periods=1).mean()

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
            for col in ['LAeq', 'LAFmax', 'LCeq', 'LAFTeq']:
                values = df.loc[mask, col].values
                if col == 'LAFmax':
                    if len(values) > 0:
                        max_value = values.max()
                    else:
                        max_value = np.nan
                    row[f'{col}'] = max_value
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
    
    def dfspektren(self):
        spektren = pd.read_excel(
            self.stfile,
            sheet_name='Global',
            usecols='BA:CE',
            skiprows=1,
            nrows=1
        ).T
        spektren.columns = ['dB(A)']
        spektren.index.name = 'Frequenz'
        spektren.index = spektren.index.str.replace('G3_FRQ_LEQ_', '', regex=False)
        return spektren