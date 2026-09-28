# Nexova inventory manager

Standalone React/Vite application for inventory item management.

## Run locally

```sh
npm install
npm run dev
```

The app sends `X-Inventory-User: local-user` to `http://localhost:8001` by default. Set `window.INVENTORY_API_URL` or `window.INVENTORY_USER_ID` before the app loads to override those values. The user must exist in the inventory API with the `inventory-manager` role.
