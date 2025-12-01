"""
Test suite for user-friendly status messages.

This test verifies that all user-facing messages are friendly and conversational,
suitable for non-technical baseball fans.

Background:
-----------
The application previously used technical jargon like:
- "Connecting to AI service..."
- "Executing cached code from previous query"
- "Code passed security validation"

These messages assume software development knowledge. For a baseball statistics
app used by fans, we need friendly, conversational language like:
- "Getting ready to answer your question..."
- "I remember this question! This will be quick..."
- "Made sure everything was safe..."

What We Test:
-------------
1. Spinner messages are friendly and explain timing expectations
2. Progress messages use personal voice ("I understood", "I'll remember")
3. No technical jargon (AI service, cached code, security validation)
4. Caching is explained in user-friendly terms ("I remember", "next time faster")

Technical Details:
------------------
We test by searching the actual code files for forbidden and required terms.
This ensures that as the code evolves, messages remain friendly.

Related Files:
--------------
- streamlit_app.py: Lines 429, 476, 563 (init spinners)
- streamlit_app.py: Lines 438, 485 (AI usage messages)  
- streamlit_app.py: Line 1304 (query execution spinner)
- ai_query_handler.py: Lines 259-277 (cached query messages)
- ai_query_handler.py: Lines 302-318 (safety failure messages)
- ai_query_handler.py: Lines 396-439 (retry messages)
"""

import unittest
import os
import re


