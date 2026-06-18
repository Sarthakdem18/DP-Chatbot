# """
# Delhi Police Assistant — FastAPI Backend (v1)
# Keyword-based matcher over the full service catalog.
# Drop-in contract: POST /query → {answer, services[]}
# Frontend never changes; swap this file for RAG in v2+.
# """

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import json, re
# from pathlib import Path
# import torch
# from transformers import AutoTokenizer, AutoModel
# import torch.nn.functional as F

# app = FastAPI(title="Delhi Police Assistant API", version="1.0.0")

# # Allow Chrome extension to call this
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["POST", "GET"],
#     allow_headers=["*"],
# )

# # ---------------------------------------------------------------------------
# # Load catalog once at startup
# # ---------------------------------------------------------------------------
# CATALOG_PATH = Path(__file__).parent / "services.json"
# with open(CATALOG_PATH, encoding="utf-8") as f:
#     ALL_SERVICES = json.load(f)["services"]

# # ---------------------------------------------------------------------------
# # Load IndicBERTv2 model for multilingual semantic search
# # ---------------------------------------------------------------------------
# MODEL_DIR = Path(__file__).parent / "model"
# print(f"Loading local IndicBERTv2 model from {MODEL_DIR}...")
# tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
# model = AutoModel.from_pretrained(str(MODEL_DIR))
# model.eval()
# print("Model loaded successfully!")

# def mean_pooling(model_output, attention_mask):
#     token_embeddings = model_output[0]
#     input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
#     return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# def get_embedding(texts: list[str]):
#     encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
#     with torch.no_grad():
#         model_output = model(**encoded_input)
#     embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
#     return F.normalize(embeddings, p=2, dim=1)

# # Pre-compute service embeddings
# print("Pre-computing service embeddings...")
# service_texts = []
# for s in ALL_SERVICES:
#     desc = s.get("description", "")
#     kws = ", ".join(s.get("keywords", []))
#     text = f"Service: {s['name']}. Description: {desc}. Keywords: {kws}."
#     service_texts.append(text)

# SERVICE_EMBEDDINGS = get_embedding(service_texts)
# print(f"Pre-computed {len(ALL_SERVICES)} service embeddings.")

# # ---------------------------------------------------------------------------
# # Hindi keyword map → English intent words
# # Keeps the frontend language toggle working without a translation API.
# # ---------------------------------------------------------------------------
# HINDI_MAP = {
#     "खोया": "lost",
#     "चोरी": "stolen theft",
#     "वाहन": "vehicle",
#     "मोबाइल": "mobile phone",
#     "एफआईआर": "fir",
#     "शिकायत": "complaint",
#     "प्रमाण": "certificate",
#     "पुलिस": "police",
#     "गुमशुदा": "missing",
#     "रिपोर्ट": "report",
#     "सत्यापन": "verification",
#     "किरायेदार": "tenant",
#     "लाइसेंस": "license",
#     "अनुमति": "permission",
#     "वरिष्ठ": "senior citizen",
#     "नागरिक": "citizen",
#     "फॉर्म": "form",
#     "आरटीआई": "rti",
#     "पीसीसी": "pcc",
#     "सीवीआर": "cvr",
#     "एनओसी": "noc",
# }

# # ---------------------------------------------------------------------------
# # Priority pinning: high-frequency services surfaced first regardless of score
# # ---------------------------------------------------------------------------
# PRIORITY_IDS = [
#     "lost_report",
#     "mv_theft_e_fir",
#     "theft_e_fir",
#     "police_clearance_certificate",
#     "character_verification_report",
# ]

# # ---------------------------------------------------------------------------
# # Request / Response models (the fixed frontend contract)
# # ---------------------------------------------------------------------------
# class QueryRequest(BaseModel):
#     query: str
#     language: str = "en"   # "en" | "hi"

# class ServiceResult(BaseModel):
#     name: str
#     url: str
#     requires_login: bool
#     description: str

