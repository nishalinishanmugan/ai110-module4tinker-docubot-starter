"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob

class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Build a retrieval index (implemented in Phase 1)
        self.index = self.build_index(self.documents)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def tokenize(self, text):
        """
        Lowercase text, split on whitespace, and strip simple punctuation.
        Returns a list of cleaned tokens.
        """
        stopwords = {
            "the", "is", "a", "an", "and", "or", "to", "of", "in", "on", "for",
            "with", "by", "at", "from", "this", "that", "these", "those",
            "do", "does", "did", "how", "what", "where", "when", "which",
            "all", "are", "be", "been", "being", "it", "its", "as", "if",
            "i", "you", "your", "we", "they", "them", "their", "based"
        }

        tokens = []
        for word in text.lower().split():
            cleaned = word.strip(".,!?;:()[]{}\"'`<>/-")
            if cleaned and cleaned not in stopwords:
                tokens.append(cleaned)
        return tokens

    def split_into_sections(self, text):
        """
        Split a document into smaller retrieval units using blank lines.
        Filters out empty sections.
        """
        sections = []
        for section in text.split("\n\n"):
            cleaned = section.strip()
            if cleaned:
                sections.append(cleaned)
        return sections
    
    def build_index(self, documents):
        """
        TODO (Phase 1):
        Build a tiny inverted index mapping lowercase words to the documents
        they appear in.

        Example structure:
        {
            "token": ["AUTH.md", "API_REFERENCE.md"],
            "database": ["DATABASE.md"]
        }

        Keep this simple: split on whitespace, lowercase tokens,
        ignore punctuation if needed.
        """
        index = {}

        for filename, text in documents:
            unique_words = set(self.tokenize(text))

            for word in unique_words:
                if word not in index:
                    index[word] = []
                index[word].append(filename)

        return index
    
    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        TODO (Phase 1):
        Return a simple relevance score for how well the text matches the query.

        Suggested baseline:
        - Convert query into lowercase words
        - Count how many appear in the text
        - Return the count as the score
        """
        query_words = set(self.tokenize(query))
        text_words = set(self.tokenize(text))

        score = 0
        for word in query_words:
            if word in text_words:
                score += 1

                if len(word) >= 7:
                    score += 1

        return score

    def retrieve(self, query, top_k=3):
        """
        TODO (Phase 1):
        Use the index and scoring function to select top_k relevant document snippets.

        Return a list of (filename, text) sorted by score descending.
        """
        query_words = self.tokenize(query)

        # Guardrail: if the query has too few meaningful words, refuse
        if len(query_words) < 2:
            return []

        candidate_filenames = set()
        for word in query_words:
            if word in self.index:
                candidate_filenames.update(self.index[word])

        # If the index finds nothing, refuse instead of guessing
        if not candidate_filenames:
            return []

        candidate_docs = [
            (filename, text)
            for filename, text in self.documents
            if filename in candidate_filenames
        ]

        scored_results = []

        for filename, text in candidate_docs:
            sections = self.split_into_sections(text)

            for section in sections:
                score = self.score_document(query, section)
                if score > 0:
                    scored_results.append((score, filename, section))

        scored_results.sort(key=lambda item: (-item[0], item[1]))

        # Stronger guardrail: require at least 2 meaningful matches
        meaningful_results = [
            (filename, section)
            for score, filename, section in scored_results
            if score >= 2
        ]

        return meaningful_results[:top_k]


    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
