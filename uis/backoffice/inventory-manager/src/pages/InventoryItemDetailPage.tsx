import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { inventoryApi, type InventoryItem } from "../api/inventoryClient";
import {
  formatQuantity,
  isBelowReorderPoint,
  ItemError,
} from "./inventoryItemHelpers";

export function InventoryItemDetailPage() {
  const { itemId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const itemQuery = useQuery({
    queryKey: ["inventory-item", itemId],
    queryFn: () =>
      inventoryApi<InventoryItem>(
        `/inventory/items/${encodeURIComponent(itemId!)}`,
      ),
    enabled: Boolean(itemId),
  });
  const archiveMutation = useMutation<null, Error, void>({
    mutationFn: () =>
      inventoryApi<null>(`/inventory/items/${encodeURIComponent(itemId!)}`, {
        method: "DELETE",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["inventory-items"] });
      await queryClient.removeQueries({ queryKey: ["inventory-item", itemId] });
      navigate("/inventory");
    },
  });

  if (itemQuery.isLoading) {
    return <div className="loading-state">Loading item...</div>;
  }
  if (itemQuery.error) {
    return (
      <section className="workspace-panel inventory-empty">
        <ItemError message={itemQuery.error.message} />
        <Link className="button button-quiet" to="/inventory">
          Back to items
        </Link>
      </section>
    );
  }
  const item = itemQuery.data;
  if (!item) return null;

  return (
    <section className="workspace-panel inventory-detail-panel">
      <div className="panel-header inventory-detail-header">
        <div>
          <p className="eyebrow">Inventory item · {item.id}</p>
          <h2>{item.name}</h2>
        </div>
        <div className="action-row">
          <Link
            className="button button-quiet"
            to={`/inventory/${encodeURIComponent(item.id)}/edit`}
          >
            Edit item
          </Link>
          <button
            className="button button-danger"
            type="button"
            disabled={archiveMutation.isPending}
            onClick={() => {
              if (window.confirm(`Archive ${item.name}?`)) {
                archiveMutation.mutate();
              }
            }}
          >
            {archiveMutation.isPending ? "Archiving..." : "Archive item"}
          </button>
        </div>
      </div>
      {archiveMutation.error && (
        <ItemError message={archiveMutation.error.message} />
      )}
      {isBelowReorderPoint(item) && (
        <p className="reorder-signal reorder-signal-banner" role="alert">
          Replenishment needed: current stock of{" "}
          {formatQuantity(item.current_stock, item.unit)} is below the reorder
          point of {formatQuantity(item.reorder_point, item.unit)}.
        </p>
      )}
      <div className="inventory-detail-grid">
        <div>
          <span className="detail-label">Item ID</span>
          <span className="detail-value">{item.id}</span>
        </div>
        <div>
          <span className="detail-label">Unit of measure</span>
          <span className="detail-value">{item.unit}</span>
        </div>
        <div>
          <span className="detail-label">Reorder point</span>
          <span className="detail-value">
            {item.reorder_point === null
              ? "Not set"
              : formatQuantity(item.reorder_point, item.unit)}
          </span>
        </div>
        <div>
          <span className="detail-label">Current stock · derived</span>
          <span className="detail-value">
            {formatQuantity(item.current_stock, item.unit)}
          </span>
        </div>
      </div>
      <div className="inventory-detail-footer">
        <Link className="button button-quiet" to="/inventory">
          Back to items
        </Link>
      </div>
    </section>
  );
}
