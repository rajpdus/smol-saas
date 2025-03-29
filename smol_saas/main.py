#!/usr/bin/env python3
"""
smol-saas: A Serverless SaaS App Generator CLI

This tool guides the user through a step-by-step process to generate
a full-stack SaaS application using AWS serverless technologies.
"""

import os
import sys
import click
from typing import Optional
import asyncio
import importlib

# Don't import ensure_project_structure here to allow env var to be set first
from .steps.common import PROJECT_DIR, print_step_header
from .steps import (
    step1_problem,
    step2_architecture,
    step3_dynamodb,
    step4_ui_gen,
    step5_integration,
    step6_deployment
)
from .steps.smol_dev_integration import generate_files_from_prompt, generate_single_file

# Map step numbers to their respective modules
STEPS = {
    1: step1_problem,
    2: step2_architecture,
    3: step3_dynamodb,
    4: step4_ui_gen,
    5: step5_integration,
    6: step6_deployment
}

# Step titles for display purposes
STEP_TITLES = {
    1: "Define Problem & Requirements",
    2: "Information Architecture",
    3: "DynamoDB Data Model & Access Patterns",
    4: "Generate UI (React + shadcn/ui)",
    5: "Integrate Backend (Chalice) & Auth (Cognito)",
    6: "Assemble Infrastructure & Deploy (SAM / Chalice)"
}


@click.group()
def cli():
    """smol-saas: A Serverless SaaS App Generator CLI

    This tool guides you through building a full-stack SaaS application
    using AWS serverless technologies including DynamoDB, Chalice, Cognito, 
    React, shadcn/ui, and (optionally) OpenSearch.
    """


@cli.command()
@click.option('--dir', default='./saas-app', help='Project directory (will be created if it doesn\'t exist)')
def init(dir):
    """Initialize a new smol-saas project directory"""
    abs_dir = os.path.abspath(dir)
    os.environ['SMOL_SAAS_PROJECT_DIR'] = abs_dir
    
    click.secho(f"Initializing new smol-saas project in: {abs_dir}", fg="green")
    click.secho(f"ENV var is: {os.environ['SMOL_SAAS_PROJECT_DIR']}", fg="blue")
    
    # Use a local import to force reevaluation of the PROJECT_DIR
    from .steps.common import ensure_project_structure
    ensure_project_structure()
    
    # Verify the project directory was created
    if not os.path.exists(abs_dir):
        click.secho(f"Error: Failed to create project directory at {abs_dir}", fg="red")
        sys.exit(1)
        
    click.secho("\nProject initialized! Next steps:", fg="green")
    click.echo("1. Run 'smol-saas step 1' to define your SaaS application's problem & requirements")
    click.echo("2. Follow each step guided by the CLI")


@cli.command()
@click.argument('step_num', type=int)
@click.option('--dir', help='Project directory (defaults to the current SMOL_SAAS_PROJECT_DIR)')
@click.option('--auto-generate', '-a', is_flag=True, help='Use smol-dev to automatically generate code for this step')
@click.option('--all-steps', is_flag=True, help='Run this step and all following steps sequentially')
@click.option('--system-prompt', '-s', help='Optional system prompt for smol-dev when using auto-generate')
def step(step_num: int, dir: Optional[str] = None, auto_generate: bool = False, 
         all_steps: bool = False, system_prompt: Optional[str] = None):
    """Run a specific step in the smol-saas process"""
    if dir:
        os.environ['SMOL_SAAS_PROJECT_DIR'] = os.path.abspath(dir)
    
    if 'SMOL_SAAS_PROJECT_DIR' not in os.environ:
        click.secho("Error: Project directory not set. Run 'smol-saas init' first or specify --dir", fg="red")
        sys.exit(1)
    
    if step_num not in STEPS:
        click.secho(f"Error: Invalid step number. Choose from: {', '.join(map(str, STEPS.keys()))}", fg="red")
        sys.exit(1)
    
    # If all_steps flag is set, start from this step and run all subsequent steps
    if all_steps:
        for current_step in range(step_num, max(STEPS.keys()) + 1):
            click.secho(f"\nRunning Step {current_step}/{max(STEPS.keys())}: {STEP_TITLES[current_step]}", 
                       bold=True, fg="green")
            click.echo(f"Working directory: {os.environ['SMOL_SAAS_PROJECT_DIR']}")
            
            # Pass auto_generate and system_prompt to each step
            try:
                # Getting the run function from the step module
                run_func = getattr(STEPS[current_step], 'run')
                
                # Check if the run function accepts auto_generate and system_prompt
                import inspect
                signature = inspect.signature(run_func)
                
                # Prepare kwargs based on the function's parameters
                kwargs = {}
                if 'auto_generate' in signature.parameters:
                    kwargs['auto_generate'] = auto_generate
                if 'system_prompt' in signature.parameters:
                    kwargs['system_prompt'] = system_prompt
                
                # Run the step with appropriate parameters
                run_func(**kwargs)
                
                click.secho(f"Step {current_step} completed successfully", fg="green")
            except Exception as e:
                click.secho(f"Error in Step {current_step}: {str(e)}", fg="red")
                click.secho("Stopping the sequence due to error.", fg="red")
                sys.exit(1)
        
        click.secho(f"\nAll steps from {step_num} to {max(STEPS.keys())} completed!", fg="green", bold=True)
        return
    
    # Single step execution
    click.secho(f"Starting Step {step_num}: {STEP_TITLES[step_num]}", bold=True, fg="green")
    click.echo(f"Working directory: {os.environ['SMOL_SAAS_PROJECT_DIR']}")
    
    # Pass auto_generate and system_prompt to the step if supported
    try:
        # Getting the run function from the step module
        run_func = getattr(STEPS[step_num], 'run')
        
        # Check if the run function accepts auto_generate and system_prompt
        import inspect
        signature = inspect.signature(run_func)
        
        # Prepare kwargs based on the function's parameters
        kwargs = {}
        if 'auto_generate' in signature.parameters:
            kwargs['auto_generate'] = auto_generate
        if 'system_prompt' in signature.parameters:
            kwargs['system_prompt'] = system_prompt
        
        # Run the step with appropriate parameters
        run_func(**kwargs)
    except Exception as e:
        click.secho(f"Error in Step {step_num}: {str(e)}", fg="red")
        sys.exit(1)


