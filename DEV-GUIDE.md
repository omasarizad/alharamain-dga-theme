# Applying Platforms Code to the real site

What changes in the Al-Haramain Next.js app (Tailwind v4 + daisyUI) to match the prototype. Everything is **Tailwind utilities on Platforms Code tokens**. No Platforms Code web components or React wrappers are needed.

Every snippet below is generated from `scripts/build-home.py`, the same code that builds the prototype, so it's always current. Convert `class=` to `className=` in JSX.

## 1. Setup

1. Copy `tailwind/platforms-code.css` into the app (for example `src/styles/platforms-code.css`). It's generated from the official `@platformscode/core@0.0.53` `core.css`, so don't hand-edit it. Regenerate with `python3 scripts/build-theme.py`.
2. Import it right after Tailwind in the global stylesheet:

```css
@import "tailwindcss";
@import "./platforms-code.css";
```

3. **Remove daisyUI** (`@plugin "daisyui"` and its theme block) and the custom color variables (`--color-primary50`, `--color-secondary800`, `--color-excerptColor`, …). daisyUI classes (`btn`, `card`, `link`, `badge`, `tabs`) get replaced by the class lists in section 3.
4. The theme starts with `--color-*: initial`, which **removes Tailwind's default palette**. Any `gray-*`, `red-*` or `emerald-*` class stops working, so replace them using section 2. This is deliberate: it keeps the site on official colors only.
5. Fonts: load **IBM Plex Sans Arabic** (400/500/600/700). It's the only UI font. Keep Noto Naskh only for Quran and hadith text. Drop the "Saudi" font from headings.
6. Icons: Platforms Code uses the `@platformscode/icons` set (Hugeicons names such as `search-01` or `calendar-03`). The prototype masks the SVG so it takes `currentColor`. In React, use an `<Icon name="…">` component that does the same. The icons package license is `UNLICENSED`, so confirm usage rights with DGA or AZM before production.

## 2. Token mapping (old → new)

| Old (daisyUI / custom) | Value | New Tailwind class | Value |
|---|---|---|---|
| `primary` | `#3e7869` | `primary-600` | `#1b8354` |
| `primary50` / `primary100` | `#579f8c` / `#6ab7a3` | `primary-500` / `primary-400` | `#25935f` / `#54c08a` |
| `primary800` / `primary900` | `#d7ede4` / `#ebf6f1` | `primary-100` / `primary-50` | `#dff6e7` / `#f3fcf6` |
| `secondary` (gold, active nav, footer) | `#a68c30` | `gold-700` text · `gold-600` fill | `#b87b02` · `#dba102` |
| `secondary100`…`secondary800` (cream backgrounds) | `#faf2e3`… | `neutral-50` / `white` | `#f9fafb` / `#ffffff` |
| `accent` | `#b8557b` | `lavender-600` (if needed) | `#6d428f` |
| `base-content` | `#18181b` | `neutral-800` (headings) · `neutral-700` (body) | `#1f2a37` · `#384250` |
| `base-200` / `base-300` | `#f8f8f8` / `#eee` | `neutral-50` / `neutral-200` | `#f9fafb` / `#e5e7eb` |
| `excerptColor`, `text-gray-600` | `#4d525e` | `neutral-500` (meta) | `#6c727e` |
| `gray-200`…`gray-700` | Tailwind grays | `neutral-200`…`neutral-700` | Platforms Code grays |
| Footer gold background | `secondary` | **`success-900`** | `#074c30` |
| `--radius-box` 1rem / `--radius-field` .5rem | | `rounded-lg` (16px) cards · `rounded-sm` (4px) buttons, inputs, tags · `rounded-md` (8px) alerts, images | |
| `shadow-[0px_1px_17px_0px_#00000021]` | | none at rest (1px border), `shadow-md` on hover | |
| Text sizes | | `text-display-xs` (24/32) section titles · `text-lg` (18/28) card titles · `text-md` (16/24) body · `text-sm` (14/20) · `text-xs` (12/18) meta · `text-2xs` (10/14) tags | |

> **Gotcha:** the footer's "DarkGreen" is `--colors-green-900` in Platforms Code, so it's `bg-success-900`, not `bg-primary-900`.

## 3. Components

Each block replaces a daisyUI or custom piece. The component name in brackets is the official Platforms Code component it reproduces. Compare them visually on the [components page](components.html).

### Header (`dga-header-v2`)

Was: logo, search input, Google search, language dropdown, then a second row of icon nav with a gold active pill. Now: **one 72px white bar** with a bottom divider and `sticky top-0`. Menu items are text only (no icons). The current page is a filled `bg-primary-600` cell with white `font-semibold` text. Search and language become header actions. The four lesson pages (الدروس، المحاضرات، الدورات، السلاسل العلمية) collapse into one **الدروس والمحاضرات** item.

