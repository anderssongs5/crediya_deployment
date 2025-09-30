import boto3
import json
from datetime import datetime
from decimal import Decimal

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')

    daily_table = dynamodb.Table('daily-loan-summaries')
    global_table = dynamodb.Table('global-summary-report')

    try:
        global_response = global_table.get_item(
            Key={'PK': 'LOAN_STATUS#APPROVED'}
        )

        current_date = datetime.now().strftime('%Y-%m-%d')
        daily_response = daily_table.get_item(
            Key={'PK': f'DATE#{current_date}'}
        )

        global_summary = global_response.get('Item', {})
        daily_summary = daily_response.get('Item', {})

        report_data = {
            'date': current_date,
            'global': {
                'total_count': int(global_summary.get('totalCount', 0)),
                'total_amount': float(global_summary.get('totalAmount', 0))
            },
            'daily': {
                'total_count': int(daily_summary.get('totalCount', 0)),
                'total_amount': float(daily_summary.get('totalAmount', 0))
            }
        }

        send_report_email(report_data)

        return {
            'statusCode': 200,
            'body': json.dumps('Daily report send successfully.')
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def send_report_email(data):
    ses = boto3.client('ses')

    email_body = f"""
        Daily Approved Loan Report - {data['date']}

        Global Summary:
        - Total loans: {data['global']['total_count']}
        - Total amount: ${data['global']['total_amount']:,.2f}

        Daily Summary:
        - Loans for the day: {data['daily']['total_count']}
        - Amount for the day: ${data['daily']['total_amount']:,.2f}
    """

    ses.send_email(
        Source='anderssongarciasotelo@gmail.com',
        Destination={'ToAddresses': ['anderssongarciasotelo@gmail.com']},
        Message={
            'Subject': {'Data': f'Daily Approved Loan Report - {data["date"]}'},
            'Body': {'Text': {'Data': email_body}}
        }
    )