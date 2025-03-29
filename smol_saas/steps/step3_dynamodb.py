import click
import os
from .common import (
    print_step_header, print_guidance, print_prompt_instructions,
    load_output, STEP_OUTPUTS, PROJECT_DIR, print_project_structure,
    handle_step_auto_generation
)

STEP = 3
TITLE = "DynamoDB Data Model & Access Patterns"

@click.option('--auto-generate', is_flag=True, help='Use smol-dev to automatically generate the DynamoDB model')
@click.option('--system-prompt', help='Optional system prompt for smol-dev when using auto-generate')
def run(auto_generate=False, system_prompt=None):
    """Executes Step 3: DynamoDB Data Model."""
    print_step_header(STEP, TITLE)

    # Load previous step output
    step2_output = load_output(2)  # This gives us the information architecture

    # Provide guidance
    guidance = """
In this step, we'll design the DynamoDB data model for the SaaS application.
This includes:
1. Identifying read/write access patterns
2. Designing the table structure
3. Defining primary keys and secondary indexes
4. Generating CloudFormation snippets
5. Creating Python data access code examples

For complex search needs, we'll determine if OpenSearch is needed alongside DynamoDB.
"""
    print_guidance(guidance)
    print_project_structure()

    # Construct prompt for LLM
    prompt = f"""
You are an expert AWS solutions architect specializing in DynamoDB design for serverless applications.

Based on the following information architecture, design a comprehensive DynamoDB data model:

---
{step2_output}
---

# DynamoDB Data Model Document

## Access Patterns Analysis
First, identify and list all important access patterns from the information architecture:
- List all read patterns (e.g., "Get user by ID", "List all products for a category")
- List all write patterns (e.g., "Create new order", "Update product inventory")
- For each pattern, note frequency (high/medium/low) and consistency requirements (strong/eventual)

## Table Design Decision
- Decide between single-table design or multiple tables (with reasoning)
- If single-table, explain the overarching partition key strategy
- If multiple tables, explain the purpose of each table

## For Each Table:
- Table name
- Primary key structure (partition key and optional sort key)
- Attribute definitions
- Secondary indexes (if needed)
- Example items in JSON format showing different entity types
- Any specific settings (TTL, Streams, etc.)

## Entity Mapping
- Explain how each entity from the information architecture maps to the DynamoDB structure
- For each entity, show concrete examples of CRUD operations

## CloudFormation Snippet
Provide a CloudFormation YAML snippet for the DynamoDB table(s) definition.

## Python Access Code Examples
Provide Python code examples (using boto3) for common access patterns:
- How to create/update items
- How to query by primary key
- How to use secondary indexes
- How to handle transactions (if needed)

## Advanced Considerations
- How will you handle large item collections?
- Will you need DynamoDB Streams?
- Is OpenSearch needed for complex search? (Flag this clearly: "OpenSearch Needed: True/False")

Be specific and thorough. The data model should efficiently support all access patterns identified in the information architecture.
"""

    output_filename = "dynamodb_model.md"
    output_location = f"""
Save the LLM's response as a Markdown file:
{os.path.join(STEP_OUTPUTS, f'step{STEP}', output_filename)}

Pay special attention to whether the model flags "OpenSearch Needed: True" as this will affect later steps.
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
    
    click.secho(f"Step {STEP} complete. Make sure to note the 'OpenSearch Needed' flag for Step 5.", fg="green") 