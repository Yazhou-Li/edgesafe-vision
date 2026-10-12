FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY examples ./examples
RUN python -m pip install --no-cache-dir .
CMD ["python", "examples/end_to_end_demo.py"]
