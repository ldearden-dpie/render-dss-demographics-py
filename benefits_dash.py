from dash import Dash, dash_table, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
# from clean_data import *

# benefits_data = get_raw_data()
# clean_dataframes = clean_data(benefits_data)
# clean_benefits_dataframe = combine_dataframes(clean_dataframes)
# region_list = clean_benefits_dataframe['LGA name'].unique()

clean_benefits_dataframe = pd.read_csv('dss-demographics-lga.csv')
region_list = clean_benefits_dataframe['LGA name'].unique()


# Initialize the app - incorporate css
external_stylesheets = [dbc.themes.BOOTSTRAP,'https://cdn.jsdelivr.net/npm/nsw-design-system@3/dist/css/main.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

change_region = html.Div(
    [
        html.Div("Change Region"),
        dcc.Dropdown(region_list, 'Albury (C)', id='dropdown-selection'),
    ],
    className="pb-4",
)

benefits_payments_by_demographics = html.Div(
    [
        html.H2(children='Commonwealth Benefits payments by demographics', style={'textAlign':'center'}),
        dcc.Graph(id='graph-content')
    ],
    className="pb-4",
)

tool_header = html.Div([
    html.H1(children='Commonwealth Benefits payments Tool', style={'textAlign':'center'}),
])

app.layout = dbc.Container(
    [
        dbc.Row([dbc.Col(html.Div(className="columnOne"), width=3), dbc.Col(tool_header, lg=6), dbc.Col(html.Div(className="columnThree"), width=3)]),
        dbc.Row([dbc.Col(html.Div(className="columnOne"), width=3), dbc.Col(change_region), dbc.Col(html.Div(className="columnThree"), width=3)]),
        dbc.Row([ dbc.Col(html.Div(id="graphs"), width=8)], justify="center"),
        # dbc.Row(dbc.Col(html.A(html.Button("Download as HTML"), id="download"))),
        # dbc.Row(dbc.Col(dcc.Download(id='download_1'))),
    ],
    className="dbc p-4",
    fluid=True,
)

def get_y_values() -> list:
    y_values = list(clean_benefits_dataframe.columns)
    # remove = ['LGA', 'LGA name', 'year', 'month', 'date']
    y_values.remove('LGA')
    y_values.remove('LGA name')
    y_values.remove('year')
    y_values.remove('month')
    y_values.remove('date')
    return y_values



@callback(
    Output('graphs', 'children'),
    Input('dropdown-selection', 'value')
)

def update_graph(value):
    region_df = clean_benefits_dataframe[clean_benefits_dataframe['LGA name']==value]
    region_df = region_df.sort_values(by=['date'])
    y_values = get_y_values()
    region_df[y_values] = region_df[y_values].apply(pd.to_numeric, errors='ignore')
    
    chart = px.line(region_df, x='date', y=y_values, title="Comparison of "+value,
                template="simple_white")
    # chart.update_traces(line_color='#146CFD', name =projection_1_label,
    #                 hovertemplate='year=%{x}'+'<br>population=%{y:,.2f}')
    # chart.add_scatter(x = projection_2_df.year, y = projection_2_df.population, name = projection_2_label,
    #                 hovertemplate='year=%{x}'+'<br>population=%{y:,.2f}',
    #                 line_color='#D7153A')
    chart.update_traces(visible="legendonly") #<----- deselect all lines 
    # chart.update_traces(showlegend = True)
    # chart.write_html(test['LGA name'][0]+".html")
    chart.data[y_values.index('Commonwealth Rent Assistance')].visible=True   #<------ display the nth line
    chart.data[y_values.index('Health Care Card')].visible=True   #<------ display the nth line
    chart.data[y_values.index('JobSeeker Payment')].visible=True   #<------ display the nth line
    
    
    graph1 = dcc.Graph(figure=chart)
    
    # Accounts table
    table1 = dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True} for i in region_df.columns
        ],
        data=region_df.to_dict('records'),
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable=False,
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
    )
    
    
    return [
        dbc.Row(dbc.Col(graph1), className="plotly-full-screen"),
        dbc.Row(dbc.Col(table1, style={'overflowX':'auto'}), className=""),
    ]

# @app.callback(
#     Output('download_1','data'),
#     Input('download','n_clicks'),prevent_initial_call=True)
# def download_html(n):
#     return dcc.send_file("plotly_graph.html")


if __name__ == '__main__':
    app.run_server(debug=True)
