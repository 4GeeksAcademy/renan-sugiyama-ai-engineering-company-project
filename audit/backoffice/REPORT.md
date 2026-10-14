# Dashboard Text Contrast Fix

Updated muted and primary-action colors to the shared canonical tokens, lightened the sidebar label, and changed warning-badge text to the dark ink color. Verified contrast ratios: muted/page **5.12:1**, white/button **5.56:1**, warning text/tint **14.73:1**, and sidebar label/background **4.82:1** (WCAG AA requires 4.5:1 for normal text).

## Status Card Contrast

Changed the `Needs attention` status text from translucent white to the sidebar text color `#edf7f0`. Its contrast against the status-card background is **5.84:1**, above the WCAG AA minimum of 4.5:1 for normal text.

## Render-Blocking Font Request

Replaced the external Google Fonts stylesheet with Next.js `next/font/google` for DM Sans and Space Mono. The fonts are now self-hosted with `display: swap`; rerun Lighthouse to quantify any remaining render-blocking savings.

## After Lighthouse Results

Compared with the October 14 baseline, the after run scored **100** in all four categories; Accessibility rose from **96 to 100**. Performance remained **100**. FCP improved from **0.4 s to 0.2 s**, Speed Index from **0.4 s to 0.2 s**, and CLS from **0.012 to 0**; LCP remained **0.5 s** and TBT **0 ms**.

The previous **240 ms** render-blocking savings estimate is no longer displayed after self-hosting the fonts. The after run still reports **205 KiB** of unused JavaScript, **13 KiB** of legacy JavaScript, and a network dependency-tree insight. These are lab-run comparisons and may vary between runs.
