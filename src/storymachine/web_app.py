"""Web interface for StoryMachine using FastAPI and FastHTML."""

from pathlib import Path
from typing import List, Optional
import asyncio
import json
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fasthtml.common import fasthtml, H1, H2, P, Div, Form, Input, Textarea, Button, Script, Style
from pydantic import BaseModel
import io

from .types import WorkflowInput, FeedbackStatus, Story
from .activities import (
    get_codebase_context,
    problem_break_down,
    define_acceptance_criteria,
    enrich_context,
)
from .config import Settings


# Pydantic models for API requests/responses
class WorkflowRequest(BaseModel):
    prd_content: str
    tech_spec_content: Optional[str] = ""
    repo_url: Optional[str] = ""


class FeedbackRequest(BaseModel):
    status: str  # "accepted" or "rejected"
    comment: Optional[str] = ""


# Global variables to track workflow state
workflow_states = {}


# Create FastHTML app
app = fasthtml()

# Custom CSS for clean Google-style interface
custom_css = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #ffffff;
    color: #333333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    text-align: center;
    margin-bottom: 40px;
    padding: 20px 0;
    border-bottom: 1px solid #e0e0e0;
}

.header h1 {
    font-size: 2.5rem;
    font-weight: 300;
    color: #1a73e8;
    margin-bottom: 10px;
}

.header p {
    font-size: 1.1rem;
    color: #666666;
}

.upload-section {
    background: #f8f9fa;
    padding: 30px;
    border-radius: 8px;
    margin-bottom: 30px;
    border: 1px solid #e0e0e0;
}

.upload-section h2 {
    font-size: 1.5rem;
    font-weight: 400;
    margin-bottom: 20px;
    color: #333333;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #333333;
}

.form-control {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    transition: border-color 0.3s ease;
}

.form-control:focus {
    outline: none;
    border-color: #1a73e8;
    box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.1);
}

.btn {
    background-color: #1a73e8;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background-color 0.3s ease;
}

.btn:hover {
    background-color: #1557b0;
}

.btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.btn-secondary {
    background-color: #6c757d;
}

.btn-secondary:hover {
    background-color: #545b62;
}

.btn-success {
    background-color: #28a745;
}

.btn-success:hover {
    background-color: #1e7e34;
}

.btn-danger {
    background-color: #dc3545;
}

.btn-danger:hover {
    background-color: #c82333;
}

.story-section {
    display: none;
    margin-top: 30px;
}

.story-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.story-title {
    font-size: 1.3rem;
    font-weight: 500;
    color: #1a73e8;
    margin-bottom: 15px;
}

.story-content {
    margin-bottom: 20px;
}

.acceptance-criteria {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 4px;
    margin-top: 15px;
}

.acceptance-criteria h4 {
    margin-bottom: 10px;
    color: #333333;
}

.acceptance-criteria ul {
    margin-left: 20px;
}

.feedback-section {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #e0e0e0;
}

