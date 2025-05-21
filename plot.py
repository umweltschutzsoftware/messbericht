import random
import string

import matplotlib.pyplot as plt

def generate_random_filename():
        letters = string.ascii_lowercase
        random_filename = ''.join(random.choice(letters) for i in range(10))
        return random_filename

def plot_laeq(p):
    # Nutze als Breite die DINA4 Breite
    plt.figure(figsize=(8.27, 3.8))
    # Nutze Arial als Schriftart
    plt.rcParams['font.family'] = 'Arial'

    protocoldf = p.protocoldf
    markerdf = p.markerdf

    usedmarker = [m for m in p.markers if m not in ["Gesamt", "Ohne Marker"]]
    usedmarkerdf = markerdf[markerdf.Marker.isin(usedmarker)]

    # Zeige die Spalten LAeq, LAFmax und LAFTeq in einem Diagramm an
    protocoldf['Startuhrzeit'] = protocoldf['Startuhrzeit'].astype(str)
    plt.plot(protocoldf['Startuhrzeit'], protocoldf['LAeq'], label='LAeq', linewidth=0.3)
    plt.plot(protocoldf['Startuhrzeit'], protocoldf['LAFmax'], label='LAFmax', linewidth=0.3)
    plt.plot(protocoldf['Startuhrzeit'], protocoldf['LAFTeq'], label='LAFTeq', linewidth=0.3)

    # Weise jedem Marker eine eigene Farbe zu
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

    # Füge eine Legende für die Marker hinzu indem der Farbe der Name des Markers zugeordnet wird
    # Stelle den Bereich des Markers als Fläche in der Legende dar
    usedcolors = {}
    for index, marker_name in enumerate(usedmarker):
        plt.plot([], [], color=colors[index], label=marker_name, alpha=0.5, linewidth=6)
        usedcolors[marker_name] = colors[index]


    for index, row in usedmarkerdf.iterrows():
        plt.axvspan(row['Startuhrzeit'], row['Enduhrzeit'], color=usedcolors[row["Marker"]], alpha=0.3)

    # Finde den min und den max value der Spale LAeq
    # Setze das y Limit als die größte Ganze Zahl die 20 einheiten größer ist als der max Wert
    # Setze das y Limit als die größte Ganze Zahl die 20 einheiten kleiner ist als der min Wert
    plt.ylim(protocoldf['LAeq'].min() - 20, protocoldf['LAeq'].max() + 20)

    # Start und End das Diagramm jeweils am äußeren Rand
    plt.xlim(protocoldf['Startuhrzeit'].iloc[0], protocoldf['Startuhrzeit'].iloc[-1])
    plt.xlabel('Uhrzeit')
    plt.ylabel('dB(A)')
    plt.grid(True, linestyle='--', alpha=0.5)

    # Wähle als xticks 10 Startuhrzeiten aus
    x_ticks = protocoldf['Startuhrzeit'].iloc[::int(len(protocoldf['Startuhrzeit'])/5)]
    plt.xticks(x_ticks)

    plt.legend()
    filename = generate_random_filename()
    plt.savefig(filename + '.png')
    return filename + '.png'


def plot_spektren(spektrendf):
    # Entferne alle Zusatz Hz als Einheit
    spektrendf.index = spektrendf.index.str.replace(' Hz', '')
    # Entferne alle Zusatz kHz und setze nur k
    spektrendf.index = spektrendf.index.str.replace(' kHz', 'k')
    # Reduziere die Anzahl Anzahl der xticks auf 10, aber zeige alle Werte
    #x_ticks = spektren['Frequenz'].iloc[::int(len(spektren['Frequenz'])/5)]


    # Zeige die Spektren in einem Balkendiagramm an
    # Die x Achse beschreibt jede Spalte
    # Der Titel ist die Frequenz, d.h. jeder Spaltenname ohne den Präfix LAeq   
    # Die y Achse beschreibt den Wert der Spalte
    spektrendf.plot(kind='bar', figsize=(8.27, 3), width=0.8, color='black', legend=False, grid=True)
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