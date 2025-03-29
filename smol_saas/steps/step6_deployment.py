import click
import os
import subprocess
from .common import (
    print_step_header, print_guidance, print_prompt_instructions,
    load_output, STEP_OUTPUTS, PROJECT_DIR, handle_step_auto_generation
)

STEP = 6
TITLE = "Assemble Infrastructure & Deploy (SAM / Chalice)"

@click.option('--auto-generate', is_flag=True, help='Use smol-dev to automatically generate infrastructure')
@click.option('--system-prompt', help='Optional system prompt for smol-dev when using auto-generate')
def run(auto_generate=False, system_prompt=None):
    """Executes Step 6, guiding infrastructure assembly and deployment."""
    print_step_header(STEP, TITLE)

    # --- Load Context & Check Prerequisites --- #
    # We need snippets from Step 5 and potentially Step 3 output details
    cognito_snippet_path = os.path.join(PROJECT_DIR, 'infrastructure', 'snippets', 'cognito.yaml')
    iam_snippet_path = os.path.join(PROJECT_DIR, 'infrastructure', 'snippets', 'backend_roles.yaml')
    step3_output = load_output(3) # May contain Table ARN structure, OpenSearch flag

    required_files = {
        "Cognito Snippet": cognito_snippet_path,
        "IAM Roles Snippet": iam_snippet_path,
        "Backend Code Dir": os.path.join(PROJECT_DIR, 'backend', 'app.py'),
        "Frontend Build Dir": os.path.join(PROJECT_DIR, 'frontend', 'dist') # Assuming a standard build output
    }

    missing_files = []
    for name, path in required_files.items():
        if not os.path.exists(path):
            missing_files.append(f"- {name} ({path})")

    if missing_files:
        click.secho("Warning: Some files from previous steps are missing:", fg="yellow", bold=True)
        click.echo("\n".join(missing_files))
        if not click.confirm("Do you want to continue anyway?"):
            click.echo("\nPlease ensure the previous steps were completed successfully and files saved correctly.")
            return # Stop execution

    opensearch_needed = "OpenSearch Needed: True" in step3_output
    click.secho(f"Detected OpenSearch Need: {opensearch_needed}", fg="yellow")

    guidance = """
This step focuses on assembling the final CloudFormation template and deploying the application.

Tasks:
1.  **Assemble `template.yaml`:** Combine Cognito, IAM Roles, define API Gateway, DynamoDB Table (if not manually created), and potentially OpenSearch Domain.
2.  **Configure Chalice (if using SAM):** Ensure `.chalice/config.json` is set up for SAM deployment or use Chalice directly.
3.  **Build Frontend:** Create a production build of the React frontend.
4.  **Deploy:** Use AWS SAM CLI (`sam build && sam deploy`) or Chalice CLI (`chalice deploy`).
5.  **Post-Deployment:** Update frontend configuration with deployed API endpoint and Cognito IDs.
"""
    print_guidance(guidance)

    # --- Part 1: Assemble template.yaml --- #
    click.secho("Part 1: Assemble CloudFormation Template (`template.yaml`)", bold=True, fg="blue")
    template_yaml_path = os.path.join(PROJECT_DIR, 'infrastructure', 'template.yaml')
    infra_dir = os.path.join(PROJECT_DIR, 'infrastructure')
    os.makedirs(infra_dir, exist_ok=True)
    
    # Read snippet files to include in the prompt if they exist
    cognito_snippet = ""
    if os.path.exists(cognito_snippet_path):
        with open(cognito_snippet_path, 'r') as f:
            cognito_snippet = f.read()
    
    iam_snippet = ""
    if os.path.exists(iam_snippet_path):
        with open(iam_snippet_path, 'r') as f:
            iam_snippet = f.read()
    
    prompt_guidance_template = f"""
Act as an InfrastructureAgent following 'spec/step6-assemble-deploy.md'.

Task: Generate a complete AWS SAM `template.yaml` file for the application.

Context & Requirements:
- Use the Cognito snippet:
```yaml
{cognito_snippet if cognito_snippet else "# No Cognito snippet available. Please create UserPool and UserPoolClient resources."}
```

- Use the IAM Role snippets:
```yaml
{iam_snippet if iam_snippet else "# No IAM Role snippets available. Please create appropriate IAM Roles."}
```

- DynamoDB Table(s) information from Step 3:
{step3_output}

- Define an AWS::Serverless::Api resource for the Chalice backend.
- Define the AWS::DynamoDB::Table based on the schema from Step 3 output.
- Define the Chalice AWS::Serverless::Function resource(s). Link the appropriate IAM Role.
- If OpenSearch Needed ({opensearch_needed}):
    - Define an AWS::OpenSearchService::Domain resource (consider secure defaults, VPC integration might be needed for production).
    - Define the Indexer AWS::Serverless::Function resource, linking its IAM Role.
    - Define the DynamoDB Stream Event Source Mapping for the Indexer Lambda.
- Define necessary Outputs (e.g., ApiUrl, CognitoUserPoolId, CognitoClientId).
- Ensure resource names are parameterized or clearly defined.

Provide the *complete* `template.yaml` content.
"""
    output_location_template = f"""Save the generated content as the main infrastructure template:
  `{template_yaml_path}`

-- Important --
Make sure the template references the correct resource ARNs and includes all necessary components.
"""

    if auto_generate:
        click.secho("Generating CloudFormation template using smol-dev...", fg="green")
        handle_step_auto_generation(
            step_num=STEP,
            prompt=prompt_guidance_template,
            output_filename="template.yaml",
            target_dir=infra_dir,
            system_prompt=system_prompt,
            manual_instructions=output_location_template,
            single_file=True
        )
    else:
        print_prompt_instructions(prompt_guidance_template, output_location_template)
        input("Press Enter when ready to continue to Part 2...")

    # --- Part 2: Configure Chalice / Build Frontend (Manual Steps) --- #
    click.secho("\nPart 2: Build & Configuration (Manual Steps)", bold=True, fg="blue")
    chalice_config_dir = os.path.join(PROJECT_DIR, 'backend', '.chalice')
    os.makedirs(chalice_config_dir, exist_ok=True)
    
    chalice_config = """
{
  "version": "2.0",
  "app_name": "smol-saas-api",
  "stages": {
    "dev": {
      "api_gateway_stage": "api",
      "manage_iam_role": false,
      "iam_role_arn": "${ChaliceLambdaRole}"
    }
  }
}
"""
    
    chalice_config_path = os.path.join(chalice_config_dir, 'config.json')
    if auto_generate and not os.path.exists(chalice_config_path):
        with open(chalice_config_path, 'w') as f:
            f.write(chalice_config)
        click.secho(f"Created Chalice config: {chalice_config_path}", fg="green")
    
    guidance_build = f"""
Before deployment, you need to:

1.  **Configure Chalice:**
    - A default config has been created at: {chalice_config_path}
    - Verify the settings are correct for your deployment

2.  **Build Frontend:**
    - Navigate to the frontend directory: `cd {os.path.join(PROJECT_DIR, 'frontend')}`
    - Install dependencies: `npm install` (or `yarn install`)
    - Create a production build: `npm run build` (or `yarn build`)
    - Verify the build output exists in `{os.path.join(PROJECT_DIR, 'frontend', 'dist')}`
"""
    print_guidance(guidance_build)

    # --- Part 3: Deployment (Guidance) --- #
    click.secho("\nPart 3: Deploy Application", bold=True, fg="blue")
    deployment_instructions = f"""
Choose your deployment method:

**Method A: AWS SAM** (Recommended if using `template.yaml`)
```bash
# Navigate to the infrastructure directory
cd {os.path.join(PROJECT_DIR, 'infrastructure')}

# Build the SAM application
sam build

# Deploy (guided)
sam deploy --guided
```
Follow the prompts. Provide a stack name, region, and confirm changes.
Note the outputs (ApiUrl, Cognito IDs) provided after successful deployment.

**Method B: Chalice CLI** (Simpler if not managing complex infra with SAM)
```bash
# Navigate to the backend directory
cd {os.path.join(PROJECT_DIR, 'backend')}

# Deploy Chalice
chalice deploy --stage dev
```
Note: This won't deploy Cognito, DynamoDB, OpenSearch defined in `template.yaml`. 
You'd need to deploy those separately (e.g., via `aws cloudformation deploy`).

Need the outputs from deployment for the next step!
"""
    
    if auto_generate:
        # Save the deployment instructions as a file
        deployment_file = os.path.join(STEP_OUTPUTS, f'step{STEP}', 'deployment_instructions.md')
        os.makedirs(os.path.dirname(deployment_file), exist_ok=True)
        with open(deployment_file, 'w') as f:
            f.write(deployment_instructions)
        click.secho(f"Saved deployment instructions to: {deployment_file}", fg="green")
        
        print_guidance(deployment_instructions)
    else:
        print_guidance(deployment_instructions)

    # --- Part 4: Post-Deployment Configuration (Manual) --- #
    click.secho("\nPart 4: Update Frontend Configuration", bold=True, fg="blue")
    guidance_post_deploy = f"""
After successful deployment, you need to:

1.  **Obtain Outputs:** Get the deployed API Gateway endpoint URL, Cognito User Pool ID, and Cognito Client ID from:
    - SAM deployment outputs or 
    - Chalice deploy output / Cognito console

2.  **Update Frontend:**
    - Create a config file: {os.path.join(PROJECT_DIR, 'frontend', 'src', 'config.js')}
    - Example content:
    ```javascript
    const config = {{
      API_URL: 'https://<api-id>.execute-api.<region>.amazonaws.com/api',
      COGNITO_REGION: '<region>',
      COGNITO_USER_POOL_ID: '<user-pool-id>',
      COGNITO_CLIENT_ID: '<client-id>'
    }};

    export default config;
    ```

3.  **Re-build Frontend:**
    ```bash
    cd {os.path.join(PROJECT_DIR, 'frontend')}
    npm run build
    ```

4.  **Deploy Frontend:**
    - You might need to upload the frontend build to an S3 bucket with website hosting enabled.
    - Consider using CloudFront for HTTPS and better performance.
    - Simple S3 hosting command:
    ```bash
    aws s3 sync {os.path.join(PROJECT_DIR, 'frontend', 'dist')} s3://your-bucket-name/ --acl public-read
    ```

5.  **Test:** Access your deployed application and test the functionality.
"""
    print_guidance(guidance_post_deploy)

    # Save a consolidated output file for Step 6
    if auto_generate:
        # Create a summary file for the deployment step
        deployment_summary = f"""# Step 6: Deployment

## Infrastructure Template
Generated template: {template_yaml_path}

## Chalice Configuration
Created config: {chalice_config_path}

## Deployment Instructions
See detailed instructions in: {os.path.join(STEP_OUTPUTS, f'step{STEP}', 'deployment_instructions.md')}

## Post-Deployment
Remember to:
1. Update frontend configuration with API URL and Cognito details
2. Rebuild and deploy the frontend
3. Test the complete application

Congratulations! You've successfully created a full-stack serverless SaaS application.
"""
        
        deployment_summary_file = os.path.join(STEP_OUTPUTS, f'step{STEP}', 'deployment_summary.md')
        os.makedirs(os.path.dirname(deployment_summary_file), exist_ok=True)
        with open(deployment_summary_file, 'w') as f:
            f.write(deployment_summary)
        click.secho(f"Saved deployment summary to: {deployment_summary_file}", fg="green")

    click.secho(f"Step {STEP} guides assembly and deployment. Follow manual steps carefully.", fg="green") 