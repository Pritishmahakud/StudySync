# StudySync – Multi-Agent Generative AI Learning Ecosystem

**StudySync** is an end-to-end personalized learning ecosystem powered by **six independently developed, collaborating Generative AI systems**. Each agent specializes in a distinct pedagogical discipline, sharing events and learning analytics across a unified ledger to deliver an adaptive student experience.

---

## 🔐 Database & Security Architecture

StudySync includes a persistent SQLite database (`data/studysync.db`) and cryptographically robust user authentication:

- **Password Hashing**: PBKDF2-HMAC-SHA256 with 100,000 iterations and unique 16-byte random salts.
- **Relational Tables**:
  - `users`: Credentials, names, email uniqueness, registration dates, last login.
  - `learning_sessions`: Tracks study time per concept and subject.
  - `quiz_scores`: Historical test scores and percentages per student.
  - `flashcards`: Active SuperMemo SM-2 cards, repetitions, easiness factors, and next due review dates.
  - `user_documents`: Uploaded PDFs, Word docs, and PowerPoint decks metadata.
- **Pre-Seeded Demo Student**:
  - **Email**: `asha@studysync.edu`
  - **Password**: `Password@123`
- **User Registration**: Any student can create an account via the "Create Account" tab on the login screen.

---

## 🏛️ Ecosystem Architecture & Team Distribution

```
                                      +------------------------+
                                      |     StudySync UI /     |
                                      |   Master Orchestrator  |
                                      +-----------+------------+
                                                  |
         +--------------------+-------------------+--------------------+--------------------+
         |                    |                   |                    |                    |
+--------v-------+   +--------v-------+  +--------v-------+   +--------v-------+   +--------v-------+
|  Member 1      |   |  Member 2      |  |  Member 3      |   |  Member 4      |   |  Member 5      |
|  TutorGPT      |   |  QuizGen AI    |  |  CodeMentor AI |   |  StudyPlanner  |   |  Performance-  |
|  (Teaching)    |   |  (Assessment)  |  |  (Programming) |   |  (Scheduler)   |   |  Analyst AI    |
+--------+-------+   +--------+-------+  +--------+-------+   +--------+-------+   +--------+-------+
         |                    |                   |                    ^                    ^
         |                    |                   |                    |                    |
         |                    +--------+----------+                    |                    |
         |                             |                               |                    |
         |                             v (Test & Code Scores)          |                    |
         |                    +--------+-------+                       |                    |
         |                    | Shared Events  +-----------------------+--------------------+
         |                    |     Ledger     |  (Weak concepts: e.g. DBMS.Normalization)
         |                    +--------+-------+
         |                             |
         |                             v (High-priority remediation trigger)
         |                    +--------+-------+
         +------------------->|  Member 6      |
           (Course notes)     |  RevisionGPT   |
                              |  (Flashcards & |
                              |  SM-2 SRS)     |
                              +----------------+
```

---

## 👥 Division of the Six GenAI Projects

### 🧑‍🏫 Member 1 — TutorGPT (Your Project)
* **Role**: AI Teaching Agent
* **GenAI Focus**: LLMs, RAG (Retrieval-Augmented Generation), Prompt Engineering, Pedagogy
* **Core Capabilities**:
  - Explains complex academic concepts using structured scaffolds (analogy, formal definition, step-by-step mechanism, practical code/math example, misconceptions).
  - Supports 3 calibrated difficulty levels:
    - **Beginner**: Intuitive real-world analogies, plain English, visual mental models.
    - **Intermediate**: Standard university textbook rigor, formal definitions, time/space complexity.
    - **Advanced**: Mathematical specifications ($\mathcal{O}$ bounds, state machine transitions, invariants), distributed failure modes, production edge cases.
  - **RAG Engine**: Ingests textbooks and lecture notes, performs vector similarity search, and strictly grounds answers with verifiable citations (`[Source: filename, Chunk #id]`).
  - **Socratic Guidance**: Guides students through probing questions and progressive hints.

