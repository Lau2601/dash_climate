# Importing the libraries
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import dash_table
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
from sqlalchemy import text

#.env
username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PW')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('PORT_SQL')

#READ CSV
df = pd.read_csv('../Users/lauraacevedo/Documents/SPICED ACADEMY/Github/dash_climate/data/df_countries.csv')
df_countries_avg = df[df['country'].isin(['Argentina', 'Colombia', 'Germany', 'Spain'])]

#FILTER data
df_countries_avg= df_countries_avg.groupby(['city','country','month', 'month_num',]).agg({
    'maxtemp_c': 'max',
    'mintemp_c': 'min',
    'avgtemp_c': 'mean'
}).reset_index()
df_countries_avg['avgtemp_c']=df_countries_avg['avgtemp_c'].round(2)
df_countries_avg.sort_values(['country','month_num'], inplace=True)

# Table
columns_to_exclude=['month_num','country']
visible_columns = [col for col in df_countries_avg.columns if col not in columns_to_exclude]

d_table_countries = dash_table.DataTable(df_countries_avg.to_dict('records'),
                                  [{"name": i, "id": i} for i in visible_columns],
                              page_size= 11,
                              style_header={'fontWeight': 'bold'},
                              style_table={
                                         'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
                                         'minWidth': '900px', 'width': '900px', 'maxWidth': '900px', 
                                         'marginLeft': 'auto', 'marginRight': 'auto',
                                     'marginTop': 0, 'marginBottom': 25}) #General syntax for a table

color_palette={
                       'Argentina': '#008B8B',    # Set your desired color for Argentina
                       'Colombia': '#8B008B',    # Set your desired color for Colombia
                       'Germany': '#00CED1',    # Set your desired color for Germany
                       'Spain': '#E9967A'          # Set your desired color for Spain
             }

# Graph 1
fig_1 = px.bar(df_countries_avg, 
             x='month', 
             y='maxtemp_c',  
             color='country',
             color_discrete_map=color_palette,
             barmode='group',
             height=300, title = "Max temperature per month in 2023",
             range_y=[0,35],
            
            )

fig_1 = fig_1.update_layout(
        plot_bgcolor="whitesmoke", paper_bgcolor="white", font_color="black"
    )
graph = dcc.Graph(figure=fig_1)

#Line graph
fig_2 = px.line(df_countries_avg, x='month', y='mintemp_c', height=300, title="Min temperature per month in 2023", 
                    markers=True,
                    color= 'country',
                    color_discrete_map= color_palette)
fig_2 = fig_2.update_layout(
        plot_bgcolor="whitesmoke", paper_bgcolor="white", font_color="black"
    )

graph_2 = dcc.Graph(figure=fig_2)


# Animated map
fig3 = px.choropleth(df_countries_avg, locations='country', 
                    projection='natural earth', 
                    animation_frame="month",
                    color='avgtemp_c', 
                    locationmode='country names', 
                    color_continuous_scale=px.colors.sequential.thermal)

fig3 = fig3.update_layout(
        plot_bgcolor="lightgray", paper_bgcolor="white", font_color="black", geo_bgcolor="white"
    )

graph_3 = dcc.Graph(figure=fig3)

#since we are using multi parameter, this time we need a list of the all unique values 
#in the "country" column to use in the function of the callback
countries = df_countries_avg['country'].unique().tolist()

# Define the Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])
server = app.server

dropdown = dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in df_countries_avg['country'].unique()],
            value=['Argentina', 'Colombia', 'Germany', 'Spain'],
            clearable=True,
            multi=True  # Allow selecting multiple countries
        )


# Define the layout of the app
app.layout = html.Div([
    html.H1('My Climate Dash', style={'textAlign': 'center', 'color': 'Turquoise'}),
    html.Div(html.P("Argentina, Colombia, Germany & Spain"), 
             style={'textAlign': 'center','marginLeft': 50, 'marginRight': 25}),
    html.Div([graph_3,
        html.Div('Weather data per month', 
                 style={'backgroundColor': 'cornflowerblue', 'color': 'white', 
                        'width': '900px', 'marginLeft': 'auto', 'marginRight': 'auto'}),
        d_table_countries, 
        dropdown,
        dcc.Graph(id='graph'),  # Placeholder for the graph
        dcc.Graph(id='graph_2')
    ])
])
# Define callback to update the table and graphs based on dropdown selection
@callback(
    [Output('graph', 'figure'),
    Output('graph_2', 'figure')], 
    [Input(dropdown, 'value')]
)
def update_graphs(selected_countries): 
    if not selected_countries:
        return [{},{}]  # Return empty figure if no country is selected
    
    mask = df_countries_avg['country'].isin(selected_countries)  # Filter data based on selected countries
    filtered_data = df_countries_avg[mask]
    
    fig_1 = px.bar(filtered_data, 
                 x='month', 
                 y='maxtemp_c',  
                 color='country',
                 color_discrete_map=color_palette,
                 barmode='group',
                 height=300, 
                 title='Max temperature per month in 2023')
    
    fig_2 = px.line(filtered_data, 
                   x='month', 
                   y='mintemp_c',  
                   color='country',
                   color_discrete_map=color_palette,
                   height=300, 
                   title='Min temperature per month in 2023')
    
    for fig in [fig_1,fig_2]:
        fig.update_layout(
            plot_bgcolor="whitesmoke", 
            paper_bgcolor="white", 
            font_color="black")

    return fig_1,fig_2

# Run the app
if __name__ == '__main__':
    app.run_server(mode="inline", host="localhost")