"""Service for running focused brand analysis using NewsAPI data only."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from loguru import logger

from app.tools.data_collection_tools import MultiPlatformDataCollector

# Basic sentiment lexicon (tunable). Using lightweight lists keeps analysis fast without heavy ML deps.
POSITIVE_WORDS = {
    "amazing", "awesome", "benefit", "best", "boost", "celebrate", "delight",
    "excellent", "favorable", "good", "great", "improve", "innovation", "leading",
    "love", "positive", "successful", "support", "win", "growth", "record", "strong"
}

NEGATIVE_WORDS = {
    "awful", "bad", "concern", "crisis", "decline", "delay", "fail", "failure",
    "lawsuit", "loss", "negative", "poor", "problem", "recall", "risk", "scandal",
    "shortage", "slow", "threat", "warning", "weak", "drop", "fall"
}

STOPWORDS = {
    "the", "and", "for", "with", "that", "from", "this", "have", "will", "they",
    "their", "about", "into", "after", "before", "over", "under", "more", "less",
    "than", "been", "being", "through", "across", "between", "within", "without",
    "company", "brand", "inc", "llc", "corp"
}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


@dataclass
class ArticleSentiment:
    sentiment: str
    score: float


class BrandAnalysisService:
    """Collects NewsAPI articles and produces lightweight sentiment insights."""

    def __init__(self) -> None:
        self.collector = MultiPlatformDataCollector()

    async def run_analysis(
        self,
        brand_name: str,
        max_articles: int = 10,
        days_back: int = 7,
    ) -> Dict[str, object]:
        logger.info("Running brand analysis", brand=brand_name, max_articles=max_articles)

        keywords = [brand_name]
        collection = await self.collector.collect_comprehensive_data(
            keywords=keywords,
            platforms=["news"],
            max_results_per_platform=max_articles,
            days_back=days_back,
        )

        news_result = collection.get("platform_results", {}).get("news", {})
        articles = news_result.get("articles", [])

        processed_articles: List[Dict[str, object]] = []
        for article in articles:
            processed_articles.append(
                self._process_article(article, brand_name=brand_name)
            )

        summary = self._build_summary(processed_articles, brand_name)

        response = {
            "brand_name": brand_name,
            "timeframe_days": days_back,
            "fetched_at": datetime.utcnow().isoformat(),
            "articles": processed_articles,
            "summary": summary,
        }

        logger.info(
            "Brand analysis complete",
            brand=brand_name,
            total_articles=summary.get("total_articles", 0),
        )
        return response

    def _process_article(self, article: Dict[str, object], brand_name: str) -> Dict[str, object]:
        title = str(article.get("title") or "").strip()
        description = str(article.get("description") or "").strip()
        content = str(article.get("content") or "").strip()
        combined_text = " ".join(part for part in [title, description, content] if part)

        sentiment = self._analyze_sentiment(combined_text)
        keywords = self._extract_keywords(combined_text, brand_name)

        published_at = (
            article.get("published_date")
            or article.get("created_at")
            or article.get("metadata", {}).get("published_at")
        )

        return {
            "title": title,
            "source": article.get("metadata", {}).get("source", "Unknown"),
            "url": article.get("url"),
            "published_at": published_at,
            "sentiment": sentiment.sentiment,
            "sentiment_score": round(sentiment.score, 3),
            "excerpt": description[:220] if description else content[:220],
            "keywords": keywords,
        }

    def _analyze_sentiment(self, text: str) -> ArticleSentiment:
        if not text:
            return ArticleSentiment("neutral", 0.0)

        tokens = _tokenize(text)
        if not tokens:
            return ArticleSentiment("neutral", 0.0)

        pos_hits = sum(1 for token in tokens if token in POSITIVE_WORDS)
        neg_hits = sum(1 for token in tokens if token in NEGATIVE_WORDS)

        total = pos_hits + neg_hits
        if total == 0:
            score = 0.0
        else:
            score = (pos_hits - neg_hits) / total

        sentiment = "neutral"
        if score > 0.1:
            sentiment = "positive"
        elif score < -0.1:
            sentiment = "negative"

        return ArticleSentiment(sentiment, float(score))

    def _extract_keywords(self, text: str, brand_name: str) -> List[str]:
        tokens = _tokenize(text)
        brand_tokens = set(_tokenize(brand_name))
        filtered = [
            token
            for token in tokens
            if token not in STOPWORDS and token not in brand_tokens and len(token) > 3
        ]
        top_keywords = [word for word, _ in Counter(filtered).most_common(5)]
        return top_keywords

    def _build_summary(
        self, articles: List[Dict[str, object]], brand_name: str
    ) -> Dict[str, object]:
        total = len(articles)
        sentiment_counts = Counter(article["sentiment"] for article in articles)

        avg_score = 0.0
        if total > 0:
            avg_score = sum(article["sentiment_score"] for article in articles) / total

        keyword_counter: Counter[str] = Counter()
        for article in articles:
            keyword_counter.update(article.get("keywords", []))

        top_keywords = [word for word, _ in keyword_counter.most_common(8)]

        insights: List[str] = []
        if sentiment_counts.get("positive", 0) > sentiment_counts.get("negative", 0):
            insights.append(f"Positive coverage outweighs negative mentions for {brand_name}.")
        elif sentiment_counts.get("negative", 0) > 0:
            insights.append(
                f"Negative coverage detected for {brand_name}; review highlighted articles promptly."
            )

        if total == 0:
            insights.append("No recent articles were found; widen your search keywords if needed.")

        recommendations: List[str] = []
        if sentiment_counts.get("negative", 0) >= math.ceil(total * 0.4) and total > 0:
            recommendations.append(
                "Coordinate a response plan – over 40% of recent coverage trends negative."
            )
        if total > 0 and sentiment_counts.get("positive", 0) == 0:
            recommendations.append("Promote positive stories to balance the narrative.")
        if not recommendations and total > 0:
            recommendations.append("Continue monitoring – sentiment distribution remains balanced.")

        return {
            "total_articles": total,
            "positive": sentiment_counts.get("positive", 0),
            "neutral": sentiment_counts.get("neutral", 0),
            "negative": sentiment_counts.get("negative", 0),
            "average_sentiment_score": round(avg_score, 3) if total > 0 else 0.0,
            "top_keywords": top_keywords,
            "insights": insights,
            "recommendations": recommendations,
        }


brand_analysis_service = BrandAnalysisService()
"""Singleton instance used by API routes."""
