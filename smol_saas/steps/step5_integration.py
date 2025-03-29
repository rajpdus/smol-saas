import click
import os
from .common import (
    print_step_header, print_guidance, print_prompt_instructions,
    load_output, STEP_OUTPUTS, PROJECT_DIR, print_project_structure,
    handle_step_auto_generation
)

STEP = 5
TITLE = "Integrate Backend (Chalice) & Auth (Cognito)"

@click.option('--auto-generate', is_flag=True, help='Use smol-dev to automatically generate code')
@click.option('--system-prompt', help='Optional system prompt for smol-dev when using auto-generate')
def run(auto_generate=False, system_prompt=None):
    """Executes Step 5, guiding multiple LLM interactions."""
    print_step_header(STEP, TITLE)

    # --- Load Context --- #
    step2_output = load_output(2) # Logical Model
    step3_output = load_output(3) # DynamoDB design, snippets, code examples, OpenSearch flag

    # Check for OpenSearch flag from Step 3 output (requires parsing the saved file)
    opensearch_needed = "OpenSearch Needed: True" in step3_output
    click.secho(f"Detected OpenSearch Need: {opensearch_needed}", fg="yellow")

    guidance = """
This is a multi-part step to generate the backend, authentication, and connect the UI.
We will prompt the LLM multiple times:
1.  Generate Cognito CloudFormation.
2.  Generate Backend Chalice code (integrating DB, Cognito, CORS, maybe OpenSearch).
3.  Generate IAM Role CloudFormation for the backend Lambda(s).
4.  Update Frontend code to use the real API and authentication.

Follow the save instructions carefully for each part.
"""
    print_guidance(guidance)
    print_project_structure()

    # --- Part 1: Generate Cognito --- #
    click.secho("Part 1: Generate Cognito CloudFormation", bold=True, fg="blue")
    cognito_prompt = f"""
Act as an AuthAgent following 'spec/step5-integrate-backend-auth.md'.
Generate the CloudFormation YAML *snippet* for:
1.  An Amazon Cognito User Pool suitable for a standard web app (allow email/password signup).
2.  An associated Cognito User Pool Client.

Ensure standard security practices (e.g., password policies are reasonable).
Output *only* the YAML snippet, clearly marked.
"""
    cognito_file = "cognito.yaml"
    cognito_dir = os.path.join(PROJECT_DIR, 'infrastructure', 'snippets')
    os.makedirs(cognito_dir, exist_ok=True)
    cognito_output_path = os.path.join(cognito_dir, cognito_file)
    
    cognito_output_location = f"""Save the generated Cognito YAML snippet to:
  {cognito_output_path}
(Create the 'snippets' directory if it doesn't exist)."""

    if auto_generate:
        click.secho("Generating Cognito CloudFormation using smol-dev...", fg="green")
        handle_step_auto_generation(
            step_num=STEP,
            prompt=cognito_prompt,
            output_filename="part1_cognito.md",
            target_dir=cognito_dir,
            system_prompt=system_prompt,
            manual_instructions=cognito_output_location,
            single_file=True
        )
    else:
        print_prompt_instructions(cognito_prompt, cognito_output_location)
        input("Press Enter when ready to continue to Part 2...")

    # --- Part 2: Generate Backend Code --- #
    click.secho("\nPart 2: Generate Backend Chalice Code", bold=True, fg="blue")

    # Construct conditional parts for the prompt
    opensearch_req_line = "'opensearch-py'" if opensearch_needed else "''"
    opensearch_indexer_point = ("'5. `backend/lambda/indexer.py`: If OpenSearch is needed, generate Python code for a separate Lambda function "
                              "to process DynamoDB Stream events and index data into OpenSearch. Include necessary error handling.'"
                              if opensearch_needed else "''")

    backend_prompt = f"""
Act as a BackendAgent following 'spec/step5-integrate-backend-auth.md'.
Use Python and the Chalice framework.

Context:
- Logical Model (Step 2):
{step2_output}
- DynamoDB Design & Access Patterns (Step 3):
{step3_output}
- Cognito will be defined by the snippet saved in 'infrastructure/snippets/cognito.yaml'.
- Frontend anticipates standard CRUD API endpoints for the defined entities.
- OpenSearch Needed: {opensearch_needed}

Generate the following files for the Chalice backend application, placing code within the 'backend/' directory structure:
1.  `backend/app.py`: Define Chalice app, implement API routes for CRUD operations (using REST principles), integrate Cognito token validation (e.g., using a Chalice authorizer or JWT validation), configure CORS (allow typical web app origins, potentially parameterize later), include structured logging.
2.  `backend/chalicelib/` (if needed): Place helper functions, data access logic (using boto3 examples from Step 3 output), validation logic (e.g., using Pydantic) into appropriate modules within `chalicelib/`.
3.  `backend/requirements.txt`: List runtime dependencies (chalice, boto3, pyjwt, pydantic, requests, etc. {opensearch_req_line}).
4.  `backend/requirements-dev.txt`: List dev dependencies (pytest, flake8, bandit).

{opensearch_indexer_point}

Prefix each code block clearly with the intended filename (e.g., `### backend/app.py`, `### backend/chalicelib/db.py`, `### backend/lambda/indexer.py`).
"""
    # Construct conditional part for the output location example
    opensearch_save_example = (f"\n{' ' * 2}- Save code marked `### backend/lambda/indexer.py` as "
                             f"`{os.path.join(PROJECT_DIR, 'backend', 'lambda', 'indexer.py')}`."
                             if opensearch_needed else "")

    backend_dir = os.path.join(PROJECT_DIR, 'backend')
    backend_output_location = f"""Save the LLM's generated code content DIRECTLY into the 'backend/' directory within '{PROJECT_DIR}'.

Example:
- Save code marked `### backend/app.py` as `{os.path.join(PROJECT_DIR, 'backend', 'app.py')}`.
- Save code marked `### backend/chalicelib/utils.py` as `{os.path.join(PROJECT_DIR, 'backend', 'chalicelib', 'utils.py')}`.\
{opensearch_save_example}

Create directories (`chalicelib`, `lambda`) inside '{backend_dir}' as needed.
"""

    if auto_generate:
        click.secho("Generating Backend Chalice Code using smol-dev...", fg="green")
        os.makedirs(backend_dir, exist_ok=True)
        handle_step_auto_generation(
            step_num=STEP,
            prompt=backend_prompt,
            output_filename="part2_backend.md",
            target_dir=backend_dir,
            system_prompt=system_prompt,
            manual_instructions=backend_output_location
        )
    else:
        print_prompt_instructions(backend_prompt, backend_output_location)
        input("Press Enter when ready to continue to Part 3...")

    # --- Part 3: Generate IAM Roles --- #
    click.secho("\nPart 3: Generate Backend IAM Role(s) CloudFormation", bold=True, fg="blue")

    # Construct conditional parts for IAM prompt (escape CloudFormation variables)
    opensearch_iam_permissions = (f"\n{' ' * 4}- OpenSearch access (e.g., `es:ESHttpPost`, `es:ESHttpPut`) scoped to the OpenSearch domain ARN "
                                 "(you might need to use a placeholder ARN like `!Sub arn:aws:es:${{AWS::Region}}:${{AWS::AccountId}}:domain/YourDomainNameHere` "
                                 "if the domain is created in the same template)."
                                 if opensearch_needed else "")
    indexer_role_section = ("""

2.  **Indexer Lambda Role (if OpenSearch Needed):** Create a separate IAM Role for the `indexer.py` Lambda. Grant minimal permissions for:
    - DynamoDB Stream reading (`dynamodb:GetRecords`, `dynamodb:GetShardIterator`, `dynamodb:DescribeStream`, `dynamodb:ListStreams`).
    - OpenSearch writing (`es:ESHttpPost`, `es:ESHttpPut`, etc.) scoped to the domain ARN.
    - CloudWatch Logs.""" if opensearch_needed else "")

    iam_prompt = f"""
Act as an InfrastructureAgent following 'spec/step5-integrate-backend-auth.md'.

Generate CloudFormation YAML *snippet(s)* for IAM Role(s) needed by the backend generated in Part 2:
1.  **Chalice Lambda Role:** Create an IAM Role that the Chalice Lambda function(s) will assume. Grant minimal permissions for:
    - DynamoDB access (GetItem, PutItem, Query, UpdateItem, etc.) scoped *specifically* to the table ARN(s) identified in Step 3 output.
    - Cognito actions (if needed for validation/user info lookup).
    - CloudWatch Logs (CreateLogStream, PutLogEvents).{opensearch_iam_permissions}
{indexer_role_section}

Output *only* the YAML snippet(s), clearly marked (e.g., `# Chalice Lambda Role`, `# Indexer Lambda Role`).
"""
    iam_file = "backend_roles.yaml"
    iam_dir = os.path.join(PROJECT_DIR, 'infrastructure', 'snippets')
    iam_output_path = os.path.join(iam_dir, iam_file)
    
    iam_output_location = f"""Save the generated IAM Role YAML snippet(s) to:
  {iam_output_path}

-- Important --
You will need to manually extract these snippets later to integrate them into the main `template.yaml` in Step 6."""

    if auto_generate:
        click.secho("Generating IAM Roles using smol-dev...", fg="green")
        handle_step_auto_generation(
            step_num=STEP,
            prompt=iam_prompt,
            output_filename="part3_iam.md",
            target_dir=iam_dir,
            system_prompt=system_prompt,
            manual_instructions=iam_output_location,
            single_file=True
        )
    else:
        print_prompt_instructions(iam_prompt, iam_output_location)
        input("Press Enter when ready to continue to Part 4...")

    # --- Part 4: Update Frontend --- #
    click.secho("\nPart 4: Update Frontend Code (Integration)", bold=True, fg="blue")
    guidance_frontend = """
This part is often the trickiest for LLMs as it involves *modifying* existing code.
You might need to:
1.  Provide the LLM with the *content* of relevant frontend files (e.g., API service files, auth context, components using placeholders) generated in Step 4.
2.  Clearly instruct the LLM on *what specific changes* to make.
3.  Manually review and apply the LLM's suggested changes carefully, or regenerate specific files if modification proves too difficult for the LLM.
"""
    print_guidance(guidance_frontend)

    frontend_prompt = f"""
Act as a FrontendAgent following 'spec/step5-integrate-backend-auth.md'.

Task: Update the React frontend code (previously generated in Step 4 and saved in '{os.path.join(PROJECT_DIR, 'frontend')}') to integrate with the real backend API and Cognito authentication.

Context:
- Assume API endpoints are now available (provide example base URL like `https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/`).
- Assume Cognito User Pool ID and Client ID are available (provide placeholders like `YOUR_COGNITO_USER_POOL_ID` and `YOUR_COGNITO_APP_CLIENT_ID`).

Instructions (Provide content of relevant files as needed):
1.  **API Integration:** Update the placeholder API call functions/hooks (e.g., in `frontend/src/services/api.js`) to use `fetch` or `axios` to call the actual backend endpoints. Include sending the Cognito JWT token in the Authorization header for protected routes.
2.  **Authentication Integration:** Update the auth context/components (e.g., `frontend/src/contexts/AuthContext.js`, login/signup forms) to use a library like `aws-amplify` or Cognito SDKs to handle user signup, login, logout, token retrieval, and session management.
3.  **Protected Routes:** Implement logic (e.g., using the Auth Context) to redirect unauthenticated users from protected pages.
4.  **Data Display:** Connect components displaying data (tables, lists, detail views) to fetch data from the integrated API service calls.

Output the *modified code content* for the specific files that need changes, clearly prefixed with the filename (e.g., `### frontend/src/services/api.js`).
"""
    frontend_dir = os.path.join(PROJECT_DIR, 'frontend')
    frontend_output_location = f"""Carefully review the LLM's suggested modifications.
Manually apply these changes to the corresponding files within:
  '{frontend_dir}'

Alternatively, if the LLM struggles with modification, you might prompt it to regenerate specific files entirely with the integration logic included, then replace the old files.
"""

    if auto_generate:
        click.secho("Generating Frontend Updates using smol-dev...", fg="green")
        handle_step_auto_generation(
            step_num=STEP,
            prompt=frontend_prompt,
            output_filename="part4_frontend.md",
            target_dir=frontend_dir,
            system_prompt=system_prompt,
            manual_instructions=frontend_output_location
        )
    else:
        print_prompt_instructions(frontend_prompt, frontend_output_location)

    # Save a consolidated output file for Step 5
    if auto_generate:
        # Combine all parts into one output file
        consolidated_output = f"""# Step 5: Backend Integration and Authentication

## Part 1: Cognito CloudFormation
See file: {cognito_output_path}

## Part 2: Backend Chalice Code
See directory: {backend_dir}

## Part 3: IAM Roles
See file: {iam_output_path}

## Part 4: Frontend Integration
See changes in: {frontend_dir}

## OpenSearch Integration
OpenSearch Needed: {opensearch_needed}
"""
        step_output_dir = os.path.join(STEP_OUTPUTS, f'step{STEP}')
        os.makedirs(step_output_dir, exist_ok=True)
        consolidated_file = os.path.join(step_output_dir, "integration_summary.md")
        with open(consolidated_file, 'w') as f:
            f.write(consolidated_output)
        click.secho(f"Saved integration summary to: {consolidated_file}", fg="green")

    click.secho(f"Step {STEP} complete. Ensure backend code and frontend updates are saved correctly.", fg="green") 