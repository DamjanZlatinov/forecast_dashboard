# Project explanation and MLOps Design Document

## 1. Main idea

The goal of the project is to forecast daily dashboard views for the next 7 days.

The input data is JSON request logs. The model uses only valid dashboard view events:

```text
method = GET
endpoint = dashboards.view_dashboard
```

The data is aggregated to daily level. The target is:

```text
number of dashboard views per day
```

The model used is Prophet.

The solution is separated into three pipelines:

```text
1. Training pipeline
2. Forecasting pipeline
3. Monitoring pipeline
```

This separation is useful because training, forecasting, and monitoring do not need to run at the same time.

### Project structure
    ```text
dashboard-views-forecast/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
│   └── mlops_design.md
├── models/
├── notebooks/
│   ├── 01_eda_dashboard_usage.ipynb
│   └── 02_mvp_prophet_sanity_check.ipynb
├── reports/
│   ├── figures/
│   └── metrics/
├── scripts/
│   ├── step_01_prepare_data.py
│   ├── step_02_build_features.py
│   ├── step_03_train_model.py
│   ├── step_04_forecast.py
│   ├── monitor_01_create_report.py
│   ├── run_training_pipeline.py
│   ├── run_forecasting_pipeline.py
│   └── run_monitoring_pipeline.py
├── src/
│   └── dashboard_forecast/
│       ├── data_loader.py
│       ├── preprocessing.py
│       ├── features.py
│       ├── train.py
│       ├── forecast.py
│       └── monitoring.py
├── requirements.txt
└── README.md
```

###  Results

#### Forecast validation metrics

| Metric   |   Value | Meaning                                                             |
| -------- | ------: | ------------------------------------------------------------------- |
| MAE      | 45.8243 | The model is wrong by around 46 dashboard views per day on average. |
| RMSE     | 50.0035 | Similar to MAE, but it gives more weight to bigger errors.          |
| Coverage |  0.2857 | Around 29% of real values were inside the prediction interval.      |

The main metric is MAE because it is easy to understand for this use case.


---
## 2. Training pipeline

The training pipeline prepares the raw logs, creates the daily dataset, trains the Prophet model, validates it on the last 14 days, and saves the model with metrics.

Files used:

```text
step_01_prepare_data.py
step_02_build_features.py
step_03_train_model.py
run_training_pipeline.py
```

Outputs:

```text
data/interim/dashboard_events.parquet
data/processed/daily_dashboard_views.parquet
models/prophet_dashboard_views.json
data/processed/validation_predictions.parquet
reports/metrics/evaluation_metrics.json
reports/metrics/model_summary.json
```

## 3. Forecasting pipeline

The forecasting pipeline loads the trained model and daily dataset, then creates a forecast for the selected start date and horizon.

Files used:

```text
step_04_forecast.py
run_forecasting_pipeline.py
```

Example command:

```bash
python scripts/run_forecasting_pipeline.py --start-date 2021-01-11 --horizon-days 7
```

Outputs:

```text
data/processed/forecast_next_7_days.csv
reports/figures/forecast_next_7_days.html
```

## 4. Monitoring pipeline

The monitoring pipeline checks data quality, validation metrics, forecast reliability, and creates alerts if thresholds are broken.

Files used:

```text
monitor_01_create_report.py
run_monitoring_pipeline.py
```

Output:

```text
reports/metrics/monitoring_report.json
```


## 5. Deployment approach

The best deployment approach is batch deployment.

The reason is simple: dashboard view forecasts are needed daily, not instantly.

A possible production flow:

```text
1. New logs arrive in storage.
2. Data preparation runs.
3. The model creates a 7-day forecast.
4. Forecast output is saved.
5. Monitoring checks data and model quality.
6. Alerts are created if something is wrong.
```

The forecast can be saved in a database, parquet file, or CSV file. Then BI reports or business users can use it.

---

## 6. CI/CD and CT

```

### Continuous Training

CT means retraining the model when needed.

Possible retraining triggers:

```text
MAE becomes too high
forecast errors increase
new dashboards are added
usage pattern changes
data distribution changes
monitoring status is warning for many runs
```

A new model should replace the old model only if validation results are better.

CI/CD tests can be added to check the data format, validate the code, run basic pipeline tests, and make sure new changes do not break the project.

---

## 7. Monitoring and alerts

Monitoring is important because data and user behavior can change.

Alerts should be created when:

```text
input data is missing
daily views drop too much
MAE is above threshold
prediction interval coverage is too low
number of users changes too much
number of dashboards changes too much
```

An alert does not always mean that the model is bad. It means that someone should check the result.

Possible reasons for alerts:

```text
missing logs
system downtime
holiday period
tracking change
real change in dashboard usage
```

---

## 8. Model versioning

Each trained model should have a version.

For each model version, we should save:

```text
model file
training date range
validation metrics
model parameters
code version
training time
```

This makes the project reproducible.

It also makes it possible to compare old and new models.

Example:

```text
model_name = prophet_dashboard_views
model_version = 1
metric = MAE
validation_days = 14
```

---

## 9. Limitations

The current model is an MVP.

Limitations:

```text
It forecasts only total daily views.
It does not forecast per dashboard.
It does not use holidays.
It does not use external business events.
The validation period is short.
Prediction interval coverage is low.
```

The model is good as a baseline, but it can be improved.

---

## 10. Possible improvements

Possible improvements:

```text
forecast per dashboard
add holidays
add working day features
compare with other models
use more validation windows
store old forecasts and actual values
improve prediction intervals
add automatic retraining trigger
```

Storing old forecasts is important. It allows real monitoring of forecast accuracy after actual values are known.




# How to run

Install dependencies with `pip install -r requirements.txt`.
Run training with `python scripts/run_training_pipeline.py`. (add unziped requests folder to data/raw)
Run forecasting with `python scripts/run_forecasting_pipeline.py --start-date 2021-01-11 --horizon-days 7`, then run monitoring with `python scripts/run_monitoring_pipeline.py`.