import os
import requests


def run_market_analysis(topic, google_api_key, serper_api_key):
    search_results = _search_web(topic, serper_api_key)

    research_prompt = (
        "You are an expert market researcher.\n\n"
        "Based on these web search results about " + topic + ":\n\n"
        + search_results +
        "\n\nWrite a detailed research report covering:\n"
        "- Latest trends and developments\n"
        "- Key players and companies\n"
        "- Emerging technologies\n"
        "- Market impact and future outlook\n\n"
        "Be specific and use the search results as your source."
    )

    research_report = _call_gemini(research_prompt, google_api_key)

    write_prompt = (
        "You are a professional content writer.\n\n"
        "Based on this research report:\n\n"
        + research_report +
        "\n\nWrite an engaging 500-word blog post about " + topic + " that:\n"
        "- Has a catchy title\n"
        "- Is easy to understand for non-technical readers\n"
        "- Highlights the most important trends\n"
        "- Has a clear conclusion about future impact\n\n"
        "Format it with a title and clear paragraphs."
    )

    blog_post = _call_gemini(write_prompt, google_api_key)
    return blog_post


def _search_web(query, serper_api_key):
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
            results.append("- " + title + ": " + snippet + " (" + link + ")")
        return "\n".join(results) if results else "No search results found."
    except Exception as e:
        return "Search failed: " + str(e)


def _call_gemini(prompt, api_key):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.0-flash:generateContent?key=" + api_key
    )
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
            return "Gemini API error: " + data["error"]["message"]
        else:
            return "No response from Gemini."
    except Exception as e:
        return "Gemini call failed: " + str(e)

