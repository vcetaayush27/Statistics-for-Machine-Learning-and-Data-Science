# Measured project results

Input: 1000 posts. Usable: 888. Selected: Random Forest.

| Model | MAE | RMSE | R² | RMSLE | Log R² |
|---|---:|---:|---:|---:|---:|
| Median baseline | 4,481.1281 | 29,285.1866 | -0.0233 | 2.4828 | -0.0002 |
| Linear Regression | 4,477.2829 | 29,257.8921 | -0.0214 | 2.3987 | 0.0664 |
| Random Forest | 4,473.6354 | 29,270.1383 | -0.0223 | 2.4032 | 0.0629 |
| Gradient Boosting | 4,493.3320 | 29,229.2047 | -0.0194 | 2.4691 | 0.0108 |

Nominal 80% prediction-range coverage on the test set: 79.21%.

Random Forest won training cross-validation; test data did not determine selection. Negative raw R² and small positive log R² show weak predictive power. Use as a measured academic demonstration, not a reliable engagement guarantee.

The statistical tests and adjusted p-values are in artifacts/hypothesis_tests.csv. See README.md for interpretation and scope.