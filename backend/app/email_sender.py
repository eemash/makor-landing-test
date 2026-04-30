"""Email sender for daily CPG idea summaries."""

from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

logger = logging.getLogger(__name__)

RECIPIENT = "eemash@gmail.com"


def _build_html(ideas: list[dict[str, Any]]) -> str:
    """Build an HTML email body from generated ideas."""
    today = datetime.utcnow().strftime("%B %d, %Y")

    coffee_ideas = [i for i in ideas if i.get("category") == "coffee"]
    general_ideas = [i for i in ideas if i.get("category") != "coffee"]

    cards_html = ""
    for idea in ideas:
        is_coffee = idea.get("category") == "coffee"
        badge_color = "#d97706" if is_coffee else "#7c3aed"
        badge_text = "☕ Coffee" if is_coffee else "✨ General CPG"
        border_color = "#d97706" if is_coffee else "#7c3aed"
        keywords = idea.get("trend_keywords", [])
        kw_tags = "".join(
            f'<span style="display:inline-block;background:#27272a;color:#a1a1aa;'
            f'padding:2px 8px;border-radius:12px;font-size:12px;margin:2px 4px 2px 0;">'
            f"{kw}</span>"
            for kw in keywords
        )

        reasoning_paragraphs = idea.get("reasoning", "").replace("\n\n", "</p><p style='margin:8px 0;color:#d4d4d8;'>")

        cards_html += f"""
        <div style="background:#18181b;border-left:4px solid {border_color};border-radius:8px;padding:20px;margin:16px 0;">
            <span style="display:inline-block;background:{badge_color};color:white;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">{badge_text}</span>
            <h2 style="color:#f4f4f5;margin:12px 0 4px;font-size:22px;">{idea.get('brand_name', '')}</h2>
            <p style="color:#a1a1aa;font-style:italic;margin:4px 0 12px;">"{idea.get('tagline', '')}"</p>
            <p style="color:#d4d4d8;margin:4px 0;"><strong style="color:#a1a1aa;">Product:</strong> {idea.get('product_type', '')}</p>
            <p style="color:#d4d4d8;margin:4px 0;"><strong style="color:#a1a1aa;">Target:</strong> {idea.get('target_audience', '')}</p>
            <hr style="border:none;border-top:1px solid #27272a;margin:12px 0;">
            <p style="color:#a1a1aa;font-size:13px;font-weight:600;margin-bottom:8px;">Reasoning & Analysis</p>
            <p style="margin:8px 0;color:#d4d4d8;">{reasoning_paragraphs}</p>
            <hr style="border:none;border-top:1px solid #27272a;margin:12px 0;">
            <p style="color:#71717a;font-size:12px;margin-bottom:4px;">Trend Keywords</p>
            <div>{kw_tags}</div>
        </div>
        """

    html = f"""
    <html>
    <body style="background:#09090b;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:20px;margin:0;">
        <div style="max-width:640px;margin:0 auto;">
            <h1 style="color:#f97316;text-align:center;margin-bottom:4px;">CPG Idea Generator</h1>
            <p style="color:#71717a;text-align:center;margin-top:0;">Daily Ideas — {today}</p>
            <p style="color:#a1a1aa;text-align:center;font-size:14px;">{len(coffee_ideas)} coffee idea{'' if len(coffee_ideas) == 1 else 's'} + {len(general_ideas)} general CPG idea{'' if len(general_ideas) == 1 else 's'}</p>
            {cards_html}
            <p style="color:#52525b;text-align:center;font-size:12px;margin-top:24px;">Powered by Google Trends + AI</p>
        </div>
    </body>
    </html>
    """
    return html


def _build_plain_text(ideas: list[dict[str, Any]]) -> str:
    """Build a plain text fallback."""
    today = datetime.utcnow().strftime("%B %d, %Y")
    lines = [f"CPG Idea Generator — Daily Ideas ({today})", "=" * 50, ""]
    for idea in ideas:
        cat = "Coffee" if idea.get("category") == "coffee" else "General CPG"
        lines.append(f"[{cat}] {idea.get('brand_name', '')}")
        lines.append(f'  "{idea.get("tagline", "")}"')
        lines.append(f"  Product: {idea.get('product_type', '')}")
        lines.append(f"  Target: {idea.get('target_audience', '')}")
        lines.append(f"  Keywords: {', '.join(idea.get('trend_keywords', []))}")
        lines.append("")
        lines.append(f"  Reasoning: {idea.get('reasoning', '')}")
        lines.append("")
        lines.append("-" * 50)
        lines.append("")
    return "\n".join(lines)


def send_daily_email(ideas: list[dict[str, Any]]) -> bool:
    """Send the daily idea summary email.

    Requires environment variables:
      SMTP_HOST (default: smtp.gmail.com)
      SMTP_PORT (default: 587)
      SMTP_USER — sender email address
      SMTP_PASS — app password or SMTP password
    """
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")

    if not smtp_user or not smtp_pass:
        logger.warning(
            "SMTP_USER and SMTP_PASS not set — skipping email. "
            "Set these env vars to enable daily email delivery."
        )
        return False

    today = datetime.utcnow().strftime("%b %d, %Y")
    coffee_count = sum(1 for i in ideas if i.get("category") == "coffee")
    general_count = len(ideas) - coffee_count

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"CPG Ideas for {today} — {coffee_count} coffee + {general_count} general"
    msg["From"] = smtp_user
    msg["To"] = RECIPIENT

    msg.attach(MIMEText(_build_plain_text(ideas), "plain"))
    msg.attach(MIMEText(_build_html(ideas), "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, RECIPIENT, msg.as_string())
        logger.info("Daily email sent to %s", RECIPIENT)
        return True
    except Exception as e:
        logger.error("Failed to send email: %s", e)
        return False