# class QueryResponse(BaseModel):
#     answer: str
#     services: list[ServiceResult]   # top matches (up to 5)
#     all_count: int                  # total matches found


# # ---------------------------------------------------------------------------
# # Synonyms & Abbreviations Map for Robust Search
# # ---------------------------------------------------------------------------
# SYNONYMS = {
#     "rti": ["r t i", "right to information"],
#     "pcc": ["police clearance certificate", "clearance"],
#     "cvr": ["character verification report", "character"],
#     "fir": ["first information report"],
#     "noc": ["no objection certificate"],
#     "mact": ["acci claim", "accident claim"],
#     "eow": ["economic offences wing"],
#     "fsl": ["forensic science laboratory"],
#     "mv": ["motor vehicle"],
# }

# # ---------------------------------------------------------------------------
# # Matching logic
# # ---------------------------------------------------------------------------
# def translate_hindi(text: str) -> str:
#     for hindi, english in HINDI_MAP.items():
#         text = text.replace(hindi, english)
#     return text


# def normalize(text: str) -> str:
#     """Remove spaces and special characters for raw comparison."""
#     return re.sub(r'[^a-z0-9]', '', text.lower())


# def score_service(service: dict, tokens: list[str], query_clean: str) -> int:
#     """Return a robust relevance score for a service given query tokens."""
#     score = 0
#     name_clean = normalize(service["name"])
#     url_clean = normalize(service["url"])
#     desc_clean = normalize(service["description"])

#     for token in tokens:
#         token_clean = normalize(token)
#         if not token_clean:
#             continue

#         # 1. Match in normalized name
#         if token_clean == name_clean:
#             score += 15  # Exact match (e.g. token "rti" == service "rti")
#         elif token_clean in name_clean:
#             score += 8   # Substring match (e.g. token "license" in "noclicense")

#         # 2. Match in URL (strong indicator for direct landing pages)
#         if token_clean in url_clean and len(token_clean) > 2:
#             score += 6

#         # 3. Match in keywords
#         for kw in service["keywords"]:
#             kw_clean = normalize(kw)
#             if token_clean == kw_clean:
#                 score += 4
#             elif token_clean in kw_clean and len(token_clean) > 3:
#                 score += 2

#         # 4. Match in description
#         if token_clean in desc_clean and len(token_clean) > 3:
#             score += 2

#     # 5. Whole query sub-string matches
#     query_norm = normalize(query_clean)
#     if name_clean in query_norm or query_norm in name_clean:
#         score += 5

#     return score


# def find_services(query: str, language: str, top_n: int = 5) -> list[dict]:
#     q = query.lower().strip()

#     # Tokenise to check if query is empty
#     tokens = [re.sub(r"[^\w]", "", t) for t in q.split()]
#     tokens = [t for t in tokens if len(t) > 1]

#     if not tokens:
#         # No real query — return the 5 priority services
#         return [s for s in ALL_SERVICES if s["id"] in PRIORITY_IDS], len(PRIORITY_IDS)

#     # Translate Hindi words to English intent words for keyword scoring
#     q_translated = q
#     if language == "hi" or any(c > "\u0900" for c in q):
#         q_translated = translate_hindi(q)

#     keyword_tokens = [re.sub(r"[^\w]", "", t) for t in q_translated.split()]
#     keyword_tokens = [t for t in keyword_tokens if len(t) > 1]

#     # Expand synonyms/abbreviations to boost keyword matches
#     expanded_tokens = list(keyword_tokens)
#     for t in keyword_tokens:
#         if t in SYNONYMS:
#             for syn in SYNONYMS[t]:
#                 expanded_tokens.extend([re.sub(r"[^\w]", "", w) for w in syn.split() if len(w) > 1])
#     keyword_tokens = list(set(expanded_tokens))

