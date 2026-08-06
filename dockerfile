# 1. Pega uma versão leve do Python
FROM python:3.12-slim

# 2. Cria uma pasta chamada /app lá dentro e entra nela
WORKDIR /app

# 3. Copia só a lista de ingredientes primeiro e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia o resto do seu código (ignorando o que está no .dockerignore)
COPY . .

# 5. O comando de ignição do Uvicorn (já apontando para a porta do Hugging Face)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]