import os
import requests


def run_market_analysis(topic: str, google_api_key: str, serper_api_key: str) -> str:
    """
    Research a topic using Serper web search, then write a blog post
    using Google Gemini. No crewai dependency needed.
    """

    # --- Step 1: Search the web using Serper ---
    search_results = _search_web(topic, serper_api_key)

    # --- Step 2: Research agent prompt ---
    research_prompt = f"""You are an expert market researcher.
    
Based on these web search results about "{topic}":

{search_results}

Write a detailed research report covering:
- Latest trends and developments
- Key players and companies
- Emerging technologies
- Market impact and future outlook

Be specific, use the search results as your source."""

    research_report = _call_gemini(research_prompt, google_api_key)

    # --- Step 3: Writer agent prompt ---
    write_prompt = f"""You are a professional content writer.

Based on this research report:

{research_report}

Write an engaging 500-word blog post about "{topic}" that:
- Has a catchy title
- Is easy to understand for non-technical readers
- Highlights the most important trends
- Has a clear conclusion about future impact

Format it nicely with a title and paragraphs."""

    blog_post = _call_gemini(write_prompt, google_api_key)

    return blog_post


def _search_web(query: str, serper_api_key: str) -> str:
    """Search the web using Serper.dev API."""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": serper_api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": 10}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        results = []
        for item in data.get("organic", [])[:8]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"- {title}: {snippet} ({link})")

        return "\n".join(results) if results else "No search results found."

    except Exception as e:
        return f"Search failed: {str(e)}"


def _call_gemini(prompt: str, api_key: str) -> str:
    """Call Google Gemini API directly."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        data = response.json()

        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in data:
            return f"Gemini API error: {data['error']['message']}"
        else:
            return "No response from Gemini."

    except Exception as e:
        return f"Gemini call failed: {str(e)}"﻿
