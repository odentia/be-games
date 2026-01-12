FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install uv
RUN uv pip install --system .

EXPOSE 8010

CMD ["uv", "run", "python", "-m", "game_service.api"]
