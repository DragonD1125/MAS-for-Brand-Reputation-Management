"""Test script to check if NewsAPI key is loaded"""
import sys
sys.path.insert(0, 'backend')

from app.core.config import settings

print(f"NEWSAPI_KEY from settings: {settings.NEWSAPI_KEY}")
print(f"Key length: {len(settings.NEWSAPI_KEY) if settings.NEWSAPI_KEY else 0}")
print(f"Key starts with 'your_': {settings.NEWSAPI_KEY.startswith('your_') if settings.NEWSAPI_KEY else 'N/A'}")
