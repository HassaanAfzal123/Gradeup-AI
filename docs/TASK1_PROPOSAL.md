# Task-1 Project Proposal

## Project Title
**Personalized RAG-Based AI Tutoring Platform with Quiz Generation and Weakness Analytics**

**Suggested Topic Category:** Text & LLM Projects  
**Closest Suggested Topics:** RAG-based chatbot, automatic question generation from textbooks/lecture notes, document summarization, and personalized tutoring support through performance analytics.

## Abstract
This project proposes a personalized AI tutoring platform for educational PDFs. The system combines Retrieval-Augmented Generation (RAG), quiz generation, answer evaluation, and learner analytics to support more effective self-study from course material. Instead of acting as only a document chatbot or a simple PDF-to-quiz generator, the platform is designed around a learner-centered workflow: students upload study documents, ask questions grounded in those documents, take AI-generated quizzes, and receive analytics about weak concepts based on their performance. The current implementation already includes document upload and indexing, RAG-based chat, quiz generation and grading, weakness extraction, and a progress dashboard. For Task-2, the system will be extended into a stronger adaptive tutoring loop by using stored weakness information to influence future quizzes and recommendations. This makes the project suitable as a Generative AI course project under the Text & LLM domain while also providing a clear research direction in educational RAG and personalized learning support \cite{nye2023dialog,levonian2023ragmath,han2024tutoringrag,kurulkar2025quizrag,li2025tutorllm,reddig2025feedback,naseer2025adaptive,swacha2025survey}.

## 1. Introduction and Motivation
Students often prepare for exams from lengthy PDFs, lecture notes, and other unstructured study materials. Traditional revision is slow because students must manually search for important concepts, identify weak areas on their own, and create practice questions separately. Recent progress in large language models (LLMs) and Retrieval-Augmented Generation (RAG) offers a practical way to build systems that answer questions from course material while remaining grounded in retrieved document context rather than relying only on model memory \cite{levonian2023ragmath,han2024tutoringrag,swacha2025survey}.

However, many educational RAG systems remain document-centric: the system answers questions or generates quizzes from uploaded content, but it does not maintain enough learner context to support personalized improvement over time. Similarly, quiz-generation systems may create relevant questions from educational text, yet they often stop at content generation rather than building a feedback loop around student performance \cite{bhowmick2023qg,kurulkar2025quizrag}. This project addresses that gap by combining document-grounded tutoring with weakness-focused learning analytics.

## 2. Problem Statement
Most student-facing AI study tools fall into one of two categories:

1. document-based question answering systems, or
2. automated quiz generators.

Both are useful, but they are limited if they do not analyze how the learner is performing. A student may receive correct answers and take quizzes, yet still not know which concepts need revision most urgently. The core problem addressed in this project is therefore:

**How can a generative AI system support PDF-based learning while also tracking student performance and highlighting weak concepts to enable more personalized revision?**

## 3. Proposed Solution
The proposed system is a web-based AI tutoring platform in which each user uploads one or more educational PDFs and interacts with them through a grounded chat and quiz workflow.

### Main functions
1. **User authentication** for multi-user access and separation of study data.
2. **PDF upload and indexing** so learning material can be stored, chunked, embedded, and retrieved.
3. **RAG-based chat** to answer questions using context retrieved from the uploaded PDF.
4. **AI-generated quizzes** from the selected document and topic.
5. **Quiz grading and weakness extraction** to identify concepts the learner struggles with.
6. **Progress analytics dashboard** to present statistics such as quiz activity, performance, and weak concepts.

At the implementation level, the current platform uses a `FastAPI` backend, a `React` frontend, a vector-store-based retrieval pipeline, embeddings, and an LLM-based generation layer. The backend already contains dedicated routes for authentication, PDFs, chat, quizzes, and analytics, while the frontend already provides dashboard, PDF library, chat, quiz, and analytics pages. This confirms that the project has already crossed the initial prototype stage and meaningfully satisfies the Task-1 requirement of completing a significant portion of the work.

## 4. Current Implementation Status for Task-1
The project is already more than a proposal; a substantial end-to-end prototype exists in the repository.

### Implemented backend capabilities
- Application entry point and API routing in `backend/main.py`
- PDF upload and management in `backend/routers/pdf.py`
- RAG pipeline and vector retrieval in `backend/services/rag_service.py`
- Chat answering flow in `backend/routers/chat.py`
- Quiz generation and submission in `backend/routers/quiz.py`
- Weakness and progress analytics in `backend/routers/analytics.py`
- SQL models for users, PDFs, quizzes, chats, and weaknesses in `backend/database/models.py`

