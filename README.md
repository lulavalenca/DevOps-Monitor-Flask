# DevOps Monitor Flask

**Sistema de Monitoramento DevOps em Tempo Real**

![Dashboard Screenshot](static/images/dashboard.png)

## 🌟 Visão Geral
Este projeto implementa um painel de monitoramento DevOps em tempo real usando:
- **Backend**: Flask, Flask-SocketIO, psutil
- **Frontend**: Bootstrap 5, Chart.js, WebSockets
- **Monitoramento**: CPU, Memória, Disco e Rede
- **Notificações**: Alertas configuráveis (warnings e críticos)

## 🚀 Funcionalidades Implementadas
1. Monitoramento em Tempo Real: CPU, Memória, Disco, Rede
2. WebSocket para atualizações instantâneas
3. API REST completa para integração
4. Dashboard responsivo com Bootstrap 5
5. Sistema de alertas e histórico de métricas

## 📁 Estrutura do Repositório

├── app.py
├── config.py
├── monitoring.py
├── websocket_handler.py
├── test_monitoring.py
├── requirements.txt
├── .gitignore
├── README.md
└──
├── static/
│ ├── css/style.css
│ ├── js/main.js
│ └── images/
└── templates/index.html



## 🔧 Como Executar
1. Clone o repositório e ative o venv  
2. `pip install -r requirements.txt`  
3. `python app.py`  
4. Acesse `http://localhost:5000`  

## 🎯 Próximos Passos
- Redis + Celery para tasks assíncronas  
- Docker Compose para orquestração  
- Ansible para deploy  
- Prometheus + Grafana  
- Notificações por Email/Slack/Teams  

## 📜 Licença
MIT License


