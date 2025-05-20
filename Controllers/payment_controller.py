from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import requests
import os
import json
from datetime import datetime,timedelta
from dotenv import load_dotenv

load_dotenv()

# Crear el blueprint
payment_blueprint = Blueprint('payment', __name__)

class Pagos:
    def __init__(self):

        self.API_KEY = os.environ.get('KHIPU_API_KEY')
        if not self.API_KEY:
            raise ValueError("La variable de entorno KHIPU_API_KEY no esta aplicada.")
        
        self.BASE_URL = 'https://api.khipu.com/payments'
        self.RECEIVER_ID = os.environ.get('KHIPU_RECEIVER_ID')
        if not self.RECEIVER_ID:
            raise ValueError("La variable de entorno KHIPU_RECEIVER_ID no esta aplicada.")
        
        # Configurar las rutas del blueprint
        payment_blueprint.route('/generar-cobro', methods=['POST'])(self.generarCobro)
        payment_blueprint.route('/notificacion', methods=['POST'])(self.recibirNotificacion)
        payment_blueprint.route('/retorno', methods=['GET'])(self.retornoPago)
        payment_blueprint.route('/cancelacion', methods=['GET'])(self.cancelacionPago)

    def generarCobro(self):
        try:
            data = request.get_json()
            monto = data.get('amount')
            motivo = data.get('subject', 'Pago')
            moneda = data.get('moneda', 'CLP')
            transaction_id = data.get('transaction_id')
            payer_email = data.get('email')
            description = data.get('description')

            if not monto or not payer_email or not motivo:
                return jsonify({'error': 'Faltan datos requeridos'}), 400

            payload = {
                "amount": float(monto),
                "currency": moneda,
                "subject": motivo,
                "payer_email": payer_email
            }
            if transaction_id:
                payload["transaction_id"] = transaction_id
            if description:
                payload["body"] = description

            headers = {
                'x-api-key': self.API_KEY,
                'Content-Type': 'application/json'
            }

            response = requests.post(
                "https://payment-api.khipu.com/v3/payments",
                json=payload,
                headers=headers
            )

            try:
                data = response.json()
            except Exception as e:
                print("Respuesta de Khipu no es JSON. Status:", response.status_code)
                print("Texto de la respuesta:", response.text)
                raise e

            if response.status_code == 200:
                return jsonify({
                    'status': 'success',
                    'payment_id': data.get('payment_id'),
                    'payment_url': data.get('payment_url')
                })
            else:
                return jsonify({
                    'error': 'Error al generar el cobro',
                    'detalles': data
                }), response.status_code

        except Exception as e:
            print("Error en generarCobro:", e)
            return jsonify({
                'error': 'Error interno del servidor',
                'detalles': str(e)
            }), 500

    def recibirNotificacion(self):
        try:
            api_version = request.form.get('api_version')
            notification_token = request.form.get('notification_token')

            if api_version != '1.3':
                return jsonify({'error': 'Versión de API no soportada'}), 400

            headers = {
                'Authorization': f'Bearer {self.API_KEY}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f"{self.BASE_URL}/{notification_token}",
                headers=headers
            )

            if response.status_code == 200:
                payment_data = response.json()
                
                if (payment_data.get('receiver_id') == self.RECEIVER_ID and 
                    payment_data.get('status') == 'done'):
                    return jsonify({'status': 'success'}), 200
                else:
                    return jsonify({'error': 'Pago inválido'}), 400
            else:
                return jsonify({'error': 'Error al verificar el pago'}), response.status_code

        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'detalles': str(e)
            }), 500

    def retornoPago(self):
        # Página de retorno después del pago
        return render_template('payment/retorno.html')

    def cancelacionPago(self):
        return render_template('payment/cancelacion.html')

pagos = Pagos()


