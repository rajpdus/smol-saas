import click
import os
from .common import (
    print_step_header, print_guidance, print_prompt_instructions,
    load_output, STEP_OUTPUTS, PROJECT_DIR, print_project_structure,
    handle_step_auto_generation
)

STEP = 4
TITLE = "Generate UI (React + shadcn/ui)"

@click.option('--auto-generate', is_flag=True, help='Use smol-dev to automatically generate code')
@click.option('--system-prompt', help='Optional system prompt for smol-dev when using auto-generate')
def run(auto_generate=False, system_prompt=None):
    """Executes Step 4: UI Generation."""
    print_step_header(STEP, TITLE)

    # --- Load Context ---
    step2_output = load_output(2)  # This gives us the information architecture

    # Provide guidance
    guidance = """
In this step, we'll generate the frontend UI components for the SaaS application.
We'll be using React with shadcn/ui for a modern, clean interface.

The generated UI should include:
1. Components for all the entities defined in the information architecture
2. Basic layouts and navigation
3. Form components for data entry
4. List/table views for data display
5. Authentication UI (login, signup, forgot password)
6. Basic routing structure

The UI won't be connected to real APIs yet (that happens in Step 5).
For now, we'll use placeholder data and mock API calls.
"""
    print_guidance(guidance)
    print_project_structure()

    # Construct prompt for LLM
    prompt = f"""
Act as a Frontend Developer creating a React application with shadcn/ui components.

# Context
Here's the information architecture for our SaaS application:

{step2_output}

# Task
Generate a complete frontend codebase for this SaaS application using:
- React (with TypeScript)
- shadcn/ui for components
- React Router for navigation
- React Query for data fetching (with placeholder API functions)
- React Hook Form for form handling
- Zustand or Context API for state management if needed

# Requirements:
1. Create a modern, clean UI with proper responsive design
2. Implement all screens needed for the entities in the information architecture
3. Use a layout with sidebar navigation
4. Include authentication UI (login, signup, password reset)
5. Create reusable components where appropriate
6. Add proper type definitions
7. Include proper error handling and loading states
8. Use placeholder API functions (we'll connect to real APIs in Step 5)

# Expected File Structure:
/frontend
  /public
    - favicon.ico
    - index.html
  /src
    /components
      /ui                # shadcn/ui components
      /layout            # Layout components like Header, Sidebar, etc.
      /[entity-name]     # Components for each entity
    /pages               # Pages for each route
    /hooks               # Custom hooks
    /services            # API service placeholders
    /utils               # Utility functions
    /types               # TypeScript type definitions
    /contexts            # React context if needed
    /store               # State management (if using Zustand)
    - App.tsx            # Main App component
    - main.tsx           # Entry point
    - index.css          # Global styles
  - package.json         # Dependencies
  - tsconfig.json        # TypeScript configuration
  - vite.config.ts       # Vite configuration

# Output Format
Please provide code for each file in the structure, with clear filenames indicated before each code block.
For shadcn/ui components, include installation instructions.
"""

    output_filename = "ui_components.md"
    output_location = f"""
Save the generated files to the 'frontend' directory in your project:
{os.path.join(PROJECT_DIR, 'frontend')}

Follow these steps:
1. Create the necessary directory structure as outlined in the prompt
2. Save each file with its appropriate filename and path
3. Don't forget package.json and configuration files
4. Follow any additional installation instructions for shadcn/ui

Also save a consolidated version to:
{os.path.join(STEP_OUTPUTS, f'step{STEP}', output_filename)}
"""
    
    # Try to use smol-dev for auto-generation if requested
    if auto_generate:
        output_dir = os.path.join(PROJECT_DIR, 'frontend')
        handle_step_auto_generation(
            step_num=STEP,
            prompt=prompt,
            output_filename=output_filename,
            target_dir=output_dir,
            system_prompt=system_prompt,
            manual_instructions=output_location
        )
        return
    
    # Fall back to manual prompting
    print_prompt_instructions(prompt, output_location)
    
    click.secho(f"Step {STEP} complete. Once you've generated the UI components, proceed to Step 5.", fg="green") 