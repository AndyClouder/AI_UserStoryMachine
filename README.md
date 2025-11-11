# AIPM User Story Machine

基于StoryMachine的AI产品需求管理系统，支持智谱AI集成和中文本地化。

## 主要功能

- 🤖 智谱AI集成，支持用户故事自动生成
- 🇨🇳 完整的中文语言支持
- 📝 从PRD文档自动生成用户故事
- 🔧 详细的验收标准生成
- 📊 项目上下文感知

## 快速开始

1. 安装依赖：
   ```bash
   uv sync
   ```

2. 配置智谱AI：
   ```bash
   cp .env.example .env
   # 编辑.env文件，添加您的智谱AI API密钥
   ```

3. 运行程序：
   ```bash
   uv run storymachine --prd "prd/您的PRD文档.md"
   ```

## 特色功能

- 🎯 智能故事分解和优先级排序
- 📋 自动生成验收标准
- 🔄 迭代式故事优化
- 🌐 中文提示词优化
- 🐛 详细的调试和错误处理

## 技术栈

- Python 3.13+
- 智谱AI API
- UV包管理器
- 异步处理

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

