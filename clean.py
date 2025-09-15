import pandas as pd

# Load the dataset
# This might take a moment as the file is large
try:
    df = pd.read_csv('online_retail_II.csv')
    print("Dataset loaded successfully!")
except FileNotFoundError:
    print("Error: 'online_retail_II.csv' not found. Make sure it's in the same folder as your script.")
    exit()

# --- Data Cleaning ---

# 1. Display initial data info
print("\nInitial Data Info:")
df.info()

# 2. Handle missing values
# A significant number of Customer IDs are missing. Transactions without a customer are not useful for our analysis.
df.dropna(subset=['Customer ID'], inplace=True)

# 3. Convert data types
# Customer ID should be treated as a string or category, not a number for calculation
df['Customer ID'] = df['Customer ID'].astype(int).astype(str)
# Convert InvoiceDate to a datetime object, which is crucial for time-based analysis
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# 4. Remove cancelled orders
# In this dataset, cancelled orders have an invoice number starting with 'C'.
df = df[~df['Invoice'].str.startswith('C', na=False)]

# 5. Remove rows with negative quantity
df = df[df['Quantity'] > 0]

# --- Feature Engineering ---

# Create a 'TotalPrice' column, which is essential for almost all calculations
df['TotalPrice'] = df['Quantity'] * df['Price']

print("\nCleaned Data Info:")
df.info()

print("\nData Preview after Cleaning:")
print(df.head())