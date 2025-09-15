import streamlit as st
import pandas as pd

# --- This function contains your core analysis logic ---
def analyze_customer_data(df):
    # --- 1. Data Cleaning & Preparation ---
    # A more robust app would include more error handling here.
    df.dropna(subset=['Customer ID'], inplace=True)
    df['Customer ID'] = df['Customer ID'].astype(int).astype(str)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df = df[~df['Invoice'].str.startswith('C', na=False)]
    df = df[df['Quantity'] > 0]
    df['TotalPrice'] = df['Quantity'] * df['Price']

    # --- 2. Churn Calculation ---
    customer_df = df.groupby('Customer ID').agg(
        TotalSpend=('TotalPrice', 'sum'),
        TotalPurchases=('Invoice', 'nunique'),
        LastPurchaseDate=('InvoiceDate', 'max')
    ).reset_index()

    last_order_date = df['InvoiceDate'].max()
    churn_date = last_order_date - pd.to_timedelta(180, unit='d')
    customer_df['Churned'] = (customer_df['LastPurchaseDate'] < churn_date).astype(int)
    churn_rate = customer_df['Churned'].mean()

    # --- 3. Churn Analysis ---
    churn_analysis = customer_df.groupby('Churned').agg(
        AvgSpend=('TotalSpend', 'mean'),
        AvgPurchases=('TotalPurchases', 'mean'),
        CustomerCount=('Customer ID', 'count')
    ).reset_index()
    churn_analysis['Churned'] = churn_analysis['Churned'].map({0: 'Active', 1: 'Churned'})

    # --- 4. Prepare DataFrame for Visualization ---
    plot_df = churn_analysis.set_index('Churned')
    
    # The function will now return the churn rate, the analysis dataframe, and the plot dataframe
    return churn_rate, churn_analysis, plot_df

# --- The Streamlit App UI ---
st.set_page_config(layout="wide")
st.title("🛒 Customer Churn Analysis App")

st.write("Upload your e-commerce transaction data (CSV file) to analyze customer churn.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    with st.spinner('Analyzing data... This may take a moment.'):
        # Load the data
        try:
            input_df = pd.read_csv(uploaded_file)

            # Run the analysis function
            rate, analysis_df, plot_data = analyze_customer_data(input_df)

            # Display the results
            st.success("Analysis Complete!")

            st.header("📊 Key Metrics")
            col1, col2 = st.columns(2)
            col1.metric("Overall Churn Rate", f"{rate:.2%}")
            col2.metric("Overall Retention Rate", f"{1-rate:.2%}")

            st.header("📈 Analysis & Visualization")

            col1_viz, col2_viz = st.columns(2)
            with col1_viz:
                st.write("Average Spend (Active vs. Churned):")
                st.bar_chart(plot_data['AvgSpend'])

            with col2_viz:
                st.write("Average Purchases (Active vs. Churned):")
                st.bar_chart(plot_data['AvgPurchases'])
            
            st.write("Analysis Data Table:")
            st.dataframe(analysis_df)

        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            st.warning("Please ensure your CSV has the columns: 'Customer ID', 'InvoiceDate', 'Invoice', 'Quantity', and 'Price'.")