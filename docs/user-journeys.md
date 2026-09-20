# Bloop — User Journeys & Interaction Specifications

**Document Identifier:** BLOOP-JOURNEYS-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level MVP  
**Status:** Approved Specification  
**Authority:** Bloop Master Prompt & Prompt 01

---

## 1. Overview

This document specifies the end-to-end user journeys for Bloop. Each journey details the user intent, trigger, frontend state transitions, backend operations, validation boundaries, and expected system postconditions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MAP OF CORE USER JOURNEYS                          │
├────────────────────────────────┬────────────────────────────────────────────┤
│ Onboarding & Authentication    │ Journeys A, B, C                           │
│ Core Speech Synthesis Pipeline │ Journeys D, E, F, G, H, I                  │
│ User Platform & Persistence    │ Journeys J, K, L                           │
│ Quantum Intelligence Lab       │ Journeys M, N, O, P, Q                     │
└────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 2. Onboarding & Authentication Journeys

### Journey A: First Visit & Application Entry
```
Open Bloop Web App ──► Landing / Workspace ──► Feature Overview ──► Explore TTS
```
1. **Precondition:** User accesses Bloop's base URL (`https://bloop.app` or `http://localhost:3000`).
2. **Action:** The browser loads the single-page application. The landing page showcases product capabilities: ElevenLabs speech synthesis and the Quantum Intelligence Laboratory.
3. **Frontend Reaction:** Client checks for existing JWT token in `localStorage`. If absent, renders public workspace navigation with prominent "Sign In" and "Register" call-to-actions.
4. **Postcondition:** User understands Bloop's core features and can immediately transition to authentication or explore workspace components.

---

### Journey B: User Registration
```
Register View ──► Enter Email & Password ──► Client Validation ──► POST /auth/register ──► Auto-Login ──► Dashboard
```
1. **Precondition:** User is unauthenticated and navigates to `/register`.
2. **Action:** User submits email (`user@example.com`), password ($\ge 8$ characters), and optional full name.
3. **Frontend Processing:** Verifies password length, complexity, and email format. If invalid, displays inline error without submitting.
4. **Backend Processing:**
   * Receives `POST /api/v1/auth/register`.
   * Pydantic schema validates email syntax and password length.
   * Repository checks if email already exists in `users` table. If exists, returns HTTP 409 `EMAIL_ALREADY_EXISTS`.
   * Generates cryptographic salt and hashes password via `passlib.context.CryptContext(schemes=["bcrypt"])`.
   * Creates user record and default `user_preferences` row.
   * Signs and returns JWT access token.
5. **Postcondition:** User account created, token stored in browser, session established, redirected to `/workspace`.

---

### Journey C: User Authentication (Login)
```
Login View ──► Enter Credentials ──► POST /auth/login ──► JWT Issued ──► Dashboard
```
1. **Precondition:** Existing registered user arrives at `/login`.
2. **Action:** Submits email and password.
3. **Backend Processing:**
   * Queries user by email.
   * Compares plain password with stored bcrypt hash. If invalid, returns HTTP 401 `INVALID_CREDENTIALS`.
   * Generates JWT with payload: `{"sub": user.id, "email": user.email, "exp": ...}`.
4. **Frontend Reaction:**
   * `authStore` updates with user profile and token.
   * Global Axios interceptor attaches `Authorization: Bearer <token>` to all subsequent requests.
   * Redirects user to their previous requested path or `/workspace`.

---

## 3. Core Text-to-Speech Synthesis Journeys

### Journey D: Standard Speech Generation (Happy Path)
```
Workspace ──► Enter Text ──► Select Language ──► Select Voice ──► Generate Speech
                                                                      │
Player Updates ◄── Return Audio URL & Metadata ◄── ElevenLabs ◄───────┘
```
1. **User Action:**
   * User navigates to `/workspace`.
   * Types or pastes text: *"Quantum computing represents a paradigm shift in computation."*
   * Character counter shows `72 / 2500`; word counter shows `9 words`.
   * Selects Language: `en-US`.
   * Dynamic voice selector loads voices compatible with `en-US`. User selects an active voice.
   * Clicks **"Generate Speech"**.
