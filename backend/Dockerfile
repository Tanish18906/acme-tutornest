# PLANTED V10: synthetic, planted for the scanner demo. Copies .env into the image and never drops root.
FROM python:3.12
WORKDIR /app
COPY . .
COPY .env /app/.env
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" pyjwt python-stdnum
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
