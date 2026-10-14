# Backoffice Lighthouse Audit

Run against `http://localhost:3001/` on October 14, 2026, using Lighthouse 13.4.1 with desktop emulation and custom throttling.

## Scores

- Performance: **100**. First Contentful Paint: 0.4 s; Largest Contentful Paint: 0.5 s; Speed Index: 0.4 s; Total Blocking Time: 0 ms; Cumulative Layout Shift: 0.012.
- Accessibility: **96**.
- Best Practices: **100**.
- SEO: **100**.

## Main Problems to Solve

- **Improve text contrast (code fix applied).** Updated the dashboard text colors to pass WCAG AA contrast checks; re-run Lighthouse to verify the reported audit is cleared.
- **Reduce render-blocking requests.** Lighthouse estimates a potential 240 ms saving. Inspect the listed requests and defer or optimize resources not required for the initial render.
- **Reduce unused JavaScript.** Lighthouse estimates 205 KiB could be removed. Inspect the shipped bundles and avoid loading code not needed for the current page or workflow.
- **Reduce legacy JavaScript.** Lighthouse estimates 13 KiB of savings. Review browser targets and dependencies to limit unnecessary compatibility code.
- **Investigate the network dependency tree.** Lighthouse flags the request tree as an insight. Inspect it for avoidable dependencies or long critical request chains; the screenshot does not identify a specific problematic request.

The performance metrics are already strong and all other category scores are 100. The structured-data SEO item and security-policy items are shown as manual/informational checks, not failed audits.

## Core Web Vitals Follow-Up

- **Check external font loading (LCP).** `src/app/layout.tsx` loads DM Sans and Space Mono from Google Fonts through a stylesheet in the document head. Verify whether these requests are in Lighthouse's render-blocking list. If so, test Next.js `next/font` to self-host the fonts and compare equivalent runs; do not attribute the full 240 ms estimate to fonts without inspecting the request details.
- **Measure API latency impact on LCP.** `src/app/page.tsx` waits for `/dashboard` with `cache: "no-store"` on every page request and allows the fetch to run for up to five seconds. The audited lab run was fast (LCP 0.5 s), but slower API responses can delay server-rendered dashboard content. Capture TTFB and API timing under representative conditions; use short revalidation only if the dashboard's data-freshness needs allow it.
- **Stabilize the loading-to-dashboard transition (CLS).** `src/app/loading.tsx` renders only a short status line, while the completed page has a full sidebar and dashboard grid. If the API is slow, this fallback may be replaced by a much larger layout. Test with delayed API responses and, if shifts occur, use a skeleton that reserves the dashboard's major regions. The measured CLS of 0.012 is already good for the fast local run.
- **Measure INP with real interactions.** The Lighthouse capture is a page-load run, and `src/App.tsx` has no client components or custom event handlers. There is no source evidence of a JavaScript interaction bottleneck; measure actual dashboard interactions and deployed field p75 before prioritizing INP work.

The audit targets `localhost`, so it provides lab data rather than representative CrUX field measurements.
