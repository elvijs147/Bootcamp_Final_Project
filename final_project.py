from dash import Dash, dcc, Output, Input, State, callback_context
from flask import Flask
from flask_caching import Cache
from pymongo import MongoClient
import dash_bootstrap_components as dbc
import json
import plotly.graph_objects as go
import snowflake.connector


# Replace these with your MongoDB credentials
mongodb_credentials = {
    "host": "localhost",
    "port": 27017,
    "database": "project_db",
    "collection": "comments"
}

# Connect to MongoDB
mongo_client = MongoClient(mongodb_credentials["host"], mongodb_credentials["port"])
mongo_db = mongo_client[mongodb_credentials["database"]]
comments_collection = mongo_db[mongodb_credentials["collection"]]

# Replace these with your Snowflake credentials
snowflake_credentials = {
    "account": "YZYOZTS-BA97590",
    "user": "elvijs147",
    "password": "Accenture2024",
    "warehouse": "COMPUTE_WH",
    "database": "PROJECT_DB",
    "schema": "PUBLIC"
}


# Function to query Snowflake and return data as JSON with caching
def query_snowflake_json_cached(query):
    conn = snowflake.connector.connect(
        user=snowflake_credentials["user"],
        password=snowflake_credentials["password"],
        account=snowflake_credentials["account"],
        warehouse=snowflake_credentials["warehouse"],
        database=snowflake_credentials["database"],
        schema=snowflake_credentials["schema"]
    )
    cur = conn.cursor()
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()

    # Convert results to a list of dictionaries (JSON)
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in results]

    return data


