# Website Lighthouse Audit

Run against `http://localhost:3000/` on October 14, 2026, using Lighthouse 13.4.1 with desktop emulation and custom throttling.

## Scores

- Performance: **99**. Core metrics were strong: FCP 0.8 s, LCP 0.8 s, Speed Index 0.8 s, Total Blocking Time 0 ms, and CLS 0.008.
- Accessibility: **95**.
- Best Practices: **100**.
- SEO: **100**.

## Main Problems to Solve

- **Improve text contrast.** Lighthouse reports that some foreground/background color combinations do not meet the required contrast ratio. Identify the affected elements and adjust their colors, then verify contrast in the rendered page.
- **Remove or defer render-blocking requests.** Lighthouse estimates a potential 540 ms saving. Inspect the reported request chain and defer or optimize resources that are not needed for the initial render.
- **Reduce unused JavaScript.** Lighthouse estimates 205 KiB could be removed. Source and production manifest inspection found no application-owned client components or third-party scripts; the browser bundles are Next.js runtime code. No safe component-level splitting or dead-code removal is available without changing the site's delivery architecture.
- **Reduce legacy JavaScript.** Lighthouse estimates 13 KiB of savings. Review the compatibility/transpilation targets and dependencies to avoid shipping unnecessary legacy code to modern browsers.

Lighthouse also flags the network dependency tree for investigation, but the screenshot does not provide enough detail to identify a specific offending request. The SEO structured-data check is listed for manual validation, not as a failed audit.

## Core Web Vitals Follow-Up

- **Verify and optimize font delivery (LCP).** `src/app/layout.tsx` loads DM Sans and Space Mono through an external Google Fonts stylesheet. Check whether those font requests appear in Lighthouse's render-blocking request details. If they do, test Next.js `next/font` to self-host the fonts and compare the same lab run; do not assume the font request accounts for the full 540 ms estimate.
- **Check for font-related layout shifts (CLS).** The Google Fonts URL uses `display=swap`, so fallback fonts can be replaced after first paint. The measured CLS of 0.008 is already good; compare cold-load traces and only treat this as a defect if the font swap produces visible shifts.
- **Measure INP through real interactions.** This Lighthouse screenshot reports a page-load run, not an INP result. The homepage source has no client components or custom event handlers, so there is no code evidence of an interaction bottleneck. Measure representative navigation interactions and, after deployment, review field p75 data before targeting INP changes.

Because the run targets `localhost`, it cannot provide representative CrUX field data. Treat the results above as lab evidence, not as proof of real-user p75 performance.
