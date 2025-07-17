#!/bin/bash

# Script para iniciar o Dashboard Suprema Poker permanentemente
cd /home/ubuntu/workspace

# Mata processos anteriores se existirem
pkill -f "streamlit run app_final.py"

# Inicia o Streamlit em background
nohup streamlit run app_final.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &

echo "Dashboard Suprema Poker iniciado!"
echo "Acesse em: http://localhost:8501"
echo "Log disponível em: streamlit.log"

