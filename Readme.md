# CustomerChurnLab

Vorhersage von Customer Churn (Kundenabwanderung) im Telekommunikationsbereich mithilfe klassischer Machine-Learning-Verfahren. Das Projekt folgt dem **QUA³CK-Prozessmodell** (Stock et al., 2021) und endet mit einer interaktiven Streamlit-Webanwendung.

---

## Finale Ergebnisse (Holdout-Testset, 1.409 Kunden)

| Modell | F1 | Recall | Precision | ROC-AUC |
|---|---|---|---|---|
| **Logistic Regression ✅** | **0.614** | **0.783** | 0.504 | 0.841 |
| Gradient Boosting | 0.590 | 0.524 | 0.674 | 0.843 |
| Random Forest | 0.585 | 0.623 | 0.552 | 0.822 |
| Dummy (Baseline) | 0.000 | 0.000 | 0.000 | 0.500 |

**Gewähltes Modell:** Logistic Regression – bester F1 und Recall (wichtig für Frühwarnsystem).

---

## Projektstruktur

```
CustomerChurnLab/
├── Q_conception.ipynb                  # Q-Phase: Forschungsfrage, Hypothesen
├── U_EDA.ipynb                         # U-Phase: EDA mit Visualisierungen
├── U_Analyse.ipynb                     # U-Phase: Analyse-Interpretation
├── A_Development_Phase.ipynb           # A³-Phase: Pipeline & Modellvergleich
├── A_Development_Phase_Results.ipynb   # A³-Phase: Cross-Validation Ergebnisse
├── C_Evaluation_Final.py               # C-Phase: Holdout-Eval, Plots, Modell-Export
├── app.py                              # K-Phase: Streamlit-App
├── models/
│   └── logreg_churn_pipeline.pkl       # Serialisiertes finales Modell (joblib)
├── plots/                              # Generierte Visualisierungen (PNG)
├── WA_Fn-UseC_-Telco-Customer-Churn.csv  # IBM Telco Datensatz (7.043 Kunden)
├── requirements.txt
└── AI_TOOL_DISCLOSURE.ipynb            # KI-Tool-Nutzung Dokumentation
```

---

## Datensatz

**IBM Telco Customer Churn Dataset** (Kaggle, öffentlich verfügbar)
- 7.043 Kunden, 20 Features, Zielvariable: `Churn` (Yes/No)
- Churn-Rate: 26,5% (Klassenimbalance)
- Bekanntes Datenproblem: `TotalCharges` liegt als String vor → wird mit `pd.to_numeric(errors='coerce')` konvertiert

---

## Setup & Ausführung

### 1. Repository klonen
```bash
git clone https://github.com/Semineytor4/PolicyPilot.git
cd PolicyPilot
```

### 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 3. Streamlit-App starten
```bash
streamlit run app.py
```
→ App öffnet sich automatisch unter **http://localhost:8501**

> Das trainierte Modell (`models/logreg_churn_pipeline.pkl`) liegt bereits im Repo –
> kein weiterer Schritt nötig.

### Optional: Evaluation neu ausführen (alle Plots & Modell neu generieren)
```bash
python C_Evaluation_Final.py
```

---

## Methodik: QUA³CK-Prozessmodell

| Phase | Inhalt | Status |
|---|---|---|
| Q – Question | Forschungsfrage, Hypothesen H1–H3 | ✅ |
| U – Understanding | EDA, Korrelationen, Verteilungen | ✅ |
| A¹ – Algorithm Selection | LogReg, RF, GradBoost, Dummy | ✅ |
| A² – Adapting Features | ColumnTransformer, OneHot, Scaler | ✅ |
| A³ – Adjusting Parameters | 5-Fold Stratified Cross-Validation | ✅ |
| C – Conclusion | Holdout-Eval, Plots, Hypothesenprüfung | ✅ |
| K – Knowledge Transfer | Streamlit-App, Portfolio-Dokumente | ✅ |

---

## Hypothesen-Ergebnisse

- **H1** (Vertragsmerkmale > Demografik): ✅ **Bestätigt** – Contract & tenure sind stärkste Prädiktoren
- **H2** (Ensembles besser als LogReg): ❌ **Widerlegt** – LogReg erreicht besten F1 und Recall
- **H3** (Pipeline verbessert Generalisierung): ✅ **Bestätigt** – Leakage-freie Pipeline essentiell

---

## Autor

Studentisches Projekt · IU Internationale Hochschule · Machine-Learning-Kurs
Alle Ergebnisse wurden eigenständig geprüft und interpretiert.
KI-Tool-Nutzung vollständig dokumentiert in `AI_TOOL_DISCLOSURE.ipynb`.
