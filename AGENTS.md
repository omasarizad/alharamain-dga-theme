# Al-Haramain homepage: DGA Platforms Code theme

Static snapshot of https://alharamain-app-beta.it4islam.com/ar restyled with
the Saudi DGA Platforms Code design system. Unofficial prototype.

## Layout

- `index.html`: static homepage (Next.js scripts stripped, assets point at the live origin)
- `css/1nh40b4t7dbv_.css`, `css/2wj4kx8h2005e.css`: the site's original CSS (only `url()` paths rewritten)
- `js/prototype-guard.js`: blocks out-of-scope links/forms and shows a toast. Build step: every non-home `<a href>` becomes `href="#" data-out-of-scope`
- `css/dga-theme.css`: **all theme work goes here**. It loads last and remaps the site's daisyUI/Tailwind variables onto DGA tokens
- `NOTES.md`: project notes and caveats. Shown at the top of `changes.html`, so keep it current
- `scripts/build-changes.py`: builds `changes.html` from git history (CI runs it; the output is gitignored)
- `.github/workflows/pages.yml`: deploys to GitHub Pages on every push to `main`

## Rules for developers and agents

1. Change styling in `css/dga-theme.css`. Don't edit the original CSS or the markup unless a token remap can't do it.
2. Put base and component rules inside `@layer base` / `@layer components`. Unlayered rules beat Tailwind utilities and break things like `.text-white`.
3. Set page background on `:root`, never `body`. A body background covers the site's `z-index:-1` section images.
4. One logical change per commit. Write the subject in plain English and explain *why* in the body. `changes.html` is generated from these messages, so they are the changelog.
5. Before pushing, check visually: `python3 -m http.server` and compare with the live site.
6. Token values come from `@a.nemreen/dga-tokens@0.3.9` (MIT, community, not official). Check them against the official Platforms Code Figma kit before production.

## Live

- Page: https://omasarizad.github.io/alharamain-dga-theme/
- Changes: https://omasarizad.github.io/alharamain-dga-theme/changes.html
