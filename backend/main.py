"""
Delhi Police Assistant — FastAPI Backend (v1)
Keyword-based matcher over the full service catalog.
Drop-in contract: POST /query → {answer, services[]}
Frontend never changes; swap this file for RAG in v2+.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, re
from pathlib import Path

app = FastAPI(title="Delhi Police Assistant API", version="1.0.0")

# Allow Chrome extension to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load catalog once at startup
# ---------------------------------------------------------------------------
CATALOG_PATH = Path(__file__).parent / "services.json"
with open(CATALOG_PATH, encoding="utf-8") as f:
    ALL_SERVICES = json.load(f)["services"]

# ---------------------------------------------------------------------------
# Hindi keyword map → English intent words
# Keeps the frontend language toggle working without a translation API.
# ---------------------------------------------------------------------------
HINDI_MAP = {
    "खोया": "lost",
    "चोरी": "stolen theft",
    "वाहन": "vehicle",
    "मोबाइल": "mobile phone",
    "एफआईआर": "fir",
    "शिकायत": "complaint",
    "प्रमाण": "certificate",
    "पुलिस": "police",
    "गुमशुदा": "missing",
    "रिपोर्ट": "report",
    "सत्यापन": "verification",
    "किरायेदार": "tenant",
    "लाइसेंस": "license",
    "अनुमति": "permission",
    "वरिष्ठ": "senior citizen",
    "नागरिक": "citizen",
    "फॉर्म": "form",
    "आरटीआई": "rti",
    "पीसीसी": "pcc",
    "सीवीआर": "cvr",
    "एनओसी": "noc",
}

# ---------------------------------------------------------------------------
# Priority pinning: high-frequency services surfaced first regardless of score
# ---------------------------------------------------------------------------
PRIORITY_IDS = [
    "lost_report",
    "mv_theft_e_fir",
    "theft_e_fir",
    "police_clearance_certificate",
    "character_verification_report",
]

# ---------------------------------------------------------------------------
# Request / Response models (the fixed frontend contract)
# ---------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str
    language: str = "en"   # "en" | "hi"

class ServiceResult(BaseModel):
    name: str
    url: str
    requires_login: bool
    description: str

class QueryResponse(BaseModel):
    answer: str
    services: list[ServiceResult]   # top matches (up to 5)
    all_count: int                  # total matches found


# ---------------------------------------------------------------------------
# Synonyms & Abbreviations Map for Robust Search
# ---------------------------------------------------------------------------
SYNONYMS = {
    "rti": ["r t i", "right to information"],
    "pcc": ["police clearance certificate", "clearance"],
    "cvr": ["character verification report", "character"],
    "fir": ["first information report"],
    "noc": ["no objection certificate"],
    "mact": ["acci claim", "accident claim"],
    "eow": ["economic offences wing"],
    "fsl": ["forensic science laboratory"],
    "mv": ["motor vehicle"],
}

# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------
def translate_hindi(text: str) -> str:
    for hindi, english in HINDI_MAP.items():
        text = text.replace(hindi, english)
    return text


def normalize(text: str) -> str:
    """Remove spaces and special characters for raw comparison."""
    return re.sub(r'[^a-z0-9]', '', text.lower())


def score_service(service: dict, tokens: list[str], query_clean: str) -> int:
    """Return a robust relevance score for a service given query tokens."""
    score = 0
    name_clean = normalize(service["name"])
    url_clean = normalize(service["url"])
    desc_clean = normalize(service["description"])

    for token in tokens:
        token_clean = normalize(token)
        if not token_clean:
            continue

        # 1. Match in normalized name
        if token_clean == name_clean:
            score += 15  # Exact match (e.g. token "rti" == service "rti")
        elif token_clean in name_clean:
            score += 8   # Substring match (e.g. token "license" in "noclicense")

        # 2. Match in URL (strong indicator for direct landing pages)
        if token_clean in url_clean and len(token_clean) > 2:
            score += 6

        # 3. Match in keywords
        for kw in service["keywords"]:
            kw_clean = normalize(kw)
            if token_clean == kw_clean:
                score += 4
            elif token_clean in kw_clean and len(token_clean) > 3:
                score += 2

        # 4. Match in description
        if token_clean in desc_clean and len(token_clean) > 3:
            score += 2

    # 5. Whole query sub-string matches
    query_norm = normalize(query_clean)
    if name_clean in query_norm or query_norm in name_clean:
        score += 5

    return score


def find_services(query: str, language: str, top_n: int = 5) -> list[dict]:
    q = query.lower().strip()

    # Translate Hindi words to English intent words
    if language == "hi" or any(c > "\u0900" for c in q):
        q = translate_hindi(q)

    # Tokenise: split on whitespace + strip punctuation
    tokens = [re.sub(r"[^\w]", "", t) for t in q.split()]
    tokens = [t for t in tokens if len(t) > 1]

    # Expand synonyms/abbreviations to boost match coverage
    expanded_tokens = list(tokens)
    for t in tokens:
        if t in SYNONYMS:
            for syn in SYNONYMS[t]:
                expanded_tokens.extend([re.sub(r"[^\w]", "", w) for w in syn.split() if len(w) > 1])
    tokens = list(set(expanded_tokens))

    if not tokens:
        # No real query — return the 5 priority services
        return [s for s in ALL_SERVICES if s["id"] in PRIORITY_IDS]

    scored = [(score_service(s, tokens, q), s) for s in ALL_SERVICES]
    scored = [(sc, s) for sc, s in scored if sc > 0]

    # Boost priority services by +1 so ties break in their favour
    scored = [(sc + (1 if s["id"] in PRIORITY_IDS else 0), s) for sc, s in scored]
    scored.sort(key=lambda x: -x[0])

    return [s for _, s in scored[:top_n]], len(scored)


def build_answer(query: str, matches: list, language: str) -> str:
    if not matches:
        if language == "hi":
            return "माफ़ करें, आपकी क्वेरी से मेल खाने वाली कोई सेवा नहीं मिली। कृपया अलग शब्दों में पूछें।"
        return "Sorry, no matching service found. Please try different keywords."

    if language == "hi":
        if len(matches) == 1:
            return f"आपकी क्वेरी के आधार पर, हमें यह सेवा मिली: {matches[0]['name']}। नीचे दिए लिंक पर क्लिक करें।"
        return f"आपकी क्वेरी के आधार पर, हमें {len(matches)} सेवाएँ मिलीं। सबसे उपयुक्त सेवा चुनें:"
    else:
        if len(matches) == 1:
            return f"Based on your query, the most relevant service is {matches[0]['name']}. Click the link below to proceed."
        return f"Found {len(matches)} relevant services. The best match is {matches[0]['name']} — or browse the others below."


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "services_loaded": len(ALL_SERVICES)}


@app.get("/services")
def list_all_services():
    """Return the full catalog — useful for the 'Browse all' button."""
    return {"services": ALL_SERVICES, "total": len(ALL_SERVICES)}


@app.post("/query", response_model=QueryResponse)
def handle_query(req: QueryRequest):
    result = find_services(req.query, req.language, top_n=5)

    # find_services returns (list, count) when query is non-empty
    if isinstance(result, tuple):
        matches, total = result
    else:
        matches, total = result, len(result)

    return QueryResponse(
        answer=build_answer(req.query, matches, req.language),
        services=[
            ServiceResult(
                name=m["name"],
                url=m["url"],
                requires_login=m["requires_login"],
                description=m["description"],
            )
            for m in matches
        ],
        all_count=total,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)