### Implemented frontend capabilities
- Route-level application flow in `frontend/src/App.jsx`
- API integration in `frontend/src/api/client.js`
- Dashboard in `frontend/src/pages/Dashboard.jsx`
- PDF library in `frontend/src/pages/PDFLibrary.jsx`
- Chat interface in `frontend/src/pages/ChatPage.jsx`
- Quiz interface in `frontend/src/pages/QuizPage.jsx`
- Analytics dashboard in `frontend/src/pages/AnalyticsPage.jsx`

### Why this is already 50%+ complete
The core product workflow is already present:

`PDF upload -> indexing -> question answering / quiz generation -> grading -> weakness tracking -> analytics`

This means Task-1 can be defended as a working prototype with major functionality already implemented. What remains for Task-2 is not the basic system itself, but the stronger personalization layer that uses prior weaknesses to directly adapt future tutoring interactions.

## 5. Novelty and Differentiation
The key differentiator of this project is its **weakness-centric positioning**.

A simpler educational GenAI project might allow a student to upload a PDF and then generate quizzes from it. That use case is valid, but it remains largely content-centric. In contrast, this project is framed as a **personalized tutoring support system**: it not only retrieves answers and generates quizzes from study material, but also evaluates learner responses, extracts weak concepts, and presents progress analytics. This makes the system closer to an educational feedback loop than a one-shot quiz generator.

It is important to state the novelty honestly:
- The project **does use RAG**.
- The project **does support quiz generation and learner analytics**.
- The project **does not currently implement a true multi-agent architecture**.
- The project **does not yet fully adapt future tutoring behavior from stored weaknesses**, although the current design already lays the foundation for that extension.

Because of this, the correct research positioning for Task-1 is:

**a personalized RAG-based AI tutor for educational PDFs with quiz generation, grading, and weakness analytics**

and not:

**a multi-agent tutoring system**

unless a true multi-agent design is implemented later.

## 6. Research Direction and Literature Support
The proposal is supported by recent literature in four connected areas:

1. **Educational RAG and grounded tutoring** \cite{nye2023dialog,levonian2023ragmath,han2024tutoringrag,swacha2025survey}
2. **Question and quiz generation from educational content** \cite{bhowmick2023qg,kurulkar2025quizrag}
3. **Personalized feedback in intelligent tutoring systems** \cite{reddig2025feedback,levonian2025safechat}
4. **Adaptive learning analytics and personalized recommendations** \cite{li2025tutorllm,naseer2025adaptive}

These papers justify the project as academically relevant in Generative AI, especially because they show that educational systems increasingly need grounding, safety, feedback quality, and personalization rather than raw generation alone.

## 7. Task-1 vs Task-2 Scope Boundary
To keep the proposal accurate, the following boundary should be used in documentation and demo discussions.

### Task-1: already implemented or directly demonstrable
- user registration and login
- PDF upload and indexing
- document-grounded chat
- quiz generation from uploaded content
- answer submission and grading
- weak-concept extraction
- analytics and progress display

### Task-2: planned extension to complete the personalized tutoring vision
- concept mastery profile per learner
- adaptive quiz generation weighted toward weak concepts
- personalized recommendations for what to revise next
- stronger use of learner history to shape future tutoring interactions
- comparative evaluation of generic quiz generation vs weakness-aware adaptive tutoring

This distinction is important because it lets the project remain truthful for Task-1 while still presenting a strong and research-worthy completion path for Task-2.

## 8. Expected Contribution
The expected contribution of the final project is a practical, research-backed educational AI system that connects:

- RAG-based understanding of student documents,
- generative quiz support,
- learner performance analysis,
- and a pathway toward adaptive tutoring.

In short, the final contribution is not merely a chatbot and not merely a quiz generator. It is a **learner-centered RAG tutoring platform** that uses generative AI to support both understanding and revision.

## 9. Proposed Evaluation Direction for the Final Paper
To satisfy the course expectation of research contribution or comparative analysis, the final paper can compare:

1. **baseline RAG tutoring / generic quiz generation**, and
2. **weakness-aware personalized tutoring**

Possible evaluation angles:
- quality and relevance of generated quiz questions
- grounding and correctness of chat answers
- usefulness of detected weak concepts
- improvement in follow-up quiz performance
- user perception of helpfulness and personalization

This gives the final paper a clear comparative angle rather than only a system description.

## 10. References
Use the bibliography file `docs/TASK1_REFERENCES.bib` in Overleaf and cite these entries from the proposal and final paper:

- `nye2023dialog`
- `levonian2023ragmath`
- `han2024tutoringrag`
- `bhowmick2023qg`
- `kurulkar2025quizrag`
- `levonian2025safechat`
- `li2025tutorllm`
- `reddig2025feedback`
- `naseer2025adaptive`
- `swacha2025survey`
