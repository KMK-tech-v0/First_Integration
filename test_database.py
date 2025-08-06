#!/usr/bin/env python3
"""
Database configuration and SQL script tests for MMP Fiber Fault Reporting System.
"""

import pytest
import os
import json
import re


class TestDatabaseSetup:
    """Test database setup and configuration."""
    
    def test_database_setup_sql_exists(self):
        """Test that database setup SQL file exists."""
        assert os.path.exists("database_setup.sql"), "database_setup.sql should exist"
    
    def test_database_config_structure(self):
        """Test database configuration file structure."""
        if not os.path.exists("database_config.json"):
            pytest.skip("database_config.json not found")
        
        with open("database_config.json", "r") as f:
            config = json.load(f)
        
        # Test basic structure
        assert isinstance(config, dict), "Config should be a dictionary"
        
        # Test if it has reasonable database-related keys
        expected_keys = ["server", "database", "username", "password"]
        has_db_keys = any(key.lower() in str(config).lower() for key in expected_keys)
        assert has_db_keys, "Config should contain database-related configuration"
    
    def test_sql_script_basic_syntax(self):
        """Test that SQL script has basic valid syntax."""
        if not os.path.exists("database_setup.sql"):
            pytest.skip("database_setup.sql not found")
        
        with open("database_setup.sql", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Basic SQL syntax checks
        assert len(content.strip()) > 0, "SQL file should not be empty"
        
        # Check for common SQL keywords
        sql_keywords = ["CREATE", "TABLE", "INSERT", "SELECT"]
        has_sql = any(keyword in content.upper() for keyword in sql_keywords)
        assert has_sql, "SQL file should contain SQL statements"
        
        # Check for basic SQL structure patterns
        assert ";" in content, "SQL file should contain statement terminators"
    
    def test_database_instructions_exist(self):
        """Test that database setup instructions exist."""
        instruction_files = [
            "DATABASE_SETUP_INSTRUCTIONS.md",
            "README.md"
        ]
        
        has_instructions = any(os.path.exists(f) for f in instruction_files)
        assert has_instructions, "Should have database setup instructions"


class TestSQLServerConfiguration:
    """Test SQL Server specific configuration."""
    
    def test_sql_server_references(self):
        """Test that configuration references SQL Server properly."""
        if not os.path.exists("database_config.json"):
            pytest.skip("database_config.json not found")
        
        with open("database_config.json", "r") as f:
            content = f.read()
        
        # Should reference SQL Server instance
        sql_server_patterns = [
            "SQLEXPRESS",
            "sql",
            "server",
            "localhost"
        ]
        
        has_sql_server = any(pattern.lower() in content.lower() for pattern in sql_server_patterns)
        assert has_sql_server, "Config should reference SQL Server"


def test_database_files_present():
    """Test that required database files are present."""
    database_files = [
        "database_setup.sql",
        "database_config.json"
    ]
    
    missing_files = [f for f in database_files if not os.path.exists(f)]
    assert len(missing_files) == 0, f"Missing database files: {missing_files}"


if __name__ == "__main__":
    pytest.main([__file__])
