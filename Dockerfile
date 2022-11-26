FROM python:3.9.15-alpine3.16

WORKDIR /f2b-exporter

COPY ["requirements.txt", "conf.yml", "./"]
RUN pip install --no-cache-dir -r requirements.txt

COPY geoip_provider ./geoip_provider

COPY fail2ban-exporter.py .

CMD ["python", "./fail2ban-exporter.py"]
