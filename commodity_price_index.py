import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from cpi_chart_function import *
pd.set_option('future.no_silent_downcasting', True)


url ='https://github.com/natatsypora/commodity_price_index/blob/main/CMO-Historical-Data-Monthly.xlsx?raw=true' 
sheet_name='Monthly Indices'
skiprows=[1,2,3,4]

def read_and_clean_data(url, sheet_name, skiprows):
    # Read data from Excel file
    Monthly_Indices = pd.read_excel(url, sheet_name=sheet_name, skiprows=skiprows) 
    # Fill missing values for header
    for col in Monthly_Indices.columns[1:]:
        Monthly_Indices[col] = Monthly_Indices[col].ffill()
        Monthly_Indices[col] = Monthly_Indices[col].bfill()

    # Set the first row as header 
    Monthly_Indices.columns = Monthly_Indices.iloc[0]
    # Drop the 5 first rows and reset index
    df = Monthly_Indices[5:]
    df.reset_index(drop=True, inplace=True)
   # Identify and rename the unnamed column safely 
    unnamed_col = df.columns[df.columns.isna()][0] 
    df.rename(columns={unnamed_col: 'Date'}, inplace=True)
    # Remove the special character from the column names
    df.columns = [col.strip(' **') for col in df.columns]
    # Convert 'Date' column to datetime format 
    df['Date'] = pd.to_datetime(df['Date'], format='%YM%m')
    # Convert all columns (except 'Date') to numeric format    
    df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')   
    # Add year and formatted month columns using assign 
    df = df.assign(
         year=lambda x: x['Date'].dt.year, 
         month_3=lambda x: x['Date'].dt.strftime('%b'))
    # Reorder months
    month_order_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['month_3'] = df['month_3'].astype("category").cat.set_categories(month_order_list, ordered=True)     
    # Filter data by selected years (2010-2024)
    df_2010_2024 = df[df['Date'] >= '2010-01-01']

    return df_2010_2024

# Create dataframe
df = read_and_clean_data(url, sheet_name, skiprows)

# Create link button for header
link_btn = html.A( href='https://github.com/natatsypora?tab=repositories', 
                  children=[ html.I(className="fab fa-github fa-2x")], 
                  target='_blank', style={'textDecoration':'none', 'color':'rgba(31,119,180,0.7)',} )


# Create app object===========================================================================
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
#============================================================================================= 


# Create app layout=================================================
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.Img(src="/assets/Globe.png", alt="Globe", style={'height': '50px'}), 
             width=1, className='d-flex align-items-center justify-content-center'),
        dbc.Col(html.H2("World Bank Commodity Price Indices",  
                        className='text-center my-3', 
                        style={'color': 'rgba(31,119,180,0.8)'}), width=10),
        dbc.Col(link_btn,  width=1, className='d-flex align-items-center justify-content-center')
        ], class_name='mb-3 border-bottom bg-light'),
    # Control Panel
    dbc.Row([
        dbc.Col(html.Label('Select Index', className='me-3'), 
                width=2, className='d-flex align-items-center justify-content-end'),
        dbc.Col(
            dcc.Dropdown(
                id='index-group-dropdown',
                options=[{'label': i, 'value': i} for i in df.columns[2:-2]],
                value='Beverages',  # Default value
                clearable=False, 
                optionHeight=20), width=4),
        dbc.Col(html.Label('Select Year', className='me-3'), 
                width=2, className=' offset-1 d-flex align-items-center justify-content-end'),
        dbc.Col(
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': i, 'value': i} for i in df['year'].unique()[1:]],
                value=2023,  # Default value
                clearable=False, 
                optionHeight=20 ), width=2),
        ], class_name='mb-3'),    
     # Graphs
     dbc.Row([         
         dbc.Col([
             dbc.Card(dcc.Graph(id='area-graph', figure={}, config=config_dict), body=True, class_name='mb-3'),
             dbc.Card(dcc.Graph(id='mom-rate-graph', figure={}, config=config_dict), body=True)], 
             width=7),
         dbc.Col(dbc.Card([
                 dcc.Graph(id='scatter-graph', figure={}, config=config_dict),                 
                 dcc.Graph(id='yoy-graph', figure={}, config={'displayModeBar': False}),
                 dcc.Graph(id='mom-change-graph', figure={}, config=config_dict),                  
                 ], body=True, class_name='mb-3'), 
                 width=5),
         ]),           
    #Footer
    dbc.Row([                   
         dbc.Col(html.Label('Source of Data'), width=2, className='my-3 offset-1 text-end'),
         dbc.Col(html.A('World Bank Group', 
                        href='https://www.worldbank.org/en/research/commodity-markets#1', target='_blank '), 
                        width=2, className='my-3'),         
         dbc.Col([
             html.Label('Created with'), 
             html.A('Plotly', href='https://plotly.com/python/', target='_blank ', className='me-3'), 
             html.A('Dash', href='https://dash.plotly.com/', target='_blank '), 
        ], width=3, className='offset-3 my-3 d-flex align-items-center justify-content-around'),
], className='mb-3 border-top bg-light'),
])

# Callbacks==========================================================
@app.callback(
    #Output('metric-card', 'figure'),
    Output('area-graph', 'figure'),
    Output('yoy-graph', 'figure'),
    Output('scatter-graph', 'figure'),
    Output('mom-rate-graph', 'figure'),
    Output('mom-change-graph', 'figure'),
    Input('index-group-dropdown', 'value'),
    Input('year-dropdown', 'value'),
)
def update_graph(index, selected_year):
    # Filter data by selected year
    last_year = int(selected_year)
    prev_year = last_year - 1
    dff = df[['Date', index, 'year', 'month_3']].copy()
    ct_df =pd.crosstab(dff['month_3'], dff['year'], values=dff[index], aggfunc='max')
    
    area_graph = create_area_fillgradient(dff, 'Date', index, col_scale, line_color, 
        title=f'Commodity {index} Index Monthly Price<br><sub>Historical Data for 2010-2024, US$ (2010=100)</sub>') 
    
    title= f"YoY Change {last_year} vs {prev_year}" #for {index} Commodity Group"
    yoy_graph = create_bar_chart_with_changes(ct_df, last_year, prev_year, title=None)
    
    scatter_graph = create_scatter_plot_with_prc_changes(ct_df, last_year, prev_year, title)

    mom_rate_graph = line_chart_with_pos_and_neg_colors(dff, 'Date', index, pos_color, neg_col, 
                                                        title='MoM Growth Rate (%) Across Years')
    
    mom_change_graph = mom_changes_subplots(ct_df, y_col_name=last_year, title=f'MoM Change {last_year}')  
    
    return  area_graph, yoy_graph, scatter_graph, mom_rate_graph, mom_change_graph


if __name__ == '__main__':
    app.run_server(debug=False)