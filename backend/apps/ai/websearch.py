"""Web search for the AI coaches.

Lets the coaches answer questions that need current/factual information
(prices, news, versions, salaries…) with real sources instead of
guessing from stale training data.

No API key required: DuckDuckGo Instant Answer API first, falling back to
the Wikipedia REST/opensearch API. Every call is short-timed and never
raises — if the network fails, the chat just continues without search.
"""
import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

_RESULT_LIMIT = 5
_MAX_DESCRIPTION = 260
_TIMEOUT = 4


def _clean(text):
    return " ".join((text or "").split())[:_MAX_DESCRIPTION]


def _get_json(url):
    request = urllib.request.Request(url, method="GET")
    request.add_header("User-Agent", "OrbitePlatform/1.0 (Django backend)")
    with urllib.request.urlopen(request, timeout=_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _tavily(query, limit):
    """Tavily — moteur de recherche optimisé IA. Actif seulement si ORBITE_TAVILY_API_KEY est défini."""
    api_key = getattr(settings, "ORBITE_TAVILY_API_KEY", "")
    if not api_key:
        raise RuntimeError("Tavily non configuré")
    payload = json.dumps(
        {"api_key": api_key, "query": query, "search_depth": "basic", "max_results": limit}
    ).encode("utf-8")
    request = urllib.request.Request("https://api.tavily.com/search", data=payload, method="POST")
    request.add_header("Content-Type", "application/json")
    data = _get_json_request(request)
    results = []
    for item in data.get("results") or []:
        results.append(
            {
                "titre": _clean(item.get("title")),
                "url": item.get("url", ""),
                "description": _clean(item.get("content")),
            }
        )
        if len(results) >= limit:
            break
    return results


def _get_json_request(request):
    with urllib.request.urlopen(request, timeout=_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url):
    return _get_json_request(urllib.request.Request(url, method="GET"))


def _duckduckgo(query, limit):
    """Instant Answer API — le dernier recours (peut être bloqué / sans réponse)."""
    url = (
        "https://api.duckduckgo.com/"
        + urllib.parse.urlencode({"q": query, "format": "json", "no_html": 1, "skip_disambig": 1})
    )
    request = urllib.request.Request(url, method="GET")
    request.add_header("User-Agent", "OrbitePlatform/1.0 (Django backend)")
    data = _get_json_request(request)
    results = []

    abstract = _clean(data.get("Abstract") or data.get("Answer"))
    abstract_url = data.get("AbstractURL")
    if abstract and abstract_url:
        results.append({"titre": "Résumé", "url": abstract_url, "description": abstract})

    def push(topic):
        text = _clean(topic.get("Text"))
        first_url = topic.get("FirstURL")
        if text and first_url and text != abstract:
            titre = text.split(" - ", 1)[0] if " - " in text else first_url.rsplit("/", 1)[-1].replace("_", " ")
            results.append({"titre": titre[:120], "url": first_url, "description": text})

    for topic in data.get("RelatedTopics") or []:
        if "Text" in topic:
            push(topic)
        for sub in topic.get("Topics") or []:
            push(sub)
        if len(results) >= limit:
            break
    return results[:limit]


def _wikipedia(query, limit):
    """Fallback fiable sans clé : recherche plein-texte MediaWiki + résumés."""
    import html as html_module
    import re

    url = (
        "https://fr.wikipedia.org/w/api.php"
        + "?"
        + urllib.parse.urlencode(
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": min(limit, 5),
                "format": "json",
            }
        )
    )
    request = urllib.request.Request(url, method="GET")
    request.add_header("User-Agent", "OrbitePlatform/1.0 (Django backend)")
    data = _get_json_request(request)
    hits = (data.get("query") or {}).get("search") or []

    results = []
    for item in hits[:limit]:
        title = item.get("title", "")
        page_url = "https://fr.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        description = re.sub(r"<[^>]+>", "", item.get("snippet") or "")
        description = html_module.unescape(description) or ""
        try:
            summary = _get_json(
                "https://fr.wikipedia.org/api/rest_v1/page/summary/"
                + urllib.parse.quote(title.replace(" ", "_"))
            )
            description = _clean(summary.get("extract")) or _clean(description)
        except Exception:  # noqa: BLE001 - missing summary is not fatal
            description = _clean(description)
        results.append({"titre": title[:120], "url": page_url, "description": description})
        if len(results) >= limit:
            break
    return results


def search_web(query, limit=_RESULT_LIMIT):
    """Run a web search. Returns a list of {"titre","url","description"}.

    Fails silently (empty list) so the chat is never blocked by the network.
    """
    if not query or not query.strip():
        return []
    backends = []
    if getattr(settings, "ORBITE_TAVILY_API_KEY", ""):
        backends.append(_tavily)
    backends += [_wikipedia, _duckduckgo]
    for backend in backends:
        try:
            results = backend(query.strip(), limit)
        except Exception:  # noqa: BLE001
            logger.info("web search backend failed (fallback then forward): %s", backend.__name__)
            results = []
        if results:
            return results
    return []