2. **Frontend State:**
   * Generation button transitions to loading spinner (`"Synthesizing speech..."`).
   * Disables text area modifications during active synthesis.
   * Dispatches `POST /api/v1/tts` with payload: `{"text": "...", "language": "en-US", "voice_id": "..."}`.
3. **Backend Execution:**
   * Validates payload using `TTSRequest` Pydantic model.
   * Confirms `voice_id` exists and is active.
   * `TTSService` invokes `ElevenLabsProvider` with server-side `ELEVENLABS_API_KEY`.
   * Receives MPEG-3 binary audio stream.
   * Writes audio stream to persistent storage (`backend/app/storage/audio/`).
   * Saves generation record in `speech_generations` with foreign key `user_id`.
   * Responds with HTTP 200:
     ```json
     {
       "success": true,
       "data": {
         "id": 42,
         "audio_url": "/api/v1/tts/audio/bloop-gen-42.mp3",
         "download_url": "/api/v1/tts/download/bloop-gen-42.mp3",
         "duration_seconds": 4.5,
         "character_count": 72,
         "word_count": 9
       },
       "message": "Speech generated successfully"
     }
     ```
4. **Frontend Reaction:**
   * Audio player bar appears / unlocks at the bottom of the screen.
   * Auto-loads audio stream; user can immediately play, scrub, or download.
   * History list in background invalidates cache and displays new generation at top.

---

### Journey E: Empty Text Validation Guard
```
Empty Input ──► Click Generate ──► Client Rejection ──► Block External Request
```
1. **User Action:** Textarea contains only spaces or is empty. User clicks **"Generate Speech"**.
2. **Frontend Processing:** Detects `text.trim().length === 0`.
3. **Visual Feedback:** Shows warning message: *"Please enter text before generating speech."*
4. **Backend Guard (Defense in Depth):** If request bypassed client, FastAPI Pydantic validator raises `ValueError("Text cannot be empty or whitespace only")`, returning HTTP 422 with code `EMPTY_TEXT`.
5. **Postcondition:** Zero calls to ElevenLabs API; zero quota wasted.

---

### Journey F: Maximum Text Limit Exceeded
```
Enter >2,500 Chars ──► Counter Reaches Max ──► Submit Disabled ──► Authoritative Rejection
```
1. **User Action:** User pastes a long document exceeding 2,500 characters (e.g. 3,100 characters).
2. **Frontend Processing:**
   * Counter displays `3,100 / 2,500` with crimson alert badge.
   * Generate button is automatically disabled (`disabled={charCount > 2500}`).
   * Displays message: *"Text exceeds the maximum allowed limit of 2,500 characters."*
3. **Backend Guard:** If an API client attempts `POST /api/v1/tts` with $>2500$ characters, backend validator rejects with HTTP 422 `TEXT_TOO_LONG` and details: `{"excess_characters": 600}`.

---

### Journey G: Invalid Voice or Language Mismatch
```
Request ──► Backend Validation ──► Incompatible Pair ──► Reject ──► Structured JSON Error
```
1. **Precondition:** Malformed or outdated request with mismatched voice and language (e.g., German voice requested under `fr-FR`).
2. **Backend Processing:**
   * Queries voice entity in database.
   * Detects `voice.language_code != request.language`.
   * Rejects execution before calling ElevenLabs.
   * Returns HTTP 400 with code `VOICE_LANGUAGE_MISMATCH`.
3. **Frontend Reaction:** Displays warning modal instructing user to select an active voice matching their chosen language.

---

### Journey H: External TTS Provider Failure
```
Generate ──► Backend ──► ElevenLabs Outage (500/503) ──► Translate Error ──► Safe Alert
```
1. **Trigger:** ElevenLabs API returns 500, network socket drops, or API quota is exhausted.
2. **Backend Handling:**
   * `ElevenLabsProvider` catches `httpx.HTTPError` or provider status $\ge 400$.
   * Intercepts raw error to prevent leaking API keys or internal infrastructure URLs.
   * Returns HTTP 502 with structured error envelope:
     ```json
     {
       "success": false,
       "error": {
         "code": "PROVIDER_ERROR",
         "message": "Speech provider is currently unavailable. Please try again shortly."
       }
     }
     ```
3. **Frontend Reaction:**
   * Hides loading spinner.
   * Displays persistent toast notification with a **"Retry"** button.

---

