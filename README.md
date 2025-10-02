Project: 01:- California Housing Price Prediction Project

In this project, I have built a complete machine learning pipeline to predict California housing prices using various regression algorithms. I started by:
 Loading and preprocessing the dataset (housing.csv ) with careful treatment of missing values, scaling, and encoding using a custom pipeline. Stratified splitting was used to maintain income category distribution between train and test sets.

I trained and evaluated multiple algorithms including:

1. Linear Regression
2. Decision Tree Regressor
3. Random Forest Regressor

Through cross-validation, we found that Random Forest performed the best, offering the lowest RMSE and most stable results. Finally, we built a script that:

Trained the Random Forest model and saves it using joblib .
Uses an if-else logic to skip retraining if the model exists.
Applies the trained model to new data (input.csv ) to predict median_house_value , storing results in output.csv .
This pipeline ensures that predictions are accurate, efficient, and ready for production deployment
