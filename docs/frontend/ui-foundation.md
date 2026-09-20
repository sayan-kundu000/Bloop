# UI Foundation & Design System

## 1. Design System Foundations

Bloop's design system is engineered for modern AI productivity: refined dark mode, clean typography, purposeful micro-interactions, and glassmorphic depth.

### Color Palette Tokens
Tailwind CSS provides semantic color scales configured in `tailwind.config.js`:

- **Bloop Brand Scale** (`bloop-*`):
  Primary violet/indigo palette (e.g. `bloop-500: #6172f3`, `bloop-600: #444ce7`) representing speech synthesis, primary actions, and brand identity.
- **Quantum Scale** (`quantum-*`):
  Electric purple/magenta palette (e.g. `quantum-400: #c784ff`, `quantum-500: #ad4efa`) identifying quantum text, emotion, and benchmark features.
- **Surfaces & Glass**:
  Deep navy slate background (`#0b0f19`), elevated card surfaces (`rgba(17, 24, 39, 0.75)` with `backdrop-filter: blur(12px)`), and subtle border lines (`rgba(255, 255, 255, 0.08)`).
- **Status & Feedback**:
  - `emerald-*`: Success notifications and active status indicators.
  - `amber-*`: Warnings and simulation indicators.
  - `rose-*`: Error banners, destructive delete buttons, and validation warnings.

### Typography
- **Headings & Display**: `Outfit`, sans-serif.
- **Body & Controls**: `Inter`, system-ui, -apple-system, sans-serif.
- **Code & Numbers**: `JetBrains Mono`, monospace (used for character counts, duration, and quantum matrices).

---

## 2. Reusable UI Primitives (`src/components/ui/`)

| Primitive | Description | Variants / Props | Accessibility Features |
|---|---|---|---|
| **`Button`** | Core clickable control | `primary`, `secondary`, `outline`, `danger`, `ghost`<br/>Sizes: `sm`, `md`, `lg`<br/>`isLoading`, `disabled` | Semantic `<button>`, focus rings, disabled attributes, spinner with `aria-hidden` |
| **`Input`** | Single-line text input | `hasError`, standard HTML attributes | Focus outline, aria-invalid pairing, dark background |
| **`Textarea`** | Multi-line speech input | `maxCharacters`, `currentCharCount`, `resize` (`none`, `vertical`, etc.), `hasError` | Real-time character counter, over-limit warning, focus rings |
| **`Select`** | Accessible dropdown | `options: SelectOption[]`, `hasError` | Custom SVG arrow, keyboard navigable, option groups |
| **`Card`** | Surface container | `className` | Glassmorphic backdrop blur, rounded-xl borders |
| **`Badge`** | Status pill | `indigo`, `emerald`, `amber`, `rose`, `slate`, `quantum` | High-contrast text on subtle transparent backgrounds |
| **`Modal` / `Dialog`** | Centered modal overlay | `isOpen`, `onClose`, `title`, `description`, `footer`, `maxWidth` | `role="dialog"`, `aria-modal="true"`, Escape key dismiss, backdrop click |
| **`ConfirmDialog`** | Destructive confirmation | `title`, `message`, `isDestructive`, `confirmLabel`, `cancelLabel` | Clear distinction between Cancel and Delete actions |
| **`Spinner`** | Circular loading spinner | `size` (`sm`, `md`, `lg`), `label` | `role="status"`, screen reader label (`sr-only`) |
| **`Skeleton`** | Shimmer placeholder | `className`, `rounded` | `aria-hidden="true"`, subtle pulse animation |
| **`EmptyState`** | Zero-data placeholder | `title`, `description`, `icon`, `action` | Meaningful visual cues without fake placeholder data |
| **`Tooltip`** | Contextual hover hint | `content`, `position` (`top`, `bottom`, `left`, `right`) | `role="tooltip"`, accessible via both hover and keyboard focus |

---

## 3. Forms & Feedback Foundations

### FormField Component (`src/components/forms/index.tsx`)
Encapsulates accessible form layout:
- Explicit `<label>` linked via `htmlFor`.
- Required indicator (`*`) when mandatory.
- Helper text slot for guidance.
- Error message slot rendered in high-contrast `rose-400`.

### AlertBanner Component (`src/components/feedback/index.tsx`)
Provides persistent or dismissible feedback banners:
- Types: `info`, `success`, `warning`, `error`.
- Distinct icons and accessible close button.
