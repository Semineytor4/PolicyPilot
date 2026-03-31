[Readme.md](https://github.com/user-attachments/files/26387177/Readme.md)
# CustomerChurnLab

Dieses Projekt untersucht Kundenabwanderung (Customer Churn) mithilfe von Machine Learning. 
Ziel ist es, auf Basis von Kundendaten vorherzusagen, ob ein Kunde kündigt oder nicht.

## Projektstruktur

CustomerChurnLab/
│
├── 01_konzept.ipynb
├── 02_EDA.ipynb
├── data/
│ └── WA_Fn-UseC_-Telco-Customer-Churn.csv
└── README.md


## Datensatz

Der verwendete Datensatz stammt aus dem IBM Telco Customer Churn Dataset (öffentlich verfügbar, CSV-Format).  
Er enthält 7043 Kunden mit demografischen Daten, Vertragsdetails, Nutzungsverhalten und der Zielvariable **Churn**.

## Methodik

Das Projekt folgt dem QUA³CK-Prozessmodell:

- Q – Question: Forschungsfrage definieren  
- U – Understanding: Explorative Datenanalyse (EDA)  
- A – Algorithm Selection: Auswahl von ML-Algorithmen  
- A – Data Adaption: Datenaufbereitung  
- A – Parameter Adjustment: Modelloptimierung  
- C – Conclusion & Comparison: Vergleich der Modelle  
- K – Knowledge Transfer: Dokumentation der Ergebnisse  

## Explorative Datenanalyse (U-Phase)

Die U-Phase umfasst:
- Deskriptive Statistik
- Visualisierung der Churn-Verteilung
- Histogramme numerischer Features
- Korrelationsanalyse

Die Analyse wurde in Jupyter Notebook mit pandas und matplotlib durchgeführt.

## Ausführung

### Voraussetzungen
- Python 3.x
- pandas
- matplotlib

### Notebook starten

1. CSV-Datei in den Ordner `data/` legen  
2. Notebook `02_EDA.ipynb` öffnen  
3. Code-Zellen mit `Shift + Enter` ausführen  

## Autor

Studentisches Projekt im Rahmen eines Machine-Learning-Kurses.
Alle Ergebnisse wurden eigenständig geprüft und interpretiert.
