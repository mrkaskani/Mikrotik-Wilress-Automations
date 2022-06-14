FROM python:3.9.5

WORKDIR /wirless

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . ./src

CMD python ./src/main.py