import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Define colors for positive and negative values
pos_color = 'rgba(0, 160, 0, 0.7)'
neg_col = 'rgba(255, 0, 0, 0.7)'

# Define colorscale for positive and negative values
col_scale = [[0,'rgba(255, 255, 255, 0.1)'], [0.5,'rgba(31,119,180,0.2)'], [1,'rgba(31,119,180,0.5)']]
line_color = 'rgba(31,119,180,0.7)'

# Define layout parameters
layout_params = {'paper_bgcolor':'#F8F9FA', 'plot_bgcolor':'#F8F9FA', 'template': 'plotly_white'}

# Define config dictionary 
config_dict = dict(
    {'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'],
    'displaylogo': True })

def get_min_max_values_and_index(dff, x_col_name, y_col_name):
    idx_max = dff.loc[dff[y_col_name].idxmax(), x_col_name]
    idx_min = dff.loc[dff[y_col_name].idxmin(), x_col_name]
    max_val, min_val = dff[y_col_name].agg(['max', 'min'])

    return  idx_max, idx_min, max_val, min_val


def create_area_fillgradient(dff, x_col_name, y_col_name, col_scale, line_color, title):
    fig = go.Figure()
    fig.add_scatter(
        x=dff[x_col_name], y=dff[y_col_name],        
        mode='lines',  name='',
        line=dict(color=line_color, width=1), 
        fill='tozeroy',
        fillgradient=dict(            
            type = 'vertical',
            colorscale=col_scale)) 
       
    # Culculate min and max values
    xmax, xmin, ymax, ymin = get_min_max_values_and_index(dff, x_col_name, y_col_name)
    # Add vertical line for max value
    fig.add_shape(type="line", x0=xmax, y0=0, x1=xmax, y1=ymax, 
                  line=dict(color='green', width=0.5, dash='dot'))
    # Add vertical line for min value
    fig.add_shape(type="line", x0=xmin, y0=0, x1=xmin, y1=ymin, 
                  line=dict(color='red', width=0.5, dash='dot'))
    # Add markers for max and min values
    fig.add_scatter(
        x=[xmax, xmin], y=[ymax, ymin], 
        mode='markers', 
        marker=dict(color=['rgba(0, 180, 0, 1)', 'red'], size=5), 
        name='' )
    
    fig.update_traces(hovertemplate='%{x}<br>Index = $%{y:.2f}')

    # Calculate trend
    cng = dff[y_col_name].values[[0, -1]]
    trend = (cng[-1] - cng[0]) / cng[0]
    # Determine color based on trend value 
    color = 'red' if trend < 0 else 'green'
    # Define text for annotation
    text=f'15-years<br>trend<br><span style="color:{color}"><b>{trend:.1%}</span>' 
    # Add horizontal line with trend value
    fig.add_hline(y=cng[0], line=dict(color='black', width=0.5, dash='dot'), 
                  annotation_text=text, annotation_position='right')
    
    fig.update_layout(**layout_params,
        title=title, title_font_size=20,  title_y=0.94,      
        showlegend=False, modebar_orientation='v',
        height=400, xaxis_range=[dff[x_col_name].min(), dff[x_col_name].max()],
        yaxis=dict(ticklabelstandoff=5, ticksuffix='$'), xaxis_ticklabelstandoff=5,
        margin=dict(l=20, t=70, r=70, b=20))    

    return fig

# ================================================================================
def create_bar_chart_with_changes(dff, last_year, prev_year, title):
    # Get data for graph
    x = dff.index
    y1 = dff[last_year]
    y2 = dff[prev_year]
    delta_py = y1 - y2

    # Create figure
    fig = go.Figure()    
    # Define bar color
    bar_color = ['red' if i < 0 else 'rgba(0, 160, 0, 1)' if i > 0 else 'grey' for i in delta_py]
    
    #-------------------------------------------------------------
    # Add bar for last year
    fig.add_bar(
        x=x, y=y1, 
        customdata=y2, 
        hovertemplate='%{y:,.2f}$<br>PY : %{customdata:,.2f}$',                
        marker_color='rgba(31,119,180,0.5)',
        width=0.8, name='LY')
    
    # Add text with values for last year
    fig.add_scatter(
        x=x, y=y1/2, 
        mode='text', text=y1,
        hoverinfo='skip',
        #textfont=dict(color='white', size=12),         
        textposition='middle center', 
        texttemplate='%{text:,.0f} ')        
    
    #-------------------------------------------------------------
    # Add bar for changes from PY
    fig.add_bar(
        x=x, y=delta_py,         
        customdata=delta_py,        
        hovertemplate='Change : %{customdata:,.2f}$',
        marker_color=bar_color, 
        base=y2, width=0.5, name='')
    
    # Add text with values delta_py
    fig.add_scatter(
        x=x, y=y2+[n if n > 0 else 0 for n in delta_py], 
        mode='text', text=delta_py,
        hoverinfo='skip',
        textfont_color=bar_color,        
        textposition='top center',
        texttemplate=[' +%{text:,.0f}' if v > 0 else ' %{text:,.0f}' for v in delta_py])
    
    #-------------------------------------------------------------
    # Add horizontal line at zero line
    fig.add_hline(y=0, line_color='lightgrey')

    #-------------------------------------------------------------
    if y1.max() > y2.max():
        yrange = [0, y1.max()*1.1]
    else:
        yrange = [0, y2.max()*1.1]
        
    # Update properties for layout 
    fig.update_layout(**layout_params,
        title=title, title_font_size=18,
        barmode='group', bargap=0.7,
        hovermode='x unified',               
        margin=dict(t=10, b=40, l=10, r=10),        
        height=200, 
        showlegend=False, 
        yaxis=dict(range=yrange, visible=False))

    return fig

