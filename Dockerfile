FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app/
ARG DATABASE_URL
RUN sh build.sh
RUN python3 -m pip install --upgrade --disable-pip-version-check gunicorn~=23.0
EXPOSE 8000
CMD ["gunicorn", "cate.wsgi:application", "--bind", "0.0.0.0:8000"]
