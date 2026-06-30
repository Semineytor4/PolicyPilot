"""
C-Phase: Finale Evaluation – Holdout-Testset, Plots, Modellspeicherung
Alle Ergebnisse werden als PNG und JSON gespeichert für die Word-Dokumente.
"""
import os, json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    make_scorer, f1_score, precision_score, recall_score,
    roc_auc_score, average_precision_score,
    confusion_matrix, ConfusionMatrixDisplay,
    roc_curve, precision_recall_curve,
    classification_report
)
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.inspection import permutation_importance

os.makedirs("plots", exist_ok=True)
os.makedirs("models", exist_ok=True)

# ─────────────────────────────────────────
# 1. Daten laden & TotalCharges konvertieren
# ─────────────────────────────────────────
data = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")
data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce")
data = data.drop(columns=["customerID"])

print(f"Datensatz: {data.shape[0]} Kunden, {data.shape[1]} Spalten")
print(f"TotalCharges NaNs nach Konvertierung: {data['TotalCharges'].isna().sum()}")

y = (data["Churn"] == "Yes").astype(int)
X = data.drop(columns=["Churn"])

print(f"\nKlassenverteilung:\n{y.value_counts().rename({0:'Kein Churn',1:'Churn'})}")
print(f"Churn-Rate: {y.mean()*100:.1f}%")

cat_cols = X.select_dtypes(include=["object"]).columns.tolist()
num_cols = X.select_dtypes(exclude=["object"]).columns.tolist()
print(f"\nNumerische Features ({len(num_cols)}): {num_cols}")
print(f"Kategoriale Features ({len(cat_cols)}): {cat_cols}")

# ─────────────────────────────────────────
# 2. Train/Test Split (Holdout)
# ─────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

# ─────────────────────────────────────────
# 3. Preprocessing Pipeline
# ─────────────────────────────────────────
numeric_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])
categorical_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])
preprocess = ColumnTransformer([
    ("num", numeric_pipe, num_cols),
    ("cat", categorical_pipe, cat_cols)
])

