import pandas as pd

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
    df = df.rename(columns={unnamed_col: 'Date'})
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

# Create dataframe for 2010-2024
df = read_and_clean_data(url, sheet_name, skiprows)


def melt_data(dff, idx_name='Date', var_name='Index', value_name='Price'):  
    # Use melt to reshape the data 
    dfp = (pd.melt(
        dff, 
        id_vars=[idx_name], 
        var_name=var_name, 
        value_name=value_name)
        .sort_values(by=[var_name, idx_name], ascending=[True, True])
        ) 
    
    # Add price previous month and price previous year
    dfp['Price'] = dfp['Price'].astype(float)
    dfp['Price pm'] = dfp['Price'].shift(1).astype(float)
    dfp['Price py'] = dfp['Price'].shift(12).astype(float)
    
    # Add YoY and MoM changes
    dfp['MoM change'] = dfp['Price'].pct_change().astype(float)
    dfp['YoY change'] = dfp['Price'].pct_change(12).astype(float)    
   
    return dfp

# Get melted data for 13 last months
df_melt  = melt_data(df.iloc[-13 :, :-2])