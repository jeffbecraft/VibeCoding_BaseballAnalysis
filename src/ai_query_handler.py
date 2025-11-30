"""
AI-Powered Query Handler for MLB Statistics

This module uses generative AI to interpret user questions and dynamically
generate Python code to answer queries that don't match predefined patterns.

When a query fails with the standard parser, this handler:
1. Sends the question to an AI model (OpenAI GPT-4 or Ollama)
2. AI generates Python code using the MLB API
3. Code is validated and executed in a sandboxed environment
4. Results are returned to the user

Supported AI Providers:
- OpenAI (GPT-4, GPT-3.5-Turbo) - Cloud, requires API key, costs money
- Ollama (llama3.2, mistral, etc.) - Local, FREE, no API key needed

This provides unlimited query flexibility without predefined patterns.
"""

import os
import sys
import json
import re
from typing import Dict, Any, Optional, Tuple
import traceback


class AIQueryHandler:
    """
    Handles queries using AI to generate and execute code dynamically.
    """
    
    def __init__(self, data_fetcher, data_processor, provider: str = "auto"):
        """
        Initialize the AI query handler.
        
        Args:
            data_fetcher: MLBDataFetcher instance for API access
            data_processor: MLBDataProcessor instance for data processing
            provider: "auto" (default), "ollama" (free), or "openai" (cloud)
        """
        self.data_fetcher = data_fetcher
        self.data_processor = data_processor
        self.provider = None
        self.openai = None
        self.ollama = None
        self.model = None
        self.ai_available = False
        
        # Auto-detect or use specified provider
        if provider == "auto":
            # Try Ollama first (free, local)
            if self._init_ollama():
                return
            # Fallback to OpenAI
            self._init_openai()
        elif provider == "ollama":
            self._init_ollama()
        elif provider == "openai":
            self._init_openai()
    
    def _init_ollama(self) -> bool:
        """Try to initialize Ollama (free, local AI)."""
        try:
            import ollama
            # Test if Ollama is running
            try:
                ollama.list()
                self.ollama = ollama
                self.model = os.environ.get('OLLAMA_MODEL', 'llama3.2')
                self.provider = "ollama"
                self.ai_available = True
                print(f"[OK] Using Ollama (FREE) with model: {self.model}")
                return True
            except Exception as e:
                print(f"Ollama not running: {e}")
                return False
        except ImportError:
            return False
    
    def _init_openai(self) -> bool:
        """Try to initialize OpenAI (cloud, paid)."""
        try:
            import openai
            api_key = self._get_api_key()
            if api_key:
                self.openai = openai
                self.openai.api_key = api_key
                self.model = "gpt-4"
                self.provider = "openai"
                self.ai_available = True
                print(f"[OK] Using OpenAI with model: {self.model}")
                return True
            else:
                print("No OPENAI_API_KEY found")
                return False
        except ImportError:
            print("OpenAI package not installed")
            return False
    
    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment variable."""
        return os.environ.get('OPENAI_API_KEY')
    
    def is_available(self) -> bool:
        """Check if AI query handling is available."""
        return self.ai_available
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the active AI provider."""
        if not self.ai_available:
            return {
                "provider": "none",
                "model": None,
                "cost": None,
                "location": None
            }
        
        if self.provider == "ollama":
            return {
                "provider": "ollama",
                "model": self.model,
                "cost": "free",
                "location": "local"
            }
        else:  # openai
            return {
                "provider": "openai",
                "model": self.model,
                "cost": "paid",
                "location": "cloud"
            }
    
    def handle_query(self, question: str, season: int = 2024, progress_callback=None) -> Dict[str, Any]:
        """
        Use AI to interpret the question and generate code to answer it.
        
        Args:
            question: User's natural language question
            season: Season year for the query
            progress_callback: Optional function to call with progress updates
            
        Returns:
            Dictionary with results or error information
        """
        def report_progress(step: str, detail: str = ""):
            """Report progress to callback if provided."""
            if progress_callback:
                progress_callback(step, detail)
        
        if not self.ai_available:
            return {
                'success': False,
                'error': 'AI not available. Install Ollama (free) or set OPENAI_API_KEY.',
                'suggestion': 'Try rephrasing your question or use standard query patterns.'
            }
        
        try:
            # Step 1: Send question to AI
            report_progress("Step 1", f"Sending your question to {self.provider.upper()} AI model ({self.model})...")
            code = self._generate_code(question, season)
            
            if not code:
                return {
                    'success': False,
                    'error': 'AI could not generate code for this question.',
                    'suggestion': 'Try rephrasing your question more clearly.'
                }
            
            # Step 2: Validate generated code
            report_progress("Step 2", "Analyzing AI-generated code for security and safety...")
            is_safe, safety_message = self._validate_code_safety(code)
            
            if not is_safe:
                return {
                    'success': False,
                    'error': f'Generated code failed safety check: {safety_message}',
                    'code': code,
                    'steps': [
                        "✓ AI understood your question",
                        "✓ Generated Python code",
                        "✗ Code blocked by security validation"
                    ]
                }
            
            report_progress("Step 3", "Code passed security checks. Executing query against MLB API...")
            
            # Step 3: Execute the code
            result = self._execute_code(code, question, season)
            
            # Add steps to result
            if result.get('success'):
                result['steps'] = [
                    f"✓ AI ({self.provider}) interpreted your question",
                    "✓ Generated Python code to query MLB API",
                    "✓ Code passed security validation",
                    "✓ Executed query and retrieved data",
                    "✓ Processed results successfully"
                ]
                report_progress("Complete", "Query completed successfully!")
            else:
                result['steps'] = [
                    f"✓ AI ({self.provider}) interpreted your question",
                    "✓ Generated Python code",
                    "✓ Code passed security checks",
                    "✗ Execution failed (see error details)"
                ]
                report_progress("Failed", f"Execution failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'AI query handling failed: {str(e)}',
                'traceback': traceback.format_exc(),
                'steps': [
                    "✗ AI query handler encountered an error"
                ]
            }
    
    def _generate_code(self, question: str, season: int) -> str:
        """
        Use AI to generate Python code that answers the question.
        
        Args:
            question: User's question
            season: Season year
            
        Returns:
            Generated Python code as string
        """
        system_prompt = """You are a Python code generator for MLB statistics queries.

You have access to:
1. data_fetcher - An MLBDataFetcher instance with methods:
   - get_teams() -> list of teams
   - search_players(name) -> list of players
   - get_player_season_stats(player_id, season) -> player stats
   - get_team_season_stats(team_id, season, stat_group) -> team stats
   - get_stats_leaders(stat_type, season, limit, stat_group) -> league leaders

2. data_processor - An MLBDataProcessor instance with methods:
   - extract_stats_leaders(data, limit) -> processed leaders
   - extract_team_stats(teams_data, stat_name) -> team rankings
   - filter_by_season(data, season) -> filtered data

3. pandas as pd, numpy as np - for data processing

Generate ONLY the Python code needed to answer the question. The code should:
- Use the provided data_fetcher and data_processor instances
- Return a result dictionary with 'data', 'explanation', and 'answer' keys
- Handle errors gracefully
- Be efficient and clean

IMPORTANT:
- Do NOT include import statements for data_fetcher, data_processor, pd, or np
- Do NOT include any explanatory text, just the code
- Use try/except to handle potential errors
- The code will be executed in a controlled environment

Example:
Question: "Who hit the most home runs in 2024?"
Code:
```python
try:
    leaders = data_fetcher.get_stats_leaders('homeRuns', season, 1, 'hitting')
    processed = data_processor.extract_stats_leaders(leaders, 1)
    if processed:
        player = processed[0]
        result = {
            'success': True,
            'data': processed,
            'answer': f"{player['name']} hit the most home runs with {player['value']} HR",
            'explanation': 'Retrieved hitting leaders for home runs from MLB API'
        }
    else:
        result = {'success': False, 'error': 'No data found'}
except Exception as e:
    result = {'success': False, 'error': str(e)}
```

Now generate code for the user's question."""

        user_prompt = f"""Question: {question}
Season: {season}

Generate Python code to answer this question using the MLB API."""

        try:
            if self.provider == "ollama":
                # Use Ollama (free, local)
                response = self.ollama.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                generated_code = response['message']['content'].strip()
            else:
                # Use OpenAI (cloud, paid)
                response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )
                generated_code = response.choices[0].message.content.strip()
            
            # Extract code from markdown code blocks if present
            code_match = re.search(r'```python\n(.*?)\n```', generated_code, re.DOTALL)
            if code_match:
                generated_code = code_match.group(1)
            
            return generated_code
            
        except Exception as e:
            print(f"Error generating code with AI: {e}")
            return ""
    
    def _validate_code_safety(self, code: str) -> Tuple[bool, str]:
        """
        Validate that generated code is safe to execute.
        
        Args:
            code: Generated Python code
            
        Returns:
            Tuple of (is_safe: bool, message: str)
        """
        # List of dangerous patterns that should not appear in generated code
        dangerous_patterns = [
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\b__import__\s*\(',
            r'\bcompile\s*\(',
            r'\bopen\s*\(',
            r'\bfile\s*\(',
            r'\binput\s*\(',
            r'\bos\.system',
            r'\bos\.popen',
            r'\bsubprocess',
            r'\bshutil',
            r'\brmdir',
            r'\bunlink',
            r'\bremove',
            r'import\s+os',
            r'import\s+sys',
            r'import\s+subprocess',
            r'import\s+shutil',
            r'from\s+os',
            r'from\s+sys',
            r'__',  # Dunder methods (except in strings)
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Check for allowed imports only
        allowed_imports = ['pandas', 'numpy', 'json', 'datetime', 're']
        import_pattern = r'import\s+(\w+)|from\s+(\w+)'
        imports = re.findall(import_pattern, code)
        
        for imp in imports:
            module = imp[0] or imp[1]
            if module and module not in allowed_imports:
                return False, f"Unauthorized import: {module}"
        
        # Basic syntax check
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        
        return True, "Code passed safety checks"
    
    def _execute_code(self, code: str, question: str, season: int) -> Dict[str, Any]:
        """
        Execute the generated code in a controlled environment.
        
        Args:
            code: Python code to execute
            question: Original question
            season: Season year
            
        Returns:
            Results dictionary
        """
        # Create a restricted execution environment
        restricted_globals = {
            'data_fetcher': self.data_fetcher,
            'data_processor': self.data_processor,
            'season': season,
            'question': question,
            '__builtins__': {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'any': any,
                'all': all,
                'print': print,  # Allow print for debugging
                'Exception': Exception,
                'ValueError': ValueError,
                'KeyError': KeyError,
                'TypeError': TypeError,
            }
        }
        
        # Import commonly needed modules in the execution environment
        try:
            import pandas as pd
            import numpy as np
            restricted_globals['pd'] = pd
            restricted_globals['np'] = np
        except ImportError:
            pass
        
        restricted_locals = {}
        
        try:
            # Execute the generated code
            exec(code, restricted_globals, restricted_locals)
            
            # Get the result
            result = restricted_locals.get('result', {})
            
            if not isinstance(result, dict):
                result = {
                    'success': False,
                    'error': 'Generated code did not produce a result dictionary'
                }
            
            # Add metadata
            result['ai_generated'] = True
            result['generated_code'] = code
            result['original_question'] = question
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Code execution failed: {str(e)}',
                'traceback': traceback.format_exc(),
                'generated_code': code,
                'ai_generated': True
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test if AI connection is working.
        
        Returns:
            Status dictionary
        """
        if not self.ai_available:
            return {
                'success': False,
                'message': 'No AI provider available. Install Ollama or set OPENAI_API_KEY.'
            }
        
        try:
            if self.provider == "ollama":
                # Test Ollama
                response = self.ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": "Say 'OK'"}]
                )
                return {
                    'success': True,
                    'message': 'Connection successful!',
                    'model': self.model,
                    'provider': 'Ollama (FREE, local)'
                }
            else:
                # Test OpenAI
                response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Say 'OK'"}],
                    max_tokens=10
                )
                return {
                    'success': True,
                    'message': 'Connection successful!',
                    'model': self.model,
                    'provider': 'OpenAI (cloud, paid)'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}'
            }


def get_ai_handler(data_fetcher, data_processor) -> Optional[AIQueryHandler]:
    """
    Factory function to create an AI query handler.
    
    Args:
        data_fetcher: MLBDataFetcher instance
        data_processor: MLBDataProcessor instance
        
    Returns:
        AIQueryHandler instance or None if not available
    """
    handler = AIQueryHandler(data_fetcher, data_processor)
    
    if handler.is_available():
        return handler
    else:
        return None