# ─────────────────────────────────────────
# 4. Cross-Validation (reproduziert A-Phase)
# ─────────────────────────────────────────
models = {
    "Dummy (MostFrequent)": DummyClassifier(strategy="most_frequent"),
    "LogReg": LogisticRegression(max_iter=300, class_weight="balanced", random_state=42),
    "RandomForest": RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced"),
    "GradBoost": GradientBoostingClassifier(random_state=42)
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scoring = {
    "roc_auc": "roc_auc",
    "pr_auc": "average_precision",
    "f1": make_scorer(f1_score),
    "precision": make_scorer(precision_score, zero_division=0),
    "recall": make_scorer(recall_score, zero_division=0),
}

print("\n=== 5-Fold Cross-Validation ===")
cv_results = []
for name, model in models.items():
    pipe = Pipeline([("prep", preprocess), ("model", model)])
    scores = cross_validate(pipe, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
    cv_results.append({
        "Modell": name,
        "ROC-AUC": round(scores["test_roc_auc"].mean(), 4),
        "F1": round(scores["test_f1"].mean(), 4),
        "Precision": round(scores["test_precision"].mean(), 4),
        "Recall": round(scores["test_recall"].mean(), 4),
        "PR-AUC": round(scores["test_pr_auc"].mean(), 4),
    })

cv_df = pd.DataFrame(cv_results).sort_values("F1", ascending=False)
print(cv_df.to_string(index=False))

# ─────────────────────────────────────────
# 5. Finale Modelle auf vollem Trainingsset trainieren
# ─────────────────────────────────────────
trained_pipes = {}
for name, model in models.items():
    pipe = Pipeline([("prep", preprocess), ("model", model)])
    pipe.fit(X_train, y_train)
    trained_pipes[name] = pipe

# ─────────────────────────────────────────
# 6. Holdout-Testset Evaluation
# ─────────────────────────────────────────
print("\n=== Holdout-Testset Evaluation ===")
test_results = []
for name, pipe in trained_pipes.items():
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe.named_steps["model"], "predict_proba") else None
    row = {
        "Modell": name,
        "F1": round(f1_score(y_test, y_pred), 4),
        "Precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "Recall": round(recall_score(y_test, y_pred), 4),
        "ROC-AUC": round(roc_auc_score(y_test, y_prob), 4) if y_prob is not None else None,
        "PR-AUC": round(average_precision_score(y_test, y_prob), 4) if y_prob is not None else None,
    }
    test_results.append(row)
    print(f"{name}: F1={row['F1']}, Recall={row['Recall']}, Precision={row['Precision']}, ROC-AUC={row['ROC-AUC']}")

test_df = pd.DataFrame(test_results).sort_values("F1", ascending=False)

# ─────────────────────────────────────────
# 7. Bestes Modell: Logistic Regression
# ─────────────────────────────────────────
best_pipe = trained_pipes["LogReg"]
y_pred_best = best_pipe.predict(X_test)
y_prob_best = best_pipe.predict_proba(X_test)[:, 1]

print("\n=== Classification Report (LogReg, Testset) ===")
print(classification_report(y_test, y_pred_best, target_names=["Kein Churn", "Churn"]))

# ─────────────────────────────────────────
# 8. PLOTS
# ─────────────────────────────────────────

# --- EDA Plot 1: Churn-Verteilung ---
fig, ax = plt.subplots(figsize=(6, 4))
churn_counts = y.value_counts().rename({0: "Kein Churn (0)", 1: "Churn (1)"})
bars = ax.bar(churn_counts.index, churn_counts.values, color=["#4CAF50", "#F44336"], width=0.5)
ax.set_xticks([0, 1])
ax.set_xticklabels(["Kein Churn", "Churn"])
ax.set_ylabel("Anzahl Kunden")
ax.set_title("Verteilung der Zielvariable (Churn)")
for bar, val in zip(bars, churn_counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
            f'{val}\n({val/len(y)*100:.1f}%)', ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.savefig("plots/churn_distribution.png", dpi=150, bbox_inches='tight')
plt.close()
print("Gespeichert: plots/churn_distribution.png")

# --- EDA Plot 2: tenure & MonthlyCharges nach Churn ---
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
data_plot = data.copy()
data_plot["Churn_Label"] = data_plot["Churn"].map({"Yes": "Churn", "No": "Kein Churn"})

for ax, col, title in zip(axes,
    ["tenure", "MonthlyCharges"],
    ["Vertragsdauer (Monate)", "Monatliche Kosten (€)"]):
    for label, color in [("Kein Churn", "#4CAF50"), ("Churn", "#F44336")]:
        subset = data_plot[data_plot["Churn_Label"] == label][col].dropna()
        ax.hist(subset, bins=30, alpha=0.6, color=color, label=label, density=True)
    ax.set_title(title)
    ax.set_xlabel(col)
    ax.set_ylabel("Dichte")
    ax.legend()
plt.suptitle("Numerische Features nach Churn-Status", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig("plots/numeric_features_by_churn.png", dpi=150, bbox_inches='tight')
plt.close()
print("Gespeichert: plots/numeric_features_by_churn.png")

# --- EDA Plot 3: Kategoriale Features ---
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
for ax, col in zip(axes, ["Contract", "InternetService", "PaymentMethod"]):
    ct = pd.crosstab(data_plot[col], data_plot["Churn_Label"], normalize='index') * 100
    ct[["Kein Churn", "Churn"]].plot(kind='bar', ax=ax, color=["#4CAF50", "#F44336"],
                                       rot=15, legend=ax == axes[0])
    ax.set_title(col)
    ax.set_ylabel("Anteil (%)")
    ax.set_xlabel("")
plt.suptitle("Churn-Rate nach kategorialen Merkmalen", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig("plots/categorical_churn_rates.png", dpi=150, bbox_inches='tight')
plt.close()
print("Gespeichert: plots/categorical_churn_rates.png")

# --- Konfusionsmatrix ---
cm = confusion_matrix(y_test, y_pred_best)
fig, ax = plt.subplots(figsize=(5, 4))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Kein Churn", "Churn"])
disp.plot(ax=ax, colorbar=False, cmap='Blues')
ax.set_title("Konfusionsmatrix – Logistic Regression (Testset)", fontsize=11)
plt.tight_layout()
plt.savefig("plots/confusion_matrix.png", dpi=150, bbox_inches='tight')
plt.close()
print("Gespeichert: plots/confusion_matrix.png")

# --- ROC-Kurve ---
fig, ax = plt.subplots(figsize=(6, 5))
colors = {"LogReg": "#2196F3", "RandomForest": "#FF9800", "GradBoost": "#9C27B0"}
for name in ["LogReg", "RandomForest", "GradBoost"]:
    pipe = trained_pipes[name]
    y_prob = pipe.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)
    ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})", color=colors[name], lw=2)
ax.plot([0,1],[0,1], 'k--', lw=1, label="Zufallsklassifizierer")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC-Kurven – Modellvergleich (Testset)")
ax.legend(loc="lower right")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("plots/roc_curves.png", dpi=150, bbox_inches='tight')
plt.close()
print("Gespeichert: plots/roc_curves.png")

# --- Precision-Recall-Kurve ---
fig, ax = plt.subplots(figsize=(6, 5))
for name in ["LogReg", "RandomForest", "GradBoost"]:
    pipe = trained_pipes[name]
    y_prob = pipe.predict_proba(X_test)[:, 1]
    prec, rec, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)
    ax.plot(rec, prec, label=f"{name} (PR-AUC={pr_auc:.3f})", color=colors[name], lw=2)
baseline = y_test.mean()
ax.axhline(baseline, linestyle='--', color='gray', lw=1, label=f"Baseline ({baseline:.2f})")
ax.set_xlabel("Recall")
ax.set_ylabel("Precision")
ax.set_title("Precision-Recall-Kurven – Modellvergleich (Testset)")
ax.legend(loc="upper right")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("plots/pr_curves.png", dpi=150, bbox_inches='tight')
plt.close()
print("Gespeichert: plots/pr_curves.png")

