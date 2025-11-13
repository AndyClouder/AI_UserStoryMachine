"""Non-interactive version of StoryMachine CLI."""

import argparse
import asyncio
import sys
from pathlib import Path
from .types import WorkflowInput
from .workflow import generate_stories_auto
from .config import Settings


def main():
    """Auto CLI entry point for StoryMachine - non-interactive mode."""

    parser = argparse.ArgumentParser(
        description="StoryMachine Auto - Generate user stories from PRD without interaction"
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
    parser.add_argument(
        "--output",
        type=str,
        required=False,
        help="Output file path (optional, defaults to console)",
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

    # Generate stories automatically
    print("🚀 Starting automatic user story generation...\n")

    try:
        stories = asyncio.run(generate_stories_auto(workflow_input))

        # Output results
        output_content = format_stories_output(stories)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output_content, encoding='utf-8')
            print(f"\n✅ User stories saved to: {output_path}")
        else:
            print("\n" + "="*60)
            print("📋 GENERATED USER STORIES")
            print("="*60)
            print(output_content)

    except Exception as e:
        print(f"\n❌ Error generating stories: {str(e)}", file=sys.stderr)
        sys.exit(1)


def format_stories_output(stories):
    """Format stories for output."""
    if not stories:
        return "No stories were generated."

    output = f"Generated {len(stories)} user stories:\n\n"

    for i, story in enumerate(stories, 1):
        output += f"{i}. {story.title}\n"
        output += "   Acceptance Criteria:\n"
        for j, ac in enumerate(story.acceptance_criteria, 1):
            output += f"     {j}. {ac}\n"
        if story.enriched_context:
            output += "   Context:\n"
            # Format context with proper indentation
            context_lines = story.enriched_context.split('\n')
            for line in context_lines:
                if line.strip():
                    output += f"     {line}\n"
        output += "\n"

    return output


if __name__ == "__main__":
    main()