FROM python:3.13.3-alpine AS builder


WORKDIR /app
RUN python -c "import _strptime"

RUN python3 -m pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync


FROM python:3.13.3-alpine AS runtime
# add curl for healthcheck
RUN apk add --no-cache curl
EXPOSE 5023
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["./entrypoint.sh"]