.feedback-buttons {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.comment-box {
    display: none;
    margin-top: 15px;
}

.loading {
    text-align: center;
    padding: 40px;
    color: #666666;
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #1a73e8;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 2s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.download-section {
    text-align: center;
    margin-top: 30px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.error {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    padding: 12px;
    border-radius: 4px;
    margin: 10px 0;
}

.success {
    color: #155724;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 12px;
    border-radius: 4px;
    margin: 10px 0;
}
"""

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Main page with upload form and story interface."""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>StoryMachine - AI用户故事生成器</title>
        <style>{custom_css}</style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>StoryMachine</h1>
                <p>基于AI的用户故事生成器 - 从PRD文档自动生成高质量用户故事</p>
            </div>

            <div class="upload-section" id="uploadSection">
                <h2>上传产品需求文档</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="prdFile">PRD文档 * (支持 .md, .txt 格式)</label>
                        <input type="file" id="prdFile" name="prd_file" class="form-control" accept=".md,.txt" required>
                    </div>

                    <div class="form-group">
                        <label for="techSpecFile">技术规格文档 (可选)</label>
                        <input type="file" id="techSpecFile" name="tech_spec_file" class="form-control" accept=".md,.txt">
                    </div>

                    <div class="form-group">
                        <label for="repoUrl">GitHub仓库地址 (可选)</label>
                        <input type="url" id="repoUrl" name="repo_url" class="form-control" placeholder="https://github.com/owner/repo">
                    </div>

                    <button type="submit" class="btn" id="generateBtn">开始生成用户故事</button>
                </form>
            </div>

            <div class="loading" id="loadingSection" style="display: none;">
                <div class="spinner"></div>
                <p>正在分析文档并生成用户故事，请稍候...</p>
            </div>

            <div class="story-section" id="storySection">
                <h2>生成的用户故事</h2>
                <div id="storiesContainer"></div>

                <div class="download-section" id="downloadSection" style="display: none;">
                    <h3>下载用户故事</h3>
                    <button class="btn btn-success" id="downloadBtn">下载 Markdown 文件</button>
                </div>
            </div>
        </div>

        <script>
            let currentStories = [];
            let currentStoryIndex = 0;
            let sessionId = null;

            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const formData = new FormData();
                const prdFile = document.getElementById('prdFile').files[0];
                const techSpecFile = document.getElementById('techSpecFile').files[0];
                const repoUrl = document.getElementById('repoUrl').value;

                if (!prdFile) {
                    alert('请选择PRD文档');
                    return;
                }

                formData.append('prd_file', prdFile);
                if (techSpecFile) {
                    formData.append('tech_spec_file', techSpecFile);
                }
                if (repoUrl) {
                    formData.append('repo_url', repoUrl);
                }

                // Show loading
                document.getElementById('uploadSection').style.display = 'none';
                document.getElementById('loadingSection').style.display = 'block';
                document.getElementById('storySection').style.display = 'none';

                try {
                    // Start workflow
                    const response = await fetch('/api/workflow/start', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    if (result.success) {
                        sessionId = result.session_id;
                        await connectWebSocket();
                    } else {
                        throw new Error(result.error);
                    }
                } catch (error) {
                    alert('启动工作流失败: ' + error.message);
                    // Reset UI
                    document.getElementById('uploadSection').style.display = 'block';
                    document.getElementById('loadingSection').style.display = 'none';
                }
            });

            async function connectWebSocket() {
                const wsUrl = `ws://localhost:8000/ws/${{sessionId}}`;
                const ws = new WebSocket(wsUrl);

                ws.onmessage = async (event) => {
                    const data = JSON.parse(event.data);
                    await handleWebSocketMessage(data);
                };

                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    alert('WebSocket连接错误');
                };

                ws.onclose = () => {
                    console.log('WebSocket connection closed');
                };
            }

            async function handleWebSocketMessage(data) {
                const { type, content } = data;

                switch (type) {
                    case 'stories_generated':
                        currentStories = content.stories;
                        currentStoryIndex = 0;
                        document.getElementById('loadingSection').style.display = 'none';
                        document.getElementById('storySection').style.display = 'block';
                        displayStories();
                        break;

                    case 'story_detail':
                        if (currentStoryIndex < currentStories.length) {
                            currentStories[currentStoryIndex] = content.story;
                            displayCurrentStory();
                        }
                        break;

                    case 'workflow_completed':
                        document.getElementById('downloadSection').style.display = 'block';
                        break;

                    case 'error':
                        alert('处理过程中出现错误: ' + content.message);
                        break;
                }
            }

            function displayStories() {
                const container = document.getElementById('storiesContainer');
                container.innerHTML = '';

                currentStories.forEach((story, index) => (
                    displayStoryCard(story, index)
                ));
            }

            function displayStoryCard(story, index) {
                const container = document.getElementById('storiesContainer');
                const storyCard = document.createElement('div');
                storyCard.className = 'story-card';
                storyCard.id = `story-${{index}}`;

                storyCard.innerHTML = `
                    <div class="story-title">${{story.title}}</div>
                    <div class="story-content">
                        <p><strong>用户故事：</strong>${{story.description}}</p>
                        <p><strong>角色：</strong>${{story.role}}</p>
                        <p><strong>目标：</strong>${{story.goal}}</p>
                    </div>
                    <div class="acceptance-criteria" id="ac-${{index}}" style="display: none;">
                        <h4>验收标准：</h4>
                        <ul id="ac-list-${{index}}">
                        </ul>
                    </div>
                    <div class="feedback-section" id="feedback-${{index}}" style="display: none;">
                        <div class="feedback-buttons">
                            <button class="btn btn-success" onclick="approveStory(${{index}})">接受</button>
                            <button class="btn btn-danger" onclick="rejectStory(${{index}})">拒绝</button>
                        </div>
                        <div class="comment-box" id="comment-${{index}}">
                            <textarea class="form-control" rows="3" placeholder="请说明拒绝原因..."></textarea>
                            <button class="btn btn-secondary" onclick="submitFeedback(${{index}}, false)">提交反馈</button>
                        </div>
                    </div>
                `;

                container.appendChild(storyCard);
            }

            function displayCurrentStory() {
                const story = currentStories[currentStoryIndex];
                const index = currentStoryIndex;

                // Update story card
                const storyCard = document.getElementById(`story-${{index}}`);
                if (storyCard) {
                    displayStoryCard(story, index);
                }

                // Show acceptance criteria and feedback
                document.getElementById(`ac-${{index}}`).style.display = 'block';
                document.getElementById(`feedback-${{index}}`).style.display = 'block';

                // Update acceptance criteria list
                const acList = document.getElementById(`ac-list-${{index}}`);
                acList.innerHTML = '';
                if (story.acceptance_criteria) {
                    story.acceptance_criteria.forEach(ac => {
                        const li = document.createElement('li');
                        li.textContent = ac;
                        acList.appendChild(li);
                    });
                }
            }

            async function approveStory(index) {
                await submitFeedback(index, true);
            }

            async function rejectStory(index) {
                document.getElementById(`comment-${{index}}`).style.display = 'block';
            }

            async function submitFeedback(index, approved) {
                const comment = approved ? '' : document.querySelector(`#comment-${{index}} textarea`).value;

                try {
                    const response = await fetch('/api/feedback', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            session_id: sessionId,
                            story_index: index,
                            status: approved ? 'accepted' : 'rejected',
                            comment: comment
                        })
                    });

                    const result = await response.json();
                    if (result.success) {
                        currentStoryIndex++;
                        if (currentStoryIndex < currentStories.length) {
                            displayCurrentStory();
                        }
                    } else {
                        alert('提交反馈失败: ' + result.error);
                    }
                } catch (error) {
                    alert('提交反馈时出现错误: ' + error.message);
                }
            }

            document.getElementById('downloadBtn').addEventListener('click', async () => {
                try {
                    const response = await fetch(`/api/download/${{sessionId}}`);
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'user_stories.md';
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                    } else {
                        throw new Error('下载失败');
                    }
                } catch (error) {
                    alert('下载文件时出现错误: ' + error.message);
                }
            });
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.post("/api/workflow/start")
async def start_workflow(
    prd_file: UploadFile = File(...),
    tech_spec_file: Optional[UploadFile] = File(None),
    repo_url: Optional[str] = None
):
    """Start the StoryMachine workflow with uploaded files."""

    try:
        # Read PRD content
        prd_content = await prd_file.read()
        prd_text = prd_content.decode('utf-8')

        # Read tech spec content if provided
        tech_spec_text = ""
        if tech_spec_file:
            tech_spec_content = await tech_spec_file.read()
            tech_spec_text = tech_spec_content.decode('utf-8')

        # Create session
        session_id = str(uuid.uuid4())
        workflow_input = WorkflowInput(
            prd_content=prd_text,
            tech_spec_content=tech_spec_text,
            repo_url=repo_url or ""
        )

        # Store workflow state
        workflow_states[session_id] = {
            "input": workflow_input,
            "stories": [],
            "current_stage": "starting",
            "current_story_index": 0
        }

        # Start workflow in background
        asyncio.create_task(run_workflow_with_websocket(session_id, workflow_input))

        return {"success": True, "session_id": session_id}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/feedback")