#     # 1. Compute semantic similarity using IndicBERTv2
#     # We pass the original query (not translated) to IndicBERTv2 since it's multilingual
#     query_emb = get_embedding([query])
#     similarities = torch.mm(query_emb, SERVICE_EMBEDDINGS.transpose(0, 1)).squeeze(0).tolist()

#     scored = []
#     for i, s in enumerate(ALL_SERVICES):
#         sem_score = similarities[i]
#         kw_score = score_service(s, keyword_tokens, q_translated)

#         # Combine scores
#         combined = sem_score * 12.0 + kw_score

#         # Boost priority services by +1 so ties break in their favour
#         if s["id"] in PRIORITY_IDS:
#             combined += 1.0

#         scored.append((combined, s))

#     scored.sort(key=lambda x: -x[0])

#     return [s for _, s in scored[:top_n]], len(scored)


# def build_answer(query: str, matches: list, language: str) -> str:
#     if not matches:
#         if language == "hi":
#             return "माफ़ करें, आपकी क्वेरी से मेल खाने वाली कोई सेवा नहीं मिली। कृपया अलग शब्दों में पूछें।"
#         return "Sorry, no matching service found. Please try different keywords."

#     if language == "hi":
#         if len(matches) == 1:
#             return f"आपकी क्वेरी के आधार पर, हमें यह सेवा मिली: {matches[0]['name']}। नीचे दिए लिंक पर क्लिक करें।"
#         return f"आपकी क्वेरी के आधार पर, हमें {len(matches)} सेवाएँ मिलीं। सबसे उपयुक्त सेवा चुनें:"
#     else:
#         if len(matches) == 1:
#             return f"Based on your query, the most relevant service is {matches[0]['name']}. Click the link below to proceed."
#         return f"Found {len(matches)} relevant services. The best match is {matches[0]['name']} — or browse the others below."


# # ---------------------------------------------------------------------------
# # Endpoints
# # ---------------------------------------------------------------------------
# @app.get("/")
# def root():
#     return {"status": "ok", "services_loaded": len(ALL_SERVICES)}


# @app.get("/services")
# def list_all_services():
#     """Return the full catalog — useful for the 'Browse all' button."""
#     return {"services": ALL_SERVICES, "total": len(ALL_SERVICES)}


# @app.post("/query", response_model=QueryResponse)
# def handle_query(req: QueryRequest):
#     result = find_services(req.query, req.language, top_n=5)

#     # find_services returns (list, count) when query is non-empty
#     if isinstance(result, tuple):
#         matches, total = result
#     else:
#         matches, total = result, len(result)

#     return QueryResponse(
#         answer=build_answer(req.query, matches, req.language),
#         services=[
#             ServiceResult(
#                 name=m["name"],
#                 url=m["url"],
#                 requires_login=m["requires_login"],
#                 description=m["description"],
#             )
#             for m in matches
#         ],
#         all_count=total,
#     )


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

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
import torch
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F

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
# Explicit device management — uses GPU if available, else CPU
# ---------------------------------------------------------------------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

# ---------------------------------------------------------------------------
# Load IndicBERTv2 model for multilingual semantic search
# ---------------------------------------------------------------------------
MODEL_DIR = Path(__file__).parent / "model"
print(f"Loading local IndicBERTv2 model from {MODEL_DIR}...")
tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
model = AutoModel.from_pretrained(str(MODEL_DIR))
model.to(DEVICE)
model.eval()
print("Model loaded successfully!")


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def get_embedding(texts: list[str]):
    encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    encoded_input = {k: v.to(DEVICE) for k, v in encoded_input.items()}
    with torch.no_grad():
        model_output = model(**encoded_input)
    embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    return F.normalize(embeddings, p=2, dim=1)


# Pre-compute service embeddings
print("Pre-computing service embeddings...")
service_texts = []
for s in ALL_SERVICES:
    desc = s.get("description", "")
    kws = ", ".join(s.get("keywords", []))
    text = f"Service: {s['name']}. Description: {desc}. Keywords: {kws}."
    service_texts.append(text)