# ================================================================================
def create_scatter_plot_with_prc_changes(dff, last_year, prev_year, title):
    # Get data for graph
    x = dff.index
    prc_change = (dff[last_year] - dff[prev_year]) / dff[prev_year] * 100
    delta_color = ['red' if i < 0 else 'rgba(0, 160, 0, 1)' if i > 0 else 'grey' for i in prc_change]
    fig = go.Figure()

    # Add bar for changes from PY
    fig.add_bar(x=x, y=prc_change,
                name='△PY%', marker_color='grey',
                width=0.05, hoverinfo='skip' )

    # Add markers with text values prc_change
    fig.add_scatter(x=x, y=prc_change, text=prc_change,
                    textposition=['bottom center' if d < 0 else 'top center' for d in prc_change],
                    texttemplate=['+'+'%{text:.0f}%' if d > 0 else '%{text:.0f}%'  for d in prc_change],
                    mode='markers+text', hovertemplate='%{y:.2f}%',
                    marker=dict(symbol='square', size=10, color=delta_color),
                    name='', hoverinfo='skip')

    # Add horizontal line at zero line
    fig.add_hline(y=0, line_color='grey', line_width=0.5)  

    # Define y-axis range
    if prc_change.max() <= 0:  
        yrange = [prc_change.min()*1.2-20, 10]
    elif prc_change.min() >= 0:
        yrange = [-10, (prc_change.max())*1.2+20]
    else:
        yrange = [prc_change.min()*1.2-25, (prc_change.max())*1.2+25]

    # Update properties for layout
    fig.update_layout(**layout_params,
            title=title, title_font_size=18,
            barmode='group', bargap=0.7,                         
            margin=dict(t=50, b=10, l=10, r=10),        
            height=200, 
            showlegend=False, xaxis_visible=False,
            yaxis=dict(range=yrange, visible=False))

    return fig

# ================================================================================
def colorscale_with_zero_position(diff_values, neg_col, pos_color ) : 
    # Calculate min and max of the diff values
    min_diff = min(diff_values)
    max_diff = max(diff_values)
    # Normalize the zero point in the range of the data
    zero_position = (0 - min_diff) / (max_diff - min_diff)
    # Define a colorscale using zero position for negative and positive values
    colorscale=[[0, neg_col], [zero_position, neg_col], [zero_position, pos_color], [1.0 , pos_color]]
    
    return colorscale

