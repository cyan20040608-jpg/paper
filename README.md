# NLP 情感分析系统

本项目已整理为前后端分离架构：

- `backend/`：FastAPI 后端，负责模型加载、健康检查和情感分析接口
- `frontend/`：Vue3 + Element Plus 前端，通过 Nginx 提供静态页面并反向代理 `/api`
- `bert-base-chinese/`：本地 BERT 基座目录
- `model_group_a_no_cnn/`：本地训练权重目录

## Docker 文件

已提供以下部署文件：

- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `.env.example`
- `.dockerignore`

## 本地 Docker 启动

先复制环境变量文件：

```powershell
Copy-Item .env.example .env
```

构建并启动：

```powershell
docker compose up -d --build
```

查看容器状态：

```powershell
docker compose ps
```

查看后端日志：

```powershell
docker compose logs -f backend
```

查看前端日志：

```powershell
docker compose logs -f frontend
```

停止服务：

```powershell
docker compose down
```

## 访问地址

- 前端首页：`http://服务器IP/`
- 后端健康检查：`http://服务器IP:8000/api/health`
- 后端分析接口：`POST http://服务器IP:8000/api/sentiment/analyze`

## 服务器部署步骤

将项目上传到服务器后，在项目根目录执行：

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
```

如果需要更新代码后重新部署：

```bash
docker compose down
docker compose up -d --build
```

## 环境变量

`.env` 可配置以下参数：

```env
BACKEND_PORT=8000
FRONTEND_PORT=80
APP_DEFAULT_THRESHOLD=0.6
APP_ALLOW_ORIGINS=http://localhost,http://127.0.0.1
```

说明：

- `BACKEND_PORT`：宿主机映射的后端端口
- `FRONTEND_PORT`：宿主机映射的前端端口
- `APP_DEFAULT_THRESHOLD`：默认分类阈值
- `APP_ALLOW_ORIGINS`：后端允许的 CORS 来源，多个地址用逗号分隔

## 部署说明

- 前端容器内部使用 Nginx，自动将 `/api` 反向代理到 `backend:8000`
- 后端容器不直接打包模型，而是通过 `volumes` 挂载根目录下的 `bert-base-chinese/` 和 `model_group_a_no_cnn/`
- 因此服务器上的项目目录必须保留这两个模型目录
