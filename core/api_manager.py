"""API Manager - Multi-key rotation for free tier survival."""

import os
import time
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI


class APIManager:
    """Manages multiple Gemini API keys with smart rotation."""
    
    def __init__(self):
        # Load all available API keys
        self.api_keys = []
        for i in range(1, 10):  # Check for up to 10 keys
            key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if key:
                self.api_keys.append({
                    'key': key,
                    'requests_today': 0,
                    'last_reset': datetime.now(),
                    'name': f"Key {i}"
                })
        
        # Fallback to single key
        if not self.api_keys:
            single_key = os.getenv("GOOGLE_API_KEY")
            if single_key:
                self.api_keys.append({
                    'key': single_key,
                    'requests_today': 0,
                    'last_reset': datetime.now(),
                    'name': "Key 1"
                })
        
        if not self.api_keys:
            raise ValueError("No GOOGLE_API_KEY found in environment")
        
        print(f"🔑 Loaded {len(self.api_keys)} API key(s)")
        print(f"📊 Total daily capacity: {len(self.api_keys) * 20} requests")
        
        self.current_key_index = 0
        self.RPD_LIMIT = 20  # Per key limit
        self.last_minute_requests = []
    
    def get_llm(self, temperature=0.7):
        """Get LLM instance with automatic key rotation."""
        key_info = self._get_available_key()
        
        if not key_info:
            raise Exception("❌ All API keys exhausted for today! Please try tomorrow.")
        
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Latest model
            temperature=temperature,
            google_api_key=key_info['key']
        )
    
    def _get_available_key(self):
        """Find an available API key with quota remaining."""
        now = datetime.now()
        
        # Reset daily counters at midnight
        for key_info in self.api_keys:
            if now.date() > key_info['last_reset'].date():
                key_info['requests_today'] = 0
                key_info['last_reset'] = now
                print(f"♻️ {key_info['name']} reset: {key_info['requests_today']}/20")
        
        # Try to find a key with quota
        for i in range(len(self.api_keys)):
            idx = (self.current_key_index + i) % len(self.api_keys)
            key_info = self.api_keys[idx]
            
            if key_info['requests_today'] < self.RPD_LIMIT:
                # Use this key
                key_info['requests_today'] += 1
                self.current_key_index = idx
                
                # Show usage occasionally
                if key_info['requests_today'] % 5 == 0:
                    print(f"📊 {key_info['name']}: {key_info['requests_today']}/{self.RPD_LIMIT} used")
                
                return key_info
        
        # All keys exhausted
        return None
    
    def get_usage_stats(self):
        """Get current usage statistics."""
        total_used = sum(k['requests_today'] for k in self.api_keys)
        total_limit = len(self.api_keys) * self.RPD_LIMIT
        
        stats = f"📊 API Usage:\n"
        for key_info in self.api_keys:
            stats += f"   {key_info['name']}: {key_info['requests_today']}/{self.RPD_LIMIT}\n"
        stats += f"   Total: {total_used}/{total_limit} ({(total_used/total_limit*100):.1f}%)"
        
        return stats
