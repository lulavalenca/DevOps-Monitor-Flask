# Dockerfile para DevOps Monitor Flask
FROM python:3.13-slim


#Definir dirotório de trabalho
WORKDIR /app 


#Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# Copiar requirements e instalar dependências Python    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copiar todo o codigo da aplicação
COPY . .


#Expor porta 5000
EXPOSE 5000


# Variável de ambiente
ENV PYTHONUNBUFFERED=1
ENV SOCKETIO_ASYNC_MODE=threading


# Comando padrão (Flask web)
CMD ["python", "app.py"]