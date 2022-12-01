FROM python:3.9.15-alpine3.16

WORKDIR /f2b-exporter

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD ["python", "-u", "fail2ban_exporter.py"]
