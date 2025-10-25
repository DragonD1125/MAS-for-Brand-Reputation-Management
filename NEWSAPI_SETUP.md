# NewsAPI Integration Setup

## Current Status

✅ **Code Implementation**: NewsAPI integration has been successfully implemented in `backend/app/tools/data_collection_tools.py`

❌ **API Key**: The current API key in `.env` appears to be invalid or expired

## What Was Implemented

The `NewsDataTool` class now:
1. ✅ Loads the NewsAPI key from settings (`NEWSAPI_KEY`)
2. ✅ Makes HTTP GET requests to `https://newsapi.org/v2/everything`
3. ✅ Searches for articles based on brand keywords
4. ✅ Filters by date range (configurable days back)
5. ✅ Maps NewsAPI response to our internal data structure:
   - `platform`: "news"
   - `external_id`: article URL
   - `author`: article author
   - `title`: article title
   - `description`: article description
   - `content`: article content
   - `url`: article URL
   - `published_date`: when published
   - `metadata`: source name, source ID, image URL
   - `brand_keywords_found`: which keywords were found in the article
6. ✅ Falls back to mock data if API request fails

## Getting a Valid NewsAPI Key

### Step 1: Sign Up
1. Go to https://newsapi.org/
2. Click "Get API Key" or "Sign Up"
3. Create a free account

### Step 2: Get Your API Key
1. Log in to your NewsAPI dashboard
2. Copy your API key (should be a 32-character alphanumeric string)

### Step 3: Update .env File
1. Open `backend/.env`
2. Update the line:
   ```
   NEWSAPI_KEY=your_actual_api_key_here
   ```
3. Replace `your_actual_api_key_here` with your real API key

### Example:
```
NEWSAPI_KEY=abc123def456ghi789jkl012mno345pq
```

## Testing the Integration

Once you have a valid API key:

```bash
# Run the simple demo
python demo_simple.py
```

You should see real news articles being collected:
```
STEP 3: Collecting News Articles
✅ Collected 10 news articles from NewsAPI (total available: 1234)
```

## NewsAPI Free Plan Limits

- **100 requests per day**
- **Articles up to 1 month old**
- **Top headlines and everything endpoints**

For higher limits, consider upgrading to a paid plan at https://newsapi.org/pricing

## API Request Details

The implementation makes requests in this format:
```
GET https://newsapi.org/v2/everything
Parameters:
  - q: "keyword1" OR "keyword2"  (brand keywords)
  - from: YYYY-MM-DD (7 days ago by default)
  - sortBy: publishedAt
  - pageSize: 10 (max 100)
  - language: en
  - apiKey: your_key
```

## Troubleshooting

### 401 Unauthorized Error
- **Cause**: Invalid or expired API key
- **Solution**: Get a new key from https://newsapi.org/

### 429 Too Many Requests
- **Cause**: Exceeded daily limit (100 requests/day for free tier)
- **Solution**: Wait until tomorrow or upgrade your plan

### No Articles Found
- **Cause**: Keywords too specific or no recent news
- **Solution**: Try broader keywords or increase `days_back` parameter

## Current API Key Status

```
Current Key: 24bcc345-06b7-4a0b-a73f-a533a4a40a9e
Status: ❌ Invalid (401 Unauthorized)
```

This key needs to be replaced with a valid API key from https://newsapi.org/

## Mock Data Fallback

If NewsAPI is unavailable or the key is invalid, the system automatically falls back to mock data with a warning message:

```
⚠️ NewsAPI key not configured - using mock data
✅ Collected 3 news articles (mock data - NewsAPI not available)
```

This ensures the demo continues to work while you set up real API access.