def main():
    # Initialize Flask application and link it to Dash
    server = Flask(__name__)
    app = Dash(__name__, external_stylesheets=[dbc.themes.LUX], server=server)

    # Initialize Flask-Caching
    cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})

    mytitle = dcc.Markdown(id='page-title', children='# Welcome to COVID-19 Analysis Dashboard', style={'height': '50px', 'margin-top': '20px'})
    mygraph = dcc.Graph(figure={}, style={'width': '900px', 'height': '500px', 'margin': 'auto'})
    dropdown = dcc.Dropdown(options=[], value=None, clearable=False)
    query_input = dcc.Input(id='query-input', type='text', value='SELECT * FROM COVID_REAL', style={'width': '100%'})
    run_query_btn = dbc.Button("Run Query", id="run-query-btn", color="primary", className="text-left")

    # Add a modal for adding comments
    comment_modal = dbc.Modal(
        [
            dbc.ModalHeader("Add Comment"),
            dbc.ModalBody(
                [
                    dbc.Input(id="comment-author", type="text", placeholder="Your Name", style={'margin-bottom': '20px'}),
                    dcc.Textarea(id="comment-textarea", placeholder="Type your comment here", rows=5),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Submit", id="submit-comment-btn", color="primary"),
                    dbc.Button("Close", id="close-comment-btn", color="secondary"),
                ]
            ),
        ],
        id="comment-modal",
    )

    # Dummy dropdown to resolve callback exception
    dummy_dropdown = dcc.Dropdown(id='dropdown', options=[], value='Population', multi=False, style={'display': 'none'})

    # Customize your own Layout
    app.layout = dbc.Container([
        dummy_dropdown,
        
        dbc.Row([
            dbc.Col([mytitle], width=7)
        ], justify='center'),

        dbc.Row([
            dbc.Col([query_input], width=4, align='center'),
            dbc.Col([run_query_btn], width=2, align='center')
        ], justify='center'),

        dbc.Row([
            dbc.Col([mygraph], width=8, align='center')
        ], justify='center'),
            
        dbc.Row([
            dbc.Col([dropdown], width=2, align='start')
        ], justify='center'),
        
        # Hidden comment modal (displayed when a country is clicked)
        dbc.Row([
            dbc.Col([comment_modal], width=12, style={"display": "none"}),
        ], id="comment-modal-row", style={"display": "none"}),
    ], fluid=True)


    # Callback
    @app.callback(
        [
            Output(mygraph, 'figure'),
            Output('page-title', 'children'),
            Output("comment-modal", "is_open"),
            Output("comment-textarea", "value"),
            Output(dropdown, 'options'),
        ],
        [
            Input(mygraph, 'clickData'),
            Input(dropdown, 'value'),
            Input("submit-comment-btn", "n_clicks"),
            Input("close-comment-btn", "n_clicks"),
            Input("run-query-btn", "n_clicks"),
        ],
        [
            State("comment-author", "value"),
            State("comment-textarea", "value"),
            State("comment-modal", "is_open"),
            State("query-input", "value"),
            State("dropdown", "options"),
        ]
    )


    @cache.memoize(timeout=60)  # Set timeout (in seconds) based on your needs
    def update_graph_and_comments_cached(click_data, selected_column, submit_btn_clicks, close_btn_clicks, run_query_btn_clicks, author_name, comment_text, is_comment_modal_open, user_query, dropdown_options):
        try:
            # Check if the callback is triggered by a country click
            is_country_click = click_data and 'points' in click_data

            # Determine the query to execute
            if run_query_btn_clicks and user_query:
                query_to_execute = user_query
            else:
                query_to_execute = "SELECT * FROM COVID_REAL"

            # Query Snowflake and get data in JSON format
            data_json = query_snowflake_json_cached(query_to_execute)

            # Update dropdown options
            new_dropdown_options = [{'label': col, 'value': col} for col in data_json[0].keys()][2:]

            # Ensure selected_column is not None
            selected_column = selected_column or new_dropdown_options[0]['value']

            # Create a choropleth map using plotly.graph_objects
            locations = [entry['ISO'] for entry in data_json]
            values = [entry[selected_column] for entry in data_json]
            text = [entry['COUNTRY'] for entry in data_json]

            fig = go.Figure(data=go.Choropleth(
                locations=locations,
                z=values,
                text=text,
                colorscale='sunsetdark',
                autocolorscale=False,
                reversescale=False,
                marker_line_color='darkgray',
                marker_line_width=0.5,
                colorbar_tickprefix='',
                colorbar_title=selected_column,
                hoverinfo='text+z'
            ))

            # Update layout
            fig.update_layout(
                title_text=None,
                geo=dict(
                    showframe=True,
                    showcoastlines=True,
                    projection_type='equirectangular'
                ),
                annotations=[dict(
                    x=0.55,
                    y=0.1,
                    xref='paper',
                    yref='paper',
                    text='',
                    showarrow=False
                )]
            )

            clicked_country_iso = None
            is_comment_modal_open_new = is_comment_modal_open

            # Handle click on choropleth map
            if is_country_click:
                clicked_country_iso = click_data['points'][0]['location']
                is_comment_modal_open_new = True

            # Handle comment submission
            ctx = callback_context
            if ctx.triggered_id == "submit-comment-btn" and comment_text and clicked_country_iso:
                # Get full country name
                clicked_country = next((entry['COUNTRY'] for entry in data_json if entry['ISO'] == clicked_country_iso), None)
                if clicked_country:
                    # Create comment entry
                    country_comment = {
                        "country": clicked_country,
                        "column": selected_column,
                        "author": author_name,
                        "comment": comment_text,
                    }
                    comments_collection.insert_one(country_comment)
                    # Hide the comment modal after submission
                    is_comment_modal_open_new = False

            # Handle comment modal close button
            if ctx.triggered_id == "close-comment-btn":
                is_comment_modal_open_new = False

            return fig, '# Welcome to COVID-19 Analysis Dashboard', is_comment_modal_open_new, "", new_dropdown_options
        except Exception as e:
            print(f"Error: {str(e)}")  # Debug line
            return go.Figure(), f"Error: {str(e)}", is_comment_modal_open, "", dropdown_options
    
    return app  # Return the app object

# Run Flask and Dash apps
if __name__ == '__main__':
    app = main()
    app.run_server(debug=True, port=8054)
