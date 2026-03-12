FROM docker.m.daocloud.io/library/python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \ 
    torch torchvision \
    --extra-index-url https://download.pytorch.org/whl/cpu
    
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /app/backend/requirements.txt

COPY backend /app/backend
COPY bert-base-chinese /app/bert-base-chinese
COPY model_group_a_no_cnn /app/model_group_a_no_cnn

EXPOSE 8000
#frpc -c ./frpc.toml
#python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