# --- Feature Importance: LogReg Koeffizienten ---
logreg_model = best_pipe.named_steps["model"]
prep_fitted = best_pipe.named_steps["prep"]

# Featurenamen ermitteln
ohe = prep_fitted.named_transformers_["cat"].named_steps["onehot"]
cat_feature_names = ohe.get_feature_names_out(cat_cols).tolist()
feature_names = num_cols + cat_feature_names

coefs = logreg_model.coef_[0]
coef_df = pd.DataFrame({"Feature": feature_names, "Koeffizient": coefs})
coef_df = coef_df.reindex(coef_df["Koeffizient"].abs().sort_values(ascending=False).index)
top20 = coef_df.head(20)

fig, ax = plt.subplots(figsize=(8, 7))
colors_bar = ["#F44336" if c > 0 else "#4CAF50" for c in top20["Koeffizient"]]
ax.barh(top20["Feature"][::-1], top20["Koeffizient"][::-1], color=colors_bar[::-1])
ax.axvline(0, color='black', lw=0.8)
ax.set_xlabel("Koeffizient (log-odds)")
ax.set_title("Top-20 Feature-Koeffizienten – Logistic Regression\n(rot = Churn-fördernd, grün = Churn-hemmend)")
red_patch = mpatches.Patch(color='#F44336', label='Churn-fördernd (+)')
green_patch = mpatches.Patch(color='#4CAF50', label='Churn-hemmend (-)')
ax.legend(handles=[red_patch, green_patch], loc="lower right")
plt.tight_layout()
plt.savefig("plots/feature_importance_logreg.png", dpi=150, bbox_inches='tight')
plt.close()
print("Gespeichert: plots/feature_importance_logreg.png")

# --- Feature Importance: GradBoost (Vergleich) ---
gb_pipe = trained_pipes["GradBoost"]
gb_model = gb_pipe.named_steps["model"]
gb_prep = gb_pipe.named_steps["prep"]
gb_ohe = gb_prep.named_transformers_["cat"].named_steps["onehot"]
gb_cat_names = gb_ohe.get_feature_names_out(cat_cols).tolist()
gb_feature_names = num_cols + gb_cat_names

fi_df = pd.DataFrame({"Feature": gb_feature_names, "Importance": gb_model.feature_importances_})
fi_df = fi_df.sort_values("Importance", ascending=False).head(20)

fig, ax = plt.subplots(figsize=(8, 7))
ax.barh(fi_df["Feature"][::-1], fi_df["Importance"][::-1], color="#9C27B0")
ax.set_xlabel("Feature Importance (MDI)")
ax.set_title("Top-20 Feature Importance – Gradient Boosting")
plt.tight_layout()
plt.savefig("plots/feature_importance_gradboost.png", dpi=150, bbox_inches='tight')
plt.close()
print("Gespeichert: plots/feature_importance_gradboost.png")

# --- CV Ergebnisse als Balkendiagramm ---
cv_plot = cv_df[cv_df["Modell"] != "Dummy (MostFrequent)"].copy()
metrics_plot = ["ROC-AUC", "F1", "Precision", "Recall"]
x = np.arange(len(metrics_plot))
width = 0.25
fig, ax = plt.subplots(figsize=(10, 5))
colors_models = ["#2196F3", "#FF9800", "#9C27B0"]
for i, (_, row) in enumerate(cv_plot.iterrows()):
    ax.bar(x + i*width, [row[m] for m in metrics_plot], width, label=row["Modell"],
           color=colors_models[i], alpha=0.85)
ax.set_xticks(x + width)
ax.set_xticklabels(metrics_plot)
ax.set_ylim(0, 1.05)
ax.set_ylabel("Score")
ax.set_title("Cross-Validation Ergebnisse – Modellvergleich")
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("plots/cv_model_comparison.png", dpi=150, bbox_inches='tight')
plt.close()
print("Gespeichert: plots/cv_model_comparison.png")

# ─────────────────────────────────────────
# 9. Modell speichern
# ─────────────────────────────────────────
joblib.dump(best_pipe, "models/logreg_churn_pipeline.pkl")
print("\nModell gespeichert: models/logreg_churn_pipeline.pkl")

# ─────────────────────────────────────────
# 10. Ergebnisse als JSON speichern (für Word-Docs)
# ─────────────────────────────────────────
results_export = {
    "cv_results": cv_df.to_dict(orient="records"),
    "test_results": test_df.to_dict(orient="records"),
    "best_model": "LogReg",
    "best_model_test": {
        k: v for k, v in test_df[test_df["Modell"] == "LogReg"].iloc[0].items()
    },
    "confusion_matrix": cm.tolist(),
    "n_train": len(X_train),
    "n_test": len(X_test),
    "churn_rate": round(y.mean() * 100, 1),
    "top_features_logreg": coef_df.head(10).to_dict(orient="records"),
    "top_features_gradboost": fi_df.head(10).to_dict(orient="records"),
}

with open("results.json", "w") as f:
    json.dump(results_export, f, indent=2, default=str)
print("Ergebnisse gespeichert: results.json")

print("\n✅ C_Evaluation_Final.py abgeschlossen.")
