UAE Legal Compliance Engine
An Enterprise-Grade RAG (Retrieval-Augmented Generation) system for navigating UAE Federal Decree-Laws.

The Problem ??
UAE's regulatory landscape (Corporate Tax, Data Privacy, etc.) is rapidly evolving. Small businesses struggle to stay compliant without expensive legal counsel. This engine provides instant, grounded answers based on actual legal text.

The Tech Stack
- Brain: Google Gemini 1.5 Flash (1M context window)
- Search: Cohere Embed v3 + Cohere Rerank 3 (Industry-leading legal precision)
- Database: ChromaDB (Vector store)
- UI: Gradio 6.0 (Custom charcoal matte interface)

Architecture
The system utilizes a multi-stage RAG pipeline:
1. Retrieval: Converts legal PDFs into embeddings via Cohere.
2. Reranking: Re-scores search results to ensure the most relevant clause is picked.
3. Generation: Gemini synthesizes the final answer using retrieved context.