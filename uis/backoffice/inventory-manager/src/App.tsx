import {
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import {
  InventoryItemDetailPage,
  InventoryItemFormPage,
  InventoryItemsPage,
} from "./pages/InventoryItemsPage";
import { InventoryMovementPage } from "./pages/InventoryMovementPage";

export function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isForm = /\/new$|\/edit$/.test(location.pathname);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">N</span>
          <span>
            Nexova <strong>ops</strong>
          </span>
        </div>
        <p className="eyebrow">Materials management</p>
        <nav aria-label="Primary navigation">
          <NavLink
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
            end
            to="/"
          >
            <span className="nav-icon">▤</span> Inventory items
          </NavLink>
          <NavLink
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
            to="/movements/new"
          >
            <span className="nav-icon">↕</span> Register movement
          </NavLink>
          <button
            className="nav-item"
            type="button"
            onClick={() =>
              queryClient.invalidateQueries({ queryKey: ["inventory-items"] })
            }
          >
            <span className="nav-icon">↻</span> Refresh data
          </button>
        </nav>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>Inventory service</span>
          <small>Movement-derived stock</small>
        </div>
      </aside>
      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations workspace</p>
            <h1>Inventory manager</h1>
          </div>
          {!isForm && (
            <button
              className="button button-primary"
              type="button"
              onClick={() => navigate("/new")}
            >
              + New item
            </button>
          )}
        </header>
        <Routes>
          <Route path="/" element={<InventoryItemsPage />} />
          <Route path="/new" element={<InventoryItemFormPage />} />
          <Route path="/movements/new" element={<InventoryMovementPage />} />
          <Route path="/:itemId/edit" element={<InventoryItemFormPage />} />
          <Route path="/:itemId" element={<InventoryItemDetailPage />} />
        </Routes>
      </main>
    </div>
  );
}
