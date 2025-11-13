# AI User Story Machine

基于StoryMachine的云端用户故事生成器，支持在线上传PRD文档并自动生成用户故事。

## 🌐 云端版本特性

- 📝 **在线上传**: 直接在浏览器中上传PRD文档
- 🤖 **AI生成**: 智能分析文档并生成高质量用户故事
- 📋 **验收标准**: 自动生成详细的验收标准
- ☁️ **云端处理**: 无需本地安装，直接在线使用
- 🌐 **简洁界面**: 现代化的Web界面，易于使用

## 🚀 快速开始

### 在线使用
访问部署后的URL，直接在浏览器中使用：
1. 上传您的PRD文档（必需）
2. 可选：上传技术规格文档
3. 可选：提供GitHub仓库URL
4. 点击"生成用户故事"
5. 等待AI处理完成

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py

# 访问 http://localhost:8000
```

## 📋 API文档

### 主要端点

- `GET /` - Web界面
- `POST /generate-stories` - 生成用户故事
- `GET /task-status/{task_id}` - 查询任务状态
- `GET /health` - 健康检查
- `GET /info` - 应用信息

### 生成用户故事API

**请求**:
```http
POST /generate-stories
Content-Type: multipart/form-data

prd_file: [PRD文档文件]
tech_spec_file: [技术规格文档文件，可选]
repo_url: [GitHub仓库URL，可选]
```

**响应**:
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "message": "任务已提交，正在处理中..."
}
```

## 🔧 技术栈

- **后端**: FastAPI + Uvicorn
- **前端**: HTML + Tailwind CSS + JavaScript
- **AI**: StoryMachine CLI集成
- **部署**: Vercel (支持Python 3.13)

## 📄 文件要求

### PRD文档格式
- 支持 `.md` 和 `.txt` 格式
- 建议使用UTF-8编码
- 内容应包含产品需求描述

### 技术规格文档（可选）
- 支持 `.md` 和 `.txt` 格式
- 包含技术实现细节有助于生成更准确的用户故事

## 🌟 功能特点

1. **实时处理状态**: 显示AI处理进度
2. **异步处理**: 避免长时间等待，提升用户体验
3. **错误处理**: 友好的错误提示和处理
4. **响应式设计**: 支持各种设备访问
5. **CORS支持**: 可与其他前端应用集成

## 🚀 部署

### Vercel部署
项目已配置Vercel部署，直接连接GitHub仓库即可自动部署。

### 其他平台
也可以部署到支持FastAPI的平台：
- Railway
- Render
- Heroku
- 任何支持Python的云平台

## 📝 使用示例

1. 准备您的PRD文档（如 `product_requirements.md`）
2. 访问Web界面
3. 上传文档并填写相关信息
4. 等待AI生成用户故事
5. 查看并导出生成结果

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License