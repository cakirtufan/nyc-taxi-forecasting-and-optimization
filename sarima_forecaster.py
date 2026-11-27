import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

class SARIMAForecaster:

    """Fit a seasonal ARIMA model to daily taxi pickup counts."""

    def __init__(self, order, seasonal_order):

        self.order = order
        self.seasonal_order = seasonal_order
        self.training_series = None
        self.fitted_results = None

    def _validate_history(self, history_df):
        """ 
            Check required columns, data types, missing values, and duplicate dates.
            Raises ValueError for missing or invalid values and TypeError for
            unsupported column types.
        """

        if "pickup_date" not in history_df.columns:

            raise ValueError("Pickup date not in DataFrame")

        if "pickup_count" not in history_df.columns:

            raise ValueError("Pickup count not in DataFrame")

        if history_df["pickup_date"].empty or history_df["pickup_count"].empty:

           raise ValueError("Pickup date or count empty") 

        if not pd.api.types.is_datetime64_any_dtype(history_df["pickup_date"]):
            
            raise TypeError("Pickup date column must be of datetime type.")

        if not pd.api.types.is_any_real_numeric_dtype(history_df["pickup_count"]):

            raise TypeError("Pickup count column must be of numeric type.")

        if history_df["pickup_date"].isna().any() or history_df["pickup_count"].isna().any():
            
            raise ValueError("Data contains NaN values.")

        if not np.isfinite(history_df["pickup_count"]).all():

            raise ValueError("Pick up count has non-finite values")    

        if history_df["pickup_date"].nunique() != len(history_df["pickup_date"]):

            raise ValueError("Repeating pickup date")  

    def fit(self, history_df):

        """
            Fit SARIMA using the supplied historical daily pickup counts.

            The input must contain pickup_date and pickup_count. Stores the dated
            training series and fitted statsmodels results, then returns self.
        """

        self._validate_history(history_df)

        history = history_df[["pickup_date", "pickup_count"]].sort_values(by="pickup_date")
        self.training_series = history.set_index("pickup_date")["pickup_count"]

        model = SARIMAX(
            self.training_series,
            order = self.order,
            seasonal_order = self.seasonal_order,
            )

        fitted_results = model.fit()

        self.fitted_results = fitted_results

        return self

    def predict(self, target_df):

        if self.fitted_results is None:

            raise ValueError("fitted_result is None need fit()")

        steps = len(target_df)

        return self.fitted_results.forecast(steps=steps)

        