FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,destination=/root/.cache/uv <<EOF
uv sync \
  --no-dev \
  --no-install-project \
  --frozen
EOF
COPY . .

RUN chmod +x start_scripts/prestart.sh
ENTRYPOINT [ "start_scripts/prestart.sh"]

CMD [ "uv", "run", "python", "start.py" ]
