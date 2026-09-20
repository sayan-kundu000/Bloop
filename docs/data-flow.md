# Bloop — System Data Flow Specifications

**Document Identifier:** BLOOP-DATAFLOW-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level Architecture  
**Status:** Approved Technical Design  
**Authority:** Bloop Master Prompt & Prompt 02

---

## 1. Overview

This document specifies the end-to-end data flows and interaction sequence diagrams for all primary operations in Bloop. Each sequence diagram models the exact communication contracts between the User, React Frontend, FastAPI Router, Application Services, Repositories, Database, and External/Simulation Providers.

---

## 2. End-to-End Speech Synthesis Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Frontend (Workspace)
    participant Router as FastAPI Router (/api/v1/tts)
    participant Service as TTSService
    participant VoiceRepo as VoiceRepository
    participant Provider as ElevenLabsProvider / SimulationProvider
    participant Storage as Server Audio Storage
    participant GenRepo as SpeechGenerationRepository
    participant DB as PostgreSQL Database

    User->>Frontend: Types text, selects language & voice, clicks "Generate Speech"
    Frontend->>Frontend: Validates 1 <= chars <= 2500, verifies non-empty
    Frontend->>Router: POST /api/v1/tts (Bearer JWT, {text, language, voice_id})
    Router->>Router: Pydantic validates schema & length limits
    Router->>Service: synthesize_speech(user_id, request)
    Service->>VoiceRepo: get_voice(voice_id)
    VoiceRepo->>DB: SELECT * FROM voices WHERE voice_id = :id AND is_active = true
    DB-->>VoiceRepo: Voice Entity
    VoiceRepo-->>Service: Validated Voice Entity

    alt Language and Voice Mismatch
        Service-->>Router: Raise VoiceLanguageMismatchException
        Router-->>Frontend: HTTP 400 {"success": false, "error": {"code": "VOICE_LANGUAGE_MISMATCH"}}
    end

    alt ElevenLabs Configured (ELEVENLABS_API_KEY present)
        Service->>Provider: synthesize(text, voice_id, options)
        Provider->>Provider: POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
        Provider-->>Service: Binary MP3 Audio Bytes
    else Simulation Mode (No API key)
        Service->>Provider: synthesize_simulated(text, voice_id)
        Provider-->>Service: Synthetic Audio Waveform Bytes
    end

    Service->>Storage: write_audio_file(audio_bytes)
    Storage-->>Service: filename (bloop-{uuid4}.mp3)
    Service->>GenRepo: record_generation(user_id, text, voice_id, duration, filename)
    GenRepo->>DB: INSERT INTO speech_generations (...) VALUES (...)
    DB-->>GenRepo: Generation Record (id=42)
    GenRepo-->>Service: Persisted Generation Object
    Service-->>Router: TTSResponse (id, audio_url, download_url, metrics)
    Router-->>Frontend: HTTP 200 {"success": true, "data": { ... }}
    Frontend->>Frontend: Load audio into AudioPlayerBar, unlock playback
    Frontend-->>User: Audio ready for playback & download
```

---

## 3. User Authentication & JWT Authorization Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Frontend
    participant AuthRouter as FastAPI Router (/api/v1/auth)
    participant AuthService as AuthService
    participant UserRepo as UserRepository
    participant DB as PostgreSQL Database

    User->>Frontend: Submits registration (email, password)
    Frontend->>AuthRouter: POST /api/v1/auth/register {email, password}
    AuthRouter->>AuthService: register_user(email, password)
    AuthService->>UserRepo: get_by_email(email)
    UserRepo->>DB: SELECT * FROM users WHERE email = :email
    DB-->>UserRepo: None
    AuthService->>AuthService: bcrypt.hash(password, salt)
    AuthService->>UserRepo: create_user(email, hashed_password)
    UserRepo->>DB: INSERT INTO users ... RETURNING id
    DB-->>UserRepo: User Record
    AuthService->>AuthService: generate_jwt_token(user_id)
    AuthService-->>AuthRouter: TokenResponse {access_token, token_type: "bearer", user}
    AuthRouter-->>Frontend: HTTP 200 {"success": true, "data": { ... }}
    Frontend->>Frontend: Store token in localStorage & update Zustand authStore

    Note over Frontend,AuthRouter: Subsequent Protected API Requests
    Frontend->>AuthRouter: GET /api/v1/history (Header: Authorization: Bearer <token>)
    AuthRouter->>AuthRouter: Verify HMAC-SHA256 signature & expiration
    AuthRouter->>AuthRouter: Extract user_id from token 'sub' claim
    AuthRouter->>AuthRouter: Inject current_user dependency into route handler
```

---

