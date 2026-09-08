# 🩺 Diabetes Classification — Supervised Learning Models

**Experiment 6:** Build and Evaluate Classification Models using Supervised Learning Algorithms

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

---

## 📌 Overview

This experiment builds, trains, and evaluates three classic supervised classification algorithms — **Logistic Regression**, **k-Nearest Neighbors**, and **Decision Tree** — on the **Pima Indians Diabetes Dataset** to predict whether a patient has diabetes (`Outcome`: 0 = No, 1 = Yes).

The pipeline covers the full ML workflow: data cleaning → preprocessing → train/test split → scaling → model training → evaluation → comparison.

---

## 📂 Dataset

| Property | Value |
|---|---|
| **Source** | `diabetes.csv` (Pima Indians Diabetes Dataset) |
| **Shape** | 768 rows × 9 columns |
| **Target** | `Outcome` (binary: 0 / 1) |
| **Class Balance** | 500 negative (65%) · 268 positive (35%) |
| **Features** | Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age |

---

## 🧹 Data Preprocessing

Several columns (`Glucose`, `BloodPressure`, `SkinThickness`, `Insulin`, `BMI`) contain biologically invalid **zero values**, which were treated as missing and imputed with the **column median**:

```python
zero_invalid_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
for c in zero_invalid_cols:
    X_clean[c] = X_clean[c].replace(0, np.nan)
    X_clean[c] = X_clean[c].fillna(X_clean[c].median())
```

Additional steps:
- ✅ Checked and removed duplicate rows
- ✅ Stratified **80/20 train-test split** to preserve class balance
- ✅ Feature scaling with `StandardScaler`

---

## 🤖 Models Trained

```python
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "k-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
    "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=5)
}
```

Each model was trained on scaled features and evaluated using **accuracy, precision, recall, F1-score, ROC-AUC**, confusion matrices, and ROC curves.

---

## 📊 Results

### Performance Comparison

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
|---|:-:|:-:|:-:|:-:|:-:|
| Logistic Regression | 0.7078 | 0.5882 | 0.5556 | 0.5714 | 0.8263 |
| k-Nearest Neighbors | 0.8117 | 0.7358 | 0.7222 | 0.7290 | 0.8631 |
| **Decision Tree** | **0.8247** | **0.7547** | **0.7407** | **0.7477** | **0.9121** |

🏆 **Decision Tree** was the top performer across every metric — highest accuracy, recall, F1-score, and ROC-AUC.

### Overfitting Check (Train vs Test Accuracy)

| Model | Train Accuracy | Test Accuracy | Gap |
|---|:-:|:-:|:-:|
| Logistic Regression | 0.7964 | 0.7078 | 0.0886 |
| k-Nearest Neighbors | 0.8762 | 0.8117 | 0.0645 |
| Decision Tree | 0.9349 | 0.8247 | 0.1102 |

⚠️ The Decision Tree shows the **largest train-test gap**, hinting at mild overfitting despite being the best generalizer overall — worth monitoring with pruning or depth tuning.

---

## 🔍 Key Observations

- **Logistic Regression** underperforms on this dataset, likely due to non-linear relationships between features (Glucose, BMI, Age) and the outcome.
- **k-NN** offers a strong balance of accuracy and generalization with a low train-test gap.
- **Decision Tree** achieves the best raw performance and the highest ROC-AUC (0.912), indicating excellent class separability, but its higher train accuracy suggests it may benefit from regularization (e.g., limiting `max_depth` further or pruning).
- Class imbalance (65/35) means **accuracy alone is not sufficient** — Recall and F1-score for the positive (diabetic) class matter more in a medical context, where missing a true case is costlier than a false alarm.

---

## 🛠️ Tech Stack

`Python` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `Scikit-learn`

---

## ▶️ How to Run

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
python classification_models.py
```

Ensure `diabetes.csv` is in the same directory as the script.

---

## 📁 Outputs Generated

- Confusion matrices for all three models
- Bar chart comparing Accuracy / Precision / Recall / F1 / ROC-AUC
- ROC curve overlay for all models
- Train vs test accuracy overfitting summary
