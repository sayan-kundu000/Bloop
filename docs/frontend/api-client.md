# API Client Architecture & Error Normalization

## 1. API Client Overview

Bloop's frontend communicates with the FastAPI backend through a centralized **Axios** client (`src/api/client.ts`) configured with strict interceptors for authentication, session lifecycle, and standardized error normalization.

```mermaid
graph TD
  Component["React Component / Hook"] --> APIModule["API Module (authApi, ttsApi, historyApi)"]
  APIModule --> AxiosInstance["Axios Client (apiClient)"]
  
  subgraph Request_Interceptor ["Request Interceptor"]
    AxiosInstance --> CheckToken{"JWT Token in localStorage?"}
    CheckToken -- Yes --> InjectAuth["Set Header: Authorization: Bearer <token>"]
    CheckToken -- No --> ProceedReq["Send Request with Standard Headers"]
  end

  subgraph Response_Interceptor ["Response Interceptor"]
    ProceedReq --> BackendFastAPI["FastAPI Backend REST API"]
    BackendFastAPI --> HandleResp{"HTTP Status OK?"}
    HandleResp -- 2xx --> ReturnData["Return response.data"]
    HandleResp -- Error --> Normalizer["normalizeApiError()"]
    Normalizer --> Check401{"Status == 401?"}
    Check401 -- Yes --> ClearToken["Clear stale bloop_token from localStorage"]
    Check401 -- No --> ThrowNormalized["Throw FrontendApiError"]
    ClearToken --> ThrowNormalized
  end
```

---

## 2. API Contract & Response Envelopes

Every JSON endpoint conforms to the established Bloop REST contract:

### Success Envelope
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional human-readable confirmation"
}
```

### Error Envelope
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable explanation of error",
    "details": { ... }
  }
}
```

---

## 3. Normalized Error Model (`FrontendApiError`)

Raw Axios error objects and network exceptions are transformed into instances of `FrontendApiError`:

```typescript
export class FrontendApiError extends Error {
  public readonly code: string;
  public readonly status?: number;
  public readonly details?: unknown;
  public readonly timestamp: string;

  // Predicate helpers for clean UI logic:
  public isAuthError(): boolean;
  public isForbidden(): boolean;
  public isNotFound(): boolean;
  public isConflict(): boolean;
  public isValidationError(): boolean;
  public isRateLimit(): boolean;
  public isServerError(): boolean;
  public isNetworkError(): boolean;
}
```

### HTTP Status Code Mapping
| Status Code | Default User-Friendly Message | UI Behavior |
|---|---|---|
| **400 Bad Request** | The request could not be processed due to invalid parameters. | Inline field feedback |
| **401 Unauthorized** | Your session has expired or you are not signed in. | Token purged; redirect to `/login` |
| **403 Forbidden** | You do not have permission to perform this action. | Alert banner; action blocked |
| **404 Not Found** | The requested resource could not be found. | Render 404 or empty state |
| **409 Conflict** | This operation conflicts with an existing resource. | Warning banner (e.g. duplicate favorite) |
| **422 Validation Error** | Validation failed. Please check your inputs and try again. | Form field validation messages |
| **429 Rate Limit** | You have reached the current request limit. Please try again later. | Alert message; disable submission temporarily |
| **500 Internal Error** | A backend server error occurred. Please try again shortly. | General error banner; retry button |
| **503 Unavailable** | The speech generation service is temporarily unavailable. | Retry prompt without losing draft text |

---

## 4. Authentication Flow

```mermaid
graph TD
  User["User on /login"] --> SubmitCreds["Submit Email & Password"]
  SubmitCreds --> APIReq["POST /api/v1/auth/login"]
  APIReq --> FastAPIAuth["FastAPI Authentication"]
  FastAPIAuth --> JWTResponse["Return Token { access_token, user }"]
  JWTResponse --> StoreToken["Store access_token in localStorage"]
  StoreToken --> UpdateStore["useAuthStore.setState({ user, isAuthenticated: true })"]
  UpdateStore --> FetchMe["GET /api/v1/auth/me"]
  FetchMe --> ProtectApp["User granted access to protected workspace"]
```

---

## 5. TTS Speech Generation Data Flow

```mermaid
graph TD
  Workspace["User enters text & selects dynamic voice"] --> ValidateInput["Client Validation (Length 1-2500 chars)"]
  ValidateInput --> SubmitMutation["useMutation(ttsApi.generateSpeech)"]
  SubmitMutation --> DisableUI["Disable Generate Button & Show Loading Spinner"]
  DisableUI --> POST_TTS["POST /api/v1/tts"]
  
  POST_TTS --> BackendAPI["Bloop FastAPI Backend"]
  BackendAPI --> ElevenLabs["ElevenLabs Isolated Provider Pipeline"]
  ElevenLabs --> ProcessAudio["Audio Normalization & Storage"]
  ProcessAudio --> TTSResponse["Return TTSResponse { audio_url, download_url, ... }"]
  
  TTSResponse --> AudioStore["audioStore.playAudio(audio_url, title)"]
  AudioStore --> PlaybackBar["AudioPlayerBar renders player controls"]
  TTSResponse --> InvalidateCache["queryClient.invalidateQueries(['history'])"]
```

---

## 6. Frontend Security Policies

1. **No Sensitive Tokens in Logs**: Logging sensitive passwords, raw speech text, or JWT tokens in console outputs is strictly prohibited.
2. **Untrusted Content Protection**: User speech content is rendered strictly via standard React text nodes. `dangerouslySetInnerHTML` is never used for user-submitted content.
3. **Audio URL Validation**: Only relative URLs or backend URLs matching `appConfig.apiBaseUrl` are passed to media players.