SERVICE_EMBEDDINGS = get_embedding(service_texts)
print(f"Pre-computed {len(ALL_SERVICES)} service embeddings.")

# ---------------------------------------------------------------------------
# Hindi keyword map → English intent words (Devanagari script)
# ---------------------------------------------------------------------------
HINDI_MAP = {
    "खोया": "lost missing",
    "खोई": "lost missing",
    "खो": "lost missing",
    "बच्चा": "child missing",
    "बच्ची": "child missing",
    "बच्चे": "child missing",
    "चोरी": "stolen theft",
    "वाहन": "vehicle",
    "मोबाइल": "mobile phone",
    "एफआईआर": "fir",
    "शिकायत": "complaint",
    "प्रमाण": "certificate",
    "पुलिस": "police",
    "गुमशुदा": "missing person",
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
    "औरत": "woman",
    "महिला": "woman",
    "लड़की": "girl missing",
    "आदमी": "person",
    "व्यक्ति": "person missing",
    "दुर्घटना": "accident",
    "मदद": "help",
}

# ---------------------------------------------------------------------------
# Hinglish map → English intent words (Roman script Hindi)
# Covers the most common Hinglish patterns people actually type
# ---------------------------------------------------------------------------
HINGLISH_MAP = {
    # --- Filler / grammatical words — strip these ---
    "mujhe":    "",
    "muje":     "",
    "mera":     "",
    "meri":     "",
    "mere":     "",
    "meraa":    "",
    "hamare":   "",
    "hamara":   "",
    "hamari":   "",
    "apna":     "",
    "apni":     "",
    "apne":     "",
    "hai":      "",
    "hei":      "",
    "he":       "",
    "hua":      "",
    "hui":      "",
    "huyi":     "",
    "hoon":     "",
    "hun":      "",
    "hu":       "",
    "gye":      "",
    "ko":       "",
    "se":       "",
    "ka":       "",
    "ki":       "",
    "ke":       "",
    "ne":       "",
    "aur":      "",
    "ya":       "",
    "jo":       "",
    "woh":      "",
    "yeh":      "",
    "ek":       "",
    "koi":      "",
    "kuch":     "",
    "nahi":     "",
    "nhi":      "",
    "bhi":      "",
    "toh":      "",
    "to":       "",
    "abhi":     "",
    "jaldi":    "",
    "wala":     "",
    "wali":     "",
    "wale":     "",
    "please":   "",
    "sir":      "",
    "madam":    "",
    "karna":    "",
    "krna":     "",
    "karo":     "",
    "kru":      "",
    "kaise":    "",
    "chahiye":  "",
    "chahiye":  "",
    "kab":      "",
    "kahan":    "",
    "kyun":     "",
    "kya":      "",
    "par":      "",
    "pe":       "",
    "mein":     "",
    "mein":     "",
    "raha":     "",
    "rahi":     "",
    "nahi":     "",
    "nahin":    "",
    "hai":      "",
    "thi":      "",
    "tha":      "",

    # --- Lost / missing ---
    "khoya":    "lost missing",
    "khoyi":    "lost missing",
    "kho":      "lost missing",
    "gaya":     "lost missing",
    "gayi":     "lost missing",
    "gum":      "lost missing",
    "guma":     "lost missing",
    "gumsuda":  "missing person",
    "gumshuda": "missing person",
    "lapta":    "missing person",
    "missing":  "missing person",
    "dhundh":   "search missing",
    "dhundho":  "search missing",
    "milna":    "search find",

    # --- People ---
    "baccha":   "child missing",
    "bachcha":  "child missing",
    "bachi":    "child missing",
    "bachchi":  "child missing",
    "ladka":    "boy missing child",
    "ladki":    "girl missing child",
    "aurat":    "woman missing",
    "mahila":   "woman missing",
    "bhai":     "person missing",
    "behen":    "person missing",
    "papa":     "person missing elderly",
    "maa":      "person missing",
    "beta":     "child missing son",
    "beti":     "child missing daughter",
    "buzurg":   "senior citizen elderly",
    "dada":     "elderly senior citizen",
    "dadi":     "elderly senior citizen",
    "nana":     "elderly senior citizen",
    "nani":     "elderly senior citizen",

    # --- Theft / crime ---
    "chori":    "stolen theft",
    "churaya":  "stolen theft",
    "chheen":   "stolen snatched",
    "chheena":  "stolen snatched",
    "snatch":   "stolen snatched",
    "loot":     "robbery theft",
    "dakaiti":  "robbery",
    "thagi":    "fraud cheating",
    "dhoka":    "fraud cheating",
    "fraud":    "fraud financial",
    "pickpocket": "theft stolen",
    "jebkatra": "theft stolen pickpocket",
    "jeb":      "theft pickpocket",

    # --- Vehicles ---
    "gaadi":    "vehicle",
    "gadi":     "vehicle",
    "car":      "vehicle",
    "bike":     "vehicle",
    "scooter":  "vehicle",
    "auto":     "vehicle",
    "truck":    "vehicle",
    "tow":      "vehicle towed seized",
    "impound":  "vehicle seized",

    # --- Devices ---
    "mobile":   "mobile phone",
    "phone":    "mobile phone",
    "laptop":   "laptop",
    "imei":     "mobile phone imei",

    # --- Arms / weapons ---
    "gun":      "arms license weapon",
    "bandook":  "arms license gun weapon",
    "pistol":   "arms license weapon",
    "revolver": "arms license weapon",
    "rifle":    "arms license weapon",
    "silah":    "arms license weapon",
    "hathiyar": "arms license weapon",
    "shaster":  "arms license weapon",
    "parwana":  "arms license permit",

    # --- Accommodation / mess ---
    "mess":     "mess accommodation",
    "hall":     "mess accommodation hall",
    "room":     "accommodation",
    "stay":     "accommodation stay",
    "theherna": "accommodation stay",
    "rehna":    "accommodation stay",
    "book":     "booking",
    "booking":  "booking accommodation",
    "tariff":   "tariff accommodation",

    # --- Documents / services ---
    "fir":      "first information report",
    "report":   "report complaint",
    "darj":     "register complaint",
    "sikayat":  "complaint",
    "shikayat": "complaint",
    "complaint": "complaint",
    "license":  "license",
    "licence":  "license",
    "verify":   "verification",
    "noc":      "no objection certificate",
    "pcc":      "police clearance certificate",
    "cvr":      "character verification report",
    "rti":      "right to information",
    "certificate": "certificate",
    "praman":   "certificate",
    "passport": "passport",
    "pasport":  "passport",
    "kiraya":   "tenant",
    "kirayadar": "tenant",
    "naukrani": "domestic help maid",
    "bai":      "domestic help maid",
    "cook":     "domestic help cook",
    "driver":   "domestic help driver",
    "senior":   "senior citizen",
    "permission": "permission",
    "anumati":  "permission",
    "police":   "police",
    "help":     "help",
    "madad":    "help",
    "jaankari": "information",
    "jankari":  "information",
    "paise":    "money financial",
    "paisa":    "money financial",
    "register": "registration",
    "apply":    "apply",
    "form":     "form",
    "suchna":   "information rti",
    "adhikar":  "right information",
    "videsh":   "foreign overseas",
    "abroad":   "foreign overseas",
    "visa":     "visa foreign",
    "immigration": "immigration foreign",
    "rally":    "rally event procession",
    "dharna":   "protest event",
    "jaloos":   "procession event",
    "mela":     "event gathering",
    "sabha":    "gathering event",
    "accident": "accident road",
    "hadsa":    "accident road",
    "takkar":   "accident collision",
    "chot":     "injury accident",
    "compensation": "compensation claim",
    "claim":    "compensation claim",
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
# Request / Response models
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
    services: list[ServiceResult]
    all_count: int


# ---------------------------------------------------------------------------
# Synonyms & Abbreviations Map for Robust Search
# ---------------------------------------------------------------------------
SYNONYMS = {
    "rti":     ["right to information"],
    "pcc":     ["police clearance certificate", "clearance"],
    "cvr":     ["character verification report", "character verification"],
    "fir":     ["first information report"],
    "noc":     ["no objection certificate"],
    "mact":    ["accident claim"],
    "eow":     ["economic offences wing"],
    "fsl":     ["forensic science laboratory"],
    "mv":      ["motor vehicle"],
    "lost":    ["missing", "gum", "khoya"],
    "missing": ["lost", "gum", "gumsuda"],
    "child":   ["baccha", "ladka", "ladki", "minor", "kid"],
    "stolen":  ["theft", "chori", "churaya"],
}

SEM_WEIGHT    = 6.0   # semantic score multiplier
SEM_THRESHOLD = 0.30  # ignore cosine similarity below this

# ---------------------------------------------------------------------------
# Translation helpers
# ---------------------------------------------------------------------------
def translate_hindi(text: str) -> str:
    """Replace Devanagari words with English equivalents."""
    for hindi, english in HINDI_MAP.items():
        text = text.replace(hindi, english)
    return text


def translate_hinglish(text: str) -> str:
    """Replace Roman-script Hindi words with English equivalents token by token."""
    tokens = text.lower().split()
    translated = []
    for token in tokens:
        clean = re.sub(r"[^\w]", "", token)
        replacement = HINGLISH_MAP.get(clean)
        if replacement is None:
            translated.append(token)       # unknown word — keep as-is
        elif replacement == "":
            pass                            # filler word — drop it
        else:
            translated.append(replacement) # known Hinglish — replace
    return " ".join(translated)


def normalize(text: str) -> str:
    """Remove spaces and special characters for raw comparison."""
    return re.sub(r'[^a-z0-9]', '', text.lower())


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def score_service(service: dict, tokens: list[str], query_clean: str) -> int:
    score = 0
    name_clean = normalize(service["name"])
    url_clean  = normalize(service["url"])
    desc_clean = normalize(service["description"])

    for token in tokens:
        token_clean = normalize(token)
        if not token_clean:
            continue

        if token_clean == name_clean:
            score += 15
        elif token_clean in name_clean:
            score += 8

        if token_clean in url_clean and len(token_clean) > 2:
            score += 6

        for kw in service["keywords"]:
            kw_clean = normalize(kw)
            if token_clean == kw_clean:
                score += 4
            elif token_clean in kw_clean and len(token_clean) > 3:
                score += 2

        if token_clean in desc_clean and len(token_clean) > 3:
            score += 2

    query_norm = normalize(query_clean)
    if name_clean in query_norm or query_norm in name_clean:
        score += 5

    return score


# ---------------------------------------------------------------------------
# Main search
# ---------------------------------------------------------------------------
def find_services(query: str, language: str, top_n: int = 5) -> tuple[list[dict], int]:
    q = query.lower().strip()

    tokens = [re.sub(r"[^\w]", "", t) for t in q.split()]
    tokens = [t for t in tokens if len(t) > 1]

    if not tokens:
        priority = [s for s in ALL_SERVICES if s["id"] in PRIORITY_IDS]
        return priority, len(priority)

    # --- Translate to English intent words ---
    # Detect by script, not language toggle — user can type Hinglish (Roman)
    # even when Hindi mode is selected in the frontend.
    if any("\u0900" <= c <= "\u097F" for c in q):
        q_translated = translate_hindi(q)
    else:
        q_translated = translate_hinglish(q)

    keyword_tokens = [re.sub(r"[^\w]", "", t) for t in q_translated.split()]
    keyword_tokens = [t for t in keyword_tokens if len(t) > 1]

    # Expand synonyms
    expanded_tokens = list(keyword_tokens)
    for t in keyword_tokens:
        if t in SYNONYMS:
            for syn in SYNONYMS[t]:
                expanded_tokens.extend([re.sub(r"[^\w]", "", w) for w in syn.split() if len(w) > 1])
    keyword_tokens = list(set(expanded_tokens))

    # Semantic similarity
    try:
        query_emb   = get_embedding([query])
        similarities = torch.mm(query_emb, SERVICE_EMBEDDINGS.transpose(0, 1)).squeeze(0).tolist()
    except Exception as e:
        print(f"[WARNING] Embedding failed: {e}. Using keyword-only.")
        similarities = [0.0] * len(ALL_SERVICES)

    scored = []
    for i, s in enumerate(ALL_SERVICES):
        raw_sem  = similarities[i]
        sem_score = raw_sem if raw_sem >= SEM_THRESHOLD else 0.0
        kw_score  = score_service(s, keyword_tokens, q_translated)
        combined  = sem_score * SEM_WEIGHT + kw_score

        if s["id"] in PRIORITY_IDS:
            combined += 1.0

        scored.append((combined, s))

    scored.sort(key=lambda x: -x[0])
    relevant_count = sum(1 for sc, _ in scored if sc > 0)

    return [s for _, s in scored[:top_n]], relevant_count


# ---------------------------------------------------------------------------
# Answer builder
# ---------------------------------------------------------------------------
def build_answer(query: str, matches: list, language: str) -> str:
    if not matches:
        if language == "hi":
            return "माफ़ करें, आपकी क्वेरी से मेल खाने वाली कोई सेवा नहीं मिली। कृपया अलग शब्दों में पूछें।"
        return "Sorry, no matching service found. Please try different keywords."

    if language == "hi":
        if len(matches) == 1:
            return f"आपकी क्वेरी के आधार पर सबसे उपयुक्त सेवा है: \"{matches[0]['name']}\"। नीचे दिए गए लिंक पर क्लिक करके सीधे सेवा तक पहुँचें।"
        return f"आपकी क्वेरी से {len(matches)} सेवाएँ मिलीं। सबसे उपयुक्त सेवा है \"{matches[0]['name']}\" — या नीचे से अपनी ज़रूरत के अनुसार चुनें।"
    else:
        if len(matches) == 1:
            return f"Based on your query, the most relevant service is \"{matches[0]['name']}\". Click the link below to proceed."
        return f"Found {len(matches)} relevant services. The best match is \"{matches[0]['name']}\" — or browse the others below."


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "services_loaded": len(ALL_SERVICES)}


@app.get("/services")
def list_all_services():
    return {"services": ALL_SERVICES, "total": len(ALL_SERVICES)}


@app.post("/query", response_model=QueryResponse)
def handle_query(req: QueryRequest):
    matches, total = find_services(req.query, req.language, top_n=5)

    use_hi = req.language == "hi"
    return QueryResponse(
        answer=build_answer(req.query, matches, req.language),
        services=[
            ServiceResult(
                name=m["name"],
                url=m["url"],
                requires_login=m["requires_login"],
                description=m.get("description_hi", m["description"]) if use_hi else m["description"],
            )
            for m in matches
        ],
        all_count=total,
    )

@app.post("/debug")
def debug_query(req: QueryRequest):
    try:
        query_emb = get_embedding([req.query])
        similarities = torch.mm(query_emb, SERVICE_EMBEDDINGS.transpose(0, 1)).squeeze(0).tolist()
        top = sorted(enumerate(similarities), key=lambda x: -x[1])[:5]
        return {
            "top_semantic_matches": [
                {"service": ALL_SERVICES[i]["name"], "score": round(score, 4)}
                for i, score in top
            ]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
