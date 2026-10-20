# Al-Haramain homepage: Platforms Code in Tailwind

A prototype of the Al-Haramain homepage (https://alharamain-app-beta.it4islam.com/ar)
restyled to the Saudi DGA **Platforms Code** design system, written as plain
HTML with **Tailwind v4 utilities** on the official Platforms Code tokens. No
web components and no React wrappers: developers copy the class lists into the
real Next.js site. Unofficial prototype, homepage only.

## How it works

```
@platformscode/core core.css ──build-theme.py──▶ tailwind/platforms-code.css (@theme tokens)
snapshot/original.html ──extract-content.py──▶ data/content.json ──build-home.py──▶ index.html
tailwind/app.css + index.html ──tailwindcss──▶ css/app.css
```

- `tailwind/platforms-code.css`: **generated** Tailwind v4 `@theme` with the official colors, radius, shadows and type scale. Don't hand-edit it. Regenerate with `python3 scripts/build-theme.py`.
- `scripts/build-home.py`: generates `index.html`. Each helper (`button`, `tag`, `tabs`, `card`, `search_box`, `inline_alert`, `featured_icon`, `header`, `drawer`, `footer`) reproduces one official component, and its element carries `data-pc="<official tag>"`. **Edit markup here, not in `index.html`.**
- `js/home.js`: vanilla JS for the filter tabs (`aria-selected`), the mobile drawer (`<dialog>`) and the out-of-scope toast.
- `js/proto-bar.js`: the prototype bottom bar on every page.
- `DEV-GUIDE.md`: the guide for developers updating the real site. It's rendered into `changes.html`, and `<!-- snippet:NAME -->` markers are filled from `build-home.py`.
- `scripts/build-changes.py`: builds `changes.html` from `DEV-GUIDE.md` (a description of what changed, not a commit log; history is on GitHub).
- `scripts/shoot-components.js` writes `assets/ours/*.png` (our version of each component). `assets/official/*.png` are reference shots of the official web components. `scripts/build-components.py` builds `components.html` from them.
- `.github/workflows/pages.yml`: builds everything and deploys to GitHub Pages on every push to `main`.

Local build: `npm install && npm run build && python3 scripts/build-changes.py && python3 scripts/build-components.py && python3 -m http.server`.
After a visual change, re-shoot: `node scripts/shoot-components.js` (needs `playwright`) and commit `assets/ours/`.

## Rules for developers and agents

1. **Match the official component.** Before changing a helper, check the official component's computed styles (size, padding, type, colors, radius) and compare on `components.html`.
2. **Theme colors only.** No arbitrary hex in classes. The default Tailwind palette is disabled (`--color-*: initial`).
3. **Logical properties** (`ps/pe`, `start/end`) so RTL works. Keep the 2px black focus outline.
4. **Gotchas:** the footer dark green is `success-900` (`--colors-green-900`). `text-md` (16/24) is added by `build-theme.py` because `core.css` has no class for it. The header menu collapses below 1100px into the drawer.
5. **Scope:** only the homepage is real. Every other link or button gets `data-out-of-scope` and shows the toast.
6. One logical change per commit, with a plain-English subject and the *why* in the body. When a change affects how the real site should be updated, update `DEV-GUIDE.md` too.
7. Check visually at 1440px and 390px before pushing.

## Live

- Page: https://omasarizad.github.io/alharamain-dga-theme/
- Components: https://omasarizad.github.io/alharamain-dga-theme/components.html
- Developer changes: https://omasarizad.github.io/alharamain-dga-theme/changes.html
