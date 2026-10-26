import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  inventoryApi,
  type InventoryItem,
  type InventoryItemList,
} from "../api/inventoryClient";
import {
  formatQuantity,
  isBelowReorderPoint,
  ItemError,
} from "./inventoryItemHelpers";

export function InventoryItemsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["inventory-items"],
    queryFn: () => inventoryApi<InventoryItemList>("/inventory/items"),
  });

  return (
    <section className="workspace-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Materials register</p>
          <h2>Inventory items</h2>
        </div>
        <span className="result-count">
          {data ? `${data.items.length} active items` : ""}
        </span>
      </div>
      {isLoading ? (
        <div className="loading-state">Loading inventory items...</div>
      ) : error ? (
        <div className="inventory-empty">
          <ItemError message={error.message} />
        </div>
      ) : data.items.length === 0 ? (
        <div className="inventory-empty">
          <p>No inventory items yet.</p>
          <Link className="button button-primary" to="/inventory/new">
            Create first item
          </Link>
        </div>
      ) : (
        <div className="table-wrap">
          <table className="inventory-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Unit</th>
                <th>Reorder point</th>
                <th>Current stock</th>
                <th>Stock signal</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <Link
                      className="item-link"
                      to={`/inventory/${encodeURIComponent(item.id)}`}
                    >
                      {item.name}
                    </Link>
                    <span className="item-id">{item.id}</span>
                  </td>
                  <td>{item.unit}</td>
                  <td>
                    {item.reorder_point === null
                      ? "Not set"
                      : formatQuantity(item.reorder_point, item.unit)}
                  </td>
                  <td>{formatQuantity(item.current_stock, item.unit)}</td>
                  <td>
                    {isBelowReorderPoint(item) ? (
                      <span className="reorder-signal">
                        Replenishment needed
                      </span>
                    ) : (
                      "-"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
