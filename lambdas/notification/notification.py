import json
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo

def lambda_handler(event, context):
    sesClient = boto3.client('ses', region_name='us-east-1')

    print('Starting notification process')
    print(f"Event: {event}")

    for record in event['Records']:
        raw_body = record['body']
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

        message_html = build_html_message(body)
        user_email = body['user']['email']

        print(f"Sending email to {user_email}")

        sesClient.send_email(
            Source='anderssongarciasotelo@gmail.com',
            Destination={
                'ToAddresses': [user_email]
            },
            Message={
                'Subject': {
                    'Data': 'Loan Request - Status Changed!'
                },
                'Body': {
                    'Html': {
                        'Data': message_html,
                        'Charset': 'UTF-8'
                    },
                    'Text': {
                        'Data': f"Your loan request with ID {body['loanRequest']['id']} has been {body['loanRequest']['status']['name']}."
                    }
                }
            }
        )

    return {
        'statusCode': 200,
        'body': 'Emails sent successfully'
    }


def build_html_message(body):
    loan_request = body['loanRequest']
    user = body['user']
    payment_plan = body.get('paymentPlan', [])
    status_name = loan_request['status']['name'].upper()

    colombia_time = datetime.now(ZoneInfo("America/Bogota"))
    formatted_time = colombia_time.strftime('%B %d, %Y at %I:%M %p')

    payment_plan_html = ""
    if payment_plan and status_name == 'APPROVED':
        payment_plan_html = build_payment_plan_table(payment_plan)

    return f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f0f4f8;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        max-width: 700px;
                        margin: auto;
                    }}
                    .header {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #2c3e50;
                        margin-bottom: 20px;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                    }}
                    .content {{
                        font-size: 16px;
                        color: #34495e;
                        line-height: 1.6;
                    }}
                    .username {{
                        display: inline-block;
                        background-color: #3498db;
                        color: #ffffff;
                        padding: 6px 12px;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 16px;
                    }}
                    .highlight {{
                        color: #e74c3c;
                        font-weight: bold;
                    }}
                    .approved {{
                        color: #27ae60;
                        font-weight: bold;
                    }}
                    .timestamp {{
                        font-size: 14px;
                        color: #7f8c8d;
                        margin-top: 10px;
                    }}
                    .footer {{
                        margin-top: 30px;
                        font-size: 14px;
                        color: #7f8c8d;
                        text-align: center;
                    }}
                    .payment-plan {{
                        margin-top: 25px;
                        border: 1px solid #bdc3c7;
                        border-radius: 8px;
                        overflow: hidden;
                    }}
                    .payment-plan-header {{
                        background-color: #27ae60;
                        color: white;
                        padding: 15px;
                        font-size: 18px;
                        font-weight: bold;
                        text-align: center;
                    }}
                    .payment-table {{
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 14px;
                    }}
                    .payment-table th {{
                        background-color: #ecf0f1;
                        color: #2c3e50;
                        padding: 12px 8px;
                        text-align: center;
                        font-weight: bold;
                        border-bottom: 1px solid #bdc3c7;
                    }}
                    .payment-table td {{
                        padding: 10px 8px;
                        text-align: center;
                        border-bottom: 1px solid #ecf0f1;
                    }}
                    .payment-table tr:nth-child(even) {{
                        background-color: #f8f9fa;
                    }}
                    .payment-table tr:hover {{
                        background-color: #e8f4fd;
                    }}
                    .currency {{
                        font-weight: bold;
                        color: #27ae60;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">Loan Request Updated</div>
                    <div class="content">
                        Hello <span class="username">{user['name']}</span>,<br><br>
                        We wanted to let you know that your loan request with ID 
                        <span class="highlight">{loan_request['id']}</span> 
                        (<b>{loan_request['loanType']['name']}</b>) has been 
                        <span class="{'approved' if status_name == 'APPROVED' else 'highlight'}">{loan_request['status']['name']}</span>.<br><br>
                        {get_status_message(status_name, body)}
                        {payment_plan_html}
                        <div class="timestamp">Notification sent on: {formatted_time} (Colombia time)</div>
                    </div>
                    <div class="footer">
                        Best regards,<br>
                        <strong>CrediYa Team</strong>
                    </div>
                </div>
            </body>
        </html>
    """


def get_status_message(status_name, body):
    if status_name == 'APPROVED':
        return "Congratulations! Your loan has been approved. Please find your payment plan below."
    elif status_name == 'REJECTED':
        reject_reason = body.get('rejectReason', '')
        if reject_reason:
            return f"Unfortunately, your loan request has been rejected. Reason: {reject_reason}"
        return "Unfortunately, your loan request has been rejected. Please contact us for more information."
    elif status_name == 'UNDER_REVIEW':
        return "Your loan request is currently under review."
    else:
        return "If you have any questions or need further assistance, feel free to reach out to us."


def build_payment_plan_table(payment_plan):
    if not payment_plan:
        return ""
    
    rows = ""
    for payment in payment_plan:
        due_date = datetime.fromisoformat(payment['dueDate'].replace('Z', '+00:00')).strftime('%b %d, %Y')
        rows += f"""
            <tr>
                <td>{payment['paymentNumber']}</td>
                <td>{due_date}</td>
                <td class="currency">${payment['principalPayment']:,.2f}</td>
                <td class="currency">${payment['interestPayment']:,.2f}</td>
                <td class="currency">${payment['totalPayment']:,.2f}</td>
                <td class="currency">${payment['remainingBalance']:,.2f}</td>
            </tr>
        """
    
    return f"""
        <div class="payment-plan">
            <div class="payment-plan-header">
                📅 Your Payment Plan
            </div>
            <table class="payment-table">
                <thead>
                    <tr>
                        <th>Payment #</th>
                        <th>Due Date</th>
                        <th>Principal</th>
                        <th>Interest</th>
                        <th>Total Payment</th>
                        <th>Remaining Balance</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    """
