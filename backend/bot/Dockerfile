FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

COPY requirements.txt ./requirements.txt
# DEBUG: show the file to be 100% sure
RUN echo "----- BOT requirements.txt -----" && cat requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
