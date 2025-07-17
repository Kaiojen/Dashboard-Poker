import os
import sys
import subprocess
import threading
import time
from flask import Flask, redirect
from flask_cors import CORS

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Variável global para controlar o processo do Streamlit
streamlit_process = None

def start_streamlit():
    """Inicia o Streamlit em uma thread separada"""
    global streamlit_process
    try:
        # Caminho para o arquivo do Streamlit
        streamlit_file = os.path.join(os.path.dirname(__file__), 'app_final.py')
        
        # Comando para executar o Streamlit
        cmd = [sys.executable, '-m', 'streamlit', 'run', streamlit_file, '--server.port=8501', '--server.address=0.0.0.0']
        
        # Inicia o processo do Streamlit
        streamlit_process = subprocess.Popen(cmd, cwd=os.path.dirname(__file__))
        
        print("Streamlit iniciado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao iniciar Streamlit: {e}")

@app.route('/')
def index():
    """Redireciona para o Streamlit na porta 8501"""
    return redirect('http://localhost:8501')

@app.route('/health')
def health():
    """Endpoint de saúde"""
    return {'status': 'ok', 'message': 'Dashboard Suprema Poker está funcionando'}

@app.route('/dashboard')
def dashboard():
    """Redireciona para o dashboard"""
    return redirect('http://localhost:8501')

if __name__ == '__main__':
    # Inicia o Streamlit em uma thread separada
    streamlit_thread = threading.Thread(target=start_streamlit)
    streamlit_thread.daemon = True
    streamlit_thread.start()
    
    # Aguarda um pouco para o Streamlit iniciar
    time.sleep(3)
    
    # Inicia o Flask
    app.run(host='0.0.0.0', port=5000, debug=False)

