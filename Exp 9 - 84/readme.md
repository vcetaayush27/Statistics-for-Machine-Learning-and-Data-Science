```markdown
# Model Evaluation and Explainable AI on Pima Indians Diabetes Dataset

## Aim

To evaluate a machine learning model and apply explainable AI techniques on the **Pima Indians Diabetes Dataset**.

## Dataset

The dataset contains **768 female patient records**.

Target:

- `0` = Non-Diabetic
- `1` = Diabetic

## Techniques Used

- Data Preprocessing
- Train-Test Split
- Classification Model
- k-Fold Cross-Validation
- Accuracy
- F1-Score
- Brier Score
- Calibration Curve
- SHAP / LIME

## Required Libraries

```bash
pip install pandas numpy matplotlib scikit-learn shap lime jupyter
```

## How to Run

### Jupyter Notebook

```bash
git clone <repository-url>
cd <project-folder>
jupyter notebook
```

Then:

1. Open the `.ipynb` file.
2. Keep the dataset CSV file in the project folder.
3. Run all cells from top to bottom.

### Google Colab

1. Upload the `.ipynb` file.
2. Upload the dataset CSV file.
3. Install missing libraries if required.
4. Run all cells.

## Workflow

1. Load and preprocess the dataset.
2. Split data into training and testing sets.
3. Train the classification model.
4. Apply k-fold cross-validation.
5. Calculate Accuracy and F1-Score.
6. Calculate Brier Score.
7. Plot the Calibration Curve.
8. Apply SHAP or LIME.
9. Identify important features.

## Result

The model is evaluated using performance and calibration measures, and SHAP/LIME is used to understand the features influencing predictions.

## Conclusion

The experiment demonstrates model evaluation, probability calibration, and explainable AI on the Pima Indians Diabetes Dataset.
```