### 📝 Member 2 — QuizGen AI (Priyanka)
* **Role**: Assessment Agent
* **GenAI Focus**: Structured Generation, LLM-as-Judge Evaluation, Difficulty Calibration
* **Core Capabilities**:
  - Generates topic-wise MCQs and descriptive questions.
  - Grades descriptive answers against strict rubric key points.
  - Provides diagnostic explanations for student misconceptions on wrong answers.
  - Adapts test difficulty based on performance (Easy, Medium, Hard).

### 💻 Member 3 — CodeMentor AI (Kashish)
* **Role**: Programming Agent
* **GenAI Focus**: Code LLMs, Sandboxed Execution Tools, Code Evaluation
* **Core Capabilities**:
  - Explains programming code with line-by-line commentary and Big-O analysis.
  - Detects logical and syntax errors, with **sandboxed subprocess execution**.
  - Generates auto-gradable coding exercises with hidden test cases.
  - Reviews submitted code and scores readability, correctness, and efficiency.

### 📅 Member 4 — StudyPlanner AI (Diksha)
* **Role**: Planning Agent
* **GenAI Focus**: LLMs, Scheduling Algorithms, Contextual Memory
* **Core Capabilities**:
  - Creates personalized daily study schedules using an Earliest-Deadline-First heuristic.
  - Balances weekday and weekend availability and blocks out revision windows before exams.
  - **Dynamic Adaptation**: Rebuilds plans when PerformanceAnalyst reports weak concepts or when hours change.

### 📊 Member 5 — PerformanceAnalyst AI (Amit)
* **Role**: Analytics Agent
* **GenAI Focus**: Data Analysis, Machine Learning, LLM-Generated Insights
* **Core Capabilities**:
  - Ingests test and coding scores from the shared event ledger.
  - Detects weak subjects and concepts (<50% score).
  - Computes learning trajectories using **Scikit-Learn Linear Regression** trend slopes (Improving, Stable, Declining).
  - Emits rule-based priority alerts and feeds weak concept tags into StudyPlanner and RevisionGPT.

### 🔄 Member 6 — RevisionGPT (Your Project)
* **Role**: Revision Agent
* **GenAI Focus**: Summarization, Semantic Retrieval, SuperMemo SM-2 Spaced Repetition
* **Core Capabilities**:
  - **Flashcard Generation**: Extracts high-yield cards (Front, Back, Hint, Concept, Difficulty) from study materials or topic prompts.
  - **SuperMemo SM-2 Spaced Repetition (SRS)**:
    - Calculates retention intervals ($I$ in days), repetition counts ($n$), and easiness factor updates ($EF \ge 1.3$) based on user recall ratings (0–5).
    - Schedules daily due cards and tracks retention rates and workload forecasts.
  - **Targeted Remediation**: Ingests weak concepts from Member 5 and automatically generates high-priority remedial flashcards.
  - **Concise Revision Notes**: Synthesizes cheat sheets, formula tables, and 60-second exam crash-recaps.
  - **Hierarchical Summaries**: Generates 1-sentence TL;DR, Core Pillars, and Self-Test Checklists.

---

## 📂 Project Structure

