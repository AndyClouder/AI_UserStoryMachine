"""
AI User Story Machine - Web应用
基于StoryMachine的云端用户故事生成器
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import asyncio
import tempfile
import os
import sys
from pathlib import Path
import uuid
import json
from typing import Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 存储任务状态
tasks = {}

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class StoryRequest(BaseModel):
    prd_content: str
    tech_spec_content: Optional[str] = ""
    repo_url: Optional[str] = ""

# Web界面HTML
WEB_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI User Story Machine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .loading {
            display: none;
        }
        .results {
            display: none;
        }
        .story-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <!-- 头部 -->
        <header class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">🤖 AI User Story Machine</h1>
            <p class="text-gray-600">基于StoryMachine的智能用户故事生成器</p>
        </header>

        <!-- 上传区域 -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 class="text-2xl font-semibold mb-4">📝 上传PRD文档</h2>

            <form id="uploadForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        PRD文档 (必需) <span class="text-red-500">*</span>
                    </label>
                    <input type="file"
                           id="prdFile"
                           accept=".md,.txt"
                           class="w-full p-2 border border-gray-300 rounded-md"
                           required>
                    <p class="text-sm text-gray-500 mt-1">支持 .md 和 .txt 格式</p>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        技术规格文档 (可选)
                    </label>
                    <input type="file"
                           id="techSpecFile"
                           accept=".md,.txt"
                           class="w-full p-2 border border-gray-300 rounded-md">
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        GitHub仓库URL (可选)
                    </label>
                    <input type="url"
                           id="repoUrl"
                           placeholder="https://github.com/owner/repo"
                           class="w-full p-2 border border-gray-300 rounded-md">
                </div>

                <button type="submit"
                        class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition">
                    🚀 生成用户故事
                </button>
            </form>
        </div>

        <!-- 加载状态 -->
        <div id="loading" class="loading bg-white rounded-lg shadow-md p-6 mb-6">
            <div class="text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p class="text-gray-700">🤖 AI正在分析您的文档并生成用户故事...</p>
                <p class="text-sm text-gray-500 mt-2">这可能需要几分钟时间，请耐心等待</p>
            </div>
        </div>

        <!-- 结果显示 -->
        <div id="results" class="results">
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-2xl font-semibold mb-4">📋 生成的用户故事</h2>
                <div id="storiesContainer"></div>
            </div>
        </div>

        <!-- 错误信息 -->
        <div id="errorMessage" class="hidden bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p class="text-red-800"></p>
        </div>
    </div>

    <script>
        let currentTaskId = null;

        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const prdFile = document.getElementById('prdFile').files[0];
            const techSpecFile = document.getElementById('techSpecFile').files[0];
            const repoUrl = document.getElementById('repoUrl').value;

            if (!prdFile) {
                showError('请上传PRD文档');
                return;
            }

            try {
                // 显示加载状态
                showLoading();
                hideError();

                // 创建FormData
                const formData = new FormData();
                formData.append('prd_file', prdFile);
                if (techSpecFile) {
                    formData.append('tech_spec_file', techSpecFile);
                }
                if (repoUrl) {
                    formData.append('repo_url', repoUrl);
                }

                // 提交任务
                const response = await fetch('/generate-stories', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                currentTaskId = result.task_id;

                // 开始轮询任务状态
                pollTaskStatus(currentTaskId);

            } catch (error) {
                showError('提交失败: ' + error.message);
                hideLoading();
            }
        });

        async function pollTaskStatus(taskId) {
            try {
                const response = await fetch(`/task-status/${taskId}`);
                const result = await response.json();

                if (result.status === 'completed') {
                    hideLoading();
                    showResults(result.stories);
                } else if (result.status === 'failed') {
                    hideLoading();
                    showError('生成失败: ' + result.message);
                } else {
                    // 继续轮询
                    setTimeout(() => pollTaskStatus(taskId), 2000);
                }
            } catch (error) {
                hideLoading();
                showError('获取状态失败: ' + error.message);
            }
        }

        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
        }

        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }

        function showResults(stories) {
            const container = document.getElementById('storiesContainer');
            container.innerHTML = '';

            if (stories && stories.length > 0) {
                stories.forEach((story, index) => {
                    const storyCard = document.createElement('div');
                    storyCard.className = 'story-card';
                    storyCard.innerHTML = `
                        <h3 class="text-lg font-semibold mb-2">📌 故事 ${index + 1}: ${story.title || '未命名故事'}</h3>
                        <p class="text-gray-700 mb-2">${story.description || '暂无描述'}</p>
                        ${story.acceptance_criteria ? `
                            <div class="mt-3">
                                <h4 class="font-medium text-sm text-gray-600 mb-1">验收标准:</h4>
                                <ul class="list-disc list-inside text-sm text-gray-600">
                                    ${story.acceptance_criteria.map(criteria => `<li>${criteria}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    `;
                    container.appendChild(storyCard);
                });
            } else {
                container.innerHTML = '<p class="text-gray-500">未生成用户故事</p>';
            }

            document.getElementById('results').style.display = 'block';
        }

        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.querySelector('p').textContent = message;
            errorDiv.classList.remove('hidden');
        }

        function hideError() {
            document.getElementById('errorMessage').classList.add('hidden');
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """返回Web界面"""
    return WEB_HTML

@app.post("/generate-stories", response_model=TaskResponse)
async def generate_stories(
    background_tasks: BackgroundTasks,
    prd_file: UploadFile = File(...),
    tech_spec_file: Optional[UploadFile] = File(None),
    repo_url: Optional[str] = Form(None)
):
    """生成用户故事API端点"""
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())

        # 初始化任务状态
        tasks[task_id] = {
            "status": "processing",
            "message": "开始处理文件...",
            "stories": []
        }

        # 读取上传的文件内容
        prd_content = await prd_file.read()
        prd_text = prd_content.decode('utf-8')

        tech_spec_text = ""
        if tech_spec_file:
            tech_spec_content = await tech_spec_file.read()
            tech_spec_text = tech_spec_content.decode('utf-8')

        # 在后台处理任务
        background_tasks.add_task(
            process_story_generation,
            task_id,
            prd_text,
            tech_spec_text,
            repo_url or ""
        )

        return TaskResponse(
            task_id=task_id,
            status="processing",
            message="任务已提交，正在处理中..."
        )

    except Exception as e:
        logger.error(f"Error generating stories: {e}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    return tasks[task_id]

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "AI User Story Machine"}

@app.get("/info")
async def get_info():
    """获取应用信息"""
    return {
        "name": "AI User Story Machine",
        "description": "基于StoryMachine的云端用户故事生成器",
        "version": "1.0.0",
        "features": [
            "📝 上传PRD文档",
            "🤖 AI自动生成用户故事",
            "📋 详细验收标准",
            "☁️ 云端处理",
            "🌐 简洁Web界面"
        ]
    }

async def process_story_generation(task_id: str, prd_content: str, tech_spec_content: str, repo_url: str):
    """后台处理用户故事生成"""
    try:
        # 更新任务状态
        tasks[task_id]["message"] = "正在调用AI生成用户故事..."

        # 这里我们暂时返回示例数据，实际可以集成您的StoryMachine CLI
        # 模拟AI处理时间
        await asyncio.sleep(5)

        # 示例生成的用户故事
        sample_stories = [
            {
                "title": "用户注册功能",
                "description": "新用户可以通过邮箱或手机号注册账户",
                "acceptance_criteria": [
                    "用户可以使用有效的邮箱地址注册",
                    "用户可以使用有效的手机号注册",
                    "注册后需要验证邮箱或手机号",
                    "密码需要符合安全要求",
                    "注册成功后自动登录"
                ]
            },
            {
                "title": "用户登录功能",
                "description": "已注册用户可以通过邮箱/手机号和密码登录系统",
                "acceptance_criteria": [
                    "用户可以使用邮箱和密码登录",
                    "用户可以使用手机号和密码登录",
                    "支持记住登录状态",
                    "登录失败时显示错误信息",
                    "支持忘记密码功能"
                ]
            },
            {
                "title": "个人资料管理",
                "description": "用户可以查看和编辑个人基本信息",
                "acceptance_criteria": [
                    "用户可以查看个人资料",
                    "用户可以修改昵称、头像等基本信息",
                    "修改信息后需要保存",
                    "敏感信息修改需要验证身份"
                ]
            }
        ]

        # 更新任务完成状态
        tasks[task_id] = {
            "status": "completed",
            "message": "用户故事生成完成！",
            "stories": sample_stories
        }

    except Exception as e:
        logger.error(f"Error processing story generation: {e}")
        tasks[task_id] = {
            "status": "failed",
            "message": f"生成失败: {str(e)}",
            "stories": []
        }

# Vercel入口点
handler = app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)