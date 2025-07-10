# app/ml/ml_model.py
import numpy as np


class CustomLinearRegression:
    """
    Linear regression class with regularization (Ridge Regression).

    Attributes:
        coef_ (np.ndarray): model coefficients (excluding intercept).
        intercept_ (float): intercept (bias term).
        alpha (float): regularization parameter.
    """

    def __init__(self, alpha=1e-5):
        """
        Initializes the model.

        Args:
            alpha (float): regularization coefficient (default is 1e-5).
        """
        self.coef_ = None
        self.intercept_ = None
        self.alpha = alpha

    def fit(self, X, y):
        """
        Trains the model on features X and target values y.

        Args:
            X (np.ndarray): feature matrix of shape (n_samples, n_features).
            y (np.ndarray): target vector of shape (n_samples,).

        Computes coefficients and intercept considering regularization.
        """
        X = X.astype(np.float64)
        y = y.astype(np.float64)

        X = np.c_[np.ones(X.shape[0]), X]

        n_features = X.shape[1]
        I = np.eye(n_features)
        I[0, 0] = 0

        theta = np.linalg.inv(X.T.dot(X) + self.alpha * I).dot(X.T).dot(y)
        self.intercept_ = theta[0]
        self.coef_ = theta[1:]

    def predict(self, X):
        """
        Makes predictions for new data X.

        Args:
            X (np.ndarray): feature matrix of shape (n_samples, n_features).

        Returns:
            np.ndarray: prediction vector of shape (n_samples,).
        """
        X = np.c_[np.ones(X.shape[0]), X]
        return X.dot(np.r_[self.intercept_, self.coef_])

    def mean_absolute_error(self, y_true, y_pred):
        """
        Computes the mean absolute error (MAE) between true and predicted values.

        Args:
            y_true (np.ndarray): true values.
            y_pred (np.ndarray): predicted values.

        Returns:
            float: mean absolute error.
        """
        return np.mean(np.abs(y_true - y_pred))

    def mean_squared_error(self, y_true, y_pred):
        """
        Computes the mean squared error (MSE) between true and predicted values.

        Args:
            y_true (np.ndarray): true values.
            y_pred (np.ndarray): predicted values.

        Returns:
            float: mean squared error.
        """
        return np.mean((y_true - y_pred) ** 2)

    def r2_score(self, y_true, y_pred):
        """
        Computes the coefficient of determination R^2 to evaluate the model quality.

        Args:
            y_true (np.ndarray): true values.
            y_pred (np.ndarray): predicted values.

        Returns:
            float: R^2 score.
        """
        ss_total = np.sum((y_true - np.mean(y_true)) ** 2)
        ss_residual = np.sum((y_true - y_pred) ** 2)
        return 1 - (ss_residual / ss_total)
