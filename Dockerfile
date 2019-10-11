FROM python:3.7-slim-buster
RUN apt-get update && apt-get install -y git
#TODO
RUN git clone https://www.github.com/obrigg/cisco-aci-audit-exporter.git
WORKDIR /cisco-aci-audit-exporter/
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "run.py"]
