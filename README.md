# COVID-19 Data Integration, Analysis, and Visualization Platform

#### Project Name: COVID-19 Data Integration, Analysis, and Visualization Platform

#### Student: Elvijs Melnis

#### Introduction
The "COVID-19 Data Integration, Analysis, and Visualization Platform" is a comprehensive project that leverages the capabilities of the Python programming language, the Dash data visualization framework, Snowflake Data Cloud, and MongoDB. The primary focus of the project is to provide an interactive and visually appealing representation of COVID-19 metrics worldwide using an interactive world map.

#### Project Goals
Integrate diverse datasets, including the World Health Organization's latest data on COVID-19, Snowflake's COVID-19 database, and MongoDB for user comments.
Develop an interactive world map using Dash to visualize COVID-19 metrics.
Implement a MongoDB database for user comments on COVID-19 metrics, allowing users to leave comments for different countries.
Utilize Flask as the backend server for the Dash web application, enhancing performance with Flask-Caching.
Implement a forecasting model (ARIMA) using Snowflake's COVID-19 database for a chosen country (Latvia) in the year 2020.

#### Technologies Used
Python
Dash (Data Visualization Framework)
Flask (Backend Framework)
Snowflake Data Cloud
MongoDB
ARIMA (AutoRegressive Integrated Moving Average) for Time Series Forecasting

#### Data Sources
World Health Organization's latest data on COVID-19.
Snowflake's COVID-19 database (ECDC_GLOBAL table) for time series forecasting.
MongoDB for storing user comments.

#### Visualization
Interactive world map using Dash for visualizing COVID-19 metrics.
Choropleth map with the ability to switch between different metrics and filter countries or metrics.

#### User Interaction
MongoDB database used for storing user comments on COVID-19 metrics.
User can click on a country on the map to leave comments, which are stored in the "project_db" database and "comments" collection.

#### Forecasting
ARIMA time series forecasting model implemented using Snowflake's COVID-19 database for a chosen country (Latvia).

#### Performance Optimization
Larger Snowflake warehouse used for improved data loading performance.
Flask-Caching implemented to enhance performance for frequently requested data.

#### Limitations and Challenges
The primary dataset lacks time-series information, limiting the ability to analyze trends over time comprehensively.
Limitations in the ARIMA forecasting model's ability to capture underlying patterns and non-linear variations in COVID-19 cases data.

#### Future Development
Incorporate additional and more granular datasets, including real-time COVID-19 data with time-series information.
Explore integration with machine learning models for improved forecasting accuracy, especially those adept at handling non-linear trends.
Enhance the comment feature with sentiment analysis on user comments.

#### Project Execution
The project successfully integrates diverse data sources, utilizes programming languages like Python, integrates Snowflake and MongoDB databases, and orchestrates a seamless collaboration between Flask and Dash frameworks. The balance between functionality and aesthetics transforms raw COVID-19 data into a useful and visually pleasing final product.