## 4. Dynamic Voice Ingestion & Discovery Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User / Operator
    participant Frontend as React Frontend
    participant VoiceRouter as FastAPI Router (/api/v1/voices)
    participant VoiceService as VoiceService
    participant Config as voices_config.json
    participant VoiceRepo as VoiceRepository
    participant DB as PostgreSQL Database

    Note over User,DB: Flow 1: Dynamic Discovery by Language Locale
    Frontend->>VoiceRouter: GET /api/v1/voices?language_code=en-US
    VoiceRouter->>VoiceService: get_active_voices(language_code="en-US")
    VoiceService->>VoiceRepo: find_by_language("en-US")
    VoiceRepo->>DB: SELECT * FROM voices WHERE language_code = 'en-US' AND is_active = true
    DB-->>VoiceRepo: List[Voice]
    VoiceRepo-->>VoiceService: Active Voice Records
    VoiceService-->>VoiceRouter: List[VoiceResponse]
    VoiceRouter-->>Frontend: HTTP 200 {"success": true, "data": [ ... ]}
    Frontend->>Frontend: Populate voice dropdown dynamically

    Note over User,DB: Flow 2: Custom Voice Injection via UI Modal
    User->>Frontend: Enters ElevenLabs Voice ID & Name in "Inject Voice" modal
    Frontend->>VoiceRouter: POST /api/v1/voices {voice_id, name, language_code, gender}
    VoiceRouter->>VoiceService: register_custom_voice(data)
    VoiceService->>VoiceRepo: upsert_voice(data)
    VoiceRepo->>DB: INSERT INTO voices (...) ON CONFLICT (voice_id) DO UPDATE ...
    DB-->>VoiceRepo: Persisted Voice
    VoiceRepo-->>VoiceService: Voice Entity
    VoiceService-->>VoiceRouter: Success Response
    VoiceRouter-->>Frontend: HTTP 201 {"success": true, "data": Voice}
    Frontend->>Frontend: Add custom voice to dropdown and auto-select

    Note over User,DB: Flow 3: Config File Ingestion
    Operator->>Config: Edits backend/voices_config.json
    Operator->>VoiceRouter: POST /api/v1/voices/reload-config
    VoiceRouter->>VoiceService: import_voices_from_config()
    VoiceService->>Config: Read JSON definitions
    VoiceService->>VoiceRepo: Batch upsert voices into DB
    VoiceService-->>VoiceRouter: Reload summary {loaded: 4, updated: 1}
    VoiceRouter-->>Operator: HTTP 200 {"success": true, "message": "Voices reloaded"}
```

---

## 5. Audio Streaming & HTTP 206 Partial Content Range Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser as Browser Audio Element (<audio>)
    participant Router as FastAPI Router (/api/v1/tts/audio/{filename})
    participant Storage as File Storage (backend/app/storage/audio/)

    User->>Browser: Drags scrub bar to 45 seconds
    Browser->>Router: GET /api/v1/tts/audio/bloop-42.mp3 (Header: Range: bytes=1048576-)
    Router->>Storage: Verify file exists and compute total file_size
    Storage-->>Router: file_size = 3,145,728 bytes
    Router->>Router: Parse Range header: start=1048576, end=3145727
    Router->>Storage: Seek stream to byte offset 1,048,576
    Storage-->>Router: Byte chunk stream
    Router-->>Browser: HTTP 206 Partial Content
    Note over Router,Browser: Headers: <br/>Content-Range: bytes 1048576-3145727/3145728<br/>Content-Length: 2097152<br/>Content-Type: audio/mpeg
    Browser->>Browser: Resumes playback seamlessly from 45s without buffering whole file
```

---

## 6. History, Search, Filter & Bookmarking Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Frontend (History Page)
    participant Router as FastAPI Router
    participant Service as History / Favorite Service
    participant DB as PostgreSQL Database

    User->>Frontend: Types "quantum" in search bar, selects language "en-US"
    Frontend->>Frontend: Debounce 300ms
    Frontend->>Router: GET /api/v1/history?search=quantum&language=en-US&page=1&page_size=10
    Router->>Service: get_user_history(user_id, search, language, page, page_size)
    Service->>DB: SELECT * FROM speech_generations <br/>WHERE user_id = :user_id <br/>AND text ILIKE '%quantum%' <br/>AND language_code = 'en-US' <br/>ORDER BY created_at DESC LIMIT 10 OFFSET 0
    DB-->>Service: Rows + Total Count
    Service-->>Router: PaginatedResponse {items: [...], total: 14, page: 1, has_next: true}
    Router-->>Frontend: HTTP 200 {"success": true, "data": { ... }}
    Frontend->>Frontend: Renders 10 generation cards with search highlights

    Note over User,DB: Bookmarking a Generation as Favorite
    User->>Frontend: Clicks Bookmark Heart on Generation #42
    Frontend->>Router: POST /api/v1/favorites {generation_id: 42}
    Router->>Service: toggle_favorite(user_id, generation_id=42)
    Service->>DB: INSERT INTO favorites (user_id, generation_id) VALUES (:user_id, 42)
    DB-->>Service: OK
    Service-->>Router: FavoriteEntity
    Router-->>Frontend: HTTP 201 {"success": true, "data": {"favorited": true}}
    Frontend->>Frontend: Heart icon animates to active filled state
