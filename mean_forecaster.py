import pandas as pd
import numpy as np


class WeekdayMeanForecaster:

    def __init__(self, df, validation_df, window, horizon):

        self.df = df
        self.validation_df = validation_df
        self.window = window
        self.horizon = horizon

    def calculate_mae_and_bias(self, prediction, count):

        """Calculate MAE and signed bias from aligned pandas Series."""

        if prediction.isna().any() or count.isna().any():
            raise ValueError("Data contains NaN values.")

        if len(prediction) != len(count):
            raise ValueError("Prediction and count not in same length")

        if prediction.empty or count.empty:
            raise ValueError("Prediction or count is empty")

        if not np.isfinite(prediction).all() or not np.isfinite(count).all():
            raise ValueError("Prediction or count has non-finite values")

        mae = np.mean(np.abs(prediction - count))
        bias = np.mean(prediction - count)

        return mae, bias

    def all_history_weekday_mean(self, history, target):

        """Predict target weekdays using all history before the first target."""

        valid_df = target.copy()
        train_df = history.copy()

        earliest_prediction_date = valid_df["pickup_date"].min()

        train_df = train_df[
            train_df["pickup_date"] < earliest_prediction_date
        ]

        history_weekday_mean = (
            train_df.groupby("weekday")["pickup_count"].mean()
        )

        valid_df["all_history_mean_prediction"] = (
            valid_df["weekday"].map(history_weekday_mean)
        )

        mae, bias = self.calculate_mae_and_bias(
            valid_df["all_history_mean_prediction"],
            valid_df["pickup_count"]
        )

        return valid_df, mae, bias

    def windowed_weekday_mean(
        self, history, target, window, verbose=False
    ):

        """Predict target weekdays using the previous 7, 14, or 28 days."""

        if window not in [7, 14, 28]:
            raise ValueError("Please select training window in [7,14,28]")

        valid_copy = target.copy()
        train_copy = history.copy()

        earliest_prediction_date = valid_copy["pickup_date"].min()
        window_start = earliest_prediction_date - pd.Timedelta(days=window)

        windowed_train = train_copy[
            (train_copy["pickup_date"] >= window_start)
            & (train_copy["pickup_date"] < earliest_prediction_date)
        ]

        weekday_mean = (
            windowed_train.groupby("weekday")["pickup_count"].mean()
        )

        valid_copy["weekday_mean_prediction"] = (
            valid_copy["weekday"].map(weekday_mean)
        )

        mae, bias = self.calculate_mae_and_bias(
            valid_copy["weekday_mean_prediction"],
            valid_copy["pickup_count"]
        )

        if verbose:
            print(
                f"Window: {window} days, "
                f"forecast origin: {earliest_prediction_date}, "
                f"MAE: {mae}, bias: {bias}"
            )

        return valid_copy, mae, bias

    def walk_forward_evaluation(
        self, history, target, window, horizon, update_every, model
    ):

        """
        Evaluate rolling or expanding weekday-mean forecasts.

        If update every is NaN horizon also sets the update interval. 
        Assumes one row per consecutive validation day and historical counts available at
        each forecast origin. Includes partial final blocks and computes
        metrics over all individual predictions.
        """

        if model not in ["windowed", "history"]:
            raise ValueError(
                "Selected model not in ['windowed', 'history']"
            )

        if (
            not isinstance(horizon, int)
            or isinstance(horizon, bool)
            or horizon < 1
        ):
            raise ValueError("Horizon must be a positive integer")

        if update_every is None:
            update_every = horizon

        if (

            not isinstance(update_every, int)
            or isinstance(update_every, bool)
            or update_every < 1
        ):

            raise ValueError("Update every must be a positive integer")

        if update_every > horizon:
            raise ValueError("update_every cannot exceed horizon")


        validation_df = target.copy().sort_values("pickup_date")
        combined_df = history.copy()

        forecast_blocs = []

        for date in validation_df["pickup_date"].iloc[::update_every]:

            target_dates = validation_df[
                (validation_df["pickup_date"] >= date)
                & (
                    validation_df["pickup_date"]
                    < date + pd.Timedelta(days=horizon)
                )
            ]

            block = target_dates[["pickup_date"]].copy()
            block["forecast_origin"] = date
            block["pickup_count"] = target_dates["pickup_count"]
            

            available_history = combined_df[
                combined_df["pickup_date"] < date
            ]

            if model == "windowed":

                df, _, _ = self.windowed_weekday_mean(
                    history=available_history,
                    target=target_dates,
                    window=window,
                    verbose=False
                )


                block["prediction"] = df["weekday_mean_prediction"]

            elif model == "history":

                df, _, _ = self.all_history_weekday_mean(
                    history=available_history,
                    target=target_dates
                )


                block["prediction"] = df["all_history_mean_prediction"]
                

            forecast_blocs.append(block)



        forecast_df = pd.concat(forecast_blocs, ignore_index=True)

        latest = (forecast_df.sort_values(["pickup_date", "forecast_origin"])
                  .drop_duplicates("pickup_date", keep = "last")
                  .reset_index(drop = True))

        mae, bias = self.calculate_mae_and_bias(
            latest["prediction"],
            latest["pickup_count"]
        )


        return latest, mae, bias

    def compare_forecasting_baseline(self):

        """Return metrics for 20 fixed, expanding, and rolling configurations."""

        combined_df = self.df
        validation_df = self.validation_df

        windows = [7, 14, 28]
        horizons = [1, 7, 14, 28]
        results = []

        full_horizon = (
            validation_df["pickup_date"].max()
            - validation_df["pickup_date"].min()
        ).days + 1

        _, mae, bias = self.all_history_weekday_mean(
            history=combined_df,
            target=validation_df
        )

        results.append({
            "strategy": "fixed",
            "model": "history",
            "window": None,
            "horizon": full_horizon,
            "update_every": None,
            "mae": mae,
            "bias": bias
        })

        for window in windows:

            _, mae, bias = self.windowed_weekday_mean(
                history=combined_df,
                target=validation_df,
                window=window,
                verbose=False
            )

            results.append({
                "strategy": "fixed",
                "model": "windowed",
                "window": window,
                "horizon": full_horizon,
                "update_every": None,
                "mae": mae,
                "bias": bias
            })

        for horizon in horizons:

            _, mae, bias = self.walk_forward_evaluation(
                history=combined_df,
                target=validation_df,
                window=None,
                horizon=horizon,
                update_every=horizon,
                model="history"
            )

            results.append({
                "strategy": "expanding",
                "model": "history",
                "window": None,
                "horizon": horizon,
                "update_every": horizon,
                "mae": mae,
                "bias": bias
            })

        for window in windows:
            for horizon in horizons:

                _, mae, bias = self.walk_forward_evaluation(
                    history=combined_df,
                    target=validation_df,
                    window=window,
                    horizon=horizon,
                    update_every=horizon,
                    model="windowed"
                )

                results.append({
                    "strategy": "rolling",
                    "model": "windowed",
                    "window": window,
                    "horizon": horizon,
                    "update_every": horizon,
                    "mae": mae,
                    "bias": bias
                })

        return pd.DataFrame(results).sort_values(by="mae")

    def compare_additional_update_schedules(self):

        """
            Compare rolling and expanding schedules with updates more frequent
            than the forecast horizon.

            Tries 7-, 14-, and 28-day rolling windows and all-history expanding
            forecasts. Returns a DataFrame sorted by MAE. Each target day is scored
            once using its most recently issued forecast.
        """

        combined_df = self.df
        validation_df = self.validation_df

        results_w = []
        results_h = []

        for window in [7,14,28]:
            for horizon in [1,7,14,28]:
                for update in range(1, len(validation_df)):

                    if update >= horizon:

                        continue

                    else:
                        _, mae, bias = self.walk_forward_evaluation(history=combined_df,
                                    target=validation_df,
                                    window=window,
                                    horizon=horizon,
                                    update_every=update,
                                    model="windowed"
                                )

                        results_w.append({
                            "strategy": "rolling",
                            "model": "windowed",
                            "window": window,
                            "horizon": horizon,
                            "update_every": update,
                            "mae": mae,
                            "bias": bias
                        })


        walkthroug_windowed_updaterange = pd.DataFrame(results_w)
                        

        for horizon in [1,7,14,28]:
            for update in range(1, len(validation_df)):
            
                if update >= horizon:

                    continue

                else:
                    _, mae, bias = self.walk_forward_evaluation(history=combined_df,
                    target=validation_df,
                    window=None,
                    horizon=horizon,
                    update_every=update,
                    model="history"
                    )

                    results_h.append({
                        "strategy": "expanding",
                        "model": "history",
                        "window": None,
                        "horizon": horizon,
                        "update_every": update,
                        "mae": mae,
                        "bias": bias
                    })

        walkthroug_history_updaterange = pd.DataFrame(results_h)

        return pd.concat([walkthroug_history_updaterange, walkthroug_windowed_updaterange]).sort_values(by="mae")

    def fit(self, history):

        """Learn weekday means from historical daily pickup counts."""

        if history.empty:
            raise ValueError("Training data is empty")

        if self.window is not None and self.window not in [7, 14, 28]:
            raise ValueError("Window must be None, 7, 14, or 28")

        train_df = history.copy()

        self.last_training_date = train_df["pickup_date"].max()

        if self.window is not None:

            window_end = self.last_training_date + pd.Timedelta(days=1)
            window_start = window_end - pd.Timedelta(days=self.window)

            train_df = train_df[
                (train_df["pickup_date"] >= window_start)
                & (train_df["pickup_date"] < window_end)
            ]

        self.weekday_mean = (
            train_df.groupby("weekday")["pickup_count"].mean()
        )

        return self


    def predict(self, target):

        """Predict future daily counts without requiring actual pickup counts."""

        if not hasattr(self, "weekday_mean"):
            raise ValueError("Call fit() before predict()")

        target_df = target.copy()

        if target_df.empty:
            raise ValueError("Target data is empty")

        if (target_df["pickup_date"] <= self.last_training_date).any():
            raise ValueError("Target dates must be after the training period")

        weekdays = target_df["pickup_date"].dt.day_name()
        predictions = weekdays.map(self.weekday_mean)

        if predictions.isna().any():
            raise ValueError("Training data is missing a target weekday")

        return predictions.rename("prediction")
