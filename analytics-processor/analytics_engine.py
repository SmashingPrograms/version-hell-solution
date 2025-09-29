// analytics-processor/analytics_engine.py
"""
Core analytics processing engine with pandas operations
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Processes analytics data using pandas"""
    
    def generate_sales_summary(self, transactions: List[Dict]) -> Dict:
        """
        Generate summary statistics from transaction data
        
        Args:
            transactions: List of transaction dictionaries
        
        Returns:
            Summary statistics dictionary
        """
        if not transactions:
            return {
                'error': 'No transaction data provided',
                'total_transactions': 0
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Ensure required columns exist
        required_columns = ['amount', 'timestamp']
        if not all(col in df.columns for col in required_columns):
            return {'error': 'Missing required columns in transaction data'}
        
        # Convert types
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Calculate summary statistics
        summary = {
            'total_transactions': len(df),
            'total_revenue': float(df['amount'].sum()),
            'average_transaction': float(df['amount'].mean()),
            'median_transaction': float(df['amount'].median()),
            'min_transaction': float(df['amount'].min()),
            'max_transaction': float(df['amount'].max()),
            'std_deviation': float(df['amount'].std()),
            'date_range': {
                'start': df['timestamp'].min().isoformat() if not df['timestamp'].isna().all() else None,
                'end': df['timestamp'].max().isoformat() if not df['timestamp'].isna().all() else None
            }
        }
        
        # Add percentile data
        percentiles = df['amount'].quantile([0.25, 0.5, 0.75, 0.90, 0.95, 0.99])
        summary['percentiles'] = {
            'p25': float(percentiles[0.25]),
            'p50': float(percentiles[0.50]),
            'p75': float(percentiles[0.75]),
            'p90': float(percentiles[0.90]),
            'p95': float(percentiles[0.95]),
            'p99': float(percentiles[0.99])
        }
        
        logger.info(f"Generated sales summary for {len(df)} transactions")
        
        return summary
    
    def time_series_analysis(self, transactions: List[Dict], period: str) -> Dict:
        """
        Perform time series analysis on transaction data
        
        Args:
            transactions: List of transaction dictionaries
            period: Aggregation period ('daily', 'weekly', 'monthly')
        
        Returns:
            Time series analysis results
        """
        if not transactions:
            return {'error': 'No transaction data provided'}
        
        df = pd.DataFrame(transactions)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Drop rows with invalid data
        df = df.dropna(subset=['amount', 'timestamp'])
        
        if df.empty:
            return {'error': 'No valid data after cleaning'}
        
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        
        # Resample based on period
        freq_map = {
            'daily': 'D',
            'weekly': 'W',
            'monthly': 'M',
            'hourly': 'H'
        }
        
        freq = freq_map.get(period, 'D')
        
        # Aggregate by period
        resampled = df['amount'].resample(freq).agg(['sum', 'count', 'mean'])
        
        # Calculate growth rates
        resampled['growth_rate'] = resampled['sum'].pct_change() * 100
        
        # Convert to list of dictionaries
        time_series_data = []
        for timestamp, row in resampled.iterrows():
            time_series_data.append({
                'period': timestamp.isoformat(),
                'total_revenue': float(row['sum']),
                'transaction_count': int(row['count']),
                'average_transaction': float(row['mean']),
                'growth_rate': float(row['growth_rate']) if not np.isnan(row['growth_rate']) else None
            })
        
        # Calculate trend
        if len(resampled) >= 2:
            trend = 'increasing' if resampled['sum'].iloc[-1] > resampled['sum'].iloc[0] else 'decreasing'
        else:
            trend = 'insufficient_data'
        
        return {
            'period': period,
            'data_points': len(time_series_data),
            'trend': trend,
            'time_series': time_series_data,
            'total_revenue_all_periods': float(resampled['sum'].sum()),
            'average_period_revenue': float(resampled['sum'].mean())
        }
    
    def segment_customers(self, customers: List[Dict]) -> Dict:
        """
        Segment customers based on RFM (Recency, Frequency, Monetary) analysis
        
        Args:
            customers: List of customer dictionaries with purchase history
        
        Returns:
            Customer segmentation results
        """
        if not customers:
            return {'error': 'No customer data provided'}
        
        df = pd.DataFrame(customers)
        
        # Calculate RFM metrics
        current_date = datetime.now()
        
        # Recency: days since last purchase
        if 'last_purchase_date' in df.columns:
            df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'], errors='coerce')
            df['recency'] = (current_date - df['last_purchase_date']).dt.days
        else:
            df['recency'] = 0
        
        # Frequency: number of purchases
        df['frequency'] = df.get('purchase_count', 0)
        
        # Monetary: total spend
        df['monetary'] = pd.to_numeric(df.get('total_spend', 0), errors='coerce')
        
        # Calculate quartiles for segmentation
        df['r_quartile'] = pd.qcut(df['recency'], q=4, labels=['4', '3', '2', '1'], duplicates='drop')
        df['f_quartile'] = pd.qcut(df['frequency'], q=4, labels=['1', '2', '3', '4'], duplicates='drop')
        df['m_quartile'] = pd.qcut(df['monetary'], q=4, labels=['1', '2', '3', '4'], duplicates='drop')
        
        # Create RFM score
        df['rfm_score'] = df['r_quartile'].astype(str) + df['f_quartile'].astype(str) + df['m_quartile'].astype(str)
        
        # Define segments
        def segment_customer(row):
            score = int(row['r_quartile']) + int(row['f_quartile']) + int(row['m_quartile'])
            
            if score >= 10:
                return 'Champions'
            elif score >= 8:
                return 'Loyal'
            elif score >= 6:
                return 'Potential'
            elif score >= 4:
                return 'At Risk'
            else:
                return 'Lost'
        
        df['segment'] = df.apply(segment_customer, axis=1)
        
        # Generate segment summary
        segment_summary = []
        for segment_name in df['segment'].unique():
            segment_df = df[df['segment'] == segment_name]
            
            segment_summary.append({
                'segment': segment_name,
                'customer_count': len(segment_df),
                'avg_recency': float(segment_df['recency'].mean()),
                'avg_frequency': float(segment_df['frequency'].mean()),
                'avg_monetary': float(segment_df['monetary'].mean()),
                'total_revenue': float(segment_df['monetary'].sum()),
                'percentage_of_customers': float(len(segment_df) / len(df) * 100)
            })
        
        return {
            'total_customers': len(df),
            'segments': segment_summary,
            'segmentation_date': current_date.isoformat()
        }
    
    def analyze_product_performance(self, products: List[Dict]) -> Dict:
        """
        Analyze product performance metrics
        
        Args:
            products: List of product dictionaries with sales data
        
        Returns:
            Product performance analysis
        """
        if not products:
            return {'error': 'No product data provided'}
        
        df = pd.DataFrame(products)
        
        # Ensure numeric columns
        numeric_columns = ['units_sold', 'revenue', 'returns', 'profit_margin']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate performance metrics
        df['return_rate'] = (df.get('returns', 0) / df.get('units_sold', 1) * 100).fillna(0)
        df['revenue_per_unit'] = (df.get('revenue', 0) / df.get('units_sold', 1)).fillna(0)
        
        # Rank products
        df['revenue_rank'] = df['revenue'].rank(ascending=False)
        df['units_rank'] = df['units_sold'].rank(ascending=False)
        
        # Identify top performers
        top_revenue = df.nlargest(10, 'revenue')
        top_units = df.nlargest(10, 'units_sold')
        
        # Calculate category performance if available
        category_performance = {}
        if 'category' in df.columns:
            category_agg = df.groupby('category').agg({
                'revenue': 'sum',
                'units_sold': 'sum',
                'returns': 'sum'
            }).reset_index()
            
            category_performance = category_agg.to_dict('records')
        
        return {
            'total_products': len(df),
            'total_revenue': float(df['revenue'].sum()) if 'revenue' in df.columns else 0,
            'total_units_sold': int(df['units_sold'].sum()) if 'units_sold' in df.columns else 0,
            'average_revenue_per_product': float(df['revenue'].mean()) if 'revenue' in df.columns else 0,
            'top_products_by_revenue': top_revenue[['product_id', 'product_name', 'revenue', 'units_sold']].to_dict('records')[:10] if 'product_id' in df.columns else [],
            'top_products_by_units': top_units[['product_id', 'product_name', 'revenue', 'units_sold']].to_dict('records')[:10] if 'product_id' in df.columns else [],
            'category_performance': category_performance
        }
