"""Simple Web interface for StoryMachine using FastAPI."""

from pathlib import Path
from typing import List, Optional
import asyncio
import json
import uuid
import io

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .types import WorkflowInput, FeedbackStatus, Story
from .workflow import w1
from .activities import (
    get_codebase_context,
    problem_break_down,
    define_acceptance_criteria,
    enrich_context,
)


# Create FastAPI app
app = FastAPI(title="StoryMachine Web Interface", description="AI用户故事生成器网页版")

# Set up templates (we'll create the template inline)
templates = {}


class WebWorkflow:
    """Web-friendly wrapper for the StoryMachine workflow."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.stories: List[Story] = []
        self.current_stage = "starting"
        self.feedback_history = []

    async def run_workflow(self, workflow_input: WorkflowInput) -> List[Story]:
        """Run the web-friendly workflow without CLI interactions."""
        try:
            print(f"Starting web workflow for session {self.session_id}")
            print(f"PRD content length: {len(workflow_input.prd_content)}")

            # Add repository context if provided (simplified for web)
            if workflow_input.repo_url:
                print("Getting codebase context...")
                workflow_input.repo_context = await get_codebase_context(workflow_input)
                print(f"Codebase context length: {len(workflow_input.repo_context)}")
            else:
                workflow_input.repo_context = ""
                print("No repository URL provided, skipping codebase context")

            # Generate stories using the existing function - run in thread pool to avoid blocking
            print("Starting problem breakdown...")

            # Run the synchronous problem_breakdown in a thread pool
            import asyncio
            loop = asyncio.get_event_loop()
            self.stories = await loop.run_in_executor(None, problem_break_down, workflow_input, [], "")
            print(f"Generated {len(self.stories)} stories")

            # For each story, generate acceptance criteria and enrich context without CLI interaction
            for i, story in enumerate(self.stories):
                print(f"Processing story {i+1}: {story.title}")

                # Generate acceptance criteria (no user feedback needed for web version)
                print("Defining acceptance criteria...")
                updated_story = await loop.run_in_executor(None, define_acceptance_criteria, story, "")

                # Enrich context (no user feedback needed for web version)
                print("Enriching context...")
                updated_story = await loop.run_in_executor(None, enrich_context, updated_story, workflow_input, "")

                self.stories[i] = updated_story
                print(f"Story {i+1} processed successfully")

            print(f"Web workflow completed. Total stories: {len(self.stories)}")
            return self.stories

        except Exception as e:
            print(f"Web workflow error: {e}")
            import traceback
            traceback.print_exc()
            # Return a dummy story for debugging
            from .types import Story
            dummy_story = Story(
                title="调试故事",
                description=f"这是一个调试故事。错误信息: {str(e)}",
                role="调试者",
                goal="调试网页版功能",
                acceptance_criteria=["能够看到这个故事"]
            )
            return [dummy_story]


# Session storage
active_sessions = {}


@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify server is working."""
    return {"message": "Server is working!"}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Main page with upload form."""

    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>StoryMachine - AI用户故事生成器</title>
        <style>
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
                max-width: 1000px;
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

            .btn-success {
                background-color: #28a745;
                margin-left: 10px;
            }

            .btn-success:hover {
                background-color: #1e7e34;
            }

            .loading {
                display: none;
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

            .results-section {
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

            .debug-info {
                color: #6c757d;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 12px;
                border-radius: 4px;
                margin: 10px 0;
                font-family: monospace;
                font-size: 12px;
                white-space: pre-wrap;
            }
        </style>
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
                    <button type="button" class="btn" id="testBtn" style="background: #6c757d; margin-left: 10px;">测试API连接</button>
                    <button type="button" class="btn btn-success" id="downloadBtn" style="display: none;">下载 Markdown 文件</button>
                </form>
            </div>

            <div class="loading" id="loadingSection">
                <div class="spinner"></div>
                <p>正在分析文档并生成用户故事，请稍候...</p>
            </div>

            <div class="results-section" id="resultsSection">
                <h2>生成的用户故事</h2>
                <div id="storiesContainer"></div>
            </div>
        </div>

        <script>
            let currentStories = [];
            let sessionId = null;

            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                console.log('=== FORM SUBMIT EVENT TRIGGERED ===');
                e.preventDefault();
                console.log('Default prevented');

                console.log('Getting file inputs...');
                const prdFileInput = document.getElementById('prdFile');
                const techSpecFileInput = document.getElementById('techSpecFile');
                const repoUrlInput = document.getElementById('repoUrl');

                console.log('PRD file input:', prdFileInput);
                console.log('PRD files:', prdFileInput.files);
                console.log('PRD first file:', prdFileInput.files[0]);

                const prdFile = prdFileInput.files[0];
                const techSpecFile = techSpecFileInput.files[0];
                const repoUrl = repoUrlInput.value;

                console.log('File values:', { prdFile, techSpecFile, repoUrl });

                if (!prdFile) {
                    console.log('ERROR: No PRD file selected');
                    alert('请选择PRD文档');
                    return;
                }

                console.log('Creating FormData...');
                const formData = new FormData();
                formData.append('prd_file', prdFile);
                console.log('Added prd_file to FormData');

                if (techSpecFile) {
                    formData.append('tech_spec_file', techSpecFile);
                    console.log('Added tech_spec_file to FormData');
                }
                if (repoUrl) {
                    formData.append('repo_url', repoUrl);
                    console.log('Added repo_url to FormData');
                }

                console.log('FormData created successfully');
                console.log(' FormData entries:');
                for (let [key, value] of formData.entries()) {
                    console.log(`  ${key}:`, value);
                }

                // Show loading
                document.getElementById('uploadSection').style.display = 'none';
                document.getElementById('loadingSection').style.display = 'block';
                document.getElementById('resultsSection').style.display = 'none';
                document.getElementById('downloadBtn').style.display = 'none';

                try {
                    console.log('=== STARTING FETCH REQUEST ===');
                    console.log('URL: /api/generate-stories');
                    console.log('Method: POST');
                    console.log('FormData entries:');
                    for (let [key, value] of formData.entries()) {
                        console.log(`  ${key}:`, value.name || value);
                    }

                    console.log('Sending fetch request...');
                    const response = await fetch('/api/generate-stories', {
                        method: 'POST',
                        body: formData
                    });

                    console.log('=== FETCH RESPONSE RECEIVED ===');
                    console.log('Response status:', response.status);
                    console.log('Response ok:', response.ok);
                    console.log('Response headers:', response.headers);

                    const result = await response.json();

                    console.log('=== API RESPONSE RECEIVED ===');
                  console.log('Response result:', result);
                  console.log('result.success:', result.success);
                  console.log('result.stories:', result.stories);
                  console.log('result.session_id:', result.session_id);

                  if (result.success) {
                        currentStories = result.stories || [];
                        sessionId = result.session_id;

                        console.log('About to call displayStories with:', currentStories);
                        displayStories();

                        document.getElementById('loadingSection').style.display = 'none';
                        document.getElementById('resultsSection').style.display = 'block';
                        document.getElementById('downloadBtn').style.display = 'inline-block';

                        console.log('Stories generated successfully:', result);
                        console.log('SUCCESS: Stories should now be visible');
                    } else {
                        console.error('=== API RESPONSE ERROR ===');
                        console.error('Error:', result.error);
                        console.error('Details:', result.error_details);

                        // Display error in the UI instead of just alert
                        currentStories = [];
                        displayStories();

                        document.getElementById('loadingSection').style.display = 'none';
                        document.getElementById('resultsSection').style.display = 'block';

                        // Add error message to the container
                        const container = document.getElementById('storiesContainer');
                        container.innerHTML = `
                            <div class="story-card" style="border-left: 4px solid #dc3545; background: #f8d7da;">
                                <div class="story-title">❌ 生成失败</div>
                                <div class="story-content">
                                    <p><strong>错误信息：</strong> ${result.error}</p>
                                    ${result.error_details ? `
                                    <details>
                                        <summary style="cursor: pointer;">查看详细错误信息</summary>
                                        <pre style="background: #f8d7da; padding: 10px; border-radius: 4px; margin-top: 10px; white-space: pre-wrap;">${result.error_details}</pre>
                                    </details>
                                    ` : ''}
                                </div>
                            </div>
                        `;

                        alert(`生成失败: ${result.error}`);
                    }
                } catch (error) {
                    console.error('=== CATCH BLOCK ERROR ===');
                    console.error('Error object:', error);
                    console.error('Error message:', error.message);
                    console.error('Error stack:', error.stack);

                    // Display error in UI
                    currentStories = [];
                    displayStories();

                    document.getElementById('loadingSection').style.display = 'none';
                    document.getElementById('resultsSection').style.display = 'block';

                    const container = document.getElementById('storiesContainer');
                    container.innerHTML = `
                        <div class="story-card" style="border-left: 4px solid #dc3545; background: #f8d7da;">
                            <div class="story-title">❌ 网络请求失败</div>
                            <div class="story-content">
                                <p><strong>错误类型：</strong> 前端请求异常</p>
                                <p><strong>错误信息：</strong> ${error.message}</p>
                                <p><strong>可能原因：</strong></p>
                                <ul>
                                    <li>网络连接问题</li>
                                    <li>服务器未响应</li>
                                    <li>CORS跨域问题</li>
                                    <li>服务器内部错误</li>
                                </ul>
                                <details>
                                    <summary style="cursor: pointer;">查看技术详情</summary>
                                    <pre style="background: #f8d7da; padding: 10px; border-radius: 4px; margin-top: 10px; white-space: pre-wrap;">${error.stack}</pre>
                                </details>
                            </div>
                        </div>
                    `;

                    alert('生成用户故事失败: ' + error.message);
                    // Reset UI
                    document.getElementById('uploadSection').style.display = 'block';
                }
            });

            function displayStories() {
                const container = document.getElementById('storiesContainer');
                container.innerHTML = '';

                console.log('=== DEBUG: displayStories called ===');
                console.log('currentStories:', currentStories);
                console.log('currentStories type:', typeof currentStories);
                console.log('currentStories length:', currentStories ? currentStories.length : 'null');

                // Always show the results section, even if no stories
                document.getElementById('resultsSection').style.display = 'block';

                if (!currentStories || currentStories.length === 0) {
                    container.innerHTML = `
                        <div class="story-card">
                            <div class="story-title">系统消息</div>
                            <div class="story-content">
                                <p><strong>状态：</strong> 没有找到生成的用户故事</p>
                                <p><strong>可能原因：</strong></p>
                                <ul>
                                    <li>API调用失败，请检查网络连接</li>
                                    <li>后端服务异常，请查看服务器日志</li>
                                    <li>PRD文档格式不正确或内容为空</li>
                                </ul>
                                <p><strong>调试信息：</strong></p>
                                <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
故事数量: ${currentStories ? currentStories.length : 'null'}
故事数据: ${JSON.stringify(currentStories, null, 2)}
                                </pre>
                            </div>
                        </div>
                    `;
                    return;
                }

                console.log(`=== 开始处理 ${currentStories.length} 个故事 ===`);

                currentStories.forEach((story, index) => {
                    console.log(`Processing story ${index}:`, story);

                    const storyCard = document.createElement('div');
                    storyCard.className = 'story-card';

                    // 更宽松的数据检查 - 只要有数据就显示
                    const title = story.title || `用户故事 ${index + 1}`;
                    const description = story.description || story.summary || '暂无描述';
                    const role = story.role || '用户';
                    const goal = story.goal || '完成目标';

                    storyCard.innerHTML = `
                        <div class="story-title">${index + 1}. ${title}</div>
                        <div class="story-content">
                            <p><strong>用户故事：</strong> ${description}</p>
                            <p><strong>角色：</strong> ${role}</p>
                            <p><strong>目标：</strong> ${goal}</p>
                        </div>
                        ${story.acceptance_criteria && story.acceptance_criteria.length > 0 ? `
                        <div class="acceptance-criteria">
                            <h4>验收标准：</h4>
                            <ul>
                                ${story.acceptance_criteria.map(ac => `<li>${ac}</li>`).join('')}
                            </ul>
                        </div>
                        ` : '<div style="color: #666; font-style: italic; margin: 10px 0;">验收标准：暂无</div>'}

                        <!-- 调试信息 -->
                        <details style="margin-top: 10px;">
                            <summary style="cursor: pointer; color: #666;">调试信息 (点击展开)</summary>
                            <pre style="background: #f5f5f5; padding: 8px; border-radius: 4px; font-size: 11px; margin-top: 5px;">
${JSON.stringify(story, null, 2)}
                            </pre>
                        </details>
                    `;

                    container.appendChild(storyCard);
                    console.log(`Story ${index + 1} added to DOM`);
                });

                console.log('=== displayStories completed ===');
            }

            // Test API button
            document.getElementById('testBtn').addEventListener('click', async () => {
                console.log('=== TEST BUTTON CLICKED ===');
                try {
                    console.log('Testing /test endpoint...');
                    const response = await fetch('/test');
                    console.log('Test response status:', response.status);
                    const result = await response.json();
                    console.log('Test response:', result);
                    alert('API测试成功: ' + result.message);
                } catch (error) {
                    console.error('Test API error:', error);
                    alert('API测试失败: ' + error.message);
                }
            });

            document.getElementById('downloadBtn').addEventListener('click', async () => {
                if (!sessionId) return;

                try {
                    const response = await fetch(`/api/download/${sessionId}`);
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


@app.post("/api/generate-stories")
async def generate_stories(
    prd_file: UploadFile = File(...),
    tech_spec_file: Optional[UploadFile] = File(None),
    repo_url: Optional[str] = None
):
    """Generate stories from uploaded files."""

    try:
        print("Starting API request to generate stories")

        # Read PRD content
        prd_content = await prd_file.read()
        prd_text = prd_content.decode('utf-8')
        print(f"PRD file read successfully, size: {len(prd_text)} bytes")

        # Read tech spec content if provided
        tech_spec_text = ""
        if tech_spec_file:
            tech_spec_content = await tech_spec_file.read()
            tech_spec_text = tech_spec_content.decode('utf-8')
            print(f"Tech spec file read successfully, size: {len(tech_spec_text)} bytes")

        # Create workflow input
        workflow_input = WorkflowInput(
            prd_content=prd_text,
            tech_spec_content=tech_spec_text,
            repo_url=repo_url or ""
        )
        print(f"Workflow input created, repo_url: {repo_url}")

        # Create session and workflow
        session_id = str(uuid.uuid4())
        web_workflow = WebWorkflow(session_id)
        active_sessions[session_id] = web_workflow
        print(f"Session created: {session_id}")

        # Run workflow
        stories = await web_workflow.run_workflow(workflow_input)
        print(f"Workflow completed, returned {len(stories)} stories")

        # Convert stories to dict format for JSON response
        stories_dict = []
        for i, story in enumerate(stories):
            # Debug story object structure
            print(f"Story {i+1} raw object: {story}")
            print(f"Story {i+1} type: {type(story)}")
            print(f"Story {i+1} attributes: {dir(story)}")

            story_dict = {
                "title": getattr(story, 'title', f'用户故事 {i+1}'),
                "description": getattr(story, 'description', story.summary if hasattr(story, 'summary') else '暂无描述'),
                "role": getattr(story, 'role', '用户'),
                "goal": getattr(story, 'goal', '完成目标'),
                "acceptance_criteria": getattr(story, 'acceptance_criteria', [])
            }
            stories_dict.append(story_dict)
            print(f"Story {i+1} converted: {story_dict}")

        print(f"API request completed successfully")
        return {
            "success": True,
            "session_id": session_id,
            "stories": stories_dict,
            "count": len(stories_dict)
        }

    except Exception as e:
        print(f"Error generating stories: {e}")
        import traceback
        traceback.print_exc()

        # Return error response
        return {
            "success": False,
            "error": str(e),
            "error_details": traceback.format_exc()
        }


@app.get("/api/download/{session_id}")
async def download_stories(session_id: str):
    """Download stories as Markdown file."""

    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    web_workflow = active_sessions[session_id]
    stories = web_workflow.stories

    # Generate Markdown content
    markdown_content = "# 用户故事\n\n"

    for i, story in enumerate(stories, 1):
        markdown_content += f"## {i}. {story.title}\n\n"
        markdown_content += f"**用户故事：** {story.description}\n\n"
        markdown_content += f"**角色：** {story.role}\n\n"
        markdown_content += f"**目标：** {story.goal}\n\n"

        if hasattr(story, 'acceptance_criteria') and story.acceptance_criteria:
            markdown_content += "**验收标准：**\n\n"
            for ac in story.acceptance_criteria:
                markdown_content += f"- {ac}\n"
            markdown_content += "\n"

        markdown_content += "---\n\n"

    # Create streaming response
    return StreamingResponse(
        io.StringIO(markdown_content),
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=user_stories.md"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)