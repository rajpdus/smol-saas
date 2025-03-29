#!/bin/bash
#
# Setup script for new smol-saas project with auto-generation
#

set -e

# Text formatting
BOLD="\033[1m"
RESET="\033[0m"
GREEN="\033[32m"
BLUE="\033[34m"
YELLOW="\033[33m"

# Default project directory
PROJECT_DIR="./my-saas-app"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dir)
      PROJECT_DIR="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --dir VALUE     Set the project directory (default: ./my-saas-app)"
      echo "  --help          Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo -e "${BOLD}${BLUE}Setting up a new smol-saas project${RESET}"
echo -e "Project directory: ${BOLD}${PROJECT_DIR}${RESET}\n"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo -e "${BOLD}${YELLOW}Error: pip not found. Please install Python and pip first.${RESET}"
    exit 1
fi

# Check if Python version is 3.8+
python_version=$(python3 --version 2>&1 | awk '{print $2}')
major=$(echo $python_version | cut -d. -f1)
minor=$(echo $python_version | cut -d. -f2)

if [[ $major -lt 3 || ($major -eq 3 && $minor -lt 8) ]]; then
    echo -e "${BOLD}${YELLOW}Error: Python 3.8+ is required. You have: $python_version${RESET}"
    exit 1
fi

echo -e "${BOLD}1. Installing smol-saas with auto-generation support...${RESET}"
pip install "smol-saas[auto]"

echo -e "\n${BOLD}2. Initializing project...${RESET}"
smol-saas init --dir "$PROJECT_DIR"

echo -e "\n${BOLD}3. Project ready - next steps:${RESET}"
echo -e "${GREEN}cd $PROJECT_DIR${RESET}"
echo -e "${GREEN}smol-saas step 1 --auto-generate${RESET} # Define problem & requirements"
echo -e "${GREEN}smol-saas step 2 --auto-generate${RESET} # Information architecture"
echo -e "${GREEN}# ... and so on for each step, or use:${RESET}"
echo -e "${GREEN}smol-saas step 1 --auto-generate --all-steps${RESET} # Run all steps with auto-generation"
echo ""
echo -e "${BOLD}${BLUE}Setup complete!${RESET}" 