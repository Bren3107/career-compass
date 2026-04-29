
In the 2026 Sydney market, where "AI-adjacent" roles are the fastest-growing but most ill-defined, **The Career Compass** acts as the missing translation layer. It is designed to turn *"I have no experience"* into *"I have verified capability in High-ROI domains."*

# 🧭 Project Overview: The Career Compass

**Vision:** An end-to-end NLP application that ingests unstructured "student-speak" (university labs, internships, personal interests) and outputs a precise, market-aligned career roadmap. 

---

## 🎯 Core Project Goals (The "Triple Threat")

* **Clarity of Identity:** Move from vague titles like "Data Scientist" to high-demand 2026 niches like *AI UX Translator* or *Production-Grade Data Modeler*.
* **The Signal Gap Fix:** Identify exactly which 2–3 technical skills are preventing a "Match" with high-paying Sydney firms (e.g., switching from "Dashboarding" to "ETL Fundamentals").
* **Impact Translation:** Use NLP to rewrite technical university tasks (like a UTS capstone) into "Business Outcome" stories that recruiters actually value.

---

## 🛠️ Technical Roadmap & Techniques

The project follows a three-phase NLP pipeline designed to be both lightweight and technically sophisticated.

### Phase 1: Feature Extraction (The "Brain Dump" Parser)
* **Technique:** Named Entity Recognition (NER) and Part-of-Speech (POS) Tagging.
* **The Work:** Using a library like `spaCy` or a lightweight LLM (Llama-3-8B), the tool extracts "latent skills" from a student's unstructured text.
* **Example:** It identifies "worked with Epicor and SSRS" and extracts entities: `[Domain: ERP]`, `[Tool: SQL/SSRS]`, `[Capability: Enterprise Reporting]`.

### Phase 2: Semantic Mapping (The "Matchmaker")
* **Technique:** Sentence Embeddings and Cosine Similarity.
* **The Work:** Convert extracted features into a high-dimensional vector and compare it against a "Market Vector" created from a dataset of 2026 Australian job descriptions.
* **The Math:** Similarity is calculated using:
    $$\cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$
* **Outcome:** If the score is $>0.85$, the tool confirms: *"You are mathematically aligned for a BI Engineer role."*

### Phase 3: Generative Gap Analysis (The "Roadmap")
* **Technique:** Retrieval-Augmented Generation (RAG).
* **The Work:** The system retrieves the requirements of the matched role and generates a 30-day learning plan to bridge the gap.
* **Example:** *"You have SQL fluency, but Sydney firms now require 'dbt' or 'Fabric'. Spend Week 1 on this specific module."*

---

## 🧰 The NLP Toolkit (2026 Standard)

| Category | Tool / Library | Why? |
| :--- | :--- | :--- |
| **Language Model** | Hugging Face Transformers | Access to `all-MiniLM-L6-v2` for fast, local embedding. |
| **Backend** | Python / FastAPI | Industry standard for data-driven APIs. |
| **User Interface** | Streamlit | Build a professional dashboard in pure Python. |
| **Data Storage** | FAISS | To store and search through job description vectors instantly. |

---

## ✨ Expected Outcomes

1.  **A "Market-Ready" Profile:** A generated PDF or Profile Link that emphasizes **Outcomes** over **Responsibilities**.
2.  **A Precision Filter:** Instead of applying to 100 jobs, the student applies to the 5 where they have a $>90\%$ semantic match.
3.  **The Confidence Boost:** By seeing an "unstructured life" turned into a "Technical Capability Map," the student realizes their true value in the current market.