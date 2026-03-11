# NLP 情感分析系统

当前推荐的运行方式是不使用 Docker 和 Nginx，而是在本地直接运行 FastAPI，并让 FastAPI 同时提供前端静态页面和 `/api` 接口，再通过 FRP 暴露这一个统一入口。

## 项目结构

- `backend/`：FastAPI 后端，负责模型加载、健康检查和情感分析接口
- `frontend/`：Vue 3 前端，构建后生成静态资源
- `bert-base-chinese/`：本地 BERT 基座目录
- `model_group_a_no_cnn/`：本地训练权重目录

## 推荐运行方式

### 1. 启动本地后端

在项目根目录执行：

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

后端启动后：

- `/api/health` 和 `/api/sentiment/analyze` 继续由 FastAPI 处理
- `/` 和前端路由会由 FastAPI 直接返回 `frontend/dist` 中的静态资源

### 2. 构建前端静态资源

```bash
cd frontend
npm install
npm run build
```

构建完成后会生成：

```text
frontend/dist
```

如果没有先构建，访问前端页面时会返回明确错误，提示先执行 `npm run build`。

### 3. 本地访问

后端启动且前端构建完成后，直接访问：

```text
http://127.0.0.1:8000/
```

也可以验证：

```text
http://127.0.0.1:8000/sentiment
http://127.0.0.1:8000/api/health
```

### 4. 使用 FRP 暴露统一入口

推荐直接暴露本地 FastAPI 的 `8000` 端口，不再暴露 Vite 开发服务器，也不再单独加本地 Nginx。

`frpc.toml` 示例：

```toml
serverAddr = "8.152.168.40"
serverPort = 7000

[[proxies]]
name = "web"
type = "tcp"
localIP = "127.0.0.1"
localPort = 8000
remotePort = 6000
```

这样公网访问地址就是：

```text
http://8.152.168.40:6000/
```

访问链路：

```text
浏览器 -> 8.152.168.40:6000 -> frps/frpc -> 本地 FastAPI:8000 -> 前端静态页面 / API
```

## 前端开发说明

开发调试仍然可以使用：

```bash
cd frontend
npm run dev
```

开发服务器配置在：

[`frontend/vite.config.js`](/D:/pycharm/code/paper/frontend/vite.config.js)

开发时：

- 监听地址：`0.0.0.0`
- 端口：`5173`
- `/api` 会代理到 `http://127.0.0.1:8000`

但 `npm run dev` 只用于本地开发，不建议直接通过 FRP 对公网暴露。

## Docker 说明

仓库中仍保留 Docker 相关文件：

- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`

但对于当前模型体量和低内存机器，更推荐优先使用本地运行方案。
