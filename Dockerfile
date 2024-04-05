FROM python:3.11-slim-bullseye
ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1
RUN pip install --upgrade pip
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]