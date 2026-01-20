import requests
import os
from flask import current_app

class AbacatePayment:
    """Gerenciamento de pagamentos com AbacatePay"""
    
    BASE_URL = "https://api.abacatepay.com/v1"
    
    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Bearer {os.environ.get('ABACATE_API_KEY')}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def create_customer(name, email, tax_id=None):
        """Criar cliente no AbacatePay"""
        url = f"{AbacatePayment.BASE_URL}/customer/create"
        payload = {
            "name": name,
            "email": email,
        }
        if tax_id:
            payload["taxId"] = tax_id
            
        try:
            response = requests.post(url, json=payload, headers=AbacatePayment._get_headers())
            return response.json()
        except Exception as e:
            print(f"Erro ao criar cliente AbacatePay: {e}")
            return None

    @staticmethod
    def create_billing(customer_id, amount_cents, description, return_url, completion_url):
        """
        Criar uma cobrança (Billing).
        amount_cents: Valor em centavos (int)
        """
        url = f"{AbacatePayment.BASE_URL}/billing/create"
        payload = {
            "customerId": customer_id,
            "amount": amount_cents,
            "description": description,
            "returnUrl": return_url,
            "completionUrl": completion_url,
             # AbacatePay pode ter campos específicos para métodos de pagamento, por padrão aceita PIX/Boleto, etc.
             "methods": ["PIX", "CREDIT_CARD"] 
        }
        
        try:
            response = requests.post(url, json=payload, headers=AbacatePayment._get_headers())
            return response.json()
        except Exception as e:
            print(f"Erro ao criar billing AbacatePay: {e}")
            return None

    @staticmethod
    def list_customers(email):
        """Listar clientes para encontrar ID existente"""
        url = f"{AbacatePayment.BASE_URL}/customer/list"
        # Simplificação: AbacatePay pode não ter filtro direto por email na listagem simples ou ter paginação
        # Vamos tentar criar sempre ou gerenciar no nosso banco o ID.
        pass
