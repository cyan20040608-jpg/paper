# NLP 情感分析系统

当前推荐的运行方式是不使用 Docker 和 Nginx，而是在本地直接运行 FastAPI，并让 FastAPI 同时提供前端静态页面和 `/api` 接口，再通过 FRP 暴露这一个统一入口。

当前版本已经做了两项首屏优化：

- 模型改为后台加载，页面不再等待模型完全就绪才打开
- FastAPI 会对较大的响应启用 GZip 压缩，并为 `/assets/` 下带 hash 的静态资源返回长缓存头

## 项目结构

- `backend/`：FastAPI 后端，负责模型加载、健康检查和情感分析接口
- `frontend/`：Vue 3 前端，构建后生成静态资源
- `bert-base-chinese/`：本地 BERT 基座目录
- `model_group_a_no_cnn/`：本地训练权重目录

## 推荐运行方式

### 1. 构建前端静态资源

```bash
cd frontend
npm install
npm run build
```

构建完成后会生成：

```text
frontend/dist
```

### 2. 启动本地后端

在项目根目录执行：

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

后端启动后：

- FastAPI 会立即对外提供页面和接口
- 模型会在后台线程继续加载
- `/api/health` 会先返回 `loading`，加载完成后变为 `ready`
- `/assets/*.css` 和 `/assets/*.js` 会带缓存头，重复访问时浏览器无需重新下载

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

如果没有先构建前端，访问页面时会返回明确错误，提示先执行 `npm run build`。

### 4. 使用 FRP 暴露统一入口

推荐直接暴露本地 FastAPI 的 `8000` 端口，不再暴露 Vite 开发服务器。

`frpc.toml` 示例：

```toml
serverAddr = "8.152.168.40"
serverPort = 7000

[[proxies]]
name = "web"
type = "tcp"
localIP = "127.0.0.1"
localPort = 8000
remotePort = 18000
```

这样公网访问地址就是：

```text
http://8.152.168.40:18000/
```

注意：不要使用 `6000` 这类浏览器限制端口。

访问链路：

```text
浏览器 -> 8.152.168.40:18000 -> frps/frpc -> 本地 FastAPI:8000 -> 前端静态页面 / API
```

## 用户体验说明

- 页面会先打开，不再等待模型完全加载完毕
- 页面顶部会显示“模型加载中”
- 模型未就绪时，分析按钮会禁用
- 模型加载完成后，页面无需刷新即可自动切换为“模型已就绪”
- 非首屏页面已改为路由懒加载，趋势图、高频词统计、历史记录不会再进入首页首包

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