async def submit_feedback(
    session_id: str,
    story_index: int,
    status: str,
    comment: Optional[str] = ""
):
    """Submit feedback for a story."""

    if session_id not in workflow_states:
        return {"success": False, "error": "Invalid session ID"}

    try:
        # Store feedback
        workflow_states[session_id]["feedback"] = {
            "story_index": story_index,
            "status": status,
            "comment": comment
        }

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/download/{session_id}")
async def download_stories(session_id: str):
    """Download stories as Markdown file."""

    if session_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Session not found")

    stories = workflow_states[session_id]["stories"]
    markdown_content = generate_markdown(stories)

    # Return file response
    return FileResponse(
        path=None,  # We'll create the content directly
        filename="user_stories.md",
        media_type="text/markdown",
        content=markdown_content.encode('utf-8')
    )


def generate_markdown(stories: List[Story]) -> str:
    """Generate Markdown content from stories."""

    content = "# 用户故事\n\n"

    for i, story in enumerate(stories, 1):
        content += f"## {i}. {story.title}\n\n"
        content += f"**用户故事：** {story.description}\n\n"
        content += f"**角色：** {story.role}\n\n"
        content += f"**目标：** {story.goal}\n\n"

        if story.acceptance_criteria:
            content += "**验收标准：**\n\n"
            for ac in story.acceptance_criteria:
                content += f"- {ac}\n"
            content += "\n"

        content += "---\n\n"

    return content


async def run_workflow_with_websocket(session_id: str, workflow_input: WorkflowInput):
    """Run the StoryMachine workflow and send updates via WebSocket."""

    try:
        # This is a simplified version that would need to be integrated
        # with the actual workflow logic
        stories = await w1(workflow_input)

        # Store stories
        if session_id in workflow_states:
            workflow_states[session_id]["stories"] = stories

        # Send completion message (this would be handled by WebSocket in real implementation)

    except Exception as e:
        print(f"Workflow error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)