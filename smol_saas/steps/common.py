"""
Common utilities and functions shared across all steps.
"""

import os
import click
import yaml
from typing import Dict, Any, Optional
import asyncio

# Default output directory structure (defer loading the actual path until needed)
def get_project_dir():
    """Get the project directory path from environment or default"""
    return os.environ.get('SMOL_SAAS_PROJECT_DIR', os.path.abspath('./saas-app'))

# Use a function to get the current project directory
PROJECT_DIR = get_project_dir()
STEP_OUTPUTS = os.path.join(PROJECT_DIR, 'outputs')

# Import our smol-dev integration
try:
    from .smol_dev_integration import generate_files_from_prompt, generate_single_file
    HAS_SMOL_DEV = True
except ImportError:
    HAS_SMOL_DEV = False
    
    # Placeholders if smol-dev is not installed
    async def generate_files_from_prompt(*args, **kwargs):
        click.secho("Error: smol-dev integration is not available. Using manual prompting.", fg="red")
        return {}
    
    async def generate_single_file(*args, **kwargs):
        click.secho("Error: smol-dev integration is not available. Using manual prompting.", fg="red")
        return None

def ensure_project_structure():
    """
    Ensures the project directory structure exists.
    Creates necessary folders if they don't exist.
    """
    # Get a fresh reference to the project directory
    project_dir = get_project_dir()
    step_outputs = os.path.join(project_dir, 'outputs')
    
    # Main project directory
    try:
        os.makedirs(project_dir, exist_ok=True)
        
        # Step outputs directory
        os.makedirs(step_outputs, exist_ok=True)
        
        # Create step output directories
        for step in range(1, 7):
            os.makedirs(os.path.join(step_outputs, f'step{step}'), exist_ok=True)
        
        # Create other necessary directories
        os.makedirs(os.path.join(project_dir, 'frontend'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'backend'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'infrastructure', 'snippets'), exist_ok=True)
        
        click.secho(f"Project structure created at {project_dir}", fg="green")
    except Exception as e:
        click.secho(f"Error creating project structure: {str(e)}", fg="red")
        raise

def print_step_header(step_num: int, title: str):
    """
    Prints a formatted header for a step.
    
    Args:
        step_num: The step number
        title: The step title
    """
    border = "=" * (len(title) + 15)
    click.secho(f"\n{border}", fg="blue", bold=True)
    click.secho(f"   Step {step_num}: {title}", fg="blue", bold=True)
    click.secho(f"{border}\n", fg="blue", bold=True)

def print_guidance(text: str):
    """
    Prints formatted guidance text.
    
    Args:
        text: The guidance text to print
    """
    click.secho("\n--- Guidance ---", fg="yellow")
    click.echo(text)
    click.secho("---------------\n", fg="yellow")

def print_prompt_instructions(prompt_guidance: str, output_location: str, auto_generate: bool = False):
    """
    Prints formatted LLM prompt instructions.
    
    Args:
        prompt_guidance: The prompt/guidance to provide to the LLM
        output_location: Instructions on where to save the LLM's output
        auto_generate: Whether to attempt auto-generation with smol-dev
    """
    if auto_generate and HAS_SMOL_DEV:
        click.secho("\n--- USING SMOL-DEV FOR AUTOMATED GENERATION ---", fg="green", bold=True)
        click.echo("The following prompt will be sent to smol-dev:")
        click.echo(prompt_guidance)
        click.echo("\nOutput will be saved according to these instructions:")
        click.echo(output_location)
        click.secho("---------------\n", fg="green")
        return
        
    # Original manual prompt behavior
    click.secho("\n--- LLM PROMPT ---", fg="green", bold=True)
    click.secho("Copy the following prompt to your preferred LLM (like ChatGPT, Claude, etc.):\n", fg="green")
    click.echo(prompt_guidance)
    
    click.secho("\n--- OUTPUT INSTRUCTIONS ---", fg="cyan", bold=True)
    click.secho("After receiving the LLM's response:", fg="cyan")
    click.echo(output_location)
    click.secho("\n---------------\n", fg="cyan")

