FROM python:3.8-slim

COPY . .

RUN pip install --upgrade pip -r requirements.txt

ENTRYPOINT [ "python", "/src/main.py" ]
