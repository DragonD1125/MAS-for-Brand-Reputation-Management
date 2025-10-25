"""
Simple Direct Test - Collect News Articles for Google Brand
This demo focuses on NewsAPI integration to collect real news articles
"""

import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_section(text):
    print("-"*70)
    print(f"{text}")
    print("-"*70)

def run_simple_demo():
    """Run a simple demo focusing on NewsAPI"""
    
    print_header("BRAND REPUTATION ANALYSIS - NEWSAPI DEMO")
    print(f"Brand: Google")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Mode: NewsAPI Integration")
    
    try:
        # Import the NewsAPI data collection tool
        from app.tools.data_collection_tools import NewsDataTool
        
        print_section("STEP 1: Collecting News Articles")
        news_tool = NewsDataTool()
        news_data = news_tool._run("Google", max_results=10)
        news_result = json.loads(news_data) if isinstance(news_data, str) else news_data
        
        print(f"✅ Found {news_result.get('articles_found', 0)} news articles")
        if news_result.get('mock_mode'):
            print("   (Using mock data - NewsAPI key not configured)")
        else:
            print(f"   (Real NewsAPI data - {news_result.get('total_results', 0)} total articles available)")
        
        for i, article in enumerate(news_result.get('articles', [])[:10], 1):
            print(f"\n   Article #{i}:")
            print(f"   Source: {article.get('metadata', {}).get('source', 'Unknown')}")
            print(f"   Title: {article.get('title', 'N/A')[:80]}...")
            print(f"   Published: {article.get('published_date', 'N/A')}")
            if article.get('description'):
                print(f"   Summary: {article.get('description', '')[:100]}...")
        
        print_header("SUMMARY")
        total_articles = news_result.get('articles_found', 0)
        
        print(f"📊 Total Articles Collected: {total_articles}")
        print(f"   • News Articles: {total_articles}")
        
        print("\n💡 INSIGHTS:")
        if news_result.get('mock_mode'):
            print("   • Demo using mock data - configure NewsAPI key for real articles")
            print("   • System ready for real news collection")
        else:
            print("   • Real news articles collected from NewsAPI")
            print("   • Articles span recent news coverage")
            print("   • Ready for sentiment analysis and brand monitoring")
        
        print("\n✅ Demo completed successfully!")
        if news_result.get('mock_mode'):
            print("\n📝 Note: Configure NEWSAPI_KEY in backend/.env for real news data.")
        else:
            print("\n📝 Note: NewsAPI integration working - real articles collected!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_simple_demo()
