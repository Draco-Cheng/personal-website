# AI_README: Frontend (Next.js) Conventions & Index

This file is for AI assistants and future contributors.  
It describes the architecture, conventions, and best practices for the frontend app.

---

## Framework & Stack

- **Framework:** Next.js 15+ (App Router)
- **Language:** TypeScript
- **Styling:** CSS Modules (per component/page)
- **Component Architecture:** Atomic Design (atoms, molecules, organisms, templates, pages)
- **State/Logic:** Prefer custom React hooks (in `/src/hooks`)
- **API Integration:** All API calls use `/api` prefix, proxied in dev via `next.config.ts`
- **Routing:** All route files (`page.tsx`, `layout.tsx`) live in `src/app/` and subfolders

---

## Directory Structure

```
apps/frontend/
├── src/
│   ├── app/                # Next.js routes, layouts, config
│   │   ├── page.tsx        # Dashboard route
│   │   ├── ping/page.tsx   # /ping route
│   │   └── ...
│   ├── components/
│   │   ├── atoms/
│   │   ├── molecules/
│   │   ├── organisms/
│   │   ├── templates/
│   │   └── pages/
│   └── hooks/              # Custom React hooks (e.g., usePingApi)
└── ...
```

---

## Conventions

- **Component Naming:** PascalCase for all components.
- **CSS Modules:** Each component/page has its own `.module.css` file.
- **Atomic Design:**  
  - Atoms: Basic UI elements (Button, Footer, etc.)
  - Molecules: Small reusable groups (ApiResult, etc.)
  - Organisms: Complex UI blocks (Card, etc.)
  - Templates: Application-level layout/composition (Menu, etc.)
  - Pages: Page-level components, imported by route files
- **Hooks:** Place all custom hooks in `src/hooks/`, use strict typing.
- **API Prefix:** Import from `src/app/config.ts` for consistency.

---


### Styling & Tokens
- Global design tokens live in `src/styles/tokens.css`, imported once from `src/app/globals.css`
- Reference shared colors, spacing, radii, and shadows via CSS variables (e.g., `var(--color-surface)`) inside component modules
- Keep component-specific overrides inside their local `.module.css` unless a value will be reused elsewhere

### Theming
- Light and dark palettes are defined via CSS variables in `src/styles/tokens.css` (`:root` for light, `.dark` overrides for dark)
- `src/app/globals.css` toggles palettes using the `.dark` class plus `color-scheme`; ensure the `<html>` element receives the class via your theme switcher
- Tailwind reads the same tokens through `tailwind.config.ts`, so utilities like `bg-primary` and CSS Modules both resolve to the shared values
## Application-level Logic

- Components using Next.js context (e.g., `usePathname`, navigation) should be placed in `templates/` or `pages/`, not in atomic folders.
- Only route files in `src/app/` define actual routes.

---

## AI Usage

- Reference this file for conventions, structure, and best practices when using GPT or other AI tools.
- Follow the Atomic Design and Next.js conventions described here.
