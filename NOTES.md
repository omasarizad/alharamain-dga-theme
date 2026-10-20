# Notes

- **Rebuilt from scratch with Platforms Code.** Every UI element is an official Platforms Code web component (`@platformscode/core@0.0.53`) or layout CSS on its tokens. No CSS or markup from the original site is used. Only the content (text, images, section order) is carried over.
- **Component source.** `@platformscode/core` is published on npm by AZM (`azmx.sa`), which appears to be DGA's Platforms Code vendor. design.dga.gov.sa was unreachable from our network, so check the component choices against the official templates page.
- **Icon licensing.** Icons come from `@platformscode/icons`, whose license is `UNLICENSED`. They're loaded at runtime from the npm CDN and never committed. Confirm usage rights with DGA or AZM before production.
- **Only the homepage is in scope.** Every link to another page, the search, the language switch and the "نصي" tab show a Platforms Code toast saying the page is outside the prototype's scope. Home links stay on the page.
- **Working interactions:** the place tabs (الكل / المسجد الحرام / المسجد النبوي) filter their section's cards, the mobile menu opens a drawer (Esc closes it), and the header search opens.
- **Content is a snapshot** of the beta site from 2026-10-20. Images still load from the beta site and its CDN. Two cards had no image, so they show the Haram or Nabawi photo instead. The hero subtitle is new placeholder copy.
- **Public but marked unofficial.** The page has a robots `noindex` tag and an "unofficial prototype" banner so it isn't mistaken for the official site.
