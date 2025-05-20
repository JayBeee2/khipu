from flask import Flask, render_template, request, redirect, url_for, jsonify
from Controllers.payment_controller import payment_blueprint
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.register_blueprint(payment_blueprint, url_prefix='/payment')

API_KEY = os.environ.get('KHIPU_API_KEY')
if not API_KEY:
    raise ValueError("La variable de entorno KHIPU_API_KEY no esta aplicada.")
# NOTIFY_URL = os.environ.get('KHIPU_NOTIFY_URL', 'https://tu-dominio.com/payment/notification')
BASE_URL = 'https://api.khipu.com/payments'



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
