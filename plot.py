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
    plt.close()
    return filename + '.png'


def plot_spektren(spektrendf):
    # Arbeite auf einer Kopie, damit der übergebene DataFrame nicht verändert wird
    spektrendf = spektrendf.copy()
    # Bereinige die Frequenz-Labels für die Darstellung: "20Hz" -> "20", "1kHz" -> "1k"
    spektrendf.index = spektrendf.index.str.replace('kHz', 'k', regex=False)
    spektrendf.index = spektrendf.index.str.replace('Hz', '', regex=False)

    # Nutze Arial als Schriftart und die DIN A4 Breite
    plt.rcParams['font.family'] = 'Arial'

    # Zeige das Lfeq-Terzspektrum als Balkendiagramm an
    # x-Achse: Frequenz (Terzband), y-Achse: unbewerteter Pegel in dB
    ax = spektrendf.plot(kind='bar', figsize=(8.27, 3.6), width=0.8,
                         color='black', legend=False, grid=True)
    ax.set_axisbelow(True)  # Gitter hinter die Balken legen
    plt.xlabel('Frequenz [Hz]')
    plt.ylabel('dB')
    plt.grid(True, linestyle='-', alpha=0.5)
    plt.xticks(rotation=90)

    # Zahlenwerte über den Balken anzeigen (deutsches Komma, eine Nachkommastelle)
    werte = spektrendf.iloc[:, 0]
    ax.set_ylim(0, werte.max() + 8)
    labels = [f"{v:.1f}".replace(".", ",") for v in werte]
    ax.bar_label(ax.containers[0], labels=labels, rotation=90,
                 padding=2, fontsize=6)

    plt.tight_layout()
    filename = generate_random_filename()
    plt.savefig(filename + '.png')
    plt.close()
    return filename + '.png'