def load_output(step_num: int) -> str:
    """
    Loads the output from a previous step.
    
    Args:
        step_num: The step number to load output from
        
    Returns:
        The content of the output file as a string
    """
    step_output_dir = os.path.join(STEP_OUTPUTS, f'step{step_num}')
    
    # Look for the first .md, .yaml, or .json file in the directory
    for ext in ['.md', '.yaml', '.json', '.yml', '.txt']:
        for filename in os.listdir(step_output_dir):
            if filename.endswith(ext):
                filepath = os.path.join(step_output_dir, filename)
                with open(filepath, 'r') as f:
                    return f.read()
    
    # If no file is found
    click.secho(f"Warning: No output found for Step {step_num}. Make sure you've completed that step first.", fg="yellow")
    return ""

def save_output(step_num: int, content: str, filename: str):
    """
    Saves output content to a file in the appropriate step directory.
    
    Args:
        step_num: The step number
        content: The content to save
        filename: The filename to save to
    """
    step_output_dir = os.path.join(STEP_OUTPUTS, f'step{step_num}')
    os.makedirs(step_output_dir, exist_ok=True)
    
    filepath = os.path.join(step_output_dir, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    
    click.secho(f"Output saved to: {filepath}", fg="green")

def save_yaml_output(step_num: int, data: Dict[str, Any], filename: str):
    """
    Saves YAML data to a file in the appropriate step directory.
    
    Args:
        step_num: The step number
        data: The data to save as YAML
        filename: The filename to save to
    """
    step_output_dir = os.path.join(STEP_OUTPUTS, f'step{step_num}')
    os.makedirs(step_output_dir, exist_ok=True)
    
    filepath = os.path.join(step_output_dir, filename)
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    
    click.secho(f"YAML output saved to: {filepath}", fg="green")

def print_project_structure():
    """Prints the current project directory structure."""
    click.secho("\nCurrent Project Structure:", fg="blue")
    
    # Simple recursive function to print the directory structure
    def print_dir(path, prefix=""):
        entries = sorted(os.listdir(path))
        count = len(entries)
        
        for i, entry in enumerate(entries):
            is_last = i == count - 1
            entry_path = os.path.join(path, entry)
            
            if os.path.isdir(entry_path):
                click.echo(f"{prefix}{'└── ' if is_last else '├── '}{entry}/")
                print_dir(entry_path, prefix + ('    ' if is_last else '│   '))
            else:
                click.echo(f"{prefix}{'└── ' if is_last else '├── '}{entry}")
    
    # Print only two levels deep to avoid clutter
    entries = sorted(os.listdir(PROJECT_DIR))
    for entry in entries:
        entry_path = os.path.join(PROJECT_DIR, entry)
        if os.path.isdir(entry_path):
            click.echo(f"├── {entry}/")
            subentries = os.listdir(entry_path)
            for subentry in sorted(subentries):
                subentry_path = os.path.join(entry_path, subentry)
                if os.path.isdir(subentry_path):
                    click.echo(f"│   ├── {subentry}/")
                else:
                    click.echo(f"│   ├── {subentry}")
        else:
            click.echo(f"├── {entry}")

def handle_auto_generation(prompt: str, output_dir: str, filename: str = None, system_prompt: str = None):
    """
    Handles automated code generation using smol-dev if available.
    
    Args:
        prompt: The prompt to send to smol-dev
        output_dir: Directory to save generated files to
        filename: If provided, only generates a single file with this name
        system_prompt: Optional system prompt to guide smol-dev
        
    Returns:
        True if auto-generation was performed, False otherwise
    """
    if not HAS_SMOL_DEV:
        return False
        
    try:
        # Create directories if they don't exist
        os.makedirs(output_dir, exist_ok=True)
        
        if filename:
            # Generate a single file
            result = asyncio.run(generate_single_file(
                prompt=prompt,
                filename=filename,
                output_directory=output_dir,
                system_prompt=system_prompt
            ))
        else:
            # Generate multiple files
            result = asyncio.run(generate_files_from_prompt(
                prompt=prompt,
                output_directory=output_dir,
                system_prompt=system_prompt
            ))
            
        if not result:
            click.secho("Auto-generation failed. Please use the manual approach instead.", fg="red")
            return False
            
        click.secho("Auto-generation completed successfully!", fg="green")
        return True
            
    except Exception as e:
        click.secho(f"Error during auto-generation: {str(e)}", fg="red")
        click.secho("Falling back to manual prompting.", fg="yellow")
        return False

def auto_generate_and_save(step_num: int, prompt: str, filename: str, output_dir: str = None, 
                           system_prompt: str = None, single_file: bool = False):
    """
    Uses smol-dev to generate code and save it as step output.
    
    Args:
        step_num: The step number
        prompt: The prompt to send to smol-dev
        filename: Name of the output file to save
        output_dir: Optional specific directory to save generated files to
        system_prompt: Optional system prompt
        single_file: Whether to generate a single file
        
    Returns:
        True if generation was successful, False otherwise
    """
    if not HAS_SMOL_DEV:
        click.secho("Error: smol-dev integration is not available. Cannot auto-generate.", fg="red")
        return False
    
    # First, try to generate the code
    try:
        if output_dir is None:
            # Save to the step output directory if no specific output directory provided
            step_output_dir = os.path.join(STEP_OUTPUTS, f'step{step_num}')
            os.makedirs(step_output_dir, exist_ok=True)
        else:
            step_output_dir = output_dir
            os.makedirs(step_output_dir, exist_ok=True)
        
        click.secho(f"Generating output using smol-dev for Step {step_num}...", fg="blue")
        
        if single_file:
            # Generate a single file with specific content
            content = asyncio.run(generate_single_file(
                prompt=prompt,
                filename=filename,
                output_directory=step_output_dir,
                system_prompt=system_prompt
            ))
            
            if content:
                # Also save a copy to the step outputs directory for next steps
                if output_dir is not None:
                    save_output(step_num, content, filename)
                click.secho(f"Successfully generated {filename}", fg="green")
                return True
        else:
            # Generate multiple files
            result = asyncio.run(generate_files_from_prompt(
                prompt=prompt,
                output_directory=step_output_dir,
                system_prompt=system_prompt
            ))
            
            if result:
                # If generating multiple files, we also want to save a consolidated
                # version in the step outputs directory for use by future steps
                consolidated = ""
                for fname, content in result.items():
                    consolidated += f"# {fname}\n\n```\n{content}\n```\n\n"
                
                if output_dir is not None:
                    # Save consolidated output to step outputs for next steps
                    save_output(step_num, consolidated, filename)
                
                click.secho(f"Successfully generated {len(result)} files", fg="green")
                return True
        
        click.secho("Auto-generation failed to produce any output.", fg="red")
        return False
        
    except Exception as e:
        click.secho(f"Error during auto-generation: {str(e)}", fg="red")
        return False

def handle_step_auto_generation(step_num: int, prompt: str, output_filename: str, 
                               target_dir: str = None, system_prompt: str = None, 
                               manual_instructions: str = None, single_file: bool = False):
    """
    Common handler for step auto-generation with smol-dev.
    
    Args:
        step_num: The step number 
        prompt: The prompt to use for generation
        output_filename: The filename to save output as
        target_dir: Optional target directory for multiple file generation
        system_prompt: Optional system prompt for smol-dev
        manual_instructions: Instructions to show if auto-generation fails
        single_file: Whether to generate a single file
        
    Returns:
        True if auto-generation was successful, False otherwise
    """
    success = auto_generate_and_save(
        step_num=step_num,
        prompt=prompt,
        filename=output_filename,
        output_dir=target_dir,
        system_prompt=system_prompt,
        single_file=single_file
    )
    
    if success:
        click.secho(f"Step {step_num} completed with auto-generation.", fg="green")
        # Show success message with file info
        if target_dir:
            click.echo(f"Files have been saved to: {target_dir}")
        click.echo(f"Step output saved for next steps: {os.path.join(STEP_OUTPUTS, f'step{step_num}', output_filename)}")
        return True
    else:
        click.secho("Auto-generation was not successful. Please use manual instructions instead.", fg="yellow")
        if manual_instructions:
            print_prompt_instructions(prompt, manual_instructions)
        return False 