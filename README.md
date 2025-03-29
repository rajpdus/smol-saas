# smol-saas

A CLI tool for generating serverless SaaS applications on AWS, powered by AI.

## Overview

smol-saas guides you through the process of creating a complete serverless SaaS application using AWS technologies. It combines a structured step-by-step approach with AI assistance to help you define, architect, and implement your SaaS product quickly.

## Features

- **Guided Process**: Follow a structured 6-step process from problem definition to deployment
- **AI-Powered Generation**: Leverage AI to generate code, architecture, and documentation
- **AWS Serverless Stack**: Build on AWS technologies (Lambda, DynamoDB, Cognito, etc.)
- **Modern Frontend**: Generate React frontends with shadcn/ui components
- **Complete Solution**: From data modeling to authentication to deployment

## Installation

```bash
pip install smol-saas
```

### Auto-Generation Support

For automatic code generation features, install with the `auto` extra:

```bash
pip install "smol-saas[auto]"
```

## Prerequisites

- Python 3.8+
- AWS CLI configured with appropriate credentials
- For deployment: AWS SAM CLI
- For auto-generation: smol-dev 0.0.4+

## Quick Start

### Option 1: Setup Script (Recommended)

Use our setup script to quickly get started with auto-generation:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/smol-saas/main/scripts/setup-new-project.sh | bash
```

Or with a custom directory:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/smol-saas/main/scripts/setup-new-project.sh | bash -s -- --dir my-custom-project
```

### Option 2: Manual Setup

1. Initialize a new project:
   ```bash
   smol-saas init --dir my-saas-project
   ```

2. Run through each step sequentially:
   ```bash
   smol-saas step 1  # Define Problem
   smol-saas step 2  # Information Architecture
   smol-saas step 3  # DynamoDB Data Model
   smol-saas step 4  # Generate UI
   smol-saas step 5  # Backend & Auth
   smol-saas step 6  # Deploy
   ```

3. Or run all steps with auto-generation:
   ```bash
   smol-saas step 1 --auto-generate --all-steps
   ```

## Workflow

smol-saas employs a step-by-step approach to guide you through building your SaaS application:

1. **Define Problem & Requirements**: Clearly articulate what problem you're solving and for whom
2. **Information Architecture**: Define core entities, relationships, and workflows
3. **DynamoDB Data Model**: Design your NoSQL database with access patterns in mind
4. **Generate UI**: Create a React frontend with shadcn/ui components
5. **Integrate Backend & Auth**: Build an AWS Chalice backend with Cognito authentication
6. **Infrastructure & Deployment**: Assemble CloudFormation and deploy with AWS SAM

Each step builds upon the previous ones, creating a cohesive application by the end.

## Auto-Generation

For each step, you can use the `--auto-generate` flag to leverage AI for automatic code and document generation:

```bash
smol-saas step 3 --auto-generate
```

This utilizes the `smol-dev` library to generate code based on prompts and previous step outputs.

## Project Structure

A typical smol-saas project follows this structure:

```
my-saas-project/
├── backend/           # Chalice application
│   ├── app.py         # Main backend application
│   └── .chalice/      # Chalice configuration
├── frontend/          # React application
│   ├── src/           # Frontend source code
│   └── package.json   # Frontend dependencies
├── infrastructure/    # AWS CloudFormation templates
│   ├── template.yaml  # Main CloudFormation template
│   └── snippets/      # Generated CloudFormation snippets
└── outputs/           # Step-by-step outputs
    ├── step1/         # Problem definition
    ├── step2/         # Information architecture
    └── ...            # Additional step outputs
```

## Customization

You can provide custom system prompts to the AI generator:

```bash
smol-saas step 4 --auto-generate --system-prompt "Focus on accessibility and mobile-first design"
```

## Contributing

Contributions are welcome! Please check out our [contribution guidelines](CONTRIBUTING.md) for more information.

## License

MIT License

## Acknowledgements

- Built with [smol-dev](https://github.com/smol-ai/developer) for AI code generation
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Backend powered by [AWS Chalice](https://github.com/aws/chalice) 