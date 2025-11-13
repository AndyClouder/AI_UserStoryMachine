# 智谱AI (Bigmodel) 配置指南

本指南将帮助您配置 StoryMachine 使用智谱AI (Bigmodel) API 而不是 OpenAI API。

## 🚀 快速配置

### 1. 获取智谱AI API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并登录账户
3. 在控制台中创建新的 API Key
4. 复制您的 API Key

### 2. 配置环境变量

创建或编辑 `.env` 文件：

```bash
# 使用智谱AI作为AI提供商
API_PROVIDER=zhipuai

# 智谱AI API Key (必需)
ZHIPUAI_API_KEY=您的智谱AI API密钥

# GitHub Token (用于仓库访问，可选)
GITHUB_TOKEN=ghp_您的GitHub令牌

# GitLab Token (用于GitLab仓库访问，可选)
GITLAB_TOKEN=glpat_您的GitLab令牌

# 模型设置 (可选)
MODEL=glm-4-flash
```

### 3. 可用的智谱AI模型

- `glm-4-flash` - 快速响应模型 (推荐)
- `glm-4` - 标准模型
- `glm-4-plus` - 增强模型
- `glm-4-long` - 长文本模型

## 📋 配置选项说明

| 环境变量 | 必需 | 默认值 | 说明 |
|---------|------|--------|------|
| `API_PROVIDER` | 否 | `zhipuai` | AI提供商，可选值: `openai` 或 `zhipuai` |
| `ZHIPUAI_API_KEY` | 使用智谱AI时必需 | - | 智谱AI的API密钥 |
| `OPENAI_API_KEY` | 使用OpenAI时必需 | - | OpenAI的API密钥 |
| `MODEL` | 否 | `glm-4-flash` | 要使用的模型名称 |
| `GITHUB_TOKEN` | 否 | - | GitHub访问令牌 |
| `GITLAB_TOKEN` | 否 | - | GitLab访问令牌 |

## 🔄 切换AI提供商

### 从OpenAI切换到智谱AI：

```bash
# 注释掉OpenAI配置
# OPENAI_API_KEY=your-openai-key

# 启用智谱AI
API_PROVIDER=zhipuai
ZHIPUAI_API_KEY=your-zhipuai-key
MODEL=glm-4-flash
```

### 从智谱AI切换到OpenAI：

```bash
# 注释掉智谱AI配置
# ZHIPUAI_API_KEY=your-zhipuai-key

# 启用OpenAI
API_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
MODEL=gpt-4
```

## 🧪 测试配置

运行测试以确保配置正确：

```bash
# 运行所有测试
uv run --frozen pytest

# 只运行配置相关测试
uv run --frozen pytest tests/test_config.py
```

## 📝 使用示例

配置完成后，正常使用 StoryMachine：

```bash
# 使用智谱AI生成用户故事
uv run storymachine --prd path/to/prd.md --tech-spec path/to/tech-spec.md --repo https://github.com/owner/repo
```

## ⚠️ 注意事项

1. **API Key 安全**: 不要将 `.env` 文件提交到版本控制系统
2. **模型选择**: `glm-4-flash` 适合快速响应，`glm-4-plus` 适合复杂任务
3. **GitHub Token**: 如果需要访问私有仓库，请确保GitHub token有适当的权限
4. **网络连接**: 确保您的网络可以访问智谱AI的API端点

## 🔧 故障排除

### 常见错误：

1. **"ZhipuAI API key is required"**
   - 检查 `ZHIPUAI_API_KEY` 是否正确设置
   - 确认 `API_PROVIDER=zhipuai`

2. **"Failed to connect to API"**
   - 检查网络连接
   - 验证API Key是否有效

3. **"Model not found"**
   - 确认模型名称正确
   - 查看智谱AI文档了解可用模型

## 📚 更多资源

- [智谱AI官方文档](https://open.bigmodel.cn/dev/guides)
- [StoryMachine README](README.md)
- [问题反馈](https://github.com/your-repo/storymachine/issues)