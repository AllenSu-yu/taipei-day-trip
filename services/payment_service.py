# services/payment_service.py
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class PaymentService:
    """處理付款相關的業務邏輯"""
    
    @staticmethod
    def tappay_payment(prime, amount, phone_number, name, email):
        """呼叫 TapPay API 進行付款"""
        url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": os.getenv("x-api-key")
        }
        
        payload = {
            "prime": prime,
            "partner_key": os.getenv("x-api-key"),
            "merchant_id": "tppf_allensu_GP_POS_3",
            "details": "TapPay Test",
            "amount": amount,
            "cardholder": {
                "phone_number": phone_number,
                "name": name,
                "email": email
            }
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        print("Status Code:", response.status_code)
        response_data = response.json()
        print("Response Body:", response_data)
        
        return response.status_code, response_data
