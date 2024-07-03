FROM python:alpine3.19

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt

COPY script.py .
CMD [ "python", "-u", "script.py" ]
