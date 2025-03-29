import click
import os
from .common import (
    print_step_header, print_guidance, print_prompt_instructions,
    load_output, STEP_OUTPUTS, PROJECT_DIR, save_output,
    handle_step_auto_generation
)

STEP = 1
TITLE = "Define Problem & Requirements"

@click.option('--auto-generate', is_flag=True, help='Use smol-dev to automatically generate code')
@click.option('--system-prompt', help='Optional system prompt for smol-dev when using auto-generate')
def run(auto_generate=False, system_prompt=None):
    """Executes Step 1: Problem Definition."""
    print_step_header(STEP, TITLE)
    
    # Provide guidance
    guidance = """
In this step, you'll define the problem your SaaS application will solve.
Think about:
1. Who are your users?
2. What problem are they facing?
3. How will your SaaS application solve this problem?
4. What are the key features needed?
5. What are your technical constraints or preferences?

Be as specific as possible. The quality of your problem definition will 
directly impact the quality of the generated application.
"""
    print_guidance(guidance)
    
    # Construct prompt for LLM
    prompt = """
You are an expert product manager helping define a B2B SaaS application using AWS serverless technologies.

Please help me define a comprehensive problem statement and requirements document for a new SaaS application. The output should include:

# Problem Statement
- Clearly state the problem being solved
- Identify the target users/customers
- Explain the current challenges/pain points
- Describe the impact of these challenges

# Proposed Solution
- Overview of the SaaS application
- Core value proposition
- Key differentiators from existing solutions
- Business model (pricing approach)

# Requirements
## Functional Requirements
- List of essential features (prioritized)
- User roles and permissions
- Key workflows
- Integration requirements

## Non-Functional Requirements
- Performance expectations
- Security requirements
- Scalability needs
- Compliance requirements (if any)

## Technical Constraints
- AWS serverless technologies to be used (Lambda, DynamoDB, API Gateway, etc.)
- Frontend technologies (e.g., React)
- Authentication approach (e.g., Cognito)
- Any specific technical decisions already made

# Success Metrics
- How will we measure the success of this application?
- What are the key performance indicators (KPIs)?

Please be specific and thorough. The information provided will be used to guide the architecture design and implementation of the SaaS application.
"""

    output_filename = "problem_definition.md"
    output_location = f"""
Save the LLM's response as a Markdown file:
{os.path.join(STEP_OUTPUTS, f'step{STEP}', output_filename)}

This document will be referenced in future steps to ensure alignment with your initial vision.
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
    
    click.secho(f"Step {STEP} complete. After saving the problem definition, proceed to Step 2.", fg="green") 