# Text Contrast Fix

Darkened the shared muted-text token to `#626b64` and primary orange to `#a94d24` in `uis/website/src/styles.css`.

The lowest checked muted-text contrast is now 4.81:1 on the orange-tinted card background; white text on primary orange is 5.56:1. Both exceed WCAG AA's 4.5:1 requirement for normal text.

Replaced the external Google Fonts stylesheet with `next/font/google` for DM Sans and Space Mono. Next.js now self-hosts the fonts, removing the browser's third-party font stylesheet request; `display: swap` remains enabled.
