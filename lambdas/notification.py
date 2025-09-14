import json
import boto3

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
                        max-width: 600px;
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
                    .footer {{
                        margin-top: 30px;
                        font-size: 14px;
                        color: #7f8c8d;
                        text-align: center;
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
                        <span class="highlight">{loan_request['status']['name']}</span>.<br><br>
                        If you have any questions or need further assistance, feel free to reach out to us.
                    </div>
                    <div class="footer">
                        Best regards,<br>
                        <strong>CrediYa Team</strong>
                    </div>
                </div>
            </body>
        </html>
    """
