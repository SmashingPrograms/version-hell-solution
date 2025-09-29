"""
Report generation in various formats
"""

import json
import csv
import io
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates analytics reports in various formats"""
    
    def generate(self, report_type: str, data: Dict, format: str = 'json') -> Dict:
        """
        Generate report based on type and format
        
        Args:
            report_type: Type of report ('summary', 'detailed', 'executive')
            data: Data to include in report
            format: Output format ('json', 'csv')
        
        Returns:
            Generated report
        """
        report_methods = {
            'summary': self._generate_summary_report,
            'detailed': self._generate_detailed_report,
            'executive': self._generate_executive_report
        }
        
        generator = report_methods.get(report_type, self._generate_summary_report)
        report_data = generator(data)
        
        if format == 'csv':
            return self._convert_to_csv(report_data)
        
        return report_data
    
    def _generate_summary_report(self, data: Dict) -> Dict:
        """Generate summary-level report"""
        from datetime import datetime
        
        return {
            'report_type': 'summary',
            'generated_at': datetime.utcnow().isoformat(),
            'summary': {
                'total_revenue': data.get('total_revenue', 0),
                'transaction_count': data.get('transaction_count', 0),
                'average_transaction': data.get('average_transaction', 0),
                'period': data.get('period', 'N/A')
            },
            'data': data
        }
    
    def _generate_detailed_report(self, data: Dict) -> Dict:
        """Generate detailed report with breakdowns"""
        from datetime import datetime
        
        return {
            'report_type': 'detailed',
            'generated_at': datetime.utcnow().isoformat(),
            'executive_summary': self._create_executive_summary(data),
            'detailed_metrics': data,
            'recommendations': self._generate_recommendations(data)
        }
    
    def _generate_executive_report(self, data: Dict) -> Dict:
        """Generate executive-level report"""
        from datetime import datetime
        
        return {
            'report_type': 'executive',
            'generated_at': datetime.utcnow().isoformat(),
            'key_insights': self._extract_key_insights(data),
            'recommendations': self._generate_recommendations(data),
            'action_items': self._generate_action_items(data)
        }
    
    def _create_executive_summary(self, data: Dict) -> Dict:
        """Create executive summary from data"""
        return {
            'total_revenue': data.get('total_revenue', 0),
            'growth_rate': data.get('growth_rate', 0),
            'top_performing_products': data.get('top_products', [])[:5],
            'areas_of_concern': self._identify_concerns(data)
        }
    
    def _extract_key_insights(self, data: Dict) -> List[str]:
        """Extract key insights from data"""
        insights = []
        
        # Revenue insights
        total_revenue = data.get('total_revenue', 0)
        if total_revenue > 1000000:
            insights.append(f"Strong revenue performance: ${total_revenue:,.2f}")
        
        # Growth insights
        growth_rate = data.get('growth_rate')
        if growth_rate and growth_rate > 10:
            insights.append(f"Positive growth trend: {growth_rate:.1f}% increase")
        elif growth_rate and growth_rate < -5:
            insights.append(f"Concerning decline: {abs(growth_rate):.1f}% decrease")
        
        # Customer insights
        customer_count = data.get('customer_count', 0)
        if customer_count > 0:
            insights.append(f"Active customer base: {customer_count:,} customers")
        
        return insights
    
    def _generate_recommendations(self, data: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for declining metrics
        growth_rate = data.get('growth_rate', 0)
        if growth_rate < 0:
            recommendations.append("Investigate cause of revenue decline and implement corrective measures")
        
        # Check for high-performing products
        top_products = data.get('top_products', [])
        if top_products:
            recommendations.append("Increase inventory and marketing for top-performing products")
        
        # Check for customer segments
        if data.get('at_risk_customers', 0) > 0:
            recommendations.append("Implement re-engagement campaign for at-risk customers")
        
        return recommendations
    
    def _generate_action_items(self, data: Dict) -> List[Dict]:
        """Generate specific action items"""
        actions = []
        
        if data.get('low_stock_items'):
            actions.append({
                'priority': 'high',
                'action': 'Restock low inventory items',
                'deadline': '7 days',
                'owner': 'Inventory Manager'
            })
        
        if data.get('growth_rate', 0) < -5:
            actions.append({
                'priority': 'critical',
                'action': 'Revenue recovery plan',
                'deadline': '3 days',
                'owner': 'Sales Director'
            })
        
        return actions
    
    def _identify_concerns(self, data: Dict) -> List[str]:
        """Identify areas of concern"""
        concerns = []
        
        if data.get('return_rate', 0) > 10:
            concerns.append("High product return rate")
        
        if data.get('growth_rate', 0) < -5:
            concerns.append("Negative revenue growth")
        
        if data.get('customer_churn', 0) > 15:
            concerns.append("Elevated customer churn rate")
        
        return concerns
    
    def _convert_to_csv(self, data: Dict) -> str:
        """Convert report data to CSV format"""
        output = io.StringIO()
        
        # Flatten nested data for CSV
        flattened_data = self._flatten_dict(data)
        
        if flattened_data:
            writer = csv.DictWriter(output, fieldnames=flattened_data[0].keys())
            writer.writeheader()
            writer.writerows(flattened_data)
        
        return output.getvalue()
    
    def _flatten_dict(self, data: Dict, parent_key: str = '') -> List[Dict]:
        """Flatten nested dictionary for CSV export"""
        items = []
        
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, new_key))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                for item in value:
                    items.append(self._flatten_dict(item, new_key)[0] if isinstance(item, dict) else {new_key: item})
            else:
                items.append({new_key: value})
        
        return items if items else [data]
