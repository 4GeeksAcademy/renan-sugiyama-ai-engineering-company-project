# Inventory Manager Performance Decisions

## Lazy-loaded routes

The inventory list is the default view, so it remains in the initial bundle. The create/edit form, item detail view, and movement form are separate route modules loaded with `React.lazy` and `Suspense` in `uis/backoffice/inventory-manager/src/App.tsx`.

Deferring these routes is justified because users do not need their code to view the item list, and each workflow is only used after navigating to its route. Keeping these workflows out of the initial load reduces JavaScript downloaded and parsed for the common list-view entry path. The item form and detail view were separated from the list module so they can be split into independent chunks; the movement workflow was already a separate module.

## Memoized lookup

The movement form loads the active inventory-item list and finds the selected item by ID. The API returns the full list without pagination, making this a linear lookup whose cost grows with the number of active items. Form input updates trigger rerenders, so the lookup previously ran again while the item list and selected ID were unchanged.

`useMemo` caches this lookup using `inventoryItems` and `itemId` as dependencies. It recomputes when either the query result changes or the user selects a different item, and skips repeat scans during unrelated form-state updates. The memoization is limited to this list lookup; simple rendering and formatting operations remain un-memoized.

## Validation

The inventory manager passed `npm run typecheck` and `npm run build`. The production build emitted separate chunks for the item form, item detail, and movement route modules.
