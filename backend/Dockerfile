FROM python:3.8.16-slim-buster

ENV FLASK_APP=server_app.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y libgomp1 unzip

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install pandas  # Install pandas library

RUN pip install gdown

RUN gdown 'https://drive.google.com/uc?id=1-rF_um4AObZJwEusAPjkBp3aH9EIySB3&export=download' -O best_model.pt
RUN mkdir -p /audio/model
RUN mv best_model.pt /audio/model

RUN gdown "https://drive.google.com/uc?id=1tVt-CBoAZyQIM1_cGn1mRlRZHefI5vBJ" -O VENGEWAV.zip && \
    unzip VENGEWAV.zip -d /static && \
    rm -d VENGEWAV.zip

EXPOSE 8000
COPY . .

RUN ["python", "separate.py"]

RUN ["python", "startDB.py"]

CMD ["python", "server_app.py"]
