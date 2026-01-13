import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def main(clean_dir="data_clean", reports_dir="reports", plots_dir="plots", start_date=None, end_date=None):

     # Parse date filters safely
    if start_date:
        start_date = pd.to_datetime(start_date)
    if end_date:
        end_date = pd.to_datetime(end_date)

    customers = pd.read_csv(f"{clean_dir}/customers.csv")
    products = pd.read_csv(f"{clean_dir}/products.csv")
    transactions = pd.read_csv(f"{clean_dir}/transactions.csv")

    #to store reports and plots after analysis
    report_tables = {}
    plots_to_save = []

    #Merging transactions and products dataframes to get an unified dataframe for analysis
    txn_prod = transactions.merge(products, on='product_id', how='left')

    # Standardize datetime
    txn_prod['transaction_date'] = pd.to_datetime(txn_prod['transaction_date'])

    # Apply date filtering
    if start_date:
        txn_prod = txn_prod[txn_prod['transaction_date'] >= start_date]
    if end_date:
        txn_prod = txn_prod[txn_prod['transaction_date'] <= end_date]

    #Time-based Revenue Trends
    txn_prod['month'] = txn_prod['transaction_date'].dt.to_period('M')
    txn_prod['cost_amount'] = txn_prod['cost_price'] * txn_prod['quantity']
    txn_prod['selling_amount'] = txn_prod['price'] * txn_prod['quantity']
    txn_prod['profit'] = txn_prod['selling_amount'] - txn_prod['cost_amount']
    txn_prod['profit_pct'] = (txn_prod['profit'] / txn_prod['cost_amount']) * 100

    monthly_trends = (txn_prod.groupby('month').agg(
            total_cost=('cost_amount', 'sum'),
            total_revenue=('selling_amount', 'sum'),
            total_profit=('profit', 'sum')).reset_index())

    monthly_trends['profit_pct'] = (monthly_trends['total_profit'] / monthly_trends['total_cost']) * 100
    monthly_trends['revenue_growth_pct'] = monthly_trends['total_revenue'].pct_change() * 100

    report_tables['monthly_trends'] = monthly_trends

    #Plot for time-based revenue trends
    def plot_monthly_financials_with_profit_pct(monthly_trends):
        x = range(len(monthly_trends))  # Use numeric index instead of string
        x_labels = monthly_trends['month'].astype(str)  # Keep labels as strings
        fig, ax1 = plt.subplots(figsize=(9, 5))
        
        # Left axis: amounts
        ax1.plot(x, monthly_trends['total_cost'], label='Total Cost')
        ax1.plot(x, monthly_trends['total_revenue'], label='Total Revenue')
        ax1.plot(x, monthly_trends['total_profit'], label='Total Profit')
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Amount")
        ax1.set_xticks(x)
        ax1.set_xticklabels(x_labels, rotation=45)
        
        # Right axis: profit % and revenue growth %
        ax2 = ax1.twinx()
        ax2.plot(x, monthly_trends['profit_pct'], linestyle='--', marker='o', label='Profit %')
        ax2.plot(x, monthly_trends['revenue_growth_pct'], linestyle='--', marker='s', label='Revenue Growth %')
        ax2.axhline(0, linestyle=':', color='gray', alpha=0.5)
        ax2.set_ylabel("Percentage (%)")
        
        # Legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')
        
        plt.title("Monthly Cost, Revenue, Profit, Profit % and Revenue Growth Trend")
        plt.tight_layout()
    
    plots_to_save.append(("monthly_financial_trends",lambda: plot_monthly_financials_with_profit_pct(monthly_trends)))

    #Product Performance Analysis
    product_metrics = (txn_prod.groupby('product_id')
        .agg(
            total_cost=('cost_amount', 'sum'),
            total_revenue=('selling_amount', 'sum'),
            total_profit=('profit', 'sum')
        ).reset_index())
    product_metrics['profit_pct'] = (product_metrics['total_profit'] /product_metrics['total_cost']) * 100

    report_tables['product_metrics'] = product_metrics

    #Plot for Product Metrics - top 10 products
    def plot_product_profit_pct(product_metrics, top_n=10):
        top_products = product_metrics.sort_values('total_revenue', ascending=False).head(top_n)

        plt.figure(figsize=(9, 5))
        x = range(len(top_products))
        x_labels = top_products['product_id'].astype(str)
        
        plt.bar(x, top_products['profit_pct'])
        plt.xticks(x, x_labels, rotation=45)
        
        plt.xlabel("Product ID")
        plt.ylabel("Profit %")
        plt.title(f"Top {top_n} Products by Revenue - Profit %")
        plt.tight_layout()

    plots_to_save.append(("product_performance_analysis",lambda: plot_product_profit_pct(product_metrics))) 

    #Category Performance Analysis
    category_metrics = (txn_prod.groupby('category')
        .agg(
            total_cost=('cost_amount', 'sum'),
            total_revenue=('selling_amount', 'sum'),
            total_profit=('profit', 'sum')
        ).reset_index())
    category_metrics['profit_pct'] = (category_metrics['total_profit'] / category_metrics['total_cost']) * 100

    report_tables['category_metrics'] = category_metrics

    #Plot for Category metrics
    def plot_category_financials(category_metrics):
        x_pos = range(len(category_metrics))  # Numeric positions
        x_labels = category_metrics['category']  # String labels
        width = 0.35

        fig, ax1 = plt.subplots(figsize=(9, 5))

        ax1.bar([p - width/2 for p in x_pos], category_metrics['total_revenue'], width=width, label='Revenue', alpha=0.7)
        ax1.bar([p + width/2 for p in x_pos], category_metrics['total_cost'], width=width, label='Cost', alpha=0.7)
        ax1.set_ylabel("Amount")
        ax1.set_xlabel("Category")
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(x_labels, rotation=45)

        ax2 = ax1.twinx()
        ax2.plot(x_pos, category_metrics['profit_pct'], marker='o', linestyle='--', label='Profit %')
        ax2.set_ylabel("Profit %")

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')

        plt.title("Category-wise Cost, Revenue and Profit %")
        plt.tight_layout()

    plots_to_save.append(("category_performance_analysis", lambda: plot_category_financials(category_metrics)))

    #=======================
    # KPIs
    #=======================

    #Average Order Value (AOV)
    monthly_aov = (txn_prod.groupby('month')
        .agg(
            total_revenue=('selling_amount', 'sum'),
            total_transactions=('transaction_id', 'nunique')
        ).reset_index())
    monthly_aov['aov'] = monthly_aov['total_revenue'] / monthly_aov['total_transactions']

    report_tables['monthly_aov'] = monthly_aov

    #Plot for AOV
    def plot_monthly_aov(monthly_aov):
        x = range(len(monthly_aov))  # Use numeric index
        x_labels = monthly_aov['month'].astype(str)  # Keep labels as strings
        
        plt.figure(figsize=(9, 5))
        plt.plot(x, monthly_aov['aov'], marker='o')
        plt.xticks(x, x_labels, rotation=45)
        plt.xlabel("Month")
        plt.ylabel("Average Order Value (AOV)")
        plt.title("Monthly Average Order Value (AOV) Trend")
        plt.tight_layout()

    plots_to_save.append(("monthly_aov",lambda: plot_monthly_aov(monthly_aov)))

    #Customer Purchase Behaviour
    customer_behavior = (txn_prod.groupby('customer_id')
        .agg(
            total_transactions=('transaction_id', 'nunique'),
            total_quantity=('quantity', 'sum'),
            total_revenue=('selling_amount', 'sum'),
            avg_order_value=('selling_amount', 'mean'),
            first_purchase=('transaction_date', 'min'),
            last_purchase=('transaction_date', 'max')
        ).reset_index().sort_values('total_revenue', ascending=False))

    customer_behavior['value_segment'] = pd.qcut(customer_behavior['total_revenue'], q=3, labels=['Low', 'Medium', 'High'], duplicates='drop')

    report_tables['customer_behavior'] = customer_behavior
    report_tables['top_10_customers'] = customer_behavior.head(10)

    segment_summary = (customer_behavior.groupby('value_segment', observed=True)
        .agg(
            num_customers=('customer_id', 'count'),
            total_revenue=('total_revenue', 'sum'),
            avg_revenue_per_customer=('total_revenue', 'mean')
        ).reset_index())

    segment_summary['revenue_pct'] = (segment_summary['total_revenue'] / segment_summary['total_revenue'].sum()) * 100

    report_tables['segment_summary'] = segment_summary

    #Active Customers Summary
    ref_date = txn_prod['transaction_date'].max()

    def active_customers_last_n_months(df, n_months, ref_date):
        cutoff_date = ref_date - pd.DateOffset(months=n_months)
        return df.loc[df['transaction_date'] >= cutoff_date, 'customer_id'].nunique()

    period_months = [15, 12, 9, 6, 3]
    active_customers_summary = pd.DataFrame({
        'period_months': period_months,
        'active_customers': [active_customers_last_n_months(txn_prod, n, ref_date) for n in period_months]
    })

    report_tables['active_customers_summary'] = active_customers_summary

    #Plot for Active Customers Summary
    def plot_active_customers_windows(active_customers_summary):
        plt.figure(figsize=(8, 5))
        plt.plot(active_customers_summary['period_months'],active_customers_summary['active_customers'],marker='o')
        plt.gca().invert_xaxis()  # 15 → 3 months (time narrowing)
        plt.xlabel("Time Window (Months)")
        plt.ylabel("Active Customers")
        plt.title("Active Customers Across Time Windows")
        plt.tight_layout()

    plots_to_save.append(("active_customers_summary",lambda: plot_active_customers_windows(active_customers_summary)))

    #Repeat Customer Summary
    def repeat_customer_rate_last_n_months(df, n_months, ref_date):
        cutoff_date = ref_date - pd.DateOffset(months=n_months)
        txn_window = df[df['transaction_date'] >= cutoff_date]
        customer_txns = (txn_window.groupby('customer_id')['transaction_id'].nunique())
        active_customers = customer_txns.count()
        repeat_customers = (customer_txns > 1).sum()
        return (repeat_customers / active_customers) * 100

    repeat_customer_summary = pd.DataFrame({
        'period_months': period_months,
        'repeat_customer_rate_pct': [
            repeat_customer_rate_last_n_months(txn_prod, 15, ref_date),
            repeat_customer_rate_last_n_months(txn_prod, 12, ref_date),
            repeat_customer_rate_last_n_months(txn_prod, 9, ref_date),
            repeat_customer_rate_last_n_months(txn_prod, 6, ref_date),
            repeat_customer_rate_last_n_months(txn_prod, 3, ref_date)
        ]})

    report_tables['repeat_customer_summary'] = repeat_customer_summary

    #Plot for Repeat Customer Summary
    def plot_repeat_customer_rate(repeat_customer_summary):
        plt.figure(figsize=(8, 5))
        plt.plot(
            repeat_customer_summary['period_months'],
            repeat_customer_summary['repeat_customer_rate_pct'],
            marker='o'
        )
        plt.gca().invert_xaxis()
        plt.xlabel("Time Window (Months)")
        plt.ylabel("Repeat Customer Rate (%)")
        plt.title("Repeat Customer Rate Across Time Windows")
        plt.tight_layout()

    plots_to_save.append(("Repeat Customers Summary",lambda: plot_repeat_customer_rate(repeat_customer_summary)))

    #Customer Demographics Analysis
    customers['signup_date'] = pd.to_datetime(customers['signup_date'])
    customer_country_summary = (customers.groupby('country')
    .agg(customer_count=('customer_id', 'count'))
    .reset_index()
    .sort_values('customer_count', ascending=False))

    report_tables['customer_country_summary'] = customer_country_summary

    #Plot for Customer Demographics
    def plot_customer_demographics(customer_country_summary):
        plt.figure(figsize=(9, 5))
        plt.barh(customer_country_summary['country'], customer_country_summary['customer_count'])
        plt.xlabel("Customer Count")
        plt.ylabel("Country")
        plt.title("Customer Count by Country")
        plt.gca().invert_yaxis()
        plt.tight_layout()

    plots_to_save.append(("customer_demographics", lambda: plot_customer_demographics(customer_country_summary)))

    # Create output folders
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    # Save all report tables
    for name, df in report_tables.items():
        df.to_csv(f"{reports_dir}/{name}.csv", index=False)

    # Save all plots
    for filename, plot_fn in plots_to_save:
        plot_fn()
        plt.savefig(f"{plots_dir}/{filename}.png")
        plt.close()

    print("Analysis is completed. Files and Plots moved to folders")

if __name__ == "__main__":
    main()