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
- **Reduce unused JavaScript.** Lighthouse estimates 205 KiB could be removed. Check the bundle and load only the code needed for the initial page and its active features.
- **Reduce legacy JavaScript.** Lighthouse estimates 13 KiB of savings. Review the compatibility/transpilation targets and dependencies to avoid shipping unnecessary legacy code to modern browsers.

Lighthouse also flags the network dependency tree for investigation, but the screenshot does not provide enough detail to identify a specific offending request. The SEO structured-data check is listed for manual validation, not as a failed audit.
