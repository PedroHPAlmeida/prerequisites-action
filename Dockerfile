FROM python:3.8-slim

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "/src/main.py" ]