# ================================================================================
def line_chart_with_pos_and_neg_colors(dff, x_col_name, y_col_name, 
                                       pos_color, neg_col, title):
    """
    Creates a line chart with positive and negative values colored differently.

    This function generates a Plotly line chart where the line's color changes
    based on whether the y-values are positive or negative. 

    Args:
        dff (pd.DataFrame): The DataFrame containing the data for the chart.
        x_col_name (str): The name of the column in 'dff' for the x-axis.
        y_col_name (str): The name of the column in 'dff' for the y-axis.
        pos_color (str): The color to use for positive y-values.
        neg_col (str): The color to use for negative y-values.        
        title (str): The title of the chart.

    Returns:
        go.Figure: The Plotly figure object representing the chart.
    """

    # Culculate the percentage change in y-values
    y = 100*dff[y_col_name].pct_change().fillna(0).values

    # Create a list of colors for each data point based on its sign
    # If the value is positive or zero, use 'pos_color', otherwise use 'neg_col'
    marker_colors = [pos_color if v >= 0 else neg_col for v in y]  

    # Generate a colorscale that transitions between neg_col and pos_color at zero    
    colorscale = colorscale_with_zero_position(y, neg_col, pos_color)  

    # Create a new Plotly figure
    fig = go.Figure()  

    # Add a scatter trace to the figure, representing the line chart
    fig.add_scatter(
        x=dff[x_col_name],  # Set x-axis values
        y=y,  # Set y-axis values
        name='',  # Trace name 
        hovertemplate='%{x}<br>MoM growth = %{y:.2f}%',  # Hover text format
        mode='markers',  # Display as connected points with colored markers
        marker=dict(color=marker_colors, size=0.1),  # Marker styling
        fill='tozeroy',  # Fill area under the line to zero
        fillgradient=dict(type="vertical", colorscale=colorscale) # Apply vertical fill gradient
    )
    # Add horizontal lines for max rate
    fig.add_hline(y=max(y), line=dict(color='green', width=0.5, dash='dot'), 
                  annotation_text=f'Max<br><span style="color:green"><b>{max(y):.1f}%</span>',
                  annotation_position='right')
    # Add horizontal lines for min rate
    fig.add_hline(y=min(y), line=dict(color='red', width=0.5, dash='dot'), 
                  annotation_text=f'Min<br><span style="color:red"><b>{min(y):.1f}%</span>', 
                  annotation_position='right')
    
    # Update the layout of the figure for styling and labels
    fig.update_layout(**layout_params,
        title=title,  # Set chart title
        title_font_size=18,  # Set title font size        
        height=250,  # Set chart height      
        margin=dict(l=20, t=50, r=70, b=20),  # Set chart margins
        yaxis=dict(ticksuffix='%', ticklabelstandoff=5),  # Y-axis styling
        xaxis_ticklabelstandoff=10  # X-axis styling
    )
   
    return fig

def mom_changes_subplots(dff, y_col_name, title): 
    # Culculate the percentage change and the difference in y-values   
    x = dff.index
    diff_prev_month = dff[y_col_name].diff().fillna(0)
    perc_change_prev_month = 100*dff[y_col_name].pct_change().fillna(0)
    markers_color = ['red' if i < 0 else 'rgba(0, 160, 0, 1)' if i > 0 else 'grey' for i in diff_prev_month]

    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True, 
        vertical_spacing=0, 
        row_heights=[0.4, 0.6])  
     
    # Add scatter plot for percentage change
    fig.add_scatter(
        x=x, y=perc_change_prev_month, 
        mode='markers+text+lines', 
        text=perc_change_prev_month,
        textposition=['bottom center' if d < 0 else 'top center' for d in perc_change_prev_month],
        texttemplate=['+'+'%{text:.0f}%' if d > 0 else '%{text:.0f}%' for d in perc_change_prev_month],                                       
        marker=dict(symbol='square', size=10, color=markers_color),
        line=dict(color='grey', width=1),  
        name='%△PM', hovertemplate='%{y:.2f}%', 
        row=1, col=1)

    # Add bar plot for difference in y-values
    fig.add_bar(
        x=x, y=diff_prev_month,        
        customdata=perc_change_prev_month,
        hovertemplate='%{y:.2f}$ (%{customdata:.2f}%)',
        name='△PM', marker_color=markers_color, width=0.6, 
        row=2, col=1)
    
    # Add markers with text for difference in y-values
    fig.add_scatter(
        x=x, y=diff_prev_month,
        mode='text+markers', 
        marker_color='rgba(0,0,0,0)',
        text=diff_prev_month,
        texttemplate=['+'+'%{text:.0f} ' if py > 0 else '%{text:.0f} ' for py in diff_prev_month],
        textposition=['bottom center' if d < 0 else 'top center' for d in diff_prev_month],
        name='△PM', hoverinfo='skip',
        row=2, col=1)

    # Add zeroline for bar plot
    fig.add_hline(y=0, line_color='grey', line_width=1, row=2)

    # Define y and x axis properties
    fig.update_yaxes(visible=False)
    fig.update_xaxes(visible=False, ticklabelstandoff=5, row=1)

    # Update layout
    fig.update_layout(**layout_params,
        title=title, titlefont_size=18,
        hovermode='x unified', 
        margin=dict(t=50, b=10, l=10, r=10),
        height=300, showlegend=False,
        yaxis1_range=[min(perc_change_prev_month)*1.2-20, max(perc_change_prev_month)*1.2+20],
        yaxis2_range=[min(diff_prev_month)*1.2-40, max(diff_prev_month)*1.2+40])

    return fig

