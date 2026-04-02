# Videobot – Video Interactive Chat Assistant 🤖📹

An intelligent video-based conversational agent featuring a visual avatar that delivers guided assistance, tutorials, and service explanations. This system utilizes a multimodal interface combining speech, text, and visuals, powered by advanced Retrieval-Augmented Generation (RAG) for document-based knowledge retrieval.

## 🚀 Key Features

* **Multimodal Input:** Seamlessly accepts text and voice queries.
* **Real-time Avatar Lip-sync:** Generates animated avatar responses synchronized with synthesized speech.
* **RAG-Powered Knowledge Base:** Context-aware responses grounded in custom document and video transcript data.
* **Multilingual Transcription:** High-accuracy audio transcription using OpenAI's Whisper across different languages and noise conditions.
* **Interactive UI:** Split-screen interface featuring a video player with timestamps and an interactive chat window for contextual Q&A.

## 🏗️ System Architecture

The Videobot system integrates a modern frontend, high-performance API, vector database, and an avatar rendering engine:

* **Frontend:** React.js + Vite + Tailwind CSS
* **Backend:** FastAPI + Uvicorn (Asynchronous API management)
* **Speech-to-Text (STT):** OpenAI Whisper
* **Vector Database:** ChromaDB (for storing 768-dimensional document embeddings)
* **LLM Engine:** LLaMA 4 (via Groq Cloud) for zero-latency, context-grounded response generation

## 🧩 Core Modules

1. **Input Handling:** Captures user audio, video, and text queries via a responsive UI.
2. **Audio Transcription:** Processes video content and voice queries into text using Whisper ASR.
3. **ChromaDB Querying:** Manages document chunking, semantic embedding generation, similarity search, and retrieves contextual passages along with metadata (timestamps, source file).
4. **RAG Question Answering:** Converts the user query to embeddings, searches the vector space for the top-k relevant chunks, and passes this context to the LLM.
5. **Response Generation & Avatar Rendering:** Constructs precise LLM prompts, generates human-like responses via LLaMA 4, and formats the output for real-time avatar animation and lip-syncing.

## 🗄️ Database Schema

### Vector Storage (ChromaDB)
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `Id` | String | Unique identifier for the document chunk |
| `embedding` | Vector (768-dim) | Semantic embedding vector |
| `document` | Text | Original text content of the chunk |
| `metadata` | JSON | Source file, page number, chunk index, timestamps |

### Document Management (PostgreSQL/SQLite)
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `document_id` | INTEGER (PK) | Unique document identifier |
| `filename` | VARCHAR(255) | Original uploaded filename |
| `file_path` | TEXT | Storage location path |
| `upload_date` | DATETIME | Upload timestamp |
| `chunk_count` | INTEGER | Number of vector chunks created |
| `status` | ENUM | Processing status (`processing`, `indexed`, `failed`) |

## ⚙️ Core Algorithm (Chat Endpoint)

```javascript
const handleChat = async (prompt, video) => {
    console.log(`Incoming chat request — Prompt: ${prompt}`);
    
    // Infer most relevant video from all uploaded videos
    const videoList = getAllUploadedVideos();
    const inferredVideo = inferVideoName(prompt, videoList);
    
    // Query ChromaDB for relevant transcript chunks
    const context = queryChroma(inferredVideo, prompt);
    
    // Generate response using LLM with context
    const response = generateResponse(prompt, context, inferredVideo);
    
    return {
        answer: response,
        source: context
    };
};