@cli.command()
def list():
    """List all available steps in the smol-saas process"""
    click.secho("Available steps in the smol-saas process:", bold=True)
    for num, title in STEP_TITLES.items():
        click.echo(f"Step {num}: {title}")


@cli.command()
@click.option('--dir', help='Project directory (defaults to the current SMOL_SAAS_PROJECT_DIR)')
def status(dir: Optional[str] = None):
    """Show the status of the current project"""
    if dir:
        os.environ['SMOL_SAAS_PROJECT_DIR'] = os.path.abspath(dir)
        
    if 'SMOL_SAAS_PROJECT_DIR' not in os.environ:
        click.secho("Error: No active project. Run 'smol-saas init' first or specify --dir", fg="red")
        sys.exit(1)
    
    project_dir = os.environ['SMOL_SAAS_PROJECT_DIR']
    click.secho(f"Project directory: {project_dir}", bold=True)
    
    # Check which step outputs exist
    completed_steps = []
    for step_num in STEPS:
        step_output_dir = os.path.join(project_dir, 'outputs', f'step{step_num}')
        if os.path.exists(step_output_dir) and os.listdir(step_output_dir):
            completed_steps.append(step_num)
    
    if completed_steps:
        click.secho(f"Completed steps: {', '.join(map(str, completed_steps))}", fg="green")
        next_step = min([s for s in STEPS.keys() if s not in completed_steps], default=None)
        if next_step:
            click.secho(f"Next step: Step {next_step} - {STEP_TITLES[next_step]}", fg="blue")
        else:
            click.secho("All steps completed!", fg="green")
    else:
        click.secho("No steps completed yet. Start with 'smol-saas step 1'", fg="yellow")
    
    # Additional structure checks could be added here


@cli.command()
@click.argument('prompt_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default=None, help='Output directory for generated files')
@click.option('--system-prompt', '-s', help='Optional system prompt')
@click.option('--single-file', '-f', help='Generate only a single file with this name')
def generate(prompt_file, output_dir, system_prompt, single_file):
    """Generate code directly from a prompt file using smol-dev.
    
    PROMPT_FILE: Path to a file containing the prompt.
    """
    try:
        # Try to import smol-dev functions to check if smol-dev is installed
        from smol_dev.generate import generate_code
    except ImportError:
        click.secho("Error: smol-dev package is not installed. Please install it with 'pip install smol-dev'.", fg="red")
        sys.exit(1)
    
    # Read the prompt file
    with open(prompt_file, 'r') as f:
        prompt = f.read()
    
    # Determine output directory
    if output_dir is None:
        if 'SMOL_SAAS_PROJECT_DIR' in os.environ:
            output_dir = os.environ['SMOL_SAAS_PROJECT_DIR']
        else:
            output_dir = os.path.join(os.path.dirname(prompt_file), 'output')
    
    click.secho(f"Reading prompt from: {prompt_file}", fg="blue")
    click.secho(f"Output will be saved to: {output_dir}", fg="blue")
    click.secho(f"Prompt length: {len(prompt)} characters", fg="blue")
    
    # Confirm with the user
    if not click.confirm("Do you want to proceed with code generation?"):
        click.secho("Code generation cancelled.", fg="yellow")
        return
    
    click.secho("Starting code generation with smol-dev...", fg="green")
    
    try:
        if single_file:
            click.secho(f"Generating single file: {single_file}", fg="blue")
            result = asyncio.run(generate_single_file(
                prompt=prompt,
                filename=single_file,
                output_directory=output_dir,
                system_prompt=system_prompt,
                verbose=True
            ))
            
            if result:
                click.secho(f"Successfully generated file: {os.path.join(output_dir, single_file)}", fg="green")
            else:
                click.secho("File generation failed.", fg="red")
        else:
            click.secho("Generating multiple files based on the prompt...", fg="blue")
            result = asyncio.run(generate_files_from_prompt(
                prompt=prompt,
                output_directory=output_dir,
                system_prompt=system_prompt,
                verbose=True
            ))
            
            if result:
                click.secho(f"Successfully generated {len(result)} files in {output_dir}", fg="green")
            else:
                click.secho("Code generation failed.", fg="red")
    except Exception as e:
        click.secho(f"Error during code generation: {str(e)}", fg="red")
        sys.exit(1)


if __name__ == '__main__':
    cli() 