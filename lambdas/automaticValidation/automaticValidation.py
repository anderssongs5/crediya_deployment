import json
import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any
import boto3


def lambda_handler(event, context):
    try:
        loan_data = parse_loan_data(event)

        print(f'Loan data received: {loan_data}')

        analysis = calculate_borrowing_capacity_analysis(loan_data)

        print(f'Analysis completed: {analysis}')

        response = {
            'loanApplicationId': loan_data['loan_application_id'],
            'analysis': analysis,
            'approved': analysis['decision'] == 'APPROVED',
            'rejectionReason': analysis['reasoning'] if analysis['decision'] == 'REJECTED' else None
        }
        
        body_response = {
            'statusCode': 200,
            'body': response
        }
        
    except Exception as e:
        body_response = {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'loanApplicationId': event.get('loanApplicationId', 'unknown')
            }
        }
    
    enqueue_response(response=body_response)

    return body_response
    

def enqueue_response(response: Dict[str, Any]) -> None:
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/865937366609/crediya-validationDecision',
        MessageBody=json.dumps(response, default=decimal_serializer)
    )


def parse_loan_data(event: Dict[str, Any]) -> Dict[str, Any]:

    if 'Records' in event:
        message_body = json.loads(event['Records'][0]['body'])
        loan_data = message_body
    else:
        loan_data = event
    
    return {
        'loan_application_id': loan_data['loanApplicationId'],
        'user_email': loan_data['userEmail'],
        'user_id_number': loan_data['userIdNumber'],
        'loan_amount': Decimal(str(loan_data['loanAmount'])),
        'term_in_months': int(loan_data['termInMonths']),
        'interest_rate': Decimal(str(loan_data['interestRate'])),
        'user_base_salary': Decimal(str(loan_data['userBaseSalary'])),
        'approved_loans': [
            {
                'amount': Decimal(str(loan['amount'])),
                'term': int(loan['term']),
                'interest_rate': Decimal(str(loan['interestRate']))
            }
            for loan in loan_data.get('approvedLoans', [])
        ]
    }


def calculate_borrowing_capacity_analysis(loan_data: Dict[str, Any]) -> Dict[str, Any]:
    MAX_BORROWING_CAPACITY_PERCENTAGE = Decimal('0.35')
    MANUAL_REVIEW_SALARY_MULTIPLIER = Decimal('5')

    max_borrowing_capacity = (loan_data['user_base_salary'] * MAX_BORROWING_CAPACITY_PERCENTAGE).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    current_monthly_debt = calculate_current_monthly_debt(loan_data['approved_loans'])

    available_capacity = max_borrowing_capacity - current_monthly_debt

    new_loan_monthly_payment = calculate_monthly_payment(
        loan_data['loan_amount'],
        loan_data['interest_rate'],
        loan_data['term_in_months']
    )

    decision, reasoning = make_loan_decision(
        new_loan_monthly_payment,
        available_capacity,
        loan_data['loan_amount'],
        loan_data['user_base_salary'],
        MANUAL_REVIEW_SALARY_MULTIPLIER
    )
    
    return {
        'totalIncome': loan_data['user_base_salary'],
        'maxBorrowingCapacity': max_borrowing_capacity,
        'currentMonthlyDebt': current_monthly_debt,
        'availableCapacity': available_capacity,
        'newLoanMonthlyPayment': new_loan_monthly_payment,
        'decision': decision,
        'reasoning': reasoning
    }


def calculate_current_monthly_debt(approved_loans: List[Dict[str, Any]]) -> Decimal:
    total_monthly_debt = Decimal('0')
    
    for loan in approved_loans:
        monthly_payment = calculate_monthly_payment(
            loan['amount'],
            loan['interest_rate'],
            loan['term']
        )
        total_monthly_debt += monthly_payment
    
    return total_monthly_debt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_monthly_payment(amount: Decimal, annual_rate: Decimal, term_months: int) -> Decimal:
    # Formula: Payment = P * [r(1+r)^n] / [(1+r)^n - 1]
    # P = amount, r = Monthly interest rate, n = Number of months
    if annual_rate == 0:
        # No interest case
        return (amount / Decimal(str(term_months))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # monthly rate
    monthly_rate = annual_rate / Decimal('12')
    
    # (1 + r)^n
    one_plus_rate = Decimal('1') + monthly_rate
    power_term = one_plus_rate ** term_months

    numerator = amount * monthly_rate * power_term
    denominator = power_term - Decimal('1')
    
    monthly_payment = numerator / denominator
    
    return monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def make_loan_decision(
    new_loan_payment: Decimal,
    available_capacity: Decimal,
    loan_amount: Decimal,
    user_salary: Decimal,
    manual_review_multiplier: Decimal
) -> tuple[str, str]:
    if new_loan_payment <= available_capacity:
        salary_threshold = user_salary * manual_review_multiplier
        
        if loan_amount > salary_threshold:
            return (
                'MANUAL_REVIEW',
                f'Loan amount ${loan_amount} exceeds 5 times the user\'s salary ${user_salary} - requires manual review'
            )
        else:
            return (
                'APPROVED',
                f'Loan approved based on borrowing capacity analysis. Monthly payment ${new_loan_payment} is within available capacity ${available_capacity}'
            )
    else:
        return (
            'REJECTED',
            f'Monthly payment ${new_loan_payment} exceeds available borrowing capacity ${available_capacity}'
        )


def decimal_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
