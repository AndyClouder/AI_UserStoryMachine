"""
FastAPI应用入口文件 - 为Vercel部署准备
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import sys
import os

# 添加storymachine模块到Python路径
sys.path.insert(0, str(Path(__file__).parent / "storymachine" / "src"))

app = FastAPI(
    title="AI User Story Machine",
    description="基于StoryMachine的AI产品需求管理系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径 - 返回API信息"""
    return {
        "message": "AI User Story Machine API",
        "version": "1.0.0",
        "description": "基于StoryMachine的AI产品需求管理系统",
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

@app.get("/info")
async def get_info():
    """获取应用详细信息"""
    return {
        "name": "AI User Story Machine",
        "description": "基于StoryMachine的AI产品需求管理系统，支持智谱AI集成和中文本地化",
        "features": [
            "🤖 智谱AI集成，支持用户故事自动生成",
            "🇨🇳 完整的中文语言支持",
            "📝 从PRD文档自动生成用户故事",
            "🔧 详细的验收标准生成",
            "📊 项目上下文感知"
        ],
        "tech_stack": [
            "Python 3.13+",
            "FastAPI",
            "智谱AI API",
            "UV包管理器",
            "异步处理"
        ]
    }

# Vercel入口点
handler = app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)