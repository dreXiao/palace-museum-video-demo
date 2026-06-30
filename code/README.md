# 故宫日历·图生视频管理平台

## 快速启动

### 1. 配置环境变量
```bash
cp server/.env.example server/.env
# 编辑 server/.env 填入真实 API Key
```

### 2. 启动服务
```bash
docker compose up -d
```

### 3. 初始化数据库
```bash
# 运行迁移脚本
docker compose exec postgres psql -U palace -d palace_museum -f /docker-entrypoint-initdb.d/001_init.sql

# 或手动连接执行 SQL 文件:
# psql -h localhost -U palace -d palace_museum -f server/app/db/migrations/001_init.sql
# psql -h localhost -U palace -d palace_museum -f server/app/db/migrations/002_seed_data.sql
```

### 4. 构建前端
```bash
cd web-ui
npm install
npm run build
# 构建产物将在 web-ui/dist/ 目录
# Docker 部署时 Nginx 会自动挂载该目录
```

### 5. 访问应用
- Web 界面: http://localhost
- API 文档: http://localhost/api/docs
- MinIO 控制台: http://localhost:9001 (首次需创建 bucket: palace-museum-media)

### 默认管理员登录
- 用户名: `admin`
- 密码: `admin123` (请修改 .env 中的 ADMIN_PASSWORD)

## 开发模式

### 后端开发
```bash
cd server
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端开发
```bash
cd web-ui
npm install
npm run dev
# 访问 http://localhost:5173
# API 请求自动代理到 localhost:8000
```

## 项目结构
```
code/
├── docker-compose.yml          # 统一编排
├── nginx/nginx.conf             # Nginx 配置
├── server/                      # FastAPI 后端
│   ├── Dockerfile
│   ├── .env.example
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # 入口
│       ├── config.py            # 配置
│       ├── api/v1/              # API 路由
│       ├── services/            # 业务逻辑
│       ├── adapters/            # AI API 适配器
│       ├── models/              # SQLAlchemy ORM
│       ├── schemas/             # Pydantic Schema
│       ├── core/                # 安全/存储
│       └── db/migrations/       # SQL 迁移
└── web-ui/                      # Vue 3 前端
    ├── src/
    │   ├── pages/               # 页面组件
    │   ├── components/          # 可复用组件
    │   ├── stores/              # Pinia 状态
    │   ├── api/                 # API 客户端
    │   ├── router/              # 路由
    │   └── types/               # 类型定义
    └── package.json
```
