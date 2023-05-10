FROM python:3.8.16-slim-buster
WORKDIR /backend
ENV FLASK_APP=server_app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y libgomp1
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8000
COPY . .
CMD ["python", "server_app.py"]
