"""AI utilities and ZhipuAI abstraction for StoryMachine."""

import json
import time
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


def parse_stories_from_zhipuai_response(response_content: str) -> List[Dict]:
    """Parse stories from ZhipuAI response content."""
    try:
        # DEBUG: Save raw response for inspection
        with open("debug_response.txt", "w", encoding="utf-8") as f:
            f.write("=== RAW AI RESPONSE ===\n")
            f.write(response_content)
            f.write("\n\nResponse length: {} characters\n".format(len(response_content)))
            f.write("\n" + "="*50 + "\n\n")
        # Try to parse JSON from the response
        if "```json" in response_content:
            # Extract JSON from code block
            start = response_content.find("```json") + 7
            end = response_content.find("```", start)
            json_str = response_content[start:end].strip()
        elif "{" in response_content:
            # Find JSON object in the text
            start = response_content.find("{")
            end = response_content.rfind("}") + 1
            json_str = response_content[start:end]
        else:
            with open("debug_response.txt", "a", encoding="utf-8") as f:
                f.write("DEBUG: No JSON found in response\n")
                f.write("Response preview: {}\n".format(response_content[:200]))
            return []

        # DEBUG: Log extracted JSON
        with open("debug_response.txt", "a", encoding="utf-8") as f:
            f.write("DEBUG: Extracted JSON string:\n{}\n\n".format(json_str))

        data = json.loads(json_str)

        # DEBUG: Log parsed data
        with open("debug_response.txt", "a", encoding="utf-8") as f:
            f.write("DEBUG: JSON parsed successfully\n")
            f.write("Data type: {}\n".format(type(data).__name__))
            if isinstance(data, dict):
                f.write("Dict keys: {}\n".format(list(data.keys())))
        if isinstance(data, dict) and "stories" in data:
            # DEBUG: Log successful parsing
            with open("debug_response.txt", "a", encoding="utf-8") as f:
                f.write("DEBUG: Successfully parsed {} stories\n".format(len(data["stories"])))
                for i, story in enumerate(data["stories"][:3]):  # Log first 3 stories
                    f.write("Story {}: {}\n".format(i+1, story))
            return data["stories"]
        elif isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError as e:
        with open("debug_response.txt", "a", encoding="utf-8") as f:
            f.write("DEBUG: JSONDecodeError: {}\n".format(str(e)))
            f.write("Problematic JSON: {}\n".format(json_str[:200] if 'json_str' in locals() else 'N/A'))
        return []
    except (KeyError, TypeError) as e:
        with open("debug_response.txt", "a", encoding="utf-8") as f:
            f.write("DEBUG: KeyError/TypeError: {}\n".format(str(e)))
        return []
        return []


def call_zhipuai_api(
    prompt: str,
    tools: Optional[List[Dict]] = None,
) -> str:
    """Call ZhipuAI API using the chat completion API."""
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

        return content

    except Exception as e:
        duration = time.time() - start_time
        logger.error("zhipuai_api_error", duration_seconds=duration, error=str(e))
        raise


def supports_reasoning_parameters(model: str) -> bool:
    """Check if the model supports reasoning parameters (ZhipuAI doesn't support this feature yet)."""
    # ZhipuAI models don't support the same reasoning parameters as OpenAI
    return False


def get_prompt(filename: str, **kwargs: Any) -> str:
    """Load and format a prompt template from the prompts directory."""
    from pathlib import Path

    prompt_file = Path(__file__).parent / "prompts" / filename
    prompt_template = prompt_file.read_text()
    return prompt_template.format(**kwargs)


def display_reasoning_summaries(summaries: List[str]) -> None:
    """Display reasoning summaries (ZhipuAI doesn't provide this feature yet)."""
    # ZhipuAI doesn't provide reasoning summaries like OpenAI's o1 models
    pass


# For compatibility with existing code
def extract_reasoning_summaries(response: str) -> List[str]:
    """Extract reasoning summaries (not applicable for ZhipuAI)."""
    return []


# Create a response-like object for compatibility
class ZhipuAIResponse:
    """Compatibility layer for ZhipuAI responses."""

    def __init__(self, content: str, tool_calls: Optional[List] = None):
        self.content = content
        self.tool_calls = tool_calls or []
        self.output = []

        # Add function calls to output for compatibility
        if tool_calls:
            for tool_call in tool_calls:
                if hasattr(tool_call, 'function'):
                    self.output.append({
                        'type': 'function_call',
                        'name': tool_call.function.name,
                        'arguments': tool_call.function.arguments
                    })