### Journey I: Audio Playback, Seeking, Volume & Download
```
Player Bar ──► Play/Pause ──► Scrub Timeline ──► Volume/Rate ──► Download File
```
1. **Playback:** User clicks Play; audio element starts playback of `/api/v1/tts/audio/{filename}`.
2. **Seeking:** User drags seek scrubber to 50% timestamp. Browser sends HTTP `GET` with `Range: bytes=1048576-`. Backend handles partial content and returns HTTP 206 with correct `Content-Range`. Audio immediately resumes at scrub point without re-downloading the entire stream.
3. **Speed & Volume:** User selects 1.25x speed; audio element adjusts `playbackRate = 1.25`. User drags volume slider; updates `volume` property.
4. **Download:** User clicks **"Download Audio"**. Browser triggers download from `/api/v1/tts/download/{filename}`, downloading `bloop-speech-42.mp3` directly to the user's filesystem.

---

## 4. User Platform & History Journeys

### Journey J: Speech Generation History & Pagination
```
History Page ──► GET /history?page=1 ──► Render Generation Cards ──► Page 2
```
1. **User Action:** Navigates to `/history`.
2. **Backend Processing:**
   * Executes query: `SELECT * FROM speech_generations WHERE user_id = :current_user ORDER BY created_at DESC LIMIT 10 OFFSET 0`.
   * Returns paginated JSON envelope with generation records and pagination metadata (`total`, `page`, `page_size`, `has_next`).
3. **Frontend Rendering:** Renders generation cards showing text snippet, voice name, language badge, duration, and playback button.
4. **Pagination:** Clicking "Next Page" requests `page=2` and seamlessly swaps cards.

---

### Journey K: Favoriting & Bookmark Management
```
Generation Card ──► Click Heart Icon ──► POST /favorites ──► Synced Across Views
```
1. **User Action:** User clicks the bookmark/heart icon on a generation in the history or workspace.
2. **Backend Processing:**
   * `POST /api/v1/favorites` creates a row linking `user_id` and `generation_id`.
   * Duplicate bookmark requests are handled idempotently.
3. **Frontend Update:** Heart icon fills red with a micro-animation. Navigating to `/favorites` displays all bookmarked generations. Clicking the filled heart sends `DELETE /api/v1/favorites/{id}` to un-bookmark.

---

### Journey L: Multi-Parametric Search, Filtering & Sorting
```
History View ──► Type "quantum" ──► Filter: French ──► Sort: Oldest First ──► Dynamic Update
```
1. **User Action:** User enters search text *"quantum"* in the history search bar, sets Language filter to `fr-FR`, and changes Sort to "Oldest First".
2. **Frontend Processing:** Debounces search input (300ms) to avoid excessive queries.
3. **Backend Processing:**
   * Receives `GET /api/v1/history?search=quantum&language=fr-FR&sort=asc`.
   * SQL query builds compound filters:
     `WHERE user_id = :user_id AND text ILIKE '%quantum%' AND language_code = 'fr-FR' ORDER BY created_at ASC`.
4. **Frontend Reaction:** Results refresh instantly showing only matching filtered entries.

---

## 5. Quantum Intelligence Journeys

### Journey M: Quantum Text Intelligence (VQC Classifier)
```
Quantum Lab ──► Enter Text ──► Hilbert Angle Projection ──► VQC Ansatz ──► Style Prediction
```
1. **User Action:** Navigates to `/quantum` and selects **"Text Intelligence"**.
2. **Action:** Enters text: *"The theorem proves asymptotic convergence under bounded variance."*
3. **Backend Processing:**
   * Extracts lexical features: character length, word count, lexical diversity, vowel ratio.
   * Maps features into 4 qubit rotation angles $\theta_i \in [0, \pi]$.
   * Builds Qiskit circuit with $R_y(\theta_i)$ encoding and two-qubit CNOT entanglers.
   * Executes 1,024 shots on `AerSimulator`.
   * Measurement distribution determines classification probabilities: Technical (88%), Formal (9%), Creative (2%), Casual (1%).
   * Runs classical TF-IDF baseline for empirical comparison.
4. **Frontend Output:** Displays qubit state vector sphere visualization, bar chart of style probabilities, and comparative classical baseline table.

---

