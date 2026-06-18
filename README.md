# 🚔 Delhi Police Website Chatbot

> An intelligent, multilingual citizen-assistance chatbot for the Delhi Police website — designed to guide users through the right service, portal, or helpline based on their actual problem.

---

## 🧭 Problem Statement

The Delhi Police website hosts **40+ citizen-facing services** spread across 10+ subdomains and portals. Most citizens — whether reporting a theft, applying for a Police Clearance Certificate, or tracking a complaint — have no guidance on:

- Which service or portal to use (e-FIR vs Lost Report vs Complaint Lodging are all different)
- What documents or prerequisites are needed before they apply
- Which helpline number applies to their specific situation
- How to track something they've already filed

This chatbot is built to fix exactly that — not with generic answers, but with **specific, actionable guidance** tied to the actual Delhi Police service ecosystem.

---

## ✅ Current Features (v0.1 — In Progress)

### 🌐 Multilingual Query Support
Citizens can type their query in **Hindi, English, or Hinglish** — whichever feels most natural. The system handles all three natively, making it accessible to a wider demographic including senior citizens and low-literacy users.

Language understanding is powered by **IndicBERT** (via the [AI4Bharat](https://ai4bharat.org/) initiative), a BERT-based model specifically pre-trained on Indian languages, enabling robust comprehension of code-switched and transliterated text.

### 🔍 Keyword-Based Service Matching (FastAPI)
Once a query is submitted, a **FastAPI backend** performs keyword matching across the Delhi Police service catalogue and returns:
- The **top 5 most relevant results** for the user's query
- A **direct hyperlink** to the relevant portal or service page (not just the homepage)

This eliminates the need for users to navigate through the website themselves.

---

## 🚧 Work in Progress

This project is actively under development. The following features are planned:

| Feature | Description |
|---|---|
| 📋 Document Checklist | Pre-flight checklist before applying — lists all required documents per service |
| 🗂️ Procedure Guides | Step-by-step filing guidance for complaints, FIRs, verifications, etc. |
| 🎙️ Speech Input | Voice-based query input — critical for accessibility |
| 💡 Smart Suggestions | "Did you mean...?" suggestions for ambiguous or misspelled queries |
| 🔗 Service Tracking | Route users to the exact tracking portal based on what they filed |
| 🚨 Helpline Routing | Intent-based routing to the correct helpline (e.g., 1930 for cybercrime, not 112) |

---

## 🗂️ Repository Structure
DP-Chatbot/

├── backend/          # FastAPI server, keyword matching logic

├── frontend/         # UI layer

├── data/             # Service catalogue, portal URLs, helpline directory

├── classify.py       # Query classification logic

├── compile_services.py

├── enrich_links.py   # Adds portal hyperlinks to matched results

├── export_csv.py

├── extract.py

└── scraper.py        # Scrapes Delhi Police service data

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| NLP / Language | IndicBERT (AI4Bharat) |
| Matching | Keyword-based search over service catalogue |
| Frontend | HTML / CSS / JavaScript |
| Data | Scraped & curated Delhi Police service data |

---

## ⚠️ Data Disclaimer

This repository **does not contain any confidential Delhi Police data**. All data used is sourced exclusively from publicly accessible pages of the Delhi Police website and its affiliated portals. No internal records, case data, citizen PII, or restricted law enforcement information is included at any stage of this project.

---

## 🌱 Future Scope

Beyond the immediate roadmap, the long-term vision includes:

- **Agentic capabilities** — proactively surfacing relevant information based on inferred intent
- **RAG pipeline** — Retrieval-Augmented Generation over a curated knowledge base of Delhi Police services, forms, legal information, and FAQs
- **Unified tracking UX** — single interface to track FIRs, complaints, missing mobiles, and vehicles across siloed portals
- **Full Hindi interface** — not just transliteration support, but a complete Hindi-first experience

---


# 🧠 RAG System

## Overview

Most of our **40+ services** are simple *"go to this page"* lookups. These are handled well by the existing **keyword + IndicBERT router**, since their answers are static and rarely change.

However, four categories contain information that changes frequently:

- **Welfare**
- **Standing Orders / Circulars**
- **Security (VIP & Events)**
- **Drone / Anti-Drone Advisories**

For these categories, there is no single static page that always contains the answer. Therefore, we use **Retrieval-Augmented Generation (RAG)** instead of simple routing.

Instead of merely redirecting users to a webpage, the system retrieves and serves information directly from the latest official content.


<img width="460" height="318" alt="image" src="https://github.com/user-attachments/assets/b321174f-e9b7-4461-a61d-d6424241dfb1" />

---

# 🔄 Content Refresh Pipeline

A background job runs automatically once every day to keep the knowledge base up to date.

### 1. Scrape

Revisit the source pages/documents corresponding to the four RAG categories.

### 2. Detect Changes

Compare newly scraped content with the previous day's version using a simple fingerprint/hash check.

- Unchanged content is skipped.
- Only new or modified content is processed.

### 3. Chunk Documents

Split updated content into smaller paragraph-sized chunks.

### 4. Store

Save each chunk along with metadata:

- Source URL
- Category
- Date

This ensures that our knowledge base is never more than one day old while avoiding unnecessary reprocessing.

<img width="288" height="416" alt="image" src="https://github.com/user-attachments/assets/3c202dbe-11fa-4e5f-af9c-2502b1ffd5b4" />

---

# 🔍 Query Processing Pipeline

Whenever a user submits a query:

## Step 1: Query Classification

Determine whether the query belongs to:

### Normal Service

Handled by the existing router (unchanged).

### Dynamic Categories

- Welfare
- Circulars
- Security
- Drone Advisories

These queries are sent through the RAG pipeline.

---

## Step 2: Retrieval

Search the knowledge base for the most relevant stored chunks.

---

## Step 3: Confidence Check

### ✅ Good Match Found

Return the retrieved content along with:

- Source link
- Date of publication/update

### ⚠️ No Good Match Found

The system does **not hallucinate** or guess.

Instead, it falls back to:

> "Please refer to the official page for the latest information."

---

# ⚠️ Why We Avoid Rewriting Official Content

Security advisories and official circulars are sensitive documents.

Even small paraphrasing errors can accidentally alter:

- Dates
- Restrictions
- Instructions
- Operational details

Therefore, the current implementation prioritizes **faithful retrieval** over generation.

Retrieved passages are displayed almost verbatim, together with:

- Source URL
- Date

Future versions may allow summarization for lower-risk categories such as general welfare FAQs after accuracy has been thoroughly validated.

<img width="522" height="398" alt="image" src="https://github.com/user-attachments/assets/f7c88b87-4b8d-46c4-89aa-d5964eadfce6" />


---

# 🗂 Repository Additions

| Component | Purpose |
|------------|---------|
| `data/rag_sources/` | Raw scraped content for the four RAG categories |
| `backend/rag_engine.py` | Retrieval and answer generation logic |
| `backend/vector_store/` | Searchable vectorized chunks |
| `.github/workflows/daily_refresh.yml` | Automated daily scrape-and-update pipeline |

---

# 📌 Current Status

> **Status:** Planned — not yet implemented.

The existing router for **40+ static services** remains unchanged and continues to function independently.


## 👥 Contributors

- [Sarthakdem18](https://github.com/Sarthakdem18)
- [Lavanya](https://github.com/L-2704) 
- [Ayushi](https://github.com/yushi005)

---

## 📌 Status

> 🟡 **Active Development** — Core features functional, multilingual support live, additional modules being added iteratively.

---
