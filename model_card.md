# DocuBot Model Card

This model card is a short reflection on your DocuBot system. Fill it out after you have implemented retrieval and experimented with all three modes:

1. Naive LLM over full docs  
2. Retrieval only  
3. RAG (retrieval plus LLM)

Use clear, honest descriptions. It is fine if your system is imperfect.

---

## 1. System Overview

**What is DocuBot trying to do?**  
Describe the overall goal in 2 to 3 sentences.

> _Your answer here._

**What inputs does DocuBot take?**  
For example: user question, docs in folder, environment variables.

> _Your answer here._

**What outputs does DocuBot produce?**

> _Your answer here._

---
DocuBot is a system that is trying to help the user answer questions about the files stores in docs/ folder. It compares three approaches: naive generation over the full corpus, retrieval only, and retrieval augmented generation. DocuBot takes a user question, the documentation files stored in the docs/ folder, and environment variables such as GEMINI_API_KEY when LLM features are enabled. It also uses queries from dataset.py when the user does not type a custom question.DocuBot produces either a generated answer, retrieved snippets from the documentation, or a refusal such as “I do not know based on these docs.” depending on the selected mode. 


## 2. Retrieval Design

**How does your retrieval system work?**  
Describe your choices for indexing and scoring.

- How do you turn documents into an index?
- How do you score relevance for a query?
- How do you choose top snippets?

> _Your answer here._

**What tradeoffs did you make?**  
For example: speed vs precision, simplicity vs accuracy.

> _Your answer here._

---

The retrieval system first loads all .md and .txt files from the docs/ folder into memory. It builds the index by tokenizing each document into lowercase words, removing punctuation, stopwords, and mapping each word to the filenames wherever it appears. For retrieval, the system tokenizes the query and uses the index to find related documents. It then splits each relevant document into smaller sections using blank lines, so the retrieval is a section rather instead of the whole file. Each section is scored by counting how many meaningful query words appear in that section. The system sorts sections by score and returns the top text that passes the minimum threshold. The retrieval design was easy to implement and understand. The tradeoff is that it is fast and readable, but less precise than a stronger search system. Using blank line sections is better than returning whole documents, but it can still still have issues. The scoring is also based only on overlapping keywords, so it can miss the best section if more than one section share similar words.

## 3. Use of the LLM (Gemini)

**When does DocuBot call the LLM and when does it not?**  
Briefly describe how each mode behaves.

- Naive LLM mode:
- Retrieval only mode:
- RAG mode:

> _Your answer here._

**What instructions do you give the LLM to keep it grounded?**  
Summarize the rules from your prompt. For example: only use snippets, say "I do not know" when needed, cite files.

> _Your answer here._

---
In the Naive LLM mode, the system sends the document to the Gemini client and asks it to answer directly without retrieval. In the Retrieval only mode, the system does not call the LLM at all and it return text from the docs. In RAG mode, the system first retrieves text using the retrieval pipeline, then sends only those text plus the user’s question to the Gemini client. The LLM is instructed to answer using only the retrieved text and not rely on outside knowledge. If the text does not match anything, it should say “I do not know based on the docs I have.” The model should not guess the answer if it does not have the information. 

## 4. Experiments and Comparisons

Run the **same set of queries** in all three modes. Fill in the table with short notes.

You can reuse or adapt the queries from `dataset.py`.

| Query | Naive LLM: helpful or harmful? | Retrieval only: helpful or harmful? | RAG: helpful or harmful? | Notes |
|------|---------------------------------|--------------------------------------|---------------------------|-------|
| Example: Where is the auth token generated? | | | | |
| Example: How do I connect to the database? | | | | |
| Example: Which endpoint lists all users? | | | | |
| Example: How does a client refresh an access token? | | | | |

**What patterns did you notice?**  

- When does naive LLM look impressive but untrustworthy?  
- When is retrieval only clearly better?  
- When is RAG clearly better than both?

> _Your answer here._

