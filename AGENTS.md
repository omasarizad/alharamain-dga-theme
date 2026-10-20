# Al-Haramain homepage: rebuilt with Platforms Code

The Al-Haramain homepage (https://alharamain-app-beta.it4islam.com/ar) rebuilt
from scratch with the Saudi DGA **Platforms Code** design system: its web
components, tokens, typography and layout grid. Only the content (text, images,
sections) comes from the original site. Unofficial prototype, homepage only.

## How it works

```
snapshot/original.html ──extract-content.py──▶ data/content.json ──build-home.py──▶ index.html
```

- `snapshot/original.html`: untouched download of the live homepage. The content source.
- `scripts/extract-content.py`: pulls sections, cards (title, scholar, date, mosque, media, tags, image), stats, nav and footer text into `data/content.json`.
- `scripts/build-home.py`: generates `index.html` from the JSON using Platforms Code components. **Edit markup here, not in `index.html`.**
- `css/home.css`: page layout only (container, grids, hero, sections), written with official tokens (`--colors-*`, `--spacing-*`, `--radius-*`, `--text-*`, `--background-*`).
- `js/home.js`: place filter tabs, mobile nav drawer, footer data, out-of-scope toast.
- `js/proto-bar.js`: the prototype bottom bar (Homepage / Components / Changes / Repo) on every page. Self-contained, so it also works on pages without Platforms Code.
- `scripts/build-components.py`: builds `components.html`, which lists every `dga-*` component in `index.html`: usage count, the attributes we set checked against the official prop docs from `@platformscode/core`, a live preview, and source links. CI runs it; the output is gitignored. **If it flags a component as missing from the package, or an attribute as undocumented, fix the markup.**
- `NOTES.md`: project notes and caveats. Shown at the top of `changes.html`, so keep it current.
- `scripts/build-changes.py`: builds `changes.html` from git history (CI runs it; the output is gitignored).
- `.github/workflows/pages.yml`: deploys to GitHub Pages on every push to `main`.

Rebuild locally: `python3 scripts/build-home.py && python3 -m http.server`.
Don't open `index.html` over `file://`: the CDN blocks lazy chunks for origin `null`.

## Platforms Code packages (loaded from jsDelivr, pinned)

- `@platformscode/core@0.0.53`: web components plus `core.css` (tokens and typography classes). MIT. Maintained by AZM (`azmx.sa`).
- `@platformscode/icons@0.0.11`: icon SVGs. **UNLICENSED**, so it's loaded at runtime from npm and never committed here.

## Component map

| Section | Components |
|---|---|
| Header | `dga-header-v2`, `dga-header-menu-v2`, `dga-header-menu-item`, `dga-header-actions`, `dga-header-search-action`, `dga-header-action` |
| Mobile nav | `dga-drawer-v2`, `dga-drawer-header`, `dga-drawer-body`, `dga-drawer-nav`, `dga-drawer-nav-item` |
| Hero | `dga-tag`, `dga-search-box`, `dga-button-v2` |
| Live strip | `dga-inline-alert` |
| Content sections | `dga-tabs-v2`, `dga-tab`, `dga-card-v2`, `dga-card-content`, `dga-card-title`, `dga-tag`, `dga-button-v2`, `dga-icon` |
| Tilawat stats | `dga-featured-icon` + token typography |
| Footer | `dga-footer` (DarkGreen) |
| Out-of-scope | `dga-notification-toast` |

## Rules for developers and agents

1. **Use a Platforms Code component before writing your own.** Custom CSS is for page layout only, and it must use official tokens. No hex colors.
2. **Don't style component internals.** They use shadow DOM. If you need control, put light-DOM content in a slot (cards use a plain `<img class="card-img">` in `dga-card-content` for that reason).
3. **Icons:** `window.GDSIcons.map` (inline in `<head>`, before `core.esm.js`) resolves every icon name to `@platformscode/icons`. Keep that script first.
4. **Header collapse is ours to build.** `dga-header-menu-v2` never hides itself. Below 1100px we hide it and show the drawer button.
5. **Footer link groups** only render when `footer.NavLinks = true` (set in `js/home.js`).
6. **Scope:** only the homepage is real. Every other link or button gets `data-out-of-scope` and shows the toast.
7. One logical change per commit. Write the subject in plain English and explain *why* in the body. `changes.html` is generated from these messages.
8. Check visually at 1440px and 390px before pushing.

## Live

- Page: https://omasarizad.github.io/alharamain-dga-theme/
- Components: https://omasarizad.github.io/alharamain-dga-theme/components.html
- Changes: https://omasarizad.github.io/alharamain-dga-theme/changes.html