```

---

## 7. Quantum Text Classification (VQC) Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Frontend (Quantum Lab)
    participant Router as FastAPI Router (/api/v1/quantum/text)
    participant Service as QuantumService
    participant FeatureExtractor as FeatureExtractor
    participant VQC as TextClassifierVQC
    participant Simulator as Qiskit Aer (AerSimulator)
    participant Baseline as ClassicalBaseline (TF-IDF + Heuristic)

    User->>Frontend: Enters text and clicks "Run Quantum Text Classifier"
    Frontend->>Router: POST /api/v1/quantum/text {text: "..."}
    Router->>Service: classify_text_quantum(text)
    Service->>FeatureExtractor: extract_features(text)
    FeatureExtractor-->>Service: normalized_features in [0, pi]^4
    
    par Quantum Circuit Execution
        Service->>VQC: build_and_execute(features)
        VQC->>VQC: Construct Ry(theta_i) angle encoding + CNOT ansatz
        VQC->>Simulator: run(circuit, shots=1024)
        Simulator-->>VQC: Measurement counts
        VQC-->>Service: Style Probabilities {Technical: 0.85, Formal: 0.10, ...}
    and Classical Baseline Execution
        Service->>Baseline: evaluate_baseline(text)
        Baseline-->>Service: Baseline Style Probabilities & Confidence
    end

    Service->>Service: Aggregate comparative report & record execution
    Service-->>Router: QuantumTextResponse {quantum_results, classical_baseline, execution_time_ms}
    Router-->>Frontend: HTTP 200 {"success": true, "data": { ... }}
    Frontend->>Frontend: Render Bloch state preview, probability bars, and comparative metrics
```

---

## 8. Quantum Emotion QNN & Speech Tuning Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Frontend
    participant Router as FastAPI Router (/api/v1/quantum/emotion)
    participant Service as QuantumService
    participant QNN as EmotionQNN (PennyLane)
    participant Entropy as EntropyCalculator

    User->>Frontend: Enters script line and clicks "Analyze Emotion"
    Frontend->>Router: POST /api/v1/quantum/emotion {text: "..."}
    Router->>Service: analyze_emotion_quantum(text)
    Service->>QNN: evaluate_circuit(features)
    QNN->>QNN: Run 4-wire variational circuit on default.qubit
    QNN->>QNN: Measure Pauli-Z expectations <Z_0>, <Z_1>, <Z_2>, <Z_3>
    QNN-->>Service: Expectation Values (Joy, Sadness, Anger, Neutral)
    Service->>Entropy: compute_shannon_entropy(probabilities)
    Entropy-->>Service: Entanglement Entropy H = 1.42 bits
    Service->>Service: Derive voice parameters: pitch_mod = +12%, speed_mod = 1.1x
    Service-->>Router: QuantumEmotionResponse {emotions, entropy, voice_tuning_recommendation}
    Router-->>Frontend: HTTP 200 {"success": true, "data": { ... }}
    Frontend->>Frontend: Displays emotion radar chart & "Apply Recommended Tuning" button
    User->>Frontend: Clicks "Apply Tuning" -> Workspace loads recommended pitch and speed
```

---

## 9. Classical vs. Quantum Empirical Benchmark Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Frontend (Benchmark Tab)
    participant Router as FastAPI Router (/api/v1/quantum/benchmark)
    participant Service as QuantumService
    participant Benchmarker as BenchmarkRunner
    participant ClassicalModel as Scikit-Learn Logistic Regression
    participant QuantumModel as Qiskit VQC Model

    User->>Frontend: Selects benchmark dataset & clicks "Run Benchmark"
    Frontend->>Router: POST /api/v1/quantum/benchmark {dataset_id: "sentiment-standard", shots: 1024}
    Router->>Service: run_benchmark(dataset_id, shots)
    Service->>Benchmarker: execute_comparative_benchmark(dataset)

    Note over Benchmarker,ClassicalModel: Step 1: Classical Baseline Training
    Benchmarker->>ClassicalModel: fit(X_train, y_train) & evaluate(X_test, y_test)
    ClassicalModel-->>Benchmarker: Accuracy: 91.2%, F1: 0.90, Runtime: 14ms

    Note over Benchmarker,QuantumModel: Step 2: Quantum VQC Training on Aer
    Benchmarker->>QuantumModel: fit(X_train, y_train) & evaluate(X_test, y_test)
    QuantumModel-->>Benchmarker: Accuracy: 86.5%, F1: 0.85, Runtime: 1,380ms

    Benchmarker->>Benchmarker: Compile objective comparative report (no supremacy claims)
    Benchmarker-->>Service: BenchmarkReport
    Service-->>Router: BenchmarkResponse
    Router-->>Frontend: HTTP 200 {"success": true, "data": { ... }}
    Frontend->>Frontend: Render side-by-side metric cards, latency comparison, and scientific summary
```
