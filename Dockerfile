FROM python:3.11-slim

WORKDIR /app

COPY whatsapp_agent/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY whatsapp_agent/ ./whatsapp_agent/

EXPOSE 8000
CMD ["uvicorn", "whatsapp_agent.app:app", "--host", "0.0.0.0", "--port", "8000"]
