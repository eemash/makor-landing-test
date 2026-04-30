"""CPG brand idea generator using OpenAI + Google Trends data."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any

import random

from openai import OpenAI

from app.database import save_idea
from app.trends import (
    COFFEE_KEYWORDS,
    GENERAL_CPG_KEYWORDS,
    get_coffee_trends,
    get_general_cpg_trends,
)

logger = logging.getLogger(__name__)


def _get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("chatgpt")
    if not api_key:
        raise RuntimeError("No OpenAI API key found. Set OPENAI_API_KEY or chatgpt env var.")
    return OpenAI(api_key=api_key)


SYSTEM_PROMPT = """You are a CPG (Consumer Packaged Goods) brand strategist and startup advisor.
You analyze Google Trends data to identify emerging opportunities for new CPG brands.

When given trend data, you create a compelling brand concept with:
1. A creative, memorable brand name
2. A catchy tagline
3. The specific product type
4. Target audience
5. Detailed reasoning (3-5 paragraphs) explaining:
   - What trends support this idea
   - Why NOW is the right time
   - Who the target customer is and their pain points
   - How this brand differentiates from existing options
   - Potential go-to-market strategy

Respond ONLY with valid JSON in this exact format:
{
  "brand_name": "...",
  "tagline": "...",
  "product_type": "...",
  "target_audience": "...",
  "reasoning": "..."
}"""


def _build_prompt(trends_data: dict[str, Any], category: str) -> str:
    category_label = "coffee-related" if category == "coffee" else "general CPG"

    prompt = f"""Based on the following Google Trends data, generate a {category_label} CPG brand idea.

**Category focus**: {category_label}
**Trends data**:
- Keywords analyzed: {', '.join(trends_data.get('keywords_analyzed', []))}
"""
    scores = trends_data.get("keyword_scores", {})
    if scores:
        prompt += "\n**Keyword interest scores (0-100 scale)**:\n"
        for kw, data in scores.items():
            prompt += f"- '{kw}': current={data['current']}, avg={data['avg']}, trend={data['trend']}\n"

    rising = trends_data.get("rising_queries", {})
    if rising:
        prompt += "\n**Rising related queries**:\n"
        for kw, queries in rising.items():
            prompt += f"- For '{kw}': {', '.join(queries)}\n"

    related = trends_data.get("related_topics", {})
    if related:
        prompt += "\n**Top related topics**:\n"
        for kw, topics in related.items():
            prompt += f"- For '{kw}': {', '.join(topics)}\n"

    if category == "coffee":
        prompt += "\nThe brand MUST be coffee-related (coffee product, coffee accessory, coffee experience, etc.)"
    else:
        prompt += "\nChoose the most promising CPG category based on the trend data. Be creative — this could be food, beverage, personal care, supplements, or any consumer product."

    prompt += "\n\nGenerate a unique, market-ready brand concept. Be specific and actionable."

    return prompt


def _call_openai(trends_data: dict[str, Any], category: str) -> dict[str, Any]:
    """Call OpenAI to generate a brand concept. Returns parsed JSON or raises."""
    client = _get_client()
    user_prompt = _build_prompt(trends_data, category)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.9,
        max_tokens=1500,
    )

    raw = (response.choices[0].message.content or "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    return json.loads(raw)


def _fallback_idea(trends_data: dict[str, Any], category: str) -> dict[str, str]:
    """Generate a simple template-based idea when OpenAI is unavailable."""
    keywords = trends_data.get("keywords_analyzed", [])
    if not keywords:
        keywords = random.sample(
            COFFEE_KEYWORDS if category == "coffee" else GENERAL_CPG_KEYWORDS, 3
        )

    focus = random.choice(keywords)
    scores = trends_data.get("keyword_scores", {})
    score_info = scores.get(focus, {})
    trend_dir = score_info.get("trend", "rising")

    if category == "coffee":
        names = ["BrewShift", "MorningPulse", "Roast & Rise", "CafeCraft", "BeanForward"]
        products = ["cold brew concentrate", "mushroom-infused coffee blend", "protein coffee mix",
                     "adaptogen espresso pods", "nitro coffee cans"]
    else:
        names = ["NourishCo", "VitalPeak", "PurePath", "GreenShift", "CoreFuel"]
        products = ["functional snack bar", "probiotic sparkling drink", "plant-based protein crisp",
                     "adaptogen gummy supplement", "electrolyte hydration mix"]

    name = random.choice(names)
    product = random.choice(products)

    reasoning = (
        f"Based on trending interest in '{focus}' (trend: {trend_dir}), there's a clear "
        f"market opportunity in the {category.replace('_', ' ')} space. Consumers are increasingly "
        f"searching for products related to {', '.join(keywords[:3])}, indicating unmet demand.\n\n"
        f"The target demographic — health-conscious millennials and Gen Z — are actively seeking "
        f"premium, functional alternatives to traditional products. A brand positioning around "
        f"'{focus}' can capture this growing segment.\n\n"
        f"Note: This idea was generated with template-based analysis because the AI service was "
        f"temporarily unavailable. Re-generate for a full AI-powered analysis."
    )

    return {
        "brand_name": name,
        "tagline": f"Fuel your day with {focus}",
        "product_type": product,
        "target_audience": "Health-conscious millennials and Gen Z (ages 22-38)",
        "reasoning": reasoning,
    }


def generate_idea(category: str) -> dict[str, Any]:
    """Generate a single CPG brand idea for the given category."""
    logger.info("Generating %s idea...", category)

    if category == "coffee":
        trends_data = get_coffee_trends()
    else:
        trends_data = get_general_cpg_trends()

    try:
        parsed = _call_openai(trends_data, category)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse OpenAI response: %s", e)
        parsed = _fallback_idea(trends_data, category)
    except Exception as e:
        logger.error("OpenAI call failed: %s", e)
        parsed = _fallback_idea(trends_data, category)

    idea = {
        "created_at": datetime.utcnow().isoformat(),
        "category": category,
        "brand_name": parsed.get("brand_name", ""),
        "tagline": parsed.get("tagline", ""),
        "product_type": parsed.get("product_type", ""),
        "target_audience": parsed.get("target_audience", ""),
        "reasoning": parsed.get("reasoning", ""),
        "trends_data": trends_data,
        "trend_keywords": trends_data.get("keywords_analyzed", []),
    }

    idea_id = save_idea(idea)
    idea["id"] = idea_id
    logger.info("Saved %s idea #%d: %s", category, idea_id, idea["brand_name"])

    return idea


def generate_daily_pair() -> list[dict[str, Any]]:
    """Generate today's pair of ideas: 1 coffee + 1 general CPG."""
    coffee_idea = generate_idea("coffee")
    general_idea = generate_idea("general_cpg")
    return [coffee_idea, general_idea]
