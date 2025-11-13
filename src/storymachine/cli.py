import argparse
import asyncio
import sys
from pathlib import Path
from .types import WorkflowInput
from .workflow import w1
from .config import Settings


def main():
    """Main CLI entry point for StoryMachine."""

    parser = argparse.ArgumentParser(
        description="StoryMachine - Generate context-enriched user stories from PRD and tech spec"
    )
    parser.add_argument(
        "--prd",
        type=str,
        required=True,
        help="Path to the Product Requirements Document (PRD) file",
    )
    parser.add_argument(
        "--tech-spec",
        type=str,
        required=False,
        help="Path to the Technical Specification file (optional)",
    )
    parser.add_argument(
        "--repo",
        type=str,
        required=False,
        help="GitHub repository URL (e.g., https://github.com/owner/repo) (optional)",
    )

    args = parser.parse_args()

    prd_path = Path(args.prd)

    if not prd_path.exists():
        print(f"Error: PRD file not found: {prd_path}", file=sys.stderr)
        sys.exit(1)

    # Read file contents with UTF-8 encoding
    prd_content = prd_path.read_text(encoding='utf-8')

    # Handle optional parameters
    tech_spec_content = ""
    if args.tech_spec:
        tech_spec_path = Path(args.tech_spec)
        if not tech_spec_path.exists():
            print(f"Error: Tech spec file not found: {tech_spec_path}", file=sys.stderr)
            sys.exit(1)
        tech_spec_content = tech_spec_path.read_text(encoding='utf-8')
        print(f"Using technical specification: {tech_spec_path}")
    else:
        print("No technical specification provided - will work with PRD only")

    repo_url = args.repo or ""
    if args.repo:
        print(f"Using repository: {args.repo}")
    else:
        print("No repository provided - will work without codebase context")

    # Create workflow input
    workflow_input = WorkflowInput(
        prd_content=prd_content,
        tech_spec_content=tech_spec_content,
        repo_url=repo_url,
    )

    # Display current configuration
    settings = Settings()  # pyright: ignore[reportCallIssue]
    print(f"Model: {settings.model}")
    print(f"Reasoning Effort: {settings.reasoning_effort}")
    print()

    asyncio.run(w1(workflow_input))


if __name__ == "__main__":
    main()
