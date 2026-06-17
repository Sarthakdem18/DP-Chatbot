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

## 👥 Contributors

- [Sarthakdem18](https://github.com/Sarthakdem18)
- [Lavanya](https://github.com/L-2704) 
- [Ayushi](https://github.com/yushi005)

---

## 📌 Status

> 🟡 **Active Development** — Core features functional, multilingual support live, additional modules being added iteratively.

---
