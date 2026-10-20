# Notes

- **Token values aren't official.** The DGA site blocked scripted access, so colors and sizes come from the community package `@a.nemreen/dga-tokens@0.3.9` (MIT). They match the Platforms Code palette as far as we know. Check them against the official Platforms Code Figma kit before production.
- **The page is static.** The Next.js scripts were removed, so tabs, dropdowns and search don't work. Images and fonts still load from the live beta site (`alharamain-app-beta.it4islam.com`).
- **Public but marked unofficial.** The page has a robots `noindex` tag and an "unofficial prototype" banner so it isn't mistaken for the official site.
- **Fonts:** IBM Plex Sans Arabic / IBM Plex Sans throughout. Quran and hadith text keeps Noto Naskh, and Arabic headings keep the Saudi display font.
- **The markup is unchanged.** All theming lives in `css/dga-theme.css`, loaded after the site's own CSS. See `AGENTS.md` for the rules.