### Journey N: Quantum Emotion Analysis & Voice Recommendation
```
Text Input ──► PennyLane Hybrid QNN ──► Pauli-Z Expectations ──► Shannon Entropy ──► Voice Tuning
```
1. **User Action:** Selects **"Emotion Intelligence"** and inputs dialogue text: *"I cannot believe we finally achieved this breakthrough!"*
2. **Backend Processing:**
   * Evaluates emotional polarity features.
   * Ingests features into a PennyLane 4-wire variational circuit.
   * Measures Pauli-Z expectation values $\langle Z_i \rangle$ representing affective states: Joy, Sadness, Anger, Neutral.
   * Computes state Shannon entanglement entropy: $H = -\sum p_i \log_2(p_i)$.
   * Deterministically generates explainable speech parameter recommendation: Pitch variance $+15\%$, Speed $1.15\text{x}$.
3. **Frontend Output:** Visualizes emotion distribution spider chart, entropy gauge, and one-click button: *"Apply Recommended Speech Tuning to Workspace"*.

---

### Journey O: Quantum Semantic Similarity Kernel
```
Prompt A + Prompt B ──► Quantum Feature Maps ──► Inversion Circuit ──► Kernel State Fidelity
```
1. **User Action:** Selects **"Semantic Similarity"** and provides:
   * Prompt A: *"Exploring the depths of quantum computing."*
   * Prompt B: *"Investigating quantum circuit mechanics."*
2. **Backend Processing:**
   * Maps both texts to Hilbert space states $|\phi(A)\rangle$ and $|\psi(B)\rangle$.
   * Constructs state inversion circuit: $U^\dagger(B) U(A) |0\rangle$.
   * Simulates circuit on Qiskit Aer. The probability of measuring the all-zero ground state $|0000\rangle$ represents quantum transition fidelity $|⟨\phi(A)|\psi(B)⟩|^2$.
   * Computes classical cosine similarity for baseline comparison.
3. **Frontend Output:** Displays fidelity score (e.g. 0.842), classical similarity (e.g. 0.791), and state overlap explanation.

---

### Journey P: Quantum Circuit Laboratory & Noise Sandbox
```
Select Qubits ──► Add H/CNOT Gates ──► Enable Decoherence Noise ──► Aer Simulation ──► QASM
```
1. **User Action:** Selects **"Circuit Lab"**.
   * Selects 2 qubits.
   * Adds Hadamard gate ($H$) on Qubit 0.
   * Adds Controlled-NOT ($CNOT$) with Control on Qubit 0 and Target on Qubit 1 (creating a Bell state $|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$).
   * Toggles "Simulate Thermal Decoherence Noise" (depolarizing probability $p = 0.05$).
   * Clicks **"Run Simulation"**.
2. **Backend Processing:**
   * Compiles gates into a `qiskit.QuantumCircuit`.
   * Applies `qiskit_aer.noise.NoiseModel`.
   * Simulates 1,024 shots.
   * Generates ASCII circuit diagram and OpenQASM 2.0 export code.
3. **Frontend Output:** Displays interactive probability histogram showing $|00\rangle \approx 47\%$, $|11\rangle \approx 48\%$, and small noise leakage $|01\rangle, |10\rangle \approx 2.5\%$. OpenQASM code is copyable with one click.

---

### Journey Q: Classical vs. Quantum Machine Learning Benchmark
```
Select Benchmark Dataset ──► Run Classical (Logistic) ──► Run VQC ──► Side-by-Side Report
```
1. **User Action:** Selects **"Benchmarking"** and clicks **"Execute Controlled Benchmark"**.
2. **Backend Processing:**
   * Ingests standardized synthetic sentiment dataset.
   * Trains classical Scikit-Learn Logistic Regression model; records Accuracy, F1, and training time.
   * Trains Qiskit Variational Quantum Classifier (VQC) using parameterized 4-qubit circuit; records Accuracy, F1, and execution duration.
   * Packages metrics into structured report without bias.
3. **Frontend Output:**
   * Comparative metrics table:
     * Classical: 91.2% Accuracy | 0.90 F1 | 12ms Runtime
     * Quantum VQC: 86.4% Accuracy | 0.85 F1 | 1,420ms Runtime
   * Educational narrative explaining that quantum simulation on classical CPUs involves mathematical matrix transformation overhead.
