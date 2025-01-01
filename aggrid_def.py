import dash_ag_grid as dag
from cpi_chart_function import create_sparkline
import pandas as pd
from data_preprocessing import df_melt


# Get datafreame with graph for ag-grid table
dfgrid = create_sparkline(df_melt, 'Index')

# Create ag-grid table--------------------------------------------------------------
# Define columns headers to show in ag-grid 
maxmonth = dfgrid['Date'].max()
lastmonth_label = maxmonth.strftime('%b %Y')
prevmonth_label = (maxmonth + pd.DateOffset(months=-1)).strftime('%b %Y')
prevyear_label = (maxmonth + pd.DateOffset(years=-1)).strftime('%b %Y')


# Conditional formatting
sellstyle_condition = {   
            # Set of rules           
            "styleConditions": [
                {"condition": "params.value > 0", "style": {"color": "green"}},
                {"condition": "params.value < 0", "style": {"color": "crimson"}, 
                }],
             # Default style if no rules apply  
            "defaultStyle": {"color": "black"}}

# Column definitions for ag-grid
columnDefs = [    
    {"headerName": "Index", "field": "Index", "minWidth": 200, 
     'type': 'leftAligned', "headerClass": "header-medium"},

    # Header with subheaders
    {'headerName': 'Average Price (US$)', 
     "children": [           
         {"headerName": lastmonth_label,          
          "field": "Price",
          "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}},
         {"headerName": prevmonth_label ,         
          "field": "Price pm",
          "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}},
         {"headerName": prevyear_label,           
          "field": "Price py",
          "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}},
          ]},

    # Header with subheaders and conditional formatting
    {'headerName': 'Percent Change',  
     "children": [  
        {"headerName": "PM",        
        "field": "MoM change", "minWidth": 85,
        'headerTooltip': "Previous Month",          
        "valueFormatter": {"function": "d3.format('.1%')(params.value)"},
        'cellStyle': sellstyle_condition},

        {"headerName": "PY",        
        "field": "YoY change", "minWidth": 85,
        'headerTooltip': "Previous Year",               
        "valueFormatter": {"function": "d3.format('.1%')(params.value)"},  
        'cellStyle': sellstyle_condition }
     ]},  
        
    # Fild with graphs
    {'headerName': 'Price Trend', 
     "children": [   
        {"field": "graph",
         "cellRenderer": "DCC_GraphSparkline",
         "headerName": f"{prevyear_label} - {lastmonth_label}",     
         "filter": False, 'sortable': False,
         "maxWidth": 300,
         "minWidth": 220}
    ]}
]

# Set default column properties"
defaultColDef = {"resizable": True, "sortable": True, "filter": True, "minWidth": 115, 'type': 'rightAligned'}
# Set default table properties
dashGridOptions={"rowHeight": 49, "animateRows": False, "tooltipShowDelay":0}

# Create ag-grid table
aggrid_table = dag.AgGrid(
    id="ag-grid-with-graph",
    columnDefs=columnDefs,
    rowData=dfgrid.to_dict("records"),
    columnSize="sizeToFit",                    
    className="ag-theme-alpine",
    rowStyle={"backgroundColor": "rgba(255,255,255,1)"},
    defaultColDef=defaultColDef,                                        
    dashGridOptions=dashGridOptions,                                     
    style={"height": "794px"})                