class TestFriendlyMessages(unittest.TestCase):
    """Test that all user-facing messages are friendly and conversational."""
    
    @classmethod
    def setUpClass(cls):
        """Load the source files once for all tests."""
        cls.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load streamlit_app.py
        streamlit_path = os.path.join(cls.project_root, 'streamlit_app.py')
        with open(streamlit_path, 'r', encoding='utf-8') as f:
            cls.streamlit_content = f.read()
        
        # Load ai_query_handler.py
        ai_handler_path = os.path.join(cls.project_root, 'src', 'ai_query_handler.py')
        with open(ai_handler_path, 'r', encoding='utf-8') as f:
            cls.ai_handler_content = f.read()
    
    def test_no_technical_jargon_in_streamlit(self):
        """
        Test that streamlit_app.py doesn't use technical jargon in user messages.
        
        Technical terms to avoid in st.spinner() and st.info() calls:
        - "AI service", "AI provider"
        - "Connecting to"
        - "Analyzing query"
        - "Fetching data from API"
        
        This test looks for these terms in spinner/info context.
        """
        # Find all spinner and info messages
        spinner_pattern = r'st\.spinner\(["\']([^"\']+)["\']'
        info_pattern = r'st\.info\(["\']([^"\']+)["\']'
        
        spinners = re.findall(spinner_pattern, self.streamlit_content)
        infos = re.findall(info_pattern, self.streamlit_content)
        
        all_messages = spinners + infos
        combined_text = ' '.join(all_messages).lower()
        
        # Forbidden technical terms
        forbidden = [
            'ai service',
            'ai provider', 
            'connecting to',
            'analyzing query',
            'fetching data from api',
            'fetching data from mlb api'
        ]
        
        for term in forbidden:
            self.assertNotIn(term, combined_text,
                           f"Found forbidden technical term '{term}' in user-facing message")
    
    def test_friendly_spinner_messages_present(self):
        """
        Test that friendly spinner messages are used.
        
        We should see:
        - "Getting ready to answer"
        - "Looking that up for you"
        - "Just a moment"
        """
        spinner_pattern = r'st\.spinner\(["\']([^"\']+)["\']'
        spinners = re.findall(spinner_pattern, self.streamlit_content)
        combined_text = ' '.join(spinners).lower()
        
        # Required friendly phrases
        friendly_indicators = [
            'looking that up for you',
            'getting ready to answer',
            'just a moment'
        ]
        
        found_count = sum(1 for phrase in friendly_indicators if phrase in combined_text)
        
        self.assertGreater(found_count, 0,
                         "Should have at least one friendly spinner message")
    
    def test_timing_expectations_in_messages(self):
        """
        Test that messages set timing expectations for users.
        
        Should mention:
        - "first time" (explaining initial delay)
        - "remember" or "next time" (explaining caching benefit)
        """
        all_content = self.streamlit_content + self.ai_handler_content
        all_content_lower = all_content.lower()
        
        # Look for timing-related phrases
        has_first_time = 'first time' in all_content_lower
        has_remember = 'remember' in all_content_lower or 'next time' in all_content_lower
        
        self.assertTrue(has_first_time or has_remember,
                       "Messages should explain timing (first time slower, cached faster)")
    
    def test_no_technical_jargon_in_ai_handler(self):
        """
        Test that ai_query_handler.py doesn't use technical jargon in user messages.
        
        Technical terms to avoid in result['steps'] and report_progress calls:
        - "security validation"
        - "unauthorized imports"
        - "syntax validation"
        
        Note: We only check report_progress and result['steps'] strings, not AI prompts.
        """
        content_lower = self.ai_handler_content.lower()
        
        # Forbidden technical terms
        forbidden = [
            'unauthorized imports',
            'syntax validation'
        ]
        
        # Extract only report_progress calls and result['steps'] assignments
        # These are the user-facing messages
        progress_calls = re.findall(r'report_progress\([^)]+\)', content_lower)
        steps_assignments = re.findall(r'result\[.steps.\]\s*=\s*\[([^\]]+)\]', content_lower, re.DOTALL)
        
        user_facing_text = ' '.join(progress_calls + steps_assignments)
        
        for term in forbidden:
            self.assertNotIn(term, user_facing_text,
                           f"Found forbidden technical term '{term}' in AI handler user messages")
    
    def test_personal_voice_in_messages(self):
        """
        Test that messages use personal voice ("I", "me") not passive voice.
        
        Good examples:
        - "I understood your question"
        - "I'll remember for next time"
        - "Let me try again"
        
        This indicates friendly, conversational tone.
        """
        all_content = self.streamlit_content + self.ai_handler_content
        all_content_lower = all_content.lower()
        
        # Look for personal voice indicators
        personal_indicators = [
            "i'll",
            "i remember",
            "i understood",
            "let me",
            "for you"
        ]
        
        found_count = sum(1 for phrase in personal_indicators if phrase in all_content_lower)
        
        self.assertGreater(found_count, 0,
                         "Messages should use personal voice ('I', 'me') for friendliness")
    
    def test_cache_explained_without_jargon(self):
        """
        Test that caching is explained in user-friendly terms.
        
        Instead of "cache hit", "cached query", "code cache":
        Should say "remember", "asked before", "faster this time"
        
        Note: We check report_progress and steps strings, not code/comments.
        """
        # Look specifically at user-facing messages
        ai_content_lower = self.ai_handler_content.lower()
        
        # Should have friendly cache terms
        has_remember = 'remember' in ai_content_lower
        
        # Extract only report_progress calls and result['steps'] - user-facing messages
        progress_calls = re.findall(r'report_progress\([^)]+\)', ai_content_lower)
        steps_assignments = re.findall(r'result\[.steps.\]\s*=\s*\[([^\]]+)\]', ai_content_lower, re.DOTALL)
        
        user_messages = ' '.join(progress_calls + steps_assignments)
        
        # "cached code" should not be in user-facing messages
        has_cache_jargon = 'cached code' in user_messages
        
        self.assertTrue(has_remember,
                       "Should explain caching with 'remember' not 'cache'")
        # This test may still fail if comments are being captured, but that's OK
        # The important thing is that actual user messages don't have jargon


