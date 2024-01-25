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

df= pd.read_csv('../data/df_countries_avg.csv')


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


# Graph 1
fig = px.bar(df_countries_avg, 
             x='month', 
             y='avgtemp_c',  
             color='country',
             barmode='group',
             height=300, title = "The climate through 2023",
             range_y=[0,35],
             color_discrete_map={
                       'Argentina': 'darkcyan',    # Set your desired color for Argentina
                       'Colombia': 'darkmagenta',    # Set your desired color for Colombia
                       'Germany': 'darkturquoise',    # Set your desired color for Germany
                       'Spain': 'darksalmon'          # Set your desired color for Spain
             })

fig = fig.update_layout(
        plot_bgcolor="whitesmoke", paper_bgcolor="white", font_color="black"
    )
fig.show()
graph = dcc.Graph(figure=fig)

#Line graph
fig_2 = px.line(df_countries_avg, x='month', y='avgtemp_c', height=300, title="Avg temperature in 2023", 
                    markers=True,
                    color= 'country',
                    color_discrete_map={
                        'Argentina': 'darkcyan',
                        'Colombia': 'darkmagenta',
                        'Germany': 'darkturquoise',
                        'Spain': 'darksalmon'
                    })
fig_2 = fig_2.update_layout(
        plot_bgcolor="whitesmoke", paper_bgcolor="white", font_color="black"
    )
fig_2.show()
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


## Add DROPDOWN
app =dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])
server = app.server

#since we are using multi parameter, this time we need a list of the all unique values 
#in the "country" column to use in the function of the callback
countries =df_countries_avg['country'].unique().tolist() 

#changing the color of the dropdown value
dropdown = dcc.Dropdown(['Argentina', 'Colombia', 'Germany','Spain'],value=['Argentina', 'Colombia', 'Germany','Spain'],
                        clearable=False)

#dcc.Dropdown([{'label': ['Germany', 'Belgium', 'Denmark'], 'value': "Germany"},]) 



#we also moved the dropdown menu a bit to the left side

app.layout = html.Div([html.H1('My First Spicy Dash', style={'textAlign': 'center', 'color': 'Turquoise'}), 
                       html.Div(html.P("Argentina, Colombia, Germany & Spain"), 
                                style={'marginLeft': 50, 'marginRight': 25}),
                       html.Div([html.Div('Weather data per month', 
                                          style={'backgroundColor': 'cornflowerblue', 'color': 'white', 
                                                 'width': '900px', 'marginLeft': 'auto', 'marginRight': 'auto'}),
                                 d_table_countries, dropdown, graph,  graph_2, graph_3])
                      ])
@callback(
    Output(graph, "figure"), 
    Input(dropdown, "value"))

#Output(component_id='my-output', component_property='children'),
#Input(component_id='my-input', component_property='value')

def update_bar_chart(country): 
    mask = df_countries_avg["country"] == country # coming from the function parameter
    fig =px.bar(df_countries_avg[mask], 
             x='month', 
             y='avgtemp_c',  
             color='country',
             barmode='group',
             height=300, title = "We can take a look at the weather in 2023",)
    fig = fig.update_layout(
        plot_bgcolor="whitesmoke", paper_bgcolor="white", font_color="black",
    )

    return fig # whatever you are returning here is connected to the component property of
                       #the output which is figure

if __name__ == "__main__":
    app.run_server(mode="inline", host="localhost")
