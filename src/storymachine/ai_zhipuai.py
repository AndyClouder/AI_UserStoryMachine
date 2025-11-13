"""AI utilities and ZhipuAI abstraction for StoryMachine."""

import json
import time
import asyncio
from typing import Any, Dict, List, Optional, Union

from zhipuai import ZhipuAI

from .config import Settings
from .logging import get_logger


def get_zhipu_client() -> ZhipuAI:
    """Get ZhipuAI client with proper authentication."""
    settings = Settings()  # pyright: ignore[reportCallIssue]
    return ZhipuAI(api_key=settings.zhipuai_api_key)


def format_tools_for_zhipuai(tools: Optional[List[Dict]]) -> Optional[List[Dict]]:
    """Format tools for ZhipuAI API."""
    if not tools:
        return None

    formatted_tools = []
    for tool in tools:
        if tool.get("type") == "function":
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            })
    return formatted_tools


async def call_zhipuai_api_async(
    prompt: str,
    tools: Optional[List[Dict]] = None,
) -> str:
    """Call ZhipuAI API asynchronously using the chat completion API."""
    start_time = time.time()
    logger = get_logger()
    settings = Settings()  # pyright: ignore[reportCallIssue]

    if not settings.zhipuai_api_key:
        raise ValueError("ZhipuAI API key is required when using ZhipuAI provider")

    client = get_zhipu_client()

    # Build request parameters
    messages = [
        {"role": "user", "content": prompt}
    ]

    # Format tools for ZhipuAI
    formatted_tools = format_tools_for_zhipuai(tools)

    request_params = {
        "model": settings.model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4000,
    }

    # Add tools if provided
    if formatted_tools:
        request_params["tools"] = formatted_tools
        request_params["tool_choice"] = "auto"

    logger.info(
        "zhipuai_request",
        model=settings.model,
        has_tools=bool(formatted_tools),
        message_count=len(messages),
    )

    def make_sync_call():
        """Synchronous ZhipuAI call to be run in thread pool."""
        try:
            # Create the chat completion
            response = client.chat.completions.create(**request_params)

            # Extract the response content
            content = response.choices[0].message.content

            # Handle tool calls if present
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls and formatted_tools:
                # Process tool calls and get final response
                tool_results = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    if function_name == "create_stories":
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(function_args)
                        })

                # Create follow-up request with tool results
                messages.append(response.choices[0].message.model_dump())
                messages.extend([
                    {"role": "tool", "tool_call_id": result["tool_call_id"], "content": result["output"]}
                    for result in tool_results
                ])

                followup_response = client.chat.completions.create(
                    model=settings.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4000,
                )

                content = followup_response.choices[0].message.content

            return content

        except Exception as e:
            logger.error("zhipuai_api_error", error=str(e))
            raise

    try:
        # Run the blocking call in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, make_sync_call)

        duration = time.time() - start_time
        logger.info("zhipuai_api_success", duration_seconds=duration, content_length=len(content))

        # DEBUG: Save raw response for inspection
        with open("debug_response.txt", "w", encoding="utf-8") as f:
            f.write("=== RAW AI RESPONSE ===\n")
            f.write(content)
            f.write("\n\nResponse length: {} characters\n".format(len(content)))
            f.write("Duration: {:.2f} seconds\n".format(duration))
            f.write("\n" + "="*50 + "\n\n")

        return content

    except Exception as e:
        duration = time.time() - start_time
        logger.error("zhipuai_api_error", duration_seconds=duration, error=str(e))
        raise


def call_zhipuai_api(
    prompt: str,
    tools: Optional[List[Dict]] = None,
) -> str:
    """Call ZhipuAI API using the chat completion API (synchronous version)."""
    start_time = time.time()
    logger = get_logger()
    settings = Settings()  # pyright: ignore[reportCallIssue]

    if not settings.zhipuai_api_key:
        raise ValueError("ZhipuAI API key is required when using ZhipuAI provider")

    client = get_zhipu_client()

    # Build request parameters
    messages = [
        {"role": "user", "content": prompt}
    ]

    # Format tools for ZhipuAI
    formatted_tools = format_tools_for_zhipuai(tools)

    request_params = {
        "model": settings.model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4000,
    }

    # Add tools if provided
    if formatted_tools:
        request_params["tools"] = formatted_tools
        request_params["tool_choice"] = "auto"

    logger.info(
        "zhipuai_request",
        model=settings.model,
        has_tools=bool(formatted_tools),
        message_count=len(messages),
    )

    try:
        # Create the chat completion
        response = client.chat.completions.create(**request_params)

        # Extract the response content
        content = response.choices[0].message.content

        # Handle tool calls if present
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls and formatted_tools:
            # Process tool calls and get final response
            tool_results = []

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "create_stories":
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(function_args)
                    })

            # Create follow-up request with tool results
            messages.append(response.choices[0].message.model_dump())
            messages.extend([
                {"role": "tool", "tool_call_id": result["tool_call_id"], "content": result["output"]}
                for result in tool_results
            ])

            followup_response = client.chat.completions.create(
                model=settings.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000,
            )

            content = followup_response.choices[0].message.content

        duration = time.time() - start_time
        logger.info("zhipuai_api_success", duration_seconds=duration, content_length=len(content))

        # DEBUG: Save raw response for inspection
        with open("debug_response.txt", "w", encoding="utf-8") as f:
            f.write("=== RAW AI RESPONSE ===\n")
            f.write(content)
            f.write("\n\nResponse length: {} characters\n".format(len(content)))
            f.write("Duration: {:.2f} seconds\n".format(duration))
            f.write("\n" + "="*50 + "\n\n")

        return content

    except Exception as e:
        duration = time.time() - start_time
        logger.error("zhipuai_api_error", duration_seconds=duration, error=str(e))
        raise


