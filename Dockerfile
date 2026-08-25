FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файла зависимостей и их установка
# (Выполняется до копирования кода для кэширования слоев Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY main.py .

# Запуск FastAPI через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]