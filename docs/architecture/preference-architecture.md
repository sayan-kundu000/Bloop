# User Preferences Architecture

## 1. Core Principle: Preference != Capability != Authorization

A central architectural tenet of the Bloop platform (Prompt 15 §10) is the strict distinction between what a user prefers and what the system permits:

```text
┌───────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
│     User Preference       │  ≠   │   Provider Capability     │  ≠   │  Security Authorization   │
│  "What the user prefers"  │      │ "What models/voices exist"│      │"What user is allowed to do│
└───────────────────────────┘      └───────────────────────────┘      └───────────────────────────┘
```

Therefore:
* A stored preference for `default_voice_id` **never bypasses** runtime voice validation or capability verification.
* A stored preference for `default_language_code` **never bypasses** language validation or voice-language compatibility checks.
* Every TTS synthesis request executes full capability and compatibility checks regardless of user preference settings.

---

## 2. Dynamic Voice Invariant & Defaults (Prompt 15 §3 & §12)

In strict accordance with Prompt 15 §3 and §12:
* **No hardcoded production voice catalogues** or fabricated default voices exist in preferences.
* When a user has not configured a preferred voice:
  ```json
  "default_voice_id": null
  ```
  This is the canonical initial state. Bloop gracefully supports "No preference", prompting the user or falling back to the request payload voice without inventing artificial defaults.

---

## 3. Preference Domain Model (`user_preferences`)

The `UserPreference` table is linked 1-to-1 with `users`:

```text
users (id) ──<CASCADE>── 1:1 ──< user_preferences (user_id)
```

### Supported Attributes:
* `id` (Integer primary key)
* `user_id` (Integer foreign key referencing `users.id` with `ondelete='CASCADE'`, Unique)
* `theme` (String: `'dark'`, `'light'`, or `'system'`, default `'dark'`)
* `audio_speed` (Float: multiplier bounded between `0.5` and `2.0`, default `1.0`)
* `auto_play` (Boolean: whether audio player automatically plays synthesized speech, default `true`)
* `default_language_code` (String: BCP-47 locale code referencing `languages.code` with `ondelete='SET NULL'`, nullable)
* `default_voice_id` (String: up to 100 chars, dynamic voice identifier, nullable)
* `created_at` / `updated_at` (Audit timestamps)

---

## 4. Preference Lifecycle & API Endpoints

* `GET /api/v1/users/me/preferences`:
  - Retrieves current user preferences.
  - Automatically initializes default record if one does not exist.
* `PATCH /api/v1/users/me/preferences`:
  - Validates theme against `('dark', 'light', 'system')`.
  - Validates audio speed between `0.5` and `2.0`.
  - Validates language code against active languages.
  - Commits updates transactionally and returns standardized `ApiResponse[UserPreferenceResponse]`.
