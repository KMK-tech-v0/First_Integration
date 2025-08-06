#!/usr/bin/env python3
"""
Basic test file for pytest to ensure CI/CD pipeline passes.
This file contains basic tests for the MMP Fiber Fault Reporting System.
"""

import pytest
import os
import json
from pathlib import Path


class TestProjectStructure:
    """Test basic project structure and files."""
    
    def test_index_html_exists(self):
        """Test that the main HTML file exists."""
        assert os.path.exists("index.html"), "index.html file should exist"
    
    def test_app_js_exists(self):
        """Test that the main JavaScript file exists."""
        assert os.path.exists("app.js"), "app.js file should exist"
    
    def test_package_json_exists(self):
        """Test that package.json exists."""
        assert os.path.exists("package.json"), "package.json file should exist"
    
    def test_database_config_exists(self):
        """Test that database configuration file exists."""
        assert os.path.exists("database_config.json"), "database_config.json file should exist"


class TestDatabaseConfig:
    """Test database configuration."""
    
    def test_database_config_valid_json(self):
        """Test that database_config.json is valid JSON."""
        try:
            with open("database_config.json", "r") as f:
                config = json.load(f)
            assert isinstance(config, dict), "Config should be a dictionary"
        except FileNotFoundError:
            pytest.skip("database_config.json not found")
        except json.JSONDecodeError:
            pytest.fail("database_config.json is not valid JSON")


class TestPackageJson:
    """Test package.json configuration."""
    
    def test_package_json_valid(self):
        """Test that package.json is valid JSON and has required fields."""
        try:
            with open("package.json", "r") as f:
                package = json.load(f)
            
            assert isinstance(package, dict), "package.json should be a dictionary"
            assert "name" in package, "package.json should have a name field"
            assert "scripts" in package, "package.json should have scripts field"
            
        except FileNotFoundError:
            pytest.skip("package.json not found")
        except json.JSONDecodeError:
            pytest.fail("package.json is not valid JSON")


class TestPythonScripts:
    """Test Python utility scripts."""
    
    def test_python_files_syntax(self):
        """Test that Python files have valid syntax by importing them."""
        python_files = [
            "Daily_SM_Analysis.py",
            "daily_generated_trial.py"
        ]
        
        for py_file in python_files:
            if os.path.exists(py_file):
                # Test file syntax by attempting to compile it
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    compile(content, py_file, "exec")
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {py_file}: {e}")
                except Exception:
                    # Other exceptions are ok for this basic syntax test
                    pass


def test_project_basic_structure():
    """Test that the project has basic required structure."""
    required_files = ["index.html", "app.js"]
    
    for file in required_files:
        assert os.path.exists(file), f"Required file {file} is missing"


def test_html_basic_structure():
    """Test that index.html has basic HTML structure."""
    if not os.path.exists("index.html"):
        pytest.skip("index.html not found")
    
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Basic HTML structure checks
    assert "<!DOCTYPE html>" in content or "<!doctype html>" in content.lower(), "HTML should have DOCTYPE declaration"
    assert "<html" in content.lower(), "HTML should have html tag"
    assert "<head>" in content.lower(), "HTML should have head section"
    assert "<body>" in content.lower(), "HTML should have body section"


if __name__ == "__main__":
    pytest.main([__file__])
