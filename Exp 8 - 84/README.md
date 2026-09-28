# Clustering and Dimensionality Reduction on Pima Indians Diabetes Dataset

## Aim

To apply clustering and dimensionality reduction techniques to the **Pima Indians Diabetes Dataset** to discover hidden patterns and visualize relationships among patients.

## Dataset

The dataset contains medical information for **768 female patients**.

The main features are:

- Pregnancies
- Glucose
- Blood Pressure
- Skin Thickness
- Insulin
- BMI
- Diabetes Pedigree Function
- Age
- Outcome

The **Outcome** column represents diabetes status. It is excluded during unsupervised learning and can later be used to compare the discovered clusters with actual diabetes categories.

## Techniques Used

- Data Preprocessing
- Missing and Invalid Value Handling
- Feature Standardization
- K-Means Clustering
- Elbow Method
- Silhouette Score
- Principal Component Analysis (PCA)
- Data Visualization

## Workflow

1. Load the Pima Indians Diabetes Dataset.
2. Handle missing or invalid values.
3. Select numerical features.
4. Standardize the dataset.
5. Apply K-Means clustering.
6. Use the Elbow Method to determine a suitable number of clusters.
7. Evaluate clustering using the Silhouette Score.
8. Apply PCA for dimensionality reduction.
9. Reduce the dataset to two principal components.
10. Visualize and analyze the generated clusters.

## Technologies Used

- Python 3.x
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Jupyter Notebook / Google Colab

## Installation

Install the required Python libraries using:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
```

## How to Run

### Using Jupyter Notebook

1. Download or clone this repository.

```bash
git clone <repository-url>
```

2. Open the project folder.

```bash
cd <project-folder>
```

3. Start Jupyter Notebook.

```bash
jupyter notebook
```

4. Open the `.ipynb` file.
5. Make sure the Pima Indians Diabetes dataset CSV file is present in the project folder.
6. Run all notebook cells in sequence.

### Using Google Colab

1. Open Google Colab.
2. Upload the `.ipynb` file.
3. Upload the dataset CSV file when required.
4. Run all cells from top to bottom.

## Results

K-Means clustering groups patients based on similarities in their medical attributes.

The **Elbow Method** helps determine a suitable number of clusters, while the **Silhouette Score** measures the quality of the generated clusters.

PCA reduces the original high-dimensional dataset into two principal components, allowing the clusters to be visualized in a two-dimensional plot.

## Conclusion

This experiment demonstrates the use of unsupervised machine learning techniques for discovering hidden patterns in medical data.

K-Means clustering is used to group similar patients, while PCA reduces the dimensionality of the dataset and makes the resulting clusters easier to visualize and interpret.
