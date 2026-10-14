# Text Contrast Fix

Darkened the shared muted-text token to `#626b64` and primary orange to `#a94d24` in `uis/website/src/styles.css`.

The lowest checked muted-text contrast is now 4.81:1 on the orange-tinted card background; white text on primary orange is 5.56:1. Both exceed WCAG AA's 4.5:1 requirement for normal text.

Replaced the external Google Fonts stylesheet with `next/font/google` for DM Sans and Space Mono. Next.js now self-hosts the fonts, removing the browser's third-party font stylesheet request; `display: swap` remains enabled.

## Unused JavaScript

The homepage has no app-owned client components or third-party scripts; its client bundles are Next.js runtime modules. Keeping Next.js means these bytes cannot be safely removed with code splitting. Eliminating them requires a zero-JavaScript static delivery architecture, so no site-code change was made and the Lighthouse item remains unresolved.

## After Lighthouse Results

Compared with the October 14 baseline, the after run scored **100** in all four categories; Accessibility rose from **95 to 100**. Performance rose from **99 to 100**. FCP and Speed Index improved from **0.8 s to 0.2 s**, LCP from **0.8 s to 0.5 s**, and CLS from **0.008 to 0**; TBT remained **0 ms**.

Lighthouse's estimated render-blocking savings fell from **540 ms to 40 ms**, a reduction of **500 ms (about 93%)** after self-hosting the fonts. The unused JavaScript estimate (**205 KiB**) and legacy JavaScript estimate (**13 KiB**) remain, as does the network dependency-tree insight. These are lab-run comparisons and may vary between runs.
