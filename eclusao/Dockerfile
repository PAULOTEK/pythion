# Use a imagem oficial do Python como base
FROM python:3.13-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de requisitos e o script Python para o contêiner
COPY requirements.txt .
COPY main.py .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Defina o comando para executar o script Python
CMD ["python", "main.py"]
