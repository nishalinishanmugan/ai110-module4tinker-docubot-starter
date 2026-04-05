# DocuBot

DocuBot is a small documentation assistant that helps answer developer questions about a codebase.  
It can operate in three different modes:

1. **Naive LLM mode**  
   Sends the entire documentation corpus to a Gemini model and asks it to answer the question.

2. **Retrieval only mode**  
   Uses a simple indexing and scoring system to retrieve relevant snippets without calling an LLM.

3. **RAG mode (Retrieval Augmented Generation)**  
   Retrieves relevant snippets, then asks Gemini to answer using only those snippets.

The docs folder contains realistic developer documents (API reference, authentication notes, database notes), but these files are **just text**. They support retrieval experiments and do not require students to set up any backend systems.

---

## Setup

### 1. Install Python dependencies

    pip install -r requirements.txt

### 2. Configure environment variables

Copy the example file:

    cp .env.example .env

Then edit `.env` to include your Gemini API key:

    GEMINI_API_KEY=your_api_key_here

If you do not set a Gemini key, you can still run retrieval only mode.

---

## Running DocuBot

Start the program:

    python main.py

Choose a mode:

- **1**: Naive LLM (Gemini reads the full docs)  
- **2**: Retrieval only (no LLM)  
- **3**: RAG (retrieval + Gemini)

You can use built in sample queries or type your own.

---

## Running Retrieval Evaluation (optional)

    python evaluation.py

This prints simple retrieval hit rates for sample queries.

---

## Modifying the Project

You will primarily work in:

- `docubot.py`  
  Implement or improve the retrieval index, scoring, and snippet selection.

- `llm_client.py`  
  Adjust the prompts and behavior of LLM responses.

- `dataset.py`  
  Add or change sample queries for testing.

---

## Requirements

- Python 3.9+
- A Gemini API key for LLM features (only needed for modes 1 and 3)
- No database, no server setup, no external services besides LLM calls

## Reflect and Discuss
The summary should be 5–7 sentences covering:

- The core concept students needed to understand
- Where students are most likely to struggle
- Where AI was helpful vs misleading
- One way they would guide a student without giving the answer

The student get to understand the differences between the Native LLM, retrival only, and RAG and why it is important to provide the LLM with real evidence. The student will probably need to fix the docubot.py code several times to reach a point where the retrival only mode is more or less correct. The instructiosn mentions to run pip install -r requirement.txt, which is good because it never mentioned it in the instructions before only in the README. The AI is helpful is suggestion implementations for the functions in docubot.py, but it is easy for the AI to provide misleading code if it doesn't have the full context or if the student is vague in asking the AI. As a student, I would follow what the instructions mention where the student things about the code the AI is providing and as more questions or mention specific things that they want improved to get better results. If the student is specific and provide context to the AI, it should have better results. The student should think about the process of the system and ask specific questions instead of asking the AI to just give the answer. 