```
CodeSync/
├── tutorgpt/                   # Member 1: AI Teaching Agent (TutorGPT)
│   ├── agent.py               # TutorGPT core agent (explain, RAG QA, Socratic)
│   ├── rag.py                 # RAG Engine (chunking, vector indexing, citations)
│   ├── prompts.py             # Beginner, Intermediate, Advanced, Socratic prompts
│   ├── models.py              # Pydantic schemas (DocumentChunk, Explanation, RAGResponse)
│   └── cli.py                 # Interactive Tutor CLI
│
├── revisiongpt/               # Member 6: Revision Agent (RevisionGPT)
│   ├── agent.py               # RevisionGPT core agent (flashcards, notes, summaries)
│   ├── srs.py                 # SuperMemo SM-2 Algorithm & DeckManager
│   ├── summarizer.py          # Revision notes & topic-wise summaries
│   ├── models.py              # Flashcard, ReviewLog, Deck, RevisionNote
│   ├── storage.py             # Persistent JSON deck storage
│   └── cli.py                 # Interactive Revision CLI
│
├── quizgen/                   # Member 2: Assessment Agent (Priyanka)
│   ├── quizgen.py             # Test generation, rubric evaluation, explanation
│   ├── schemas.py             # MCQ, DescriptiveQ, Test
│   └── llm.py                 # LLM wrapper
│
├── codementor/                # Member 3: Programming Agent (Kashish)
│   ├── agent.py               # Code explanation, debugging, exercises, review
│   ├── executor.py            # Sandboxed subprocess runner
│   ├── prompts.py             # Strict JSON coding prompts
│   └── config.py              # Runtime settings
│
├── studyplanner/              # Member 4: Planning Agent (Diksha)
│   ├── scheduler.py           # Deadline-aware greedy allocation algorithm
│   ├── models.py              # PlanRequest, Subject, Session, Plan
│   ├── memory.py              # SQLite contextual memory
│   └── llm.py                 # Natural language schedule explanation
│
├── performance_analyst/       # Member 5: Analytics Agent (Amit)
│   ├── analyst.py             # Performance analyst & Scikit-Learn regression
│   └── models.py              # Analysis data structures
│
├── shared/                    # Shared Ecosystem Infrastructure
│   ├── llm_provider.py        # Resilient LLM client (Anthropic, OpenAI, Offline fallback)
│   ├── event_bus.py           # Inter-agent event logging ledger
│   ├── sample_materials.py    # Authoritative notes for DBMS, OS, Algorithms
│   └── orchestrator.py        # Master 6-agent collaborative coordinator
│
├── data/                      # Persistent storage (events, decks, database)
├── tests/                     # Comprehensive test suite (Unit & Integration)
├── app.py                     # Master Streamlit Web Application
└── requirements.txt           # Ecosystem dependencies
```

---

## 🚀 Getting Started

### 1. Requirements
Ensure Python 3.10+ is installed. Install required packages:
```bash
cd CodeSync
pip install -r requirements.txt
```

### 2. Launch Next.js Modern Web Application (Recommended)
The primary student platform features the modern Coursera/Udemy-inspired web interface:
```bash
cd frontend
npm run dev:webpack
```
Open your browser at `http://localhost:3000`.
- **Quick Demo Access**: Click "Quick Demo as Asha Sharma" on the sign-in page to instantly explore without manual registration.
- **Student Reviews**: Real-time review and feedback system where students can share ratings and comments (no fake vanity stats).
- **Lecture Theater**: Multi-tab split view with video playback, grounded TutorGPT RAG, and SuperMemo SM-2 flashcard recall.
- **Code Lab**: Interactive coding IDE integrated with CodeMentor sandbox execution.

### 3. Launch Streamlit Standalone Python Dashboard
Alternatively, you can run the pure Python Streamlit multi-page interface:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 4. Run the Automated Test Suite
Verify that all unit and integration tests pass:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 🛠️ Command-Line Interface (CLI)

### Member 1: TutorGPT
```bash
# Explain concept at a specific difficulty level
python -m tutorgpt.cli explain "Dynamic Programming" --level beginner
python -m tutorgpt.cli explain "Two-Phase Locking" --level advanced

# Query study materials with grounded RAG
python -m tutorgpt.cli rag "What are the ACID properties?"
```

### Member 6: RevisionGPT
```bash
# Generate high-yield flashcards
python -m revisiongpt.cli flashcards "ACID Transactions" --count 3

# Start an interactive SM-2 spaced repetition review session
python -m revisiongpt.cli review

# Generate concise revision cheat sheets
python -m revisiongpt.cli notes "Deadlock Coffman Conditions"

# View spaced repetition retention statistics
python -m revisiongpt.cli stats
```

---

## 🔑 LLM API Configuration (Optional)

StudySync is engineered with an **Intelligent Offline Fallback Engine** that works with zero external API keys. To connect to frontier models, simply set your environment variables:
```bash
# For Anthropic Claude:
set ANTHROPIC_API_KEY=your_key_here

# Or for OpenAI GPT-4o:
set OPENAI_API_KEY=your_key_here
```
