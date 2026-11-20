# StudySync – Major Project Presentation & Viva Guide

This guide is designed for your project presentation and viva evaluation. It details the architecture, your individual contributions (Member 1 & Member 6), how the 6 systems collaborate, and the underlying Generative AI concepts.

---

## 🎤 1. 2-Minute Elevator Pitch
> *"StudySync is an end-to-end personalized learning ecosystem powered by six collaborating Generative AI systems. Instead of a generic one-size-fits-all chatbot, each member developed a dedicated AI agent specializing in a core stage of the learning cycle:*
> 1. *TutorGPT (Teaching & RAG)*
> 2. *QuizGen AI (Assessment & Rubric Grading)*
> 3. *CodeMentor AI (Programming & Sandboxed Execution)*
> 4. *StudyPlanner AI (Deadline-Aware Scheduling)*
> 5. *PerformanceAnalyst AI (Data & Trend Tracking)*
> 6. *RevisionGPT (Active Recall & Spaced Repetition)*
>
> *I specifically developed **Member 1 (TutorGPT)** and **Member 6 (RevisionGPT)**, and integrated our friends' contributions into the unified ecosystem."*

---

## 🔍 2. Deep Dive: Member 1 — TutorGPT (Your Project)

### What it does:
- Acts as a personal AI academic professor.
- Breaks down complex concepts into pedagogical scaffolds:
  - Intuitive real-world analogy.
  - Formal academic definition.
  - Step-by-step operational mechanisms.
  - Practical code/math examples.
  - Common student misconceptions.
  - Interactive self-check question.

### GenAI Focus & Technical Architecture:
1. **Prompt Engineering & Difficulty Calibration**:
   - **Beginner**: Analogy-first, visual mental models, conversational English.
   - **Intermediate**: Standard university textbook depth, operational transitions, Big-O complexity.
   - **Advanced**: Mathematical invariants, formal specification ($\mathcal{O}$ bounds, state machine transitions), distributed systems trade-offs, and failure recovery.
2. **Retrieval-Augmented Generation (RAG)**:
   - **Ingestion & Chunking**: Splits uploaded lecture slides, notes, or textbooks into overlapping semantic chunks with metadata preservation.
   - **Vector Similarity Search**: Indexes chunks with TF-IDF / Cosine Vector Similarity (with dense sentence-transformer support) to retrieve top-$k$ relevant passages.
   - **Strict Grounding & Citation**: Forces the model to cite exact chunk sources (`[Source: DBMS_Notes.txt, Chunk #2]`) and guards against hallucinations when material is missing.
3. **Socratic Dialogue Mode**:
   - Employs pedagogical inquiry: evaluates student answers, praises correct intuition, and provides targeted hints rather than giving away solutions.

---

## 🔍 3. Deep Dive: Member 6 — RevisionGPT (Your Project)

### What it does:
- Acts as an active recall and memory retention agent.
- Converts raw study materials and weak topics into high-yield flashcards and concise revision cheat-sheets.
- Implements the scientifically validated **SuperMemo SM-2 Spaced Repetition Algorithm**.

### GenAI Focus & Technical Architecture:
1. **High-Yield Flashcard Generation**:
   - Extracts atomic factual and conceptual pairs (Front, Back, Hint, Concept, Difficulty) via structured JSON schema generation.
