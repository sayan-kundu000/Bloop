# Frontend Accessibility Standards (WCAG 2.1 AA)

## 1. Core Accessibility Principles

Bloop is designed and built following practical **WCAG 2.1 AA** accessibility requirements:

1. **Semantic Elements**:
   Interactive elements use native HTML controls (`<button>`, `<a>`, `<input>`, `<textarea>`, `<select>`). `<div>` elements are never used as substitutes for interactive controls.
2. **Keyboard Accessibility**:
   Every workflow—including speech text entry, voice selection, audio playback, dialog confirmation, and mobile menu toggling—is operable using a standard keyboard alone.
3. **Visible Focus States**:
   All interactive primitives include explicit focus indicators (`focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:outline-none`) that ensure users can easily track their focus position.
4. **Contrast & Color Independence**:
   Text meets or exceeds the 4.5:1 contrast ratio against dark backgrounds. Information and status are never conveyed through color alone; badges and alerts combine color with descriptive text or icons.

---

## 2. Dialog & Modal Semantics

The `Modal` primitive (`src/components/ui/index.tsx`) implements accessible dialog behavior:

- **ARIA Attributes**:
  - `role="dialog"`
  - `aria-modal="true"`
  - `aria-labelledby="modal-title"`
  - `aria-describedby="modal-description"`
- **Keyboard Dismissal**:
  - Automatically captures the `Escape` key and triggers `onClose()`.
- **Close Button**:
  - Clear `aria-label="Close dialog"` provided on the header close icon.

---

## 3. Responsive Mobile Navigation

The mobile navigation drawer (`src/components/common/Navbar.tsx`) adheres to mobile accessibility standards:

- The hamburger button exposes:
  - `aria-expanded={isMobileMenuOpen}`
  - `aria-controls="mobile-navigation"`
  - Dynamic `aria-label="Open menu"` / `"Close menu"`.
- Closes cleanly when the user hits `Escape` or selects any navigation link.

---

## 4. Screen Reader Support & Status Announcements

- **Loading Spinners**:
  - Include `role="status"` and visually hidden text `<span className="sr-only">Loading...</span>`.
- **Error Messages**:
  - Form errors are paired with input fields and announced clearly.
- **Audio Controls**:
  - Play, pause, volume, and download buttons in `AudioPlayerBar` carry explicit `aria-label` attributes (e.g. `aria-label="Play audio"`, `aria-label="Pause audio"`).
