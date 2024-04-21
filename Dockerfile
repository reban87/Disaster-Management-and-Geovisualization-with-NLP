FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
# FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-devel

# Clear pip cache and update pip
RUN pip install --upgrade pip && pip cache purge

# Install Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . .
WORKDIR ./app

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]