2. **SuperMemo SM-2 Spaced Repetition Algorithm (SRS)**:
   - Evaluates user recall quality $q \in \{0, 1, 2, 3, 4, 5\}$.
   - Updates Easiness Factor ($EF \ge 1.3$):
     $$EF' = EF + (0.1 - (5 - q) \times (0.08 + (5 - q) \times 0.02))$$
   - Calculates dynamic review interval ($I$ in days):
     - If $q \ge 3$: $I(1) = 1$, $I(2) = 6$, $I(n) = \text{round}(I(n-1) \times EF')$.
     - If $q < 3$: resets repetition count to 0 and interval to 1 day.
   - Tracks mastery metrics, retention rate percentage, and daily due cards.
3. **Concise Revision Notes & Hierarchical Summaries**:
   - Generates markdown comparison tables, key invariant rules, exam traps, and 60-second rapid recap sheets.

---

## 🤝 4. How the Six Agents Collaborate

| Step | Agent | What Happens |
|---|---|---|
| **1. Schedule** | **Member 4 (StudyPlanner AI)** | Creates initial schedule based on exam dates and available weekday/weekend hours. |
| **2. Learn** | **Member 1 (TutorGPT)** | Ingests course textbook and teaches topics using RAG and calibrated difficulty levels. |
| **3. Test** | **Member 2 (QuizGen AI)** | Tests student understanding with MCQs and descriptive questions, evaluating answers with rubric grading. |
| **4. Code** | **Member 3 (CodeMentor AI)** | Tests coding skills, detecting bugs and running code in a sandboxed subprocess. |
| **5. Analyze** | **Member 5 (PerformanceAnalyst AI)** | Reads quiz/code scores, applies **Scikit-Learn Linear Regression** to identify declining or weak concepts (<50%). |
| **6. Adapt** | **Member 4 (StudyPlanner AI)** | Ingests the weak concepts and rebalances the timetable, allocating priority revision blocks. |
| **7. Revise** | **Member 6 (RevisionGPT)** | Automatically generates remedial flashcards for the weak concepts and schedules daily SM-2 spaced repetition reviews! |

---

## 💡 5. Common Viva / Examiner Questions & Answers

### Q1: Why use multiple Generative AI agents instead of a single prompt or monolithic LLM?
> *"A monolithic LLM prompt suffers from context pollution, lack of specialized tools, and high hallucination rates. By decomposing the system into 6 specialized agents:
> 1. Each agent uses a dedicated prompt template and constrained JSON schema.
> 2. Tools are isolated (e.g., CodeMentor has a sandboxed code execution environment, TutorGPT has a RAG vector index, RevisionGPT has an SM-2 state machine).
> 3. Team members can develop, test, and benchmark their agents independently."*

### Q2: How does your RAG pipeline in TutorGPT prevent hallucinations?
> *"The RAG engine divides documents into semantic chunks with overlapping token windows. When a query arrives, it calculates cosine similarity against the chunk vector index and extracts the top-$k$ most relevant context blocks. In the system prompt, the LLM is instructed under strict grounding constraints to answer ONLY from the retrieved context and cite the exact source (`[Source: filename, Chunk #]`). If the context is insufficient, it explicitly warns the student before offering general knowledge."*

### Q3: How does the SuperMemo SM-2 algorithm in RevisionGPT optimize learning?
> *"Hermann Ebbinghaus discovered the Forgetting Curve: memories decay exponentially over time without reinforcement. SM-2 counters this by calculating the optimal review interval ($I$) based on recall difficulty ($q$). If recall was easy ($q=5$), the interval expands by the Easiness Factor ($EF$), pushing the next review further into the future. If recall failed ($q<3$), the interval resets to 1 day. This guarantees maximum memory retention with minimal review time."*

### Q4: How does PerformanceAnalyst track student learning progress?
> *"It applies a Scikit-Learn Linear Regression model over test score percentages versus calendar days. The slope of the trend line reveals whether a student's grasp of a specific concept is Improving ($>+1\%$/week), Declining ($<-1\%$/week), or Stable. Declining or weak concepts are flagged for immediate remediation."*

---

## 🖥️ 6. Live Demo Checklist

1. **Start Streamlit App**:
   ```bash
   cd CodeSync
   streamlit run app.py
   ```
2. **Demo Tab 1 (Overview)**: Explain the 6-agent collaborative diagram.
3. **Demo Tab 2 (TutorGPT)**:
   - Demonstrate Beginner vs. Advanced explanation for "Dynamic Programming" or "2PL".
   - Demonstrate RAG query on "ACID properties" showing retrieved chunks and citations.
4. **Demo Tab 7 (RevisionGPT)**:
   - Generate a flashcard deck on "ACID Transactions".
   - Demonstrate the interactive SM-2 flip-card review session, rating quality from 0 to 5 and showing interval expansion.
5. **Demo Tab 8 (Full 6-Agent Collaborative Cycle)**:
   - Click **"Run End-to-End Collaborative Cycle Now"** to show balloons and the live 6-step automated remediation pipeline!
