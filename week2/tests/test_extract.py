import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# Tests for LLM-based extraction
class TestExtractActionItemsLLM:
    """Test suite for extract_action_items_llm() function"""

    def test_bullet_list(self):
        """Test extraction from bullet list format"""
        text = """
        - Add user authentication
        - Create database schema
        - Implement API endpoints
        """
        items = extract_action_items_llm(text)
        
        assert len(items) >= 3
        assert any("authentication" in item.lower() for item in items)
        assert any("database" in item.lower() or "schema" in item.lower() for item in items)
        assert any("api" in item.lower() or "endpoint" in item.lower() for item in items)

    def test_checkbox_format(self):
        """Test extraction from checkbox format"""
        text = """
        - [ ] Fix login bug
        - [ ] Update documentation
        - [ ] Deploy to staging
        """
        items = extract_action_items_llm(text)
        
        assert len(items) >= 3
        assert any("login" in item.lower() or "bug" in item.lower() for item in items)
        assert any("documentation" in item.lower() for item in items)
        assert any("deploy" in item.lower() or "staging" in item.lower() for item in items)

    def test_keyword_prefixed_lines(self):
        """Test extraction from keyword-prefixed lines (TODO:, ACTION:, NEXT:)"""
        text = """
        TODO: Refactor authentication module
        ACTION: Add error handling
        NEXT: Write integration tests
        """
        items = extract_action_items_llm(text)
        
        assert len(items) >= 3
        assert any("refactor" in item.lower() or "authentication" in item.lower() for item in items)
        assert any("error" in item.lower() or "handling" in item.lower() for item in items)
        assert any("test" in item.lower() for item in items)

    def test_numbered_list(self):
        """Test extraction from numbered list"""
        text = """
        1. Set up development environment
        2. Install dependencies
        3. Run initial tests
        """
        items = extract_action_items_llm(text)
        
        assert len(items) >= 3
        assert any("environment" in item.lower() or "setup" in item.lower() for item in items)
        assert any("dependencies" in item.lower() or "install" in item.lower() for item in items)
        assert any("test" in item.lower() for item in items)

    def test_mixed_format(self):
        """Test extraction from mixed format (bullets, checkboxes, keywords)"""
        text = """
        TODO: Review pull requests
        - [ ] Update README
        * Add unit tests
        1. Deploy to production
        """
        items = extract_action_items_llm(text)
        
        assert len(items) >= 4
        assert any("review" in item.lower() or "pull request" in item.lower() for item in items)
        assert any("readme" in item.lower() for item in items)
        assert any("test" in item.lower() for item in items)
        assert any("deploy" in item.lower() or "production" in item.lower() for item in items)

    def test_natural_language(self):
        """Test extraction from natural language text"""
        text = """
        We need to improve the performance of the application.
        First, we should profile the code to identify bottlenecks.
        Then, optimize the database queries.
        Finally, add caching for frequently accessed data.
        """
        items = extract_action_items_llm(text)
        
        # LLM should extract at least some action items from natural language
        assert len(items) >= 2
        # Check that items contain relevant keywords
        all_items_text = " ".join(items).lower()
        assert "profile" in all_items_text or "optimize" in all_items_text or "caching" in all_items_text

    def test_empty_input(self):
        """Test with empty input"""
        assert extract_action_items_llm("") == []
        assert extract_action_items_llm("   ") == []
        assert extract_action_items_llm("\n\n") == []

    def test_no_action_items(self):
        """Test with text containing no clear action items"""
        text = """
        This is just a description of the project.
        It explains what the application does.
        There are no specific tasks mentioned here.
        """
        items = extract_action_items_llm(text)
        
        # LLM might extract nothing or very few items from purely descriptive text
        # We just verify it doesn't crash and returns a list
        assert isinstance(items, list)

    def test_single_item(self):
        """Test with single action item"""
        text = "- Implement user registration"
        items = extract_action_items_llm(text)
        
        assert len(items) >= 1
        assert any("registration" in item.lower() or "user" in item.lower() for item in items)

    def test_special_characters(self):
        """Test with special characters and formatting"""
        text = """
        - [ ] Fix bug #123
        - Update config.json file
        * Add @mentions support
        """
        items = extract_action_items_llm(text)
        
        assert len(items) >= 3
        # Verify items are extracted (exact format may vary)
        assert isinstance(items, list)
        assert all(isinstance(item, str) for item in items)
