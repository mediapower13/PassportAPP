"""
Data export utilities for PassportApp
Export data in CSV, JSON, and PDF formats
"""

import csv
import json
from datetime import datetime
import io


class DataExporter:
    """Export data in various formats"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'pdf', 'xlsx']
    
    def export_to_csv(self, data, filename=None, headers=None):
        """Export data to CSV format"""
        if not data:
            return None, 'No data to export'
        
        # Create CSV in memory
        output = io.StringIO()
        
        # Determine headers
        if headers is None:
            if isinstance(data[0], dict):
                headers = list(data[0].keys())
            else:
                headers = [f'Column_{i}' for i in range(len(data[0]))]
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        for row in data:
            if isinstance(row, dict):
                writer.writerow(row)
            else:
                writer.writerow(dict(zip(headers, row)))
        
        csv_data = output.getvalue()
        output.close()
        
        if filename:
            with open(filename, 'w', newline='') as f:
                f.write(csv_data)
        
        return csv_data, 'CSV export successful'
    
    def export_to_json(self, data, filename=None, pretty=True):
        """Export data to JSON format"""
        if not data:
            return None, 'No data to export'
        
        indent = 2 if pretty else None
        
        json_data = json.dumps(data, indent=indent, default=str)
        
        if filename:
            with open(filename, 'w') as f:
                f.write(json_data)
        
        return json_data, 'JSON export successful'
    
    def export_to_pdf(self, data, filename, title='Data Export'):
        """Export data to PDF format"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title_para = Paragraph(title, styles['Heading1'])
            elements.append(title_para)
            elements.append(Spacer(1, 12))
            
            # Add timestamp
            timestamp = Paragraph(
                f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                styles['Normal']
            )
            elements.append(timestamp)
            elements.append(Spacer(1, 12))
            
            # Prepare table data
            if isinstance(data[0], dict):
                headers = list(data[0].keys())
                table_data = [headers]
                
                for row in data:
                    table_data.append([str(row.get(h, '')) for h in headers])
            else:
                table_data = [data[0]]
                table_data.extend(data[1:])
            
            # Create table
            table = Table(table_data)
            
            # Style table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            return filename, 'PDF export successful'
        
        except ImportError:
            return None, 'PDF export requires reportlab library'
        except Exception as e:
            return None, f'PDF export failed: {str(e)}'
    
    def export_passports_to_csv(self, passports):
        """Export passports to CSV"""
        if not passports:
            return None, 'No passports to export'
        
        data = []
        
        for passport in passports:
            data.append({
                'Passport Number': passport.get('passport_number', ''),
                'First Name': passport.get('first_name', ''),
                'Last Name': passport.get('last_name', ''),
                'Date of Birth': passport.get('date_of_birth', ''),
                'Nationality': passport.get('nationality', ''),
                'Issue Date': passport.get('issue_date', ''),
                'Expiry Date': passport.get('expiry_date', ''),
                'Status': passport.get('status', '')
            })
        
        return self.export_to_csv(data)
    
    def export_transactions_to_csv(self, transactions):
        """Export transactions to CSV"""
        if not transactions:
            return None, 'No transactions to export'
        
        data = []
        
        for tx in transactions:
            data.append({
                'Transaction Hash': tx.get('hash', ''),
                'From': tx.get('from', ''),
                'To': tx.get('to', ''),
                'Value': tx.get('value', ''),
                'Gas Used': tx.get('gas_used', ''),
                'Gas Price': tx.get('gas_price', ''),
                'Block Number': tx.get('block_number', ''),
                'Timestamp': tx.get('timestamp', ''),
                'Status': tx.get('status', '')
            })
        
        return self.export_to_csv(data)
    
    def export_nfts_to_json(self, nfts):
        """Export NFTs to JSON"""
        if not nfts:
            return None, 'No NFTs to export'
        
        data = []
        
        for nft in nfts:
            data.append({
                'token_id': nft.get('token_id'),
                'owner': nft.get('owner'),
                'metadata_uri': nft.get('metadata_uri'),
                'passport_id': nft.get('passport_id'),
                'created_at': nft.get('created_at'),
                'listed': nft.get('listed', False),
                'price': nft.get('price')
            })
        
        return self.export_to_json(data)
    
    def export_analytics_report(self, analytics_data, filename):
        """Export analytics report to PDF"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph('PassportApp Analytics Report', styles['Heading1'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Summary
            summary = Paragraph(
                f"Report generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                styles['Normal']
            )
            elements.append(summary)
            elements.append(Spacer(1, 20))
            
            # User statistics
            if 'users' in analytics_data:
                elements.append(Paragraph('User Statistics', styles['Heading2']))
                user_table = Table([
                    ['Metric', 'Value'],
                    ['Total Users', analytics_data['users'].get('total', 0)],
                    ['Active Users', analytics_data['users'].get('active', 0)],
                    ['New Users (30d)', analytics_data['users'].get('new_30d', 0)]
                ])
                user_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(user_table)
                elements.append(Spacer(1, 20))
            
            # Transaction statistics
            if 'transactions' in analytics_data:
                elements.append(Paragraph('Transaction Statistics', styles['Heading2']))
                tx_table = Table([
                    ['Metric', 'Value'],
                    ['Total Transactions', analytics_data['transactions'].get('total', 0)],
                    ['Total Volume (ETH)', analytics_data['transactions'].get('volume_eth', 0)],
                    ['Average Gas Used', analytics_data['transactions'].get('avg_gas', 0)]
                ])
                tx_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(tx_table)
                elements.append(Spacer(1, 20))
            
            doc.build(elements)
            
            return filename, 'Analytics report exported successfully'
        
        except Exception as e:
            return None, f'Report export failed: {str(e)}'


# Global data exporter
data_exporter = DataExporter()


def export_data(data, format='csv', filename=None, **kwargs):
    """Export data in specified format"""
    if format == 'csv':
        return data_exporter.export_to_csv(data, filename, kwargs.get('headers'))
    elif format == 'json':
        return data_exporter.export_to_json(data, filename, kwargs.get('pretty', True))
    elif format == 'pdf':
        return data_exporter.export_to_pdf(data, filename, kwargs.get('title', 'Data Export'))
    else:
        return None, f'Unsupported format: {format}'


def create_export_archive(exports, archive_name='exports.zip'):
    """Create ZIP archive with multiple exports"""
    import zipfile
    import os
    
    try:
        with zipfile.ZipFile(archive_name, 'w') as zipf:
            for filename in exports:
                if os.path.exists(filename):
                    zipf.write(filename, os.path.basename(filename))
        
        return archive_name, 'Archive created successfully'
    
    except Exception as e:
        return None, f'Archive creation failed: {str(e)}'


class ReportGenerator:
    """Generate various reports"""
    
    @staticmethod
    def generate_user_report(users):
        """Generate user activity report"""
        report = {
            'total_users': len(users),
            'users_by_status': {},
            'users_by_month': {},
            'top_active_users': []
        }
        
        for user in users:
            # Count by status
            status = user.get('status', 'unknown')
            report['users_by_status'][status] = report['users_by_status'].get(status, 0) + 1
        
        return report
    
    @staticmethod
    def generate_transaction_report(transactions):
        """Generate transaction report"""
        report = {
            'total_transactions': len(transactions),
            'total_volume': 0,
            'avg_gas_price': 0,
            'transactions_by_type': {}
        }
        
        if transactions:
            total_volume = sum(float(tx.get('value', 0)) for tx in transactions)
            total_gas = sum(int(tx.get('gas_price', 0)) for tx in transactions)
            
            report['total_volume'] = total_volume
            report['avg_gas_price'] = total_gas / len(transactions) if transactions else 0
            
            for tx in transactions:
                tx_type = tx.get('type', 'unknown')
                report['transactions_by_type'][tx_type] = \
                    report['transactions_by_type'].get(tx_type, 0) + 1
        
        return report
    
    @staticmethod
    def generate_nft_report(nfts):
        """Generate NFT report"""
        report = {
            'total_nfts': len(nfts),
            'nfts_listed': 0,
            'total_value': 0,
            'nfts_by_status': {}
        }
        
        for nft in nfts:
            if nft.get('listed'):
                report['nfts_listed'] += 1
                report['total_value'] += float(nft.get('price', 0))
        
        return report


# Global report generator
report_generator = ReportGenerator()