---
For the question where does the authentication token generated, the Native LLM is harmful, the retrieval only can be both harmful and helpful, and the RAG can be both harmful and helpful. The Native mode gives and explanation but does not use the docs. Retreival found AUTH.md, but it returned the wrong section. RAG refused because Retrieval didn't give it enough evidence. For the question how do I connect to the database, Native is helpful, retrieval only is helpful, and RAG is helpful if th retrieval is correct. The docs mention DATABASE_URL, so the retrival answers should be correct. Native should be correct, but it might mention other information. For the question, which enpoint lists all users, the Native mode is harmful, the retrieval only mode is helpful, the RAG can be helpful or harmful. The Native mode can answer vaugely. The Retrieval mode should return the right sentence of GET /api/users, but it might miss the heading. And as a result, the RAG could return the correct information or it might refused because it didn't recieve all the content. For the question how does a client refresh an access token, the Native model can be harmful and helpful, the retrieval only can be helpful, and the RAG can be helpful. The documents mention /api/refresh and the Authorization header. The retrival should work if the right section is selected. Native mode might be get API and authentication confused and be harmful. Naive LLM was the least trustworthy because it confidently answered using general knowledge instead of the docs. Retrieval only mode was better because it returned document text and refused vague questions. RAG only works well when retrieval provides the right snippets. When retrieval is weak, RAG refuses even supported questions. But RAG has the potential to be the strongest out of the three if the retrival only is also strong. 

## 5. Failure Cases and Guardrails

**Describe at least two concrete failure cases you observed.**  
For each one, say:

- What was the question?  
- What did the system do?  
- What should have happened instead?

> _Failure case 1 here._

> _Failure case 2 here._

**When should DocuBot say “I do not know based on the docs I have”?**  
Give at least two specific situations.

> _Your answer here._

**What guardrails did you implement?**  
Examples: refusal rules, thresholds, limits on snippets, safe defaults.

> _Your answer here._

---
For the question how do I deploy this app to Kubernetes, Naive LLM mode generated a Kubernetes deployment guide even though the docs do not mention Kubernetes at all.The system should have refused and said it did not know based on the docs. For the question Where is the auth token generated, Retrieval only mode found the correct file, AUTH.md, but returned a section about TOKEN_LIFETIME_SECONDS instead of the section about generate_access_token. RAG then refused because the snippet did not clearly answer the question. Retrieval should have returned the token generation section, and RAG should then have answered from that evidence. DocuBot should refuse when the question is unrelated to the documents, such as asking about Kubernetes deployment when the docs only cover API, auth, database, etc. It should also refuse when retrieval finds weak answer and no section contains enough meaningful evidence to support an answer. Another refusal case is when the question is too vague or has too few meaningful words. I added a guardrail that removes common words so weak filler words do not impact retrieval. I also required a minimum number of meaningful token matches before returning a snippet. If the query has too few meaningful words or no sections meet the score threshold, the system returns “I do not know based on these docs.” Refusal is the default when evidence is weak.

## 6. Limitations and Future Improvements

**Current limitations**  
List at least three limitations of your DocuBot system.

1. _Limitation 1_
2. _Limitation 2_
3. _Limitation 3_

**Future improvements**  
List two or three changes that would most improve reliability or usefulness.

1. _Improvement 1_
2. _Improvement 2_
3. _Improvement 3_

---
Current limitations
1. The retrieval system uses keyword overlap, so it can still rank the wrong section above the best one.
2. The system splits documents by blank lines, which can separate headings from the text and makes text less complete.
3. RAG performance depends entirely on retrieval results, so if retrieval is weak, the LLM cannot answer the question even when the docs contain the answer.

Future improvements
1. Improve the system so headings stay attached to their paragraphs or sections.
2. Use stronger scoring so terms are weighted or phrase are matched instead of only counting overlapping words.
3. Add clear formatting so retrieval results are easier to interpret and verify.

## 7. Responsible Use

**Where could this system cause real world harm if used carelessly?**  
Think about wrong answers, missing information, or over trusting the LLM.

> _Your answer here._

**What instructions would you give real developers who want to use DocuBot safely?**  
Write 2 to 4 short bullet points.

- _Guideline 1_
- _Guideline 2_
- _Guideline 3 (optional)_

---
This system could cause harm if users trust naive LLM answers without checking whether they are actually supported by the documentation. A vague answer about authentication, permissions, deployment, or configuration in the real world could lead to bugs and bad decisions. It could also cause harm by neglecting important constraints, such as admin only access, and making a user think an action is allowed when it is not. 
- The user should Always verify answers against the retrieved evidence, especially for security and authentication questions.
- Prioritive refusing when the retrieved context is weak or missing.
- Test the same questions across supported and unsupported cases to make sure the system refuses when it should.
