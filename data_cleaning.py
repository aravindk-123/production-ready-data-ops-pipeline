import numpy as np
import pandas as pd
import os

# Comprehensive profile of all 3 dataframes to find unique and null counts.
def profile_dataframes(dataframes_dict):
    profiles = {}
    
    for name, df in dataframes_dict.items():
        profile_data = {
            'Column': df.columns,
            'Dtype': [df[col].dtype for col in df.columns],
            'Non-Null Count': [df[col].count() for col in df.columns],
            'Null Count': [df[col].isnull().sum() for col in df.columns],
            'Null %': [round(df[col].isnull().sum() / len(df) * 100, 2) for col in df.columns],
            'Unique Count': [df[col].nunique() for col in df.columns],
            'Sample Values': [df[col].dropna().iloc[0] if not df[col].dropna().empty else None for col in df.columns]
        }
        
        profile_df = pd.DataFrame(profile_data)
        profiles[name] = profile_df
        
        print(f"\n{'='*80}")
        print(f"PROFILE: {name.upper()}")
        print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
        print(f"{'='*80}")
        print(profile_df.to_string(index=False))
        print()
    
    return profiles

def standardize_date_columns(df, cols):
    for col in cols:
        df[col] = (df[col].astype(str).str.strip().str.replace(r'\s+', '', regex=True).str.replace('/', '-', regex=False).pipe(pd.to_datetime, errors='coerce').dt.strftime('%Y-%m-%d'))
    return df 

#All execution under the if-main block for reusability in other scripts
def main(raw_dir="data_raw", clean_dir="data_clean", start_date=None, end_date=None):

     # Parse date filters safely
    if start_date:
        start_date = pd.to_datetime(start_date)
    if end_date:
        end_date = pd.to_datetime(end_date)

    #Loading Data
    customers = pd.read_csv(f"{raw_dir}/customers.csv")
    products = pd.read_csv(f"{raw_dir}/products.csv")
    transactions = pd.read_csv(f"{raw_dir}/transactions.csv")

    profiles = profile_dataframes({
        'customers': customers,
        'products': products,
        'transactions': transactions
    })

    #Standardising dates - getting rid of separator irregularities
    customers = standardize_date_columns(customers, ['signup_date'])
    transactions = standardize_date_columns(transactions, ['transaction_date'])

    # Converting to datetime for filtering
    customers['signup_date'] = pd.to_datetime(customers['signup_date'], errors='coerce')
    transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'], errors='coerce')

    # Apply date filters
    if start_date:
        customers = customers[customers['signup_date'] >= start_date]
        transactions = transactions[transactions['transaction_date'] >= start_date]

    if end_date:
        customers = customers[customers['signup_date'] <= end_date]
        transactions = transactions[transactions['transaction_date'] <= end_date]

    #Standardizing the country column in the customers dataframe
    customers['country_clean'] = (customers['country'].str.lower().str.strip().str.replace('.', '', regex=False))

    country_mapping = {
        # United States
        'us': 'United States',
        'usa': 'United States',
        'united states': 'United States',
        # United Kingdom
        'uk': 'United Kingdom',
        'united kingdom': 'United Kingdom',
        'great britain': 'United Kingdom',
        # Canada
        'ca': 'Canada',
        'canada': 'Canada',
        # Germany
        'de': 'Germany',
        'germany': 'Germany',
        # Australia
        'au': 'Australia',
        'australia': 'Australia'
    }

    customers['country_standardized'] = (customers['country_clean'].map(country_mapping).fillna(customers['country']))
    customers['country'] = customers['country_standardized']
    customers = customers.drop(columns=['country_clean', 'country_standardized'])

    # Imputating missing values for 'Price' column found in transactions dataframe. 
    # Price of the product greatly varies with the time. So, took median rather than mean.
    price_by_product = (transactions.groupby('product_id')['price'].median())
    transactions['price'] = transactions['price'].fillna(transactions['product_id'].map(price_by_product))

    # Imputating missing values for 'Status' column found in transactions dataframe.
    transactions.loc[transactions['status'].isna()]
    transactions['status_missing'] = transactions['status'].isna()
    transactions['status'] = transactions['status'].fillna('Unknown')

    # Imputating missing values for 'Email' column found in customers dataframe.
    customers['email_missing'] = customers['email'].isna()
    customers['email'] = customers['email'].fillna('unknown')

    # Handling Duplicates in the Products dataframe.
    products.drop_duplicates(subset=['product_id', 'product_name', 'category', 'cost_price'],keep='first',inplace=True)

    # Creating output folder to save clean data
    os.makedirs(clean_dir, exist_ok=True)

    # Saving the clean datasets to clean_dir folder
    customers.to_csv(f"{clean_dir}/customers.csv", index=False)
    products.to_csv(f"{clean_dir}/products.csv", index=False)
    transactions.to_csv(f"{clean_dir}/transactions.csv", index=False)

    print("Clean data moved to folder for analysis")

if __name__ == "__main__":
    main()