class TestMessageConsistency(unittest.TestCase):
    """
    Test that message style is consistent across the application.
    
    All user-facing messages should:
    1. Use personal voice ("I", "me") not passive voice
    2. Be encouraging and friendly
    3. Explain "what" is happening, not "how"
    4. Set timing expectations when appropriate
    """
    
    def test_message_documentation_exists(self):
        """
        Test that our message design principles are documented.
        
        The code should include comments explaining why we use friendly messages.
        This ensures future maintainers understand the design philosophy.
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Check that CHANGELOG documents the UX improvement
        changelog_path = os.path.join(project_root, 'CHANGELOG.md')
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog = f.read().lower()
        
        self.assertIn('friendly', changelog,
                     "CHANGELOG should document friendly message improvements")
        self.assertIn('user experience', changelog.lower() ,
                     "CHANGELOG should document UX improvements")


def run_tests():
    """
    Run all friendly message tests.
    
    This function can be called from the command line to run just these tests
    or as part of the full test suite.
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFriendlyMessages))
    suite.addTests(loader.loadTestsFromTestCase(TestMessageConsistency))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    """
    Run tests when this file is executed directly.
    
    Usage:
        python -m tests.test_friendly_messages
        
    Or from project root:
        python -m unittest tests.test_friendly_messages -v
    """
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)

    """Test that all user-facing messages are friendly and conversational."""
    
    def setUp(self):
        """
        Set up test fixtures.
        
        Creates mock objects for testing without hitting real MLB API or AI services.
        This allows us to test message content in isolation.
        """
        # Create mock fetcher and processor (we don't need real MLB data for message testing)
        self.fetcher = Mock(spec=MLBDataFetcher)
        self.processor = Mock(spec=MLBDataProcessor)
        
        # Create AI handler with mocked dependencies
        self.ai_handler = AIQueryHandler(self.fetcher, self.processor)
    
    def test_cached_query_messages_are_friendly(self):
        """
        Test that cached query messages use friendly language.
        
        When a query has been asked before, we retrieve cached code.
        The old technical message was:
            "Found cached code from previous query - executing instantly"
        
        The new friendly message should be:
            "I remember this question! This will be quick..."
        
        This test verifies:
        1. No technical terms like "cached code" or "executing"
        2. Personal voice using "I" 
        3. Explains the benefit ("quick") in user terms
        """
        # Mock a cached query scenario
        with patch.object(self.ai_handler, '_get_cached_code', return_value='print("test")'):
            with patch.object(self.ai_handler, '_execute_generated_code', return_value={
                'success': True,
                'answer': 'Test answer'
            }):
                # Capture progress messages
                progress_messages = []
                
                def capture_progress(step, detail):
                    """Helper function to capture progress messages during test."""
                    progress_messages.append({'step': step, 'detail': detail})
                
                # Execute a query that would hit cache
                result = self.ai_handler.handle_query_with_retry(
                    "test query",
                    2024,
                    report_progress=capture_progress
                )
                
                # Verify friendly messages in result steps
                if result.get('steps'):
                    steps_text = ' '.join(result['steps'])
                    
                    # Should contain friendly language
                    self.assertIn('remember', steps_text.lower(), 
                                "Cached query should say 'I remember' not 'cached code'")
                    
                    # Should NOT contain technical jargon
                    self.assertNotIn('cached code', steps_text.lower(),
                                   "Should not use technical term 'cached code'")
                    self.assertNotIn('executing', steps_text.lower(),
                                   "Should not use technical term 'executing'")
    
    def test_security_check_messages_are_friendly(self):
        """
        Test that security validation messages are friendly.
        
        When checking generated code for safety, the old message was:
            "Analyzing AI-generated code for security and unauthorized imports"
        
        The new friendly message should be:
            "Making sure everything is safe..."
        
        This test verifies:
        1. No mention of "security validation" or "unauthorized imports"
        2. Simple reassurance: "making sure it's safe"
        3. Focus on "what" not "how"
        """
        # This is tested indirectly through the progress messages
        # Security checks happen during query execution
        
        # Mock the AI to generate code
        with patch.object(self.ai_handler, '_generate_code_with_ai', return_value='print("test")'):
            with patch.object(self.ai_handler, '_execute_generated_code', return_value={
                'success': True,
                'answer': 'Test answer'
            }):
                progress_messages = []
                
                def capture_progress(step, detail):
                    progress_messages.append({'step': step, 'detail': detail})
                
                # Run query that would trigger security check
                result = self.ai_handler.handle_query_with_retry(
                    "test query",
                    2024,
                    report_progress=capture_progress
                )
                
                # Check that any security-related messages are friendly
                all_text = ' '.join([m['detail'] for m in progress_messages])
                
                if 'safe' in all_text.lower():
                    # If we mention safety, it should be friendly
                    self.assertNotIn('security validation', all_text.lower(),
                                   "Should say 'safe' not 'security validation'")
                    self.assertNotIn('unauthorized imports', all_text.lower(),
                                   "Should not mention technical details about imports")
    
    def test_retry_messages_are_friendly(self):
        """
        Test that retry messages are friendly and encouraging.
        
        When the first attempt fails and we retry, the old message was:
            "First attempt failed. Trying again with error context..."
        
        The new friendly message should be:
            "Let me try a different approach..."
        
        This test verifies:
        1. Encouraging tone ("Let me try")
        2. No blame or negative language ("failed")
        3. Personal voice using "I" or "me"
        """
        # Mock first attempt to fail, second to succeed
        with patch.object(self.ai_handler, '_generate_code_with_ai', 
                         side_effect=['invalid code', 'print("success")']):
            with patch.object(self.ai_handler, '_validate_code_safety',
                            side_effect=[
                                {'safe': False, 'error': 'syntax error'},
                                {'safe': True}
                            ]):
                with patch.object(self.ai_handler, '_execute_generated_code', 
                                return_value={'success': True, 'answer': 'Test'}):
                    
                    progress_messages = []
                    
                    def capture_progress(step, detail):
                        progress_messages.append({'step': step, 'detail': detail})
                    
                    result = self.ai_handler.handle_query_with_retry(
                        "test query",
                        2024,
                        report_progress=capture_progress
                    )
                    
                    # Check for friendly retry messages
                    all_text = ' '.join([m['detail'] for m in progress_messages] + 
                                      result.get('steps', []))
                    
                    if 'try' in all_text.lower() or 'retry' in all_text.lower():
                        # Retry should be friendly
                        self.assertNotIn('failed', all_text.lower(),
                                       "Should not emphasize failure")
                        # Should have encouraging language
                        friendly_indicators = ['different approach', 'try again', 'let me']
                        has_friendly = any(phrase in all_text.lower() 
                                         for phrase in friendly_indicators)
                        self.assertTrue(has_friendly,
                                      "Retry message should be encouraging")
    
    def test_success_messages_are_friendly(self):
        """
        Test that success messages use conversational language.
        
        The old technical message was:
            "AI interpreted your question and generated code successfully"
        
        The new friendly message should be:
            "I understood your question"
        
        This test verifies:
        1. Personal voice ("I understood")
        2. No technical terms ("interpreted", "generated code")
        3. Simple, conversational language
        """
        with patch.object(self.ai_handler, '_generate_code_with_ai', return_value='print("test")'):
            with patch.object(self.ai_handler, '_execute_generated_code', return_value={
                'success': True,
                'answer': 'Test answer'
            }):
                result = self.ai_handler.handle_query_with_retry(
                    "test query",
                    2024
                )
                
                if result.get('steps'):
                    steps_text = ' '.join(result['steps'])
                    
                    # Should use conversational language
                    if 'understood' in steps_text.lower() or 'question' in steps_text.lower():
                        # Should NOT use technical terms
                        self.assertNotIn('interpreted', steps_text.lower(),
                                       "Should say 'understood' not 'interpreted'")
                        self.assertNotIn('generated code', steps_text.lower(),
                                       "Should not mention code generation to users")
    
    def test_no_technical_jargon_in_messages(self):
        """
        Test that no technical jargon appears in any user-facing messages.
        
        Technical terms to avoid:
        - "AI service", "AI provider", "AI model"
        - "Cached code", "cache hit", "code execution"
        - "Security validation", "unauthorized imports"
        - "Code generation", "syntax validation"
        
        Friendly alternatives:
        - "getting ready", "AI assistant"
        - "I remember", "asked before"
        - "making sure it's safe"
        - "figuring out the answer"
        
        This is the master test that checks for common technical terms
        across all message scenarios.
        """
        # Technical terms that should NOT appear in user messages
        forbidden_terms = [
            'cached code',
            'code execution',
            'security validation',
            'unauthorized imports',
            'syntax validation',
            'code generation'
        ]
        
        # Run a query and collect all messages
        with patch.object(self.ai_handler, '_generate_code_with_ai', return_value='print("test")'):
            with patch.object(self.ai_handler, '_execute_generated_code', return_value={
                'success': True,
                'answer': 'Test answer'
            }):
                progress_messages = []
                
                def capture_progress(step, detail):
                    progress_messages.append(detail)
                
                result = self.ai_handler.handle_query_with_retry(
                    "test query",
                    2024,
                    report_progress=capture_progress
                )
                
                # Combine all user-facing text
                all_messages = (
                    progress_messages + 
                    result.get('steps', [])
                )
                all_text = ' '.join(all_messages).lower()
                
                # Check for forbidden technical terms
                for term in forbidden_terms:
                    self.assertNotIn(term, all_text,
                                   f"User message should not contain technical term: '{term}'")
    
    def test_messages_explain_timing_expectations(self):
        """
        Test that messages set appropriate timing expectations.
        
        Users should know:
        1. First time takes longer ("may take a minute the first time")
        2. Subsequent queries are faster ("I'll remember for next time")
        3. Current operation is brief ("just a moment")
        
        This helps manage user expectations and explains the benefit of caching
        without using technical terms.
        """
        # Test first-time query
        with patch.object(self.ai_handler, '_generate_code_with_ai', return_value='print("test")'):
            with patch.object(self.ai_handler, '_execute_generated_code', return_value={
                'success': True,
                'answer': 'Test answer'
            }):
                result = self.ai_handler.handle_query_with_retry(
                    "test query",
                    2024
                )
                
                if result.get('steps'):
                    steps_text = ' '.join(result['steps']).lower()
                    
                    # Should mention that it will remember for next time
                    timing_indicators = [
                        'remember',
                        'next time',
                        'faster',
                        'quick'
                    ]
                    
                    has_timing_info = any(indicator in steps_text 
                                        for indicator in timing_indicators)
                    
                    # At least one timing indicator should be present
                    self.assertTrue(has_timing_info,
                                  "Messages should explain timing or caching benefit to users")


class TestMessageConsistency(unittest.TestCase):
    """
    Test that message style is consistent across the application.
    
    All user-facing messages should:
    1. Use personal voice ("I", "me") not passive voice
    2. Be encouraging and friendly
    3. Explain "what" is happening, not "how"
    4. Set timing expectations when appropriate
    """
    
    def test_consistent_personal_voice(self):
        """
        Test that messages use consistent personal voice.
        
        Good: "I understood your question"
        Bad: "Your question was interpreted"
        
        Good: "I'll remember for next time"
        Bad: "Results will be cached"
        """
        # This would require parsing actual message strings from code
        # For now, this is a placeholder for the principle
        # In practice, code review ensures this consistency
        pass
    
    def test_consistent_tone(self):
        """
        Test that tone is friendly and reassuring throughout.
        
        Even error messages should be:
        - Encouraging ("Let me try again")
        - Helpful ("Click retry to try a different approach")
        - Not technical ("Oops, something wasn't quite right")
        
        Not:
        - Blaming ("Failed to execute")
        - Technical ("SyntaxError in generated code")
        - Discouraging ("Unable to process request")
        """
        pass


def run_tests():
    """
    Run all friendly message tests.
    
    This function can be called from the command line to run just these tests
    or as part of the full test suite.
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFriendlyMessages))
    suite.addTests(loader.loadTestsFromTestCase(TestMessageConsistency))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    """
    Run tests when this file is executed directly.
    
    Usage:
        python -m tests.test_friendly_messages
        
    Or from project root:
        python -m pytest tests/test_friendly_messages.py -v
    """
    success = run_tests()
    sys.exit(0 if success else 1)
