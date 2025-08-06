#!/usr/bin/env python3
"""
Frontend tests for MMP Fiber Fault Reporting System.
Tests HTML, CSS, and JavaScript components.
"""

import pytest
import os
import re
import json


class TestHTMLStructure:
    """Test HTML file structure and content."""
    
    def test_html_meta_tags(self):
        """Test that HTML has proper meta tags."""
        if not os.path.exists("index.html"):
            pytest.skip("index.html not found")
        
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for viewport meta tag (responsive design)
        assert 'name="viewport"' in content, "HTML should have viewport meta tag"
        
        # Check for charset
        assert 'charset=' in content, "HTML should specify character encoding"
    
    def test_html_title(self):
        """Test that HTML has a title."""
        if not os.path.exists("index.html"):
            pytest.skip("index.html not found")
        
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "<title>" in content, "HTML should have a title tag"
        
        # Extract title content
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            title_text = title_match.group(1).strip()
            assert len(title_text) > 0, "Title should not be empty"
    
    def test_html_myanmar_support(self):
        """Test that HTML supports Myanmar language."""
        if not os.path.exists("index.html"):
            pytest.skip("index.html not found")
        
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for Myanmar language indicators
        myanmar_indicators = [
            'lang="my"',
            'Myanmar',
            'Padauk',
            # Myanmar Unicode characters
            '\u1000', '\u1001', '\u1002'  # Basic Myanmar characters
        ]
        
        has_myanmar = any(indicator in content for indicator in myanmar_indicators)
        assert has_myanmar, "HTML should support Myanmar language/content"


class TestJavaScriptStructure:
    """Test JavaScript file structure."""
    
    def test_js_file_not_empty(self):
        """Test that JavaScript file is not empty."""
        if not os.path.exists("app.js"):
            pytest.skip("app.js not found")
        
        with open("app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert len(content.strip()) > 0, "JavaScript file should not be empty"
    
    def test_js_basic_functions(self):
        """Test that JavaScript has basic functions."""
        if not os.path.exists("app.js"):
            pytest.skip("app.js not found")
        
        with open("app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for function definitions
        function_patterns = [
            r'function\s+\w+',
            r'const\s+\w+\s*=.*=>',
            r'let\s+\w+\s*=.*function',
            r'var\s+\w+\s*=.*function'
        ]
        
        has_functions = any(re.search(pattern, content) for pattern in function_patterns)
        assert has_functions, "JavaScript should contain function definitions"
    
    def test_js_api_configuration(self):
        """Test that JavaScript has API configuration."""
        if not os.path.exists("app.js"):
            pytest.skip("app.js not found")
        
        with open("app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for API-related configuration
        api_indicators = [
            "API_BASE_URL",
            "fetch",
            "localhost",
            "http"
        ]
        
        has_api_config = any(indicator in content for indicator in api_indicators)
        assert has_api_config, "JavaScript should have API configuration"


class TestCSS:
    """Test CSS styling."""
    
    def test_css_present(self):
        """Test that CSS styling is present."""
        if not os.path.exists("index.html"):
            pytest.skip("index.html not found")
        
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for CSS (either inline, internal, or external)
        css_indicators = [
            "<style>",
            "stylesheet",
            "css",
            "class=",
            "background-color",
            "color:"
        ]
        
        has_css = any(indicator in content.lower() for indicator in css_indicators)
        assert has_css, "HTML should contain CSS styling"
    
    def test_responsive_design(self):
        """Test for responsive design indicators."""
        if not os.path.exists("index.html"):
            pytest.skip("index.html not found")
        
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for responsive design patterns
        responsive_indicators = [
            "@media",
            "viewport",
            "max-width",
            "min-width",
            "flex",
            "grid"
        ]
        
        has_responsive = any(indicator in content.lower() for indicator in responsive_indicators)
        assert has_responsive, "Should have responsive design elements"


class TestTailwindCSS:
    """Test Tailwind CSS integration."""
    
    def test_tailwind_cdn(self):
        """Test that Tailwind CSS is included."""
        if not os.path.exists("index.html"):
            pytest.skip("index.html not found")
        
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        tailwind_indicators = [
            "tailwindcss",
            "cdn.tailwindcss.com"
        ]
        
        has_tailwind = any(indicator in content for indicator in tailwind_indicators)
        assert has_tailwind, "Should include Tailwind CSS"
    
    def test_tailwind_classes(self):
        """Test that Tailwind CSS classes are used."""
        if not os.path.exists("index.html"):
            pytest.skip("index.html not found")
        
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Common Tailwind utility classes
        tailwind_classes = [
            "flex",
            "p-4",
            "mb-4",
            "text-center",
            "bg-",
            "rounded",
            "shadow"
        ]
        
        tailwind_usage = sum(1 for cls in tailwind_classes if cls in content)
        assert tailwind_usage >= 3, "Should use multiple Tailwind CSS classes"


def test_frontend_integration():
    """Test that frontend components are properly integrated."""
    required_files = ["index.html", "app.js"]
    
    for file in required_files:
        assert os.path.exists(file), f"Frontend file {file} should exist"


if __name__ == "__main__":
    pytest.main([__file__])
