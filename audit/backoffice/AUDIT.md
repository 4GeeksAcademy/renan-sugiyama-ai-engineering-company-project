# Backoffice Lighthouse Audit

Run against `http://localhost:3001/` on October 14, 2026, using Lighthouse 13.4.1 with desktop emulation and custom throttling.

## Scores

- Performance: **100**. First Contentful Paint: 0.4 s; Largest Contentful Paint: 0.5 s; Speed Index: 0.4 s; Total Blocking Time: 0 ms; Cumulative Layout Shift: 0.012.
- Accessibility: **96**.
- Best Practices: **100**.
- SEO: **100**.

## Main Problems to Solve

- **Improve text contrast.** Lighthouse reports foreground/background color combinations with insufficient contrast. Identify the affected controls and text, correct the colors, and verify them against WCAG contrast requirements.
- **Reduce render-blocking requests.** Lighthouse estimates a potential 240 ms saving. Inspect the listed requests and defer or optimize resources not required for the initial render.
- **Reduce unused JavaScript.** Lighthouse estimates 205 KiB could be removed. Inspect the shipped bundles and avoid loading code not needed for the current page or workflow.
- **Reduce legacy JavaScript.** Lighthouse estimates 13 KiB of savings. Review browser targets and dependencies to limit unnecessary compatibility code.
- **Investigate the network dependency tree.** Lighthouse flags the request tree as an insight. Inspect it for avoidable dependencies or long critical request chains; the screenshot does not identify a specific problematic request.

The performance metrics are already strong and all other category scores are 100. The structured-data SEO item and security-policy items are shown as manual/informational checks, not failed audits.
