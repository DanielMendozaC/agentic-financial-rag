# Advanced Financial Document Analysis with Agentic RAG

## 1. Title & Abstract
**Title:** Advanced Financial Document Analysis with Agentic RAG

**Abstract:** This project develops an end‑to‑end Retrieval‑Augmented Generation (RAG) system enhanced with agentic orchestration to perform accurate, multi‑step analysis of SEC financial filings. By combining specialized chunking, hybrid retrieval, temporal and numerical reasoning, and a multi‑agent workflow, the system aims to improve factual accuracy and handle complex financial queries. The work includes a rigorous evaluation against a baseline RAG pipeline and culminates in a publishable thesis and demo.

---

## 2. Motivation & Research Questions
**Motivation:**
- Pretrained LLMs struggle with up‑to‑date, long‑form, and numeric‑heavy financial documents.  
- Financial analysts need tools that can ground answers in real filings, handle multi‑step calculations, and adaptively fetch missing context.

**Research Questions:**
1. Does agentic orchestration improve the accuracy and completeness of financial question answering compared to a standard single‑shot RAG pipeline?  
2. How do metadata‑aware chunking and hybrid retrieval strategies affect retrieval precision and downstream answer quality?  
3. What is the trade‑off between improved accuracy and additional retrieval latency in an agentic RAG system?

---

## 3. Objectives & Contributions
1. **Build a baseline RAG pipeline** using LLaMA and FAISS.  
2. **Design and evaluate metadata‑aware chunking** that tags text with fiscal period and section headers.  
3. **Implement hybrid retrieval** combining dense vectors and sparse filters for financial queries.  
4. **Develop an agentic orchestration layer** that plans, retrieves, and iterates to answer multi‑part questions.  
5. **Integrate numeric calculation tools** to verify and compute financial metrics.  
6. **Conduct a rigorous evaluation** (precision@k, numeric exact‑match, human ratings, ablation studies).

---

## 4. Methodology
### 4.1 Data Ingestion & Chunking
- Use **OpenEDGAR** or SEC API to download 10‑K/10‑Q filings.  
- Split documents into semantically coherent chunks (fixed‑length or by section using XBRL tags).  
- Attach metadata (company ticker, filing year/quarter, section name) to each chunk.

### 4.2 Indexing & Retrieval
- Build a **hybrid index**:
  - **Dense embeddings** via Sentence‑Transformers + FAISS  
  - **Sparse filters** on metadata fields (ticker, year).  
- Implement retrieval functions that return top‑k chunks filtered by metadata.

### 4.3 LLM Backbone & Prompting
- Use **LLaMA** (7B/13B) as the foundation model.  
- Apply **LoRA fine‑tuning** on a small corpus of EDGAR text for domain adaptation.  
- Craft dynamic prompts that inject retrieved chunks and guide numeric reasoning.

### 4.4 Agentic Orchestration
- Build a simple **agent loop**:
  1. **Plan:** Decompose query into sub‑tasks (e.g., extract numbers, compare sections).  
  2. **Retrieve:** Fetch relevant chunks based on plan.  
  3. **Act:** Generate interim answers or compute metrics.  
  4. **Observe:** Check if answer is complete; if not, revise plan and repeat.  
- Implement specialized agents (trend analysis, metric extraction, summary generation).

### 4.5 Numeric Tool Integration
- Expose a **calculator** tool to handle arithmetic (growth rates, ratios).  
- Have agents call the tool for precise computation when needed.

---

## 5. Evaluation Plan
### 5.1 Benchmark Dataset
- Curate 30–40 hand‑verified QA pairs covering numeric and qualitative queries across 5 companies.

### 5.2 Metrics
| Category              | Metric                                                       |
|-----------------------|--------------------------------------------------------------|
| Retrieval Quality     | Precision@k, Recall@k on labeled relevant chunks            |
| Factual Accuracy      | Exact‑match and F1 on numeric answers                         |
| Answer Quality        | Human ratings (correctness, completeness, clarity)           |
| Citation Fidelity     | % of statements traceable to retrieved chunks                |
| Efficiency           | Average number of retrieval iterations, latency per query      |

### 5.3 Experiments & Ablations
1. **Baseline RAG vs. Agentic RAG**: compare overall accuracy and citation fidelity.  
2. **Without metadata‑aware chunking** vs. **with**: measure retrieval precision gains.  
3. **With vs. without numeric tool**: quantify improvements in numeric answer accuracy.  
4. **Vary loop iterations**: analyze cost‑benefit of multiple retrieval steps.

---

## 6. Timeline & Milestones
| Weeks   | Milestone                                                         |
|--------:|-------------------------------------------------------------------|
| 1–2     | Literature review, define research questions, build QA benchmark   |
| 3–4     | Environment setup, data ingestion, baseline RAG prototype         |
| 5       | Baseline evaluation & documentation                                |
| 6–7     | Implement metadata‑aware chunking & hybrid retrieval               |
| 8       | Evaluate retrieval improvements                                   |
| 9–10    | Develop agentic loop & numeric tool integration                    |
| 11      | Compare agentic RAG vs. baseline, run ablation studies             |
| 12      | Final write‑up, paper draft, and presentation preparation         |

---

## 7. Resources & Risks
- **Compute:** GPU access (e.g., A100 or equivalent) for LLaMA and indexing.  
- **Data Parsing:** EDGAR filings may require custom HTML/PDF parsing → mitigate by using established libraries.  
- **Model Limitations:** Address LLM hallucinations with retrieval grounding and tool use.  
- **Time Management:** Focus on MVP (baseline RAG) first, then iterate to de‑risk.

---

## 8. Next Steps
1. Share this markdown with your advisor for feedback.  
2. Kick off **Week 1**: finalize research questions, assemble QA benchmark.  
3. Begin **MVP baseline** implementation (Week 3–4) to validate the end‑to‑end pipeline.

---

*End of Project Plan*

