FROM python:3.9.15-alpine3.16

WORKDIR /f2b-exporter

COPY ["src/requirements.txt", "conf.yml", "./"]
RUN pip install --no-cache-dir -r requirements.txt

COPY src/geoip_provider ./geoip_provider

COPY src/fail2ban-exporter.py .

CMD ["python", "-u", "./fail2ban-exporter.py"]
