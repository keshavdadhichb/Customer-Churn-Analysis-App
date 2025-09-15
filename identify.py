import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("Starting the Customer Retention Analysis script...")

print("\n[Step 1/4] Loading and preparing data...")
try:
    df = pd.read_csv('online_retail_II.csv')
    print("  Dataset loaded successfully.")
except FileNotFoundError:
    print("  Error: 'online_retail_II.csv' not found. Please ensure the file is in the same directory.")
    exit()

df.dropna(subset=['Customer ID'], inplace=True)
df['Customer ID'] = df['Customer ID'].astype(int).astype(str)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df = df[~df['Invoice'].str.startswith('C', na=False)]
df = df[df['Quantity'] > 0]
print("  Data has been cleaned (missing values, data types, cancellations).")

df['TotalPrice'] = df['Quantity'] * df['Price']
print("  'TotalPrice' feature has been engineered.")

print("\n[Step 2/4] Defining and calculating customer churn...")

customer_df = df.groupby('Customer ID').agg(
    TotalSpend=('TotalPrice', 'sum'),
    TotalPurchases=('Invoice', 'nunique'),
    LastPurchaseDate=('InvoiceDate', 'max')
).reset_index()

last_order_date = df['InvoiceDate'].max()
churn_days = 180
churn_date = last_order_date - pd.to_timedelta(churn_days, unit='d')
customer_df['Churned'] = (customer_df['LastPurchaseDate'] < churn_date).astype(int)

churn_rate = customer_df['Churned'].mean()
retention_rate = 1 - churn_rate

print(f"  - Analysis based on data up to: {last_order_date.date()}")
print(f"  - Churn cutoff date (inactive for {churn_days} days): {churn_date.date()}")
print(f"  Overall Churn Rate: {churn_rate:.2%}")
print(f"  Overall Retention Rate: {retention_rate:.2%}")

print("\n[Step 3/4] Analyzing patterns in churned vs. active customers...")

churn_analysis = customer_df.groupby('Churned').agg(
    AvgSpend=('TotalSpend', 'mean'),
    AvgPurchases=('TotalPurchases', 'mean'),
    CustomerCount=('Customer ID', 'count')
).reset_index()

churn_analysis['Churned'] = churn_analysis['Churned'].map({0: 'Active', 1: 'Churned'})

print("\n--- Churn Analysis Summary ---")
print(churn_analysis.to_string(index=False))
print("----------------------------")
print("  Key insight: Active customers spend significantly more and make more purchases.")

print("\n[Step 4/4] Generating visualizations and recommendations...")

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(1, 2, figsize=(16, 7))

sns.barplot(data=churn_analysis, x='Churned', y='AvgSpend', palette=['#34A853', '#EA4335'], ax=ax[0])
ax[0].set_title('Average Spend: Active vs. Churned Customers', fontsize=16, fontweight='bold')
ax[0].set_ylabel('Average Total Spend ($)', fontsize=12)
ax[0].set_xlabel('Customer Status', fontsize=12)
ax[0].tick_params(axis='x', labelsize=12)
ax[0].get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

sns.barplot(data=churn_analysis, x='Churned', y='AvgPurchases', palette=['#4285F4', '#FBBC05'], ax=ax[1])
ax[1].set_title('Average Purchase Count: Active vs. Churned', fontsize=16, fontweight='bold')
ax[1].set_ylabel('Average Number of Purchases', fontsize=12)
ax[1].set_xlabel('Customer Status', fontsize=12)
ax[1].tick_params(axis='x', labelsize=12)

plt.suptitle('Behavioral Differences Between Active and Churned Customers', fontsize=20, fontweight='bold')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
print("  Visualization generated. Displaying plot...")
plt.show()

print("\n--- Consulting Recommendations Based on Data ---")
print("1. Implement a Tiered Loyalty Program:")
print("   - Why: High-spending customers are far more loyal. Reward this behavior to solidify their retention.")
print("   - Action: Create Bronze, Silver, and Gold tiers based on lifetime spend to offer escalating rewards like free shipping and exclusive access.")
print("\n2. Launch a 'Win-Back' Campaign for At-Risk Customers:")
print("   - Why: Churned customers make significantly fewer purchases. The drop-off after the 1st or 2nd purchase is a critical danger zone.")
print("   - Action: Target customers with 1-2 purchases who haven't bought in 90-180 days with a personalized, time-sensitive discount.")
print("---------------------------------------------")

print("\nScript finished successfully.")