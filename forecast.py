import pandas as pd
import numpy as np
import snowflake.connector
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from pmdarima import auto_arima
import warnings
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt


# Replace these with your Snowflake credentials
snowflake_credentials = {
    "account": "YZYOZTS-BA97590",
    "user": "elvijs147",
    "password": "Accenture2024",
    "warehouse": "COMPUTE_WH",
    "database": "COVID19_EPIDEMIOLOGICAL_DATA",
    "schema": "PUBLIC"
}

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=snowflake_credentials["user"],
    password=snowflake_credentials["password"],
    account=snowflake_credentials["account"],
    warehouse=snowflake_credentials["warehouse"],
    database=snowflake_credentials["database"],
    schema=snowflake_credentials["schema"]
)

# Create a cursor object
cur = conn.cursor()

# Query the COVID-19 dataset from Snowflake
query = "SELECT COUNTRY_REGION, CASES, DATE FROM ECDC_GLOBAL WHERE COUNTRY_REGION = 'Latvia'"
cur.execute(query)

# Fetch the results
results = cur.fetchall()

# Close the connection
cur.close()
conn.close()

# Create a DataFrame from the results
columns = [desc[0] for desc in cur.description]  # Get column names from cursor description
df = pd.DataFrame(results, columns=columns)

# Convert 'DATE' column to datetime format
df['DATE'] = pd.to_datetime(df['DATE']) 

# Set 'DATE' column as the index
df.set_index('DATE', inplace=True)

# print(df)
df['CASES'].plot(figsize=(12,5))
plt.title('COVID-19 Cases Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Cases')
plt.show()

# ARIMA - autoregression, moving averages, integrated.
def covid_test(dataset):
    return adfuller(dataset, autolag = 'AIC')  

# Our p-value 0.0000001241862046412819. So as smaller as better. Should be < 0.05. Stationary dataset. 
# print(covid_test(df['CASES'])) 

warnings.filterwarnings("ignore")

# Tries every combination. The goal is to minimize AIC. Best model:  ARIMA(5,1,2)
stepwise_fit = auto_arima(df['CASES'], trace=True, supress_warnings=True)
# print(stepwise_fit)

# Split into training and testing.
train = df.iloc[:-30]
test = df.iloc[-30:]
# print(train.shape, test.shape)

# Train the model. Order is from stepwise_fit. 
model = ARIMA(train['CASES'], order=(5, 1, 2))
model = model.fit()
# print(model.summary())

# Make predictions.
start = len(train)
end = len(train) + len(test) - 1
pred = model.predict(start=start, end=end, typ='levels')
pred.index = df.index[start:end+1]  # Corrected assignment of the index
# print(pred)

pred.plot(legend=True)
test['CASES'].plot(legend=True)

# If mean and root mean squared error are similar, it means the model is bad. Mine are almost identical which is bad. 17 vs 16.9. 
print(test['CASES'].mean()) 
rmse = sqrt(mean_squared_error(pred,test['CASES']))
print(rmse)

# Now predicting for future dates. 
model2 = ARIMA(df['CASES'], order=(5, 1, 2))
model2 = model2.fit()

index_future_dates = pd.date_range(start='2020-12-14', end='2021-01-13')
# print(index_future_dates)
pred = model2.predict(start=len(df), end=len(df)+30, typ='levels').rename('ARIMA Predictions')
pred.index = index_future_dates
# print(pred)

# Show results. 
# Plotting the actual vs. predicted values
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['CASES'], label='Actual Cases')
plt.plot(pred.index, pred, label='Predicted Cases', color='red')
plt.title('COVID-19 Cases in Latvia and Prediction for 30 Days')
plt.xlabel('Date')
plt.ylabel('Number of Cases')
plt.legend()
plt.show()


