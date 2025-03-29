"""
Basic tests for the smol-saas CLI.
"""

import os
import tempfile
import pytest
from click.testing import CliRunner
from smol_saas.main import cli

def test_cli_init():
    """Test the CLI init command."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(cli, ['init', '--dir', temp_dir])
        assert result.exit_code == 0
        assert 'Initializing new smol-saas project' in result.output
        
        # Check that project directory was set correctly
        assert os.environ.get('SMOL_SAAS_PROJECT_DIR') == os.path.abspath(temp_dir)
        
        # Check that directories were created
        assert os.path.exists(os.path.join(temp_dir, 'outputs'))

def test_cli_list():
    """Test the CLI list command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'Available steps' in result.output
    assert 'Step 1: Define Problem & Requirements' in result.output 