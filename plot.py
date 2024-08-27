import random
import string

import matplotlib.pyplot as plt

def generate_random_filename():
        letters = string.ascii_lowercase
        random_filename = ''.join(random.choice(letters) for i in range(10))
        return random_filename

def plot_laeq(protkolldf, markerdf):
    # Nutze als Breite die DINA4 Breite
    plt.figure(figsize=(8.27, 3.8))
    # Nutze Arial als Schriftart
    plt.rcParams['font.family'] = 'Arial'

    # Zeige die Spalten LAeq, LAFmax und LAFTeq in einem Diagramm an
    protkolldf['Startuhrzeit'] = protkolldf['Startuhrzeit'].astype(str)
    plt.plot(protkolldf['Startuhrzeit'], protkolldf['LAeq'], label='LAeq', linewidth=0.3)
    #plt.plot(data_frame['Startuhrzeit'], data_frame['LAFmax'], label='LAFmax', linewidth=0.3)
    #plt.plot(data_frame['Startuhrzeit'], data_frame['LAFTeq'], label='LAFTeq', linewidth=0.3)

    # Markiere die Bereiche, in denen die Marker gesetzt sind
    # Entferne alle Zeilen in denen die Spalte Messung den Wert Summe hat
    markerdf = markerdf[markerdf.Messung != 'Summe']
    # Entferne alle Zeilen bei denen in der Spalte Marker der Begriff Gesamt vorkommt
    markerdf = markerdf[~markerdf.Marker.str.contains('Gesamt')]
    # Weise jedem Marker eine eigene Farbe zu
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

    # Füge eine Legende für die Marker hinzu indem der Farbe der Name des Markers zugeordnet wird
    # Stelle den Bereich des Markers als Fläche in der Legende dar
    usedcolors = {}
    for index, marker_name in enumerate(markerdf.Marker.unique()):
        plt.plot([], [], color=colors[index], label=marker_name, alpha=0.5, linewidth=6)
        usedcolors[marker_name] = colors[index]


    for index, row in markerdf.iterrows():
        plt.axvspan(row['Startuhrzeit'], row['Enduhrzeit'], color=usedcolors[row["Marker"]], alpha=0.3)

    # Finde den min und den max value der Spale LAeq
    # Setze das y Limit als die größte Ganze Zahl die 20 einheiten größer ist als der max Wert
    # Setze das y Limit als die größte Ganze Zahl die 20 einheiten kleiner ist als der min Wert
    plt.ylim(protkolldf['LAeq'].min() - 20, protkolldf['LAeq'].max() + 20)

    # Start und End das Diagramm jeweils am äußeren Rand
    plt.xlim(protkolldf['Startuhrzeit'].iloc[0], protkolldf['Startuhrzeit'].iloc[-1])
    plt.xlabel('Uhrzeit')
    plt.ylabel('dB(A)')
    plt.grid(True, linestyle='--', alpha=0.5)

    # Wähle als xticks 10 Startuhrzeiten aus
    x_ticks = protkolldf['Startuhrzeit'].iloc[::int(len(protkolldf['Startuhrzeit'])/5)]
    plt.xticks(x_ticks)

    plt.legend()
    filename = generate_random_filename()
    plt.savefig(filename + '.png')
    return filename + '.png'


def plot_spektren(markerdf, marker_name):

    spektren = markerdf[(markerdf.Marker == marker_name) & (markerdf.Messung == 'Summe')]
    # Alle Spalten, die nicht mit LAeq beginnen, werden entfernt
    spektren = spektren.loc[:, spektren.columns.str.startswith('LAeq')]
    # Transponiere das Dataframe, sodass die Spalten jeweils als Zeilen dargestellt werden
    spektren = spektren.T
    # Nenne den Index Frequenz
    spektren.index.name = 'Frequenz'
    # Ändere den Namen der Spalte 1 in LAeq 
    spektren = spektren.rename(columns={0: 'LAeq'})

    # Entferne den Zusatz LAeq aus dem Index
    spektren.index = spektren.index.str.replace('LAeq ', '')
    # Entferne alle Zusatz Hz als Einheit
    spektren.index = spektren.index.str.replace(' Hz', '')
    # Entferne alle Zusatz kHz und setze nur k
    spektren.index = spektren.index.str.replace(' kHz', 'k')
    # Reduziere die Anzahl Anzahl der xticks auf 10, aber zeige alle Werte
    #x_ticks = spektren['Frequenz'].iloc[::int(len(spektren['Frequenz'])/5)]

    # Entferne die Zeile mit dem Wert LAeq
    spektren = spektren.drop('LAeq')

    # Zeige die Spektren in einem Balkendiagramm an
    # Die x Achse beschreibt jede Spalte
    # Der Titel ist die Frequenz, d.h. jeder Spaltenname ohne den Präfix LAeq   
    # Die y Achse beschreibt den Wert der Spalte
    spektren.plot(kind='bar', figsize=(8.27, 3), width=0.8, color='black', legend=False, grid=True)
    plt.xlabel('Frequenz [Hz]')
    plt.ylabel('dB(A)')
    plt.tight_layout()
    plt.grid(True, linestyle='-', alpha=0.5)
    plt.xlabel('Frequenz [Hz]')
    plt.gca().set_axisbelow(True)  # Set the bars in front of the grid
    plt.tight_layout()
    plt.grid(True, linestyle='-', alpha=0.5)
    filename = generate_random_filename()
    plt.savefig(filename + '.png')
    return filename + '.png'