import click
import os
from .common import (
    print_step_header, print_guidance, print_prompt_instructions,
    load_output, STEP_OUTPUTS, PROJECT_DIR, print_project_structure,
    handle_step_auto_generation
)

STEP = 2
TITLE = "Information Architecture"

@click.option('--auto-generate', is_flag=True, help='Use smol-dev to automatically generate information architecture')
@click.option('--system-prompt', help='Optional system prompt for smol-dev when using auto-generate')
def run(auto_generate=False, system_prompt=None):
    """Executes Step 2: Information Architecture."""
    print_step_header(STEP, TITLE)

    # Load previous step output
    problem_def = load_output(1)  # Load problem definition from Step 1

    # Provide guidance
    guidance = """
In this step, we'll define the information architecture for the SaaS application.
This includes:
1. The core entities in the system
2. Their attributes and relationships
3. Important workflows and user journeys

This step is crucial as it will form the foundation for our database design,
API structure, and UI components in subsequent steps.
"""
    print_guidance(guidance)
    print_project_structure()

    # Construct prompt for LLM
    prompt = f"""
You are an expert solutions architect designing a SaaS application using AWS serverless technologies.

Based on the following problem definition, create a comprehensive information architecture document:

---
{problem_def}
---

# Information Architecture Document

## Core Entities
Define the main entities in the system. For each entity, include:
- Name and description
- Key attributes (with data types)
- Relationships to other entities

## Data Model
- Entity-Relationship Diagram (describe in text form)
- Key constraints and business rules
- Important indices for querying

## Workflows
Outline the main workflows in the application, including:
- User onboarding and authentication
- Core business processes
- Data flows between components

## API Structure
Sketch the high-level API design:
- Key endpoints
- Resource hierarchies
- Authentication and authorization approach

## User Interface Organization
Describe the main screens/pages needed:
- Dashboard components
- List/detail views
- Forms and interactive elements
- Navigation structure

Be specific and thorough. The information architecture should align with the problem definition and provide clear guidance for the DynamoDB data model in the next step.
"""

    output_filename = "information_architecture.md"
    output_location = f"""
Save the LLM's response as a Markdown file:
{os.path.join(STEP_OUTPUTS, f'step{STEP}', output_filename)}

This document will be referenced in future steps to guide the data model, API, and UI design.
"""

    # Try auto-generation if requested
    if auto_generate:
        handle_step_auto_generation(
            step_num=STEP,
            prompt=prompt,
            output_filename=output_filename,
            system_prompt=system_prompt,
            manual_instructions=output_location,
            single_file=True
        )
        return
    
    # Manual prompting approach
    print_prompt_instructions(prompt, output_location)
    
    click.secho(f"Step {STEP} complete. After saving the information architecture, proceed to Step 3.", fg="green") 