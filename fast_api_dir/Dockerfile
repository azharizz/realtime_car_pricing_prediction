# Use the official Python base image with the desired Python version
FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api_model:app", "--host", "0.0.0.0", "--port", "8000"]