<!-- snippet:header -->

Below **1100px** the menu is hidden (`hidden min-[1100px]:block`) and the **القائمة** action opens the drawer. Platforms Code leaves collapsing to the app.

### Mobile menu (`dga-drawer-v2` + `dga-drawer-nav-item`)

A native `<dialog>` opened with `showModal()`. That gives Esc-to-close, a focus trap and a backdrop for free. It's 320px wide, on the start side (right in RTL), with `shadow-2xl`. Items are 36px, `text-sm font-semibold`, with a 6px primary indicator on the current page. Return focus to the menu button on close.

<!-- snippet:drawer-item -->

### Hero (new)

There's no official hero component, so this one is built from tokens: a `bg-primary-900` section with the photo under a primary-800/900 gradient, an on-color tag, `text-display-lg` title, `text-xl` subtitle at `text-white/80`, and the search box plus an on-color button.

### Live lessons strip (`dga-inline-alert`, info, colored)

Replaces the green "البث المباشر للدروس" bar. The "جدول الدروس" and "شاهد الآن" actions can go inside it as `md` buttons.

<!-- snippet:alert -->

### Section header and "عرض الكل"

Title `text-display-xs font-bold text-neutral-800`, subtitle `text-md text-neutral-500`. Drop the decorative heading font and the gold subtitle color. "عرض الكل" is a secondary-outline button (`dga-button-v2`, md).

<!-- snippet:button -->

### Filter tabs (`dga-tabs-v2` + `dga-tab`)

Replaces the gold segmented control (الكل / المسجد الحرام / المسجد النبوي). It's an underline tab row: 44px, `text-sm`, with a 3px `primary-600` bar under the selected tab. State comes from `aria-selected`, styled with `aria-selected:` variants. Use `role="tablist"`/`role="tab"`, with arrow keys moving focus.

<!-- snippet:tabs -->

### Content card (`dga-card-v2`, stroke)

Replaces daisyUI `card` with its drop shadow and the image's asymmetric `rounded-tl-2xl rounded-br-2xl`.

- **Card:** `rounded-lg` (16px), 1px `neutral-300` border, `p-4`, with `shadow-md` only on hover.

- **Image:** 16:10, `rounded-md`.

- **Meta row:** `text-xs text-neutral-500` with 16px icons.

- **Title:** `text-lg font-bold text-neutral-700`, clamped to 2 lines, turning `primary-600` and underlined on hover.

- **Scholar:** `text-sm text-primary-600`. It's no longer gold.

- **Tags:** pinned to the bottom with `mt-auto`.

<!-- snippet:card -->

### Tag (`dga-tag`, neutral sm)

Replaces daisyUI `badge` and the outlined gold/green pills. Tags are square-cornered (`rounded-sm`), not pills.

<!-- snippet:tag -->

### Search box (`dga-search-box`, lg)

40px, 1px `neutral-400` border, `rounded-sm`, 20px search and mic icons. On focus the border turns `primary-600` with a 3px `primary-500/20` ring.

<!-- snippet:search -->

### Tilawat stats (`dga-featured-icon`)

Replaces the mint stat boxes. Each stat is a white `rounded-lg` tile with a 48px `bg-primary-50 text-primary-600` circle icon, a `text-display-xs font-bold` value and a `text-sm` label.

<!-- snippet:featured-icon -->

### Footer (`dga-footer`, DarkGreen)

Replaces the gold footer and its separate copyright strip with **one** `bg-success-900` block:

- **Logo**

- **Title:** `text-display-2xl font-bold`

- **About:** `text-display-xs`

- **Link columns:** each title is `text-lg font-semibold` over a `white/30` divider, and links are `text-sm`

- **Copyright:** `text-sm font-semibold`

### Toast (`dga-notification-toast`)

White, `rounded-md`, `shadow-3xl`, with a 40px info featured icon, a `text-md font-semibold` title, a `text-sm` body and a 32px close button. The prototype uses it for "out of scope", and the real site can use it for any transient message.

## 4. Rules

- Use **logical properties** (`ps-*`/`pe-*`, `start-*`/`end-*`, `text-start`) so RTL and LTR both work. Avoid `left`/`right`/`pl`/`pr`.

- **Focus:** a 2px black outline with 2px offset on everything (it's in the theme's base layer). Don't remove outlines.
- Only theme colors. No arbitrary hex in class names.
- Keep text at least 12px (`text-xs`) except tags (`text-2xs`, as in the official component).
- Check at 1440px and 390px.
