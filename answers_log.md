1. http://127.0.0.1:5002/answer?question=What are the production 'Do's' for RAG?
```json
{
    "answer": "Unfortunately, I don't have access to information about \"Production Readiness\" in the provided context. The closest relevant text is from [Source: Databases_for_GenAI.pdf], but it mentions only an agenda with topics such as \"Foundations\", \"Advanced Rag Patterns\", and \"Production Readiness\", without providing any specific information on what constitutes \"production readiness\" for RAG.",
    "chunks": [
        {
            "score": 0.6529,
            "source": "Architecture__Design_Patterns.pdf",
            "text": "rag architecture"
        },
        {
            "score": 0.6478,
            "source": "Databases_for_GenAI.pdf",
            "text": "advanced rag patterns"
        },
        {
            "score": 0.6318,
            "source": "Productized__Enterprise_RAG.pdf",
            "text": "23 q1 what is the main goal of rag? a. to train larger models b. to reduce hallucinations using external knowledge c. to replace ﬁne - tuning d. to speed up token generation"
        },
        {
            "score": 0.611,
            "source": "Productized__Enterprise_RAG.pdf",
            "text": "what is rag a rag system essentially correlates a user ' s prompt with a relevant data chunk. it does this by identifying the most semantically similar chunk from the database. this chunk then becomes..."
        },
        {
            "score": 0.5874,
            "source": "Databases_for_GenAI.pdf",
            "text": "3 agenda 01 02 03 foundations advanced rag patterns production readiness"
        }
    ],
    "num_chunks_retrieved": 5,
    "question": "What are the production 'Do's' for RAG?",
    "success": true
}
```

2. http://127.0.0.1:5002/answer?question=What is the difference between standard retrieval and the ColPali approach?
```json
{
    "answer": "Unfortunately, I don't have enough information to provide a clear answer. The context provided mentions various concepts related to retrieval techniques, such as vector store index, hierarchical indices, and fusion retrieval, but it doesn't explicitly mention the \"ColPali\" approach or how it differs from standard retrieval.\n\nHowever, based on the text, I can infer that the ColPali approach might be a specific implementation or configuration for retrieval, possibly related to chunking and threshold-based filtering. The speaker in the video mentions using a \"threshold 085\" when invoking the search quadrant, which is likely a parameter used in the ColPali approach.\n\nTo provide a more accurate answer, I would need more information about the ColPali approach or specific details about how it differs from standard retrieval techniques. If you have any additional context or clarification, I'll be happy to try and help!",
    "chunks": [
        {
            "score": 0.5372,
            "source": "Architecture__Design_Patterns.pdf",
            "text": "the retrieval component is responsible for sourcing relevant information from a database or document collection based on the user ' s query or input. this information is attached to prompt and passed ..."
        },
        {
            "score": 0.4696,
            "source": "Architecture__Design_Patterns.pdf",
            "text": "advanced retrieval"
        },
        {
            "score": 0.4496,
            "source": "2_part_Databases_for_GenAI.mp4",
            "text": "composition of that request that ' s agents our llem bricks like our q3 matrix then we need to find this information in our internal database or a vector system industry q3 benchmarks potentially we d..."
        },
        {
            "score": 0.4337,
            "source": "RAG_Intro.pdf",
            "text": "6 why rag matters? ● fresh additional knowledge. rag lets you ground answers in recent documents, internal wikis, or databases without retraining models. ● better accuracy. by retrieving authoritative..."
        },
        {
            "score": 0.4321,
            "source": "2nd_Part_Architecture__Design_Patterns.mp4",
            "text": "than 12 words that ' s interesting i never actually tested this. yeah. it ' s probably because it actually allows to sentences and stands up consider to sentences like this anyway we have different ch..."
        }
    ],
    "num_chunks_retrieved": 5,
    "question": "What is the difference between standard retrieval and the ColPali approach?",
    "success": true
}
```
3. http://127.0.0.1:5002/answer?question=Why is hybrid search better than vector-only search?
```json
{
    "answer": "According to the provided context, hybrid search combines the strengths of both BM25 (a traditional search algorithm) and vector-based search. The speaker mentions that:\n\n* Hybrid search has a higher accuracy rate (+10% improvement over vector-only search)\n* It also reduces retrieval failures by 67%\n* The combination of search vector + BM25 increases accuracy for more than 10 percentage points\n* When reranking is added, the hybrid system achieves even better results (+37.2% improvement in ndcg @ 3)\n\nThis suggests that hybrid search is a better approach because it leverages the strengths of both traditional and vector-based search methods to provide more accurate results.",
    "chunks": [
        {
            "score": 0.514,
            "source": "2_part_Databases_for_GenAI.mp4",
            "text": "is what bm25 it doesn ' t have semantic understanding but it ' s calculated the number of words that it finds like the same word that it ' s finding the different documents and can provide based on th..."
        },
        {
            "score": 0.4859,
            "source": "Databases_for_GenAI.pdf",
            "text": "17 hybrid search + reranking power vector - only : misses exact matches, acronyms bm25 - only : no semantic understanding anthropic contextual retrieval study : - baseline failure rate : 5. 7 % - hybr..."
        },
        {
            "score": 0.484,
            "source": "2_part_Databases_for_GenAI.mp4",
            "text": "of that emails and just to give you perspective of how it fast and what is the how fast we are moving to improving all of these tools and systems the previous result was more than 200 seconds so the o..."
        },
        {
            "score": 0.4206,
            "source": "2_part_Databases_for_GenAI.mp4",
            "text": "answer on the question quite often when we utilize the pdfs when we have a pdfs as documents we utilize the ocr for describing of that documents and then we store the information but this approach wit..."
        },
        {
            "score": 0.41,
            "source": "2_part_Databases_for_GenAI.mp4",
            "text": "vector databases when we set up like choose top five results providing to us with the answer from the five closest objects and then transform this to the text and we are basically getting that ' s tha..."
        }
    ],
    "num_chunks_retrieved": 5,
    "question": "Why is hybrid search better than vector-only search?",
    "success": true
}
```