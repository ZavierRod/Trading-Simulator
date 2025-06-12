FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# now test_feed.json is in /app/test_feed.json
CMD ["python", "runner.py", "--strategy-id", "3", "--feed-file", "test_feed.json"]