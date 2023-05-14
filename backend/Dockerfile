FROM python:3.8.16-slim-buster
WORKDIR /backend
ENV FLASK_APP=server_app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y libgomp1 wget unzip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR backend/audio/model
RUN wget -O best_model.pt 'https://drive.google.com/uc?id=1-rF_um4AObZJwEusAPjkBp3aH9EIySB3&export=download'
# RUN unzip best_model.pt && rm model.zip

WORKDIR /backend/static

RUN pip install gdown && \
    gdown "https://drive.google.com/uc?id=1tVt-CBoAZyQIM1_cGn1mRlRZHefI5vBJ" -O VENGEWAV.zip && \
    unzip VENGEWAV.zip && \
    rm VENGEWAV.zip
#RUN wget -O VENGEWAV.zip 'https://drive.google.com/uc?id=1tVt-CBoAZyQIM1_cGn1mRlRZHefI5vBJ&export=download'
#RUN unzip VENGEWAV.zip && rm VENGEWAV.zip



WORKDIR /backend
EXPOSE 8000
COPY . .

RUN ["python", "startDB.py"]

CMD ["python", "server_app.py"]
