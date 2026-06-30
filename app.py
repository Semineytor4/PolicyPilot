"""
CustomerChurnLab – Streamlit App
Churn-Vorhersage auf Basis des IBM Telco Customer Churn Datensatzes
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

# ── Seitenkonfiguration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="CustomerChurnLab",
    page_icon="📊",
    layout="wide",
)

# ── Modell laden ─────────────────────────────────────────────────────────────
MODEL_PATH = "models/logreg_churn_pipeline.pkl"

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

try:
    pipe = load_model()
except FileNotFoundError:
    st.error(f"Modell nicht gefunden: {MODEL_PATH}. Bitte zuerst C_Evaluation_Final.py ausführen.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 CustomerChurnLab")
    st.markdown("""
    **Projekt:** Customer Churn Prediction
    **Datensatz:** IBM Telco (7.043 Kunden)
    **Modell:** Logistic Regression
    **Framework:** QUA³CK-Prozessmodell

    ---
    Dieses Tool sagt vorher, wie wahrscheinlich es ist, dass ein Telekommunikationskunde
    seinen Vertrag kündigt – auf Basis von 19 Kundenmerkmalen.

    **Warum Logistic Regression?**
    Bester F1-Score (0.61) und höchster Recall (0.78) im Vergleich zu Random Forest
    und Gradient Boosting – entscheidend für frühzeitige Erkennung von Kündigern.

    ---
    *IU Internationale Hochschule*
    *Kurs: Data Science*
    """)

# ── Hauptbereich ──────────────────────────────────────────────────────────────
st.title("🔍 Churn-Wahrscheinlichkeitsrechner")
st.markdown("Geben Sie die Kundendaten ein und erhalten Sie eine Vorhersage der Kündigungswahrscheinlichkeit.")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👤 Kundenprofil")
    gender = st.selectbox("Geschlecht", ["Male", "Female"])
    senior = st.selectbox("Senior Citizen", ["Nein (0)", "Ja (1)"])
    senior_val = 1 if senior.startswith("Ja") else 0
    partner = st.selectbox("Partner", ["Yes", "No"])
    dependents = st.selectbox("Dependents (Angehörige)", ["No", "Yes"])
    tenure = st.slider("Vertragsdauer (Monate)", 0, 72, 12)

with col2:
    st.subheader("📞 Services")
    phone_service = st.selectbox("Telefonservice", ["Yes", "No"])
    multiple_lines = st.selectbox("Mehrere Leitungen", ["No", "Yes", "No phone service"])
    internet_service = st.selectbox("Internetservice", ["DSL", "Fiber optic", "No"])
    online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"])
    online_backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"])
    device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
    tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])

with col3:
    st.subheader("💳 Vertrag & Abrechnung")
    streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
    streaming_movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])
    contract = st.selectbox("Vertragstyp", ["Month-to-month", "One year", "Two year"])
    paperless = st.selectbox("Papierloses Billing", ["Yes", "No"])
    payment = st.selectbox("Zahlungsmethode", [
        "Electronic check", "Mailed check",
        "Bank transfer (automatic)", "Credit card (automatic)"
    ])
    monthly_charges = st.slider("Monatliche Kosten (€)", 18.0, 120.0, 65.0, step=0.5)
    total_charges = monthly_charges * tenure

# ── Vorhersage ────────────────────────────────────────────────────────────────
input_df = pd.DataFrame([{
    "gender": gender,
    "SeniorCitizen": senior_val,
    "Partner": partner,
    "Dependents": dependents,
    "tenure": tenure,
    "PhoneService": phone_service,
    "MultipleLines": multiple_lines,
    "InternetService": internet_service,
    "OnlineSecurity": online_security,
    "OnlineBackup": online_backup,
    "DeviceProtection": device_protection,
    "TechSupport": tech_support,
    "StreamingTV": streaming_tv,
    "StreamingMovies": streaming_movies,
    "Contract": contract,
    "PaperlessBilling": paperless,
    "PaymentMethod": payment,
    "MonthlyCharges": monthly_charges,
    "TotalCharges": total_charges,
}])

st.divider()
predict_btn = st.button("🚀 Churn-Wahrscheinlichkeit berechnen", type="primary", use_container_width=True)

if predict_btn:
    prob = pipe.predict_proba(input_df)[0][1]
    pred = pipe.predict(input_df)[0]
    prob_pct = prob * 100

    col_res1, col_res2 = st.columns([1, 2])

    with col_res1:
        st.subheader("Ergebnis")

        if prob_pct < 30:
            color = "#4CAF50"
            emoji = "🟢"
            risk = "Niedriges Risiko"
            msg = "Dieser Kunde ist wahrscheinlich **loyal**. Kein dringender Handlungsbedarf."
        elif prob_pct < 60:
            color = "#FF9800"
            emoji = "🟡"
            risk = "Mittleres Risiko"
            msg = "Erhöhtes Churn-Risiko. **Präventive Maßnahmen** (z. B. Sonderangebot) empfohlen."
        else:
            color = "#F44336"
            emoji = "🔴"
            risk = "Hohes Risiko"
            msg = "Dieser Kunde ist **sehr gefährdet** zu kündigen. Sofortige Retention-Maßnahmen empfohlen."

        st.markdown(
            f"""
            <div style='text-align:center; padding:20px; border-radius:10px; background:{color}22; border: 2px solid {color}'>
                <div style='font-size:48px'>{emoji}</div>
                <div style='font-size:36px; font-weight:bold; color:{color}'>{prob_pct:.1f}%</div>
                <div style='font-size:18px; color:{color}'>{risk}</div>
                <div style='font-size:13px; color:#555; margin-top:8px'>Kündigungswahrscheinlichkeit</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(f"\n{msg}")

    with col_res2:
        st.subheader("Wahrscheinlichkeits-Gauge")
        fig, ax = plt.subplots(figsize=(6, 1.5))
        ax.barh([""], [100], color="#eee", height=0.4)
        ax.barh([""], [prob_pct], color=color, height=0.4)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Churn-Wahrscheinlichkeit (%)")
        ax.axvline(30, color="#FF9800", linestyle="--", alpha=0.5, lw=1)
        ax.axvline(60, color="#F44336", linestyle="--", alpha=0.5, lw=1)
        ax.set_title(f"Vorhersage: {'Churn' if pred == 1 else 'Kein Churn'}", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        st.markdown("""
        **Schwellenwerte:**
        🟢 < 30% – Niedriges Risiko
        🟡 30–60% – Mittleres Risiko
        🔴 > 60% – Hohes Risiko
        """)

# ── Feature Importance ────────────────────────────────────────────────────────
st.divider()
with st.expander("📊 Feature-Wichtigkeit anzeigen (Logistic Regression Koeffizienten)"):
    model = pipe.named_steps["model"]
    prep = pipe.named_steps["prep"]

    num_cols_model = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]
    cat_cols_model = [
        "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
        "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
        "PaperlessBilling", "PaymentMethod"
    ]

    ohe = prep.named_transformers_["cat"].named_steps["onehot"]
    cat_feature_names = ohe.get_feature_names_out(cat_cols_model).tolist()
    all_features = num_cols_model + cat_feature_names

    coefs = model.coef_[0]
    coef_df = pd.DataFrame({"Feature": all_features, "Koeffizient": coefs})
    coef_df = coef_df.reindex(coef_df["Koeffizient"].abs().sort_values(ascending=False).index)
    top15 = coef_df.head(15)

    fig, ax = plt.subplots(figsize=(8, 6))
    bar_colors = ["#F44336" if c > 0 else "#4CAF50" for c in top15["Koeffizient"]]
    ax.barh(top15["Feature"][::-1], top15["Koeffizient"][::-1], color=bar_colors[::-1])
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Koeffizient (log-odds)")
    ax.set_title("Top-15 Features – Einfluss auf Churn\n(rot = erhöht Churn, grün = reduziert Churn)")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    st.caption("Positive Koeffizienten erhöhen die Churn-Wahrscheinlichkeit, negative reduzieren sie.")

# ── Modellinfo ────────────────────────────────────────────────────────────────
with st.expander("ℹ️ Modellinformationen & Ergebnisse"):
    st.markdown("""
    | Metrik | Logistic Regression | Gradient Boosting | Random Forest |
    |--------|--------------------:|------------------:|--------------:|
    | F1-Score (Test) | **0.614** | 0.590 | 0.585 |
    | Recall (Test) | **0.783** | 0.524 | 0.623 |
    | Precision (Test) | 0.504 | **0.674** | 0.552 |
    | ROC-AUC (Test) | 0.841 | **0.843** | 0.822 |

    **Warum Logistic Regression?**
    Für ein Churn-Frühwarnsystem ist **Recall** entscheidend: Man möchte möglichst wenige
    Kündiger verpassen, auch wenn dabei einige False Positives entstehen.
    Logistic Regression erzielt den höchsten Recall (0.783) bei akzeptablem F1-Score.

    **Trainingsset:** 5.634 Kunden | **Testset:** 1.409 Kunden
    **Churn-Rate:** 26,5% (Klassenimbalance beachtet via `class_weight='balanced'`)
    """)
