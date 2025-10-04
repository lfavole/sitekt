FROM debian:trixie-slim AS build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app/
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_INSTALL_DIR=/python
RUN --mount=type=cache,target=/root/.cache/uv uv sync --compile-bytecode --extra server
RUN ln -s /bin/python /bin/python3
RUN unset DATABASE_URL; sh build.sh

FROM nginx:1-trixie
ENV UV_PYTHON_INSTALL_DIR=/python
COPY --from=build /app /app
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/
COPY --from=build /python /python
RUN apt install -y --no-install-recommends nginx && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/nginx/conf.d
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
WORKDIR /app
VOLUME ["/app/media"]
EXPOSE 80
ENTRYPOINT sh -c "\
nginx -g \"daemon off;\" & \
case \"\$DATABASE_URL\" in \
    postgres*) \
        uv pip install psycopg[binary,pool]~=3.2 \
        ;; \
    mysql*) \
        uv pip install mysqlclient~=2.2 \
        ;; \
esac; \
uv run --no-sync gunicorn cate.wsgi:application --bind 0.0.0.0:8000 & \
uv run --no-sync manage.py migrate; \
uv run --no-sync manage.py createcachetable; \
wait \
"
EXPOSE 8000