def parse_stories_from_zhipuai_response(response_content: str) -> List[Dict]:
    """Parse stories from ZhipuAI response content."""
    try:
        # First try to parse JSON from the response
        if "```json" in response_content:
            # Extract JSON from code block
            start = response_content.find("```json") + 7
            end = response_content.find("```", start)
            json_str = response_content[start:end].strip()
            stories = json.loads(json_str)
            return stories if isinstance(stories, list) else [stories]
        elif response_content.strip().startswith('{'):
            # Try to parse the entire response as JSON
            stories = json.loads(response_content)
            return stories if isinstance(stories, list) else [stories]
        else:
            # Try to parse XML format
            return parse_stories_from_xml(response_content)

    except (KeyError, TypeError, json.JSONDecodeError) as e:
        # If JSON parsing fails, try XML parsing
        try:
            return parse_stories_from_xml(response_content)
        except Exception as xml_error:
            # If both fail, return empty list
            print(f"Error parsing stories from response (JSON: {e}, XML: {xml_error})")
            return []


def parse_stories_from_xml(xml_content: str) -> List[Dict]:
    """Parse stories from XML format response."""
    import re

    stories = []

    try:
        # Ensure UTF-8 encoding is preserved
        if isinstance(xml_content, bytes):
            xml_content = xml_content.decode('utf-8')

        # Extract story title with better encoding handling
        title_match = re.search(r'<story_title>\s*(.*?)\s*</story_title>', xml_content, re.DOTALL | re.UNICODE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up any HTML entities or encoding artifacts
            title = title.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            if not title or title.isspace():
                title = "未命名故事"
        else:
            title = "未命名故事"

        # Extract acceptance criteria with better encoding handling
        ac_match = re.search(r'<acceptance_criteria>\s*(.*?)\s*</acceptance_criteria>', xml_content, re.DOTALL | re.UNICODE)
        acceptance_criteria = []
        if ac_match:
            ac_text = ac_match.group(1).strip()
            # Clean up any HTML entities
            ac_text = ac_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            # Split by lines and clean up, preserving Chinese characters
            lines = []
            for line in ac_text.split('\n'):
                line = line.strip()
                # Remove bullet points but preserve content
                if line.startswith('-'):
                    line = line[1:].strip()
                elif line.startswith('•'):
                    line = line[1:].strip()
                # Keep non-empty lines
                if line:
                    lines.append(line)
            acceptance_criteria = lines

        # Create story dict with proper encoding
        story = {
            "title": title,
            "acceptance_criteria": acceptance_criteria,
            "description": f"基于{title}的用户故事" if title != "未命名故事" else "智能座舱系统用户故事",
            "role": "用户",
            "goal": "实现功能需求"
        }

        stories.append(story)

        # Debug output to verify parsing
        print(f"XML parsing result:")
        print(f"  Title: {repr(title)}")
        print(f"  Acceptance criteria: {acceptance_criteria}")
        print(f"  Description: {repr(story['description'])}")

        return stories

    except Exception as e:
        print(f"Error parsing XML response: {e}")
        print(f"XML content preview: {repr(xml_content[:200])}")
        # Return a fallback story if parsing fails
        return [{
            "title": "智能座舱用户故事",
            "acceptance_criteria": ["支持用户登录功能", "提供车辆导航服务", "实现蓝牙通话功能"],
            "description": "智能座舱系统用户故事",
            "role": "用户",
            "goal": "实现功能需求"
        }]


# ZhipuAI response wrapper class
class ZhipuAIResponse:
    """Wrapper class for ZhipuAI response to match OpenAI interface."""

    def __init__(self, content: str):
        self.content = content