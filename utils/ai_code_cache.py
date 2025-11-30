"""
AI Code Cache Module

Caches successfully-generated AI code snippets to reduce latency on repeated queries.
When a user asks a question that's been answered before (or very similar), we can
skip the 2-5 second AI generation step and execute the cached code directly.

Benefits:
- 2-5 second speedup for repeated/similar questions
- Works even if Ollama is offline (for cached queries)
- Learns from usage patterns
- Provides analytics on popular queries
"""

import hashlib
import json
import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List


class AICodeCache:
    """Cache successfully-generated AI code snippets."""
    
    def __init__(self, cache_dir: str = None, ttl_days: int = 30):
        """
        Initialize AI code cache.
        
        Args:
            cache_dir: Directory to store cached code (defaults to data/ai_code_cache)
            ttl_days: Time-to-live in days for cached code (default 30)
        """
        if cache_dir is None:
            # Default to data/ai_code_cache directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cache_dir = os.path.join(base_dir, 'data', 'ai_code_cache')
        
        self.cache_dir = cache_dir
        self.ttl = timedelta(days=ttl_days)
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _normalize_question(self, question: str, season: int) -> str:
        """
        Normalize question for cache key matching.
        
        Makes similar questions map to the same cache entry:
        - "Aaron Judge home runs 2024" 
        - "Judge HR in 2024"
        - "How many homers did Judge hit in 2024?"
        
        All become: "aaron judge home runs 2024"
        
        Args:
            question: User's question
            season: Season year
            
        Returns:
            Normalized question string
        """
        # Lowercase and remove punctuation
        normalized = question.lower().strip()
        for char in "?!.,;:":
            normalized = normalized.replace(char, "")
        
        # Normalize common abbreviations
        replacements = {
            "hr": "home runs",
            "hrs": "home runs",
            "rbi": "runs batted in",
            "rbis": "runs batted in",
            "avg": "batting average",
            "ba": "batting average",
            "obp": "on base percentage",
            "ops": "on base plus slugging",
            "slg": "slugging percentage",
            "era": "earned run average",
            "whip": "walks hits per inning pitched",
            "vs": "versus",
            "v": "versus",
            "compare": "versus",
            "comparison": "versus",
            "homers": "home runs",
            "dingers": "home runs",
            "strikeouts": "strikeouts",
            "ks": "strikeouts",
            "walks": "walks",
            "bbs": "walks",
        }
        
        words = normalized.split()
        normalized_words = [replacements.get(w, w) for w in words]
        normalized = " ".join(normalized_words)
        
        # Add season to ensure different years are cached separately
        normalized = f"{normalized} {season}"
        
        return normalized
    
    def _generate_cache_key(self, question: str, season: int) -> str:
        """
        Generate cache key from normalized question.
        
        Args:
            question: User's question
            season: Season year
            
        Returns:
            MD5 hash to use as cache key
        """
        normalized = self._normalize_question(question, season)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get file path for a cache entry."""
        return os.path.join(self.cache_dir, f"{cache_key}.code")
    
    def get(self, question: str, season: int) -> Optional[Dict[str, Any]]:
        """
        Get cached code for a question.
        
        Args:
            question: User's question
            season: Season year
            
        Returns:
            Dictionary with 'code' and metadata, or None if not found/expired
        """
        cache_key = self._generate_cache_key(question, season)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check expiration
            cached_time = cache_data.get('timestamp')
            if cached_time and datetime.now() - cached_time < self.ttl:
                # Track hits
                cache_data['hits'] = cache_data.get('hits', 0) + 1
                cache_data['last_used'] = datetime.now()
                
                # Update hit count
                with open(cache_path, 'wb') as f:
                    pickle.dump(cache_data, f)
                
                return cache_data
            else:
                # Expired - remove cache file
                os.remove(cache_path)
                return None
                
        except Exception as e:
            print(f"AI code cache read error: {e}")
            return None
    
    def set(self, question: str, season: int, code: str, 
            success: bool = True, execution_time: float = 0) -> None:
        """
        Store generated code in cache.
        
        Args:
            question: Original user question
            season: Season year
            code: Generated Python code
            success: Whether the code executed successfully (only cache if True)
            execution_time: How long the code took to execute (seconds)
        """
        if not success:
            return  # Don't cache failed code
        
        cache_key = self._generate_cache_key(question, season)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'question': question,
            'normalized': self._normalize_question(question, season),
            'season': season,
            'code': code,
            'timestamp': datetime.now(),
            'last_used': datetime.now(),
            'hits': 0,
            'execution_time': execution_time,
            'success': success
        }
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"AI code cache write error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics including:
            - total_entries: Number of cached queries
            - total_hits: Total cache hits across all entries
            - cache_dir: Cache directory path
            - top_queries: Most popular cached queries
        """
        if not os.path.exists(self.cache_dir):
            return {
                'total_entries': 0,
                'total_hits': 0,
                'cache_dir': self.cache_dir,
                'top_queries': []
            }
        
        files = [f for f in os.listdir(self.cache_dir) if f.endswith('.code')]
        total_entries = len(files)
        total_hits = 0
        all_queries = []
        
        for file in files:
            try:
                with open(os.path.join(self.cache_dir, file), 'rb') as f:
                    data = pickle.load(f)
                    hits = data.get('hits', 0)
                    total_hits += hits
                    
                    all_queries.append({
                        'question': data.get('question'),
                        'normalized': data.get('normalized'),
                        'hits': hits,
                        'last_used': data.get('last_used'),
                        'cached_at': data.get('timestamp'),
                        'execution_time': data.get('execution_time', 0)
                    })
            except Exception as e:
                print(f"Error reading cache file {file}: {e}")
        
        # Sort by hits (most popular first)
        all_queries.sort(key=lambda x: x['hits'], reverse=True)
        
        return {
            'total_entries': total_entries,
            'total_hits': total_hits,
            'cache_dir': self.cache_dir,
            'top_queries': all_queries[:20]  # Top 20 most popular
        }
    
    def clear(self) -> int:
        """
        Clear all cached code.
        
        Returns:
            Number of entries removed
        """
        if not os.path.exists(self.cache_dir):
            return 0
        
        files = [f for f in os.listdir(self.cache_dir) if f.endswith('.code')]
        count = 0
        
        for file in files:
            try:
                os.remove(os.path.join(self.cache_dir, file))
                count += 1
            except Exception as e:
                print(f"Error removing cache file {file}: {e}")
        
        return count
    
    def remove(self, cache_key: str) -> bool:
        """
        Remove a specific cached query by its cache key.
        
        Args:
            cache_key: The cache key (hash) to remove
            
        Returns:
            True if removed, False if not found
        """
        if not os.path.exists(self.cache_dir):
            return False
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.code")
        
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                return True
            except Exception as e:
                print(f"Error removing cache file {cache_key}: {e}")
                return False
        
        return False

