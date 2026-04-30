"""Google Trends data fetching for CPG categories."""

from __future__ import annotations

import logging
import random
import time
from typing import Any

from pytrends.request import TrendReq

logger = logging.getLogger(__name__)

COFFEE_KEYWORDS = [
    "cold brew", "mushroom coffee", "coffee alternative", "matcha latte",
    "nitro coffee", "coffee subscription", "instant coffee", "espresso",
    "oat milk coffee", "protein coffee", "adaptogen coffee", "decaf coffee",
    "coffee creamer", "coffee flavors", "iced coffee",
]

GENERAL_CPG_KEYWORDS = [
    "protein snack", "gut health", "electrolyte drink", "energy bar",
    "plant based", "collagen supplement", "probiotic drink", "sparkling water",
    "healthy snack", "meal replacement", "organic food", "superfood",
    "keto snack", "sugar free", "functional beverage", "nootropic drink",
    "prebiotic soda", "kombucha", "adaptogen", "sleep supplement",
    "beauty supplement", "hydration powder", "greens powder", "fiber supplement",
    "apple cider vinegar drink", "turmeric drink", "cbd drink",
    "low calorie snack", "high protein", "vegan snack",
]


def fetch_trending_data(keywords: list[str], category: str) -> dict[str, Any]:
    """Fetch Google Trends data for a set of keywords.

    Returns trending keywords with their relative interest scores.
    """
    try:
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))

        sample = random.sample(keywords, min(5, len(keywords)))

        pytrends.build_payload(sample, timeframe="today 3-m", geo="US")
        time.sleep(1)

        interest_df = pytrends.interest_over_time()

        results: dict[str, Any] = {
            "category": category,
            "keywords_analyzed": sample,
            "keyword_scores": {},
            "rising_queries": {},
            "related_topics": {},
        }

        if not interest_df.empty:
            for kw in sample:
                if kw in interest_df.columns:
                    series = interest_df[kw]
                    results["keyword_scores"][kw] = {
                        "current": int(series.iloc[-1]) if len(series) > 0 else 0,
                        "avg": round(float(series.mean()), 1),
                        "max": int(series.max()),
                        "trend": "rising" if len(series) > 1 and series.iloc[-1] > series.mean() else "stable",
                    }

        for kw in sample[:2]:
            try:
                pytrends.build_payload([kw], timeframe="today 3-m", geo="US")
                time.sleep(1)
                related = pytrends.related_queries()
                if kw in related and related[kw]["rising"] is not None:
                    rising_df = related[kw]["rising"].head(5)
                    results["rising_queries"][kw] = rising_df["query"].tolist()
                if kw in related and related[kw]["top"] is not None:
                    top_df = related[kw]["top"].head(5)
                    results["related_topics"][kw] = top_df["query"].tolist()
            except Exception as e:
                logger.warning("Failed to get related queries for %s: %s", kw, e)

        return results

    except Exception as e:
        logger.error("Google Trends fetch failed: %s", e)
        return {
            "category": category,
            "keywords_analyzed": keywords[:5],
            "keyword_scores": {},
            "rising_queries": {},
            "related_topics": {},
            "error": str(e),
        }


def get_coffee_trends() -> dict[str, Any]:
    return fetch_trending_data(COFFEE_KEYWORDS, "coffee")


def get_general_cpg_trends() -> dict[str, Any]:
    return fetch_trending_data(GENERAL_CPG_KEYWORDS, "general_cpg")
