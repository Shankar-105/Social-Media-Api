FROM python:3.12-slim

# Install system deps for Postgres (psycopg2 needs 'em)
WORKDIR /code

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copying and installing Python deps
# first copy and then install so that docker doesnt reinstall everything if
# nothing has changed from the previous requirements.txt to the current requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copying the whole code
COPY . .

# Expose port
EXPOSE 8000

# first run the migrations and then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]