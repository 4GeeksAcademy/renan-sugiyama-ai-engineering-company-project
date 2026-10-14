# Dashboard Text Contrast Fix

Updated muted and primary-action colors to the shared canonical tokens, lightened the sidebar label, and changed warning-badge text to the dark ink color. Verified contrast ratios: muted/page **5.12:1**, white/button **5.56:1**, warning text/tint **14.73:1**, and sidebar label/background **4.82:1** (WCAG AA requires 4.5:1 for normal text).

## Render-Blocking Font Request

Replaced the external Google Fonts stylesheet with Next.js `next/font/google` for DM Sans and Space Mono. The fonts are now self-hosted with `display: swap`; rerun Lighthouse to quantify any remaining render-blocking savings.
