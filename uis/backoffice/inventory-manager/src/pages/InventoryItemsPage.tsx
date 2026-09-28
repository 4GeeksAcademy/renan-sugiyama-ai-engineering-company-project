import { useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  inventoryApi,
  type InventoryItem,
  type InventoryItemCreate,
  type InventoryItemList,
  type InventoryItemUpdate,
  type InventoryUnit,
} from "../api/inventoryClient";

const units: InventoryUnit[] = [
  "unit",
  "pack",
  "box",
  "ream",
  "roll",
  "liter",
  "kg",
];

function formatQuantity(value: number | null, unit: string): string {
  return value === null
    ? "No movements"
    : `${new Intl.NumberFormat(undefined, { maximumFractionDigits: 3 }).format(value)} ${unit}`;
}

function ItemError({ message }: { message: string }) {
  return (
    <p className="inventory-error" role="alert">
      {message}
    </p>
  );
}

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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export function InventoryItemFormPage() {
  const { itemId } = useParams();
  const itemQuery = useQuery({
    queryKey: ["inventory-item", itemId],
    queryFn: () =>
      inventoryApi<InventoryItem>(
        `/inventory/items/${encodeURIComponent(itemId!)}`,
      ),
    enabled: Boolean(itemId),
  });

  if (itemId && itemQuery.isLoading) {
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
  return <InventoryItemForm key={itemId || "new"} item={itemQuery.data} />;
}

function InventoryItemForm({ item }: { item?: InventoryItem }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [id, setId] = useState(item?.id || "");
  const [name, setName] = useState(item?.name || "");
  const [unit, setUnit] = useState<InventoryUnit>(item?.unit || "unit");
  const [reorderPoint, setReorderPoint] = useState(
    item?.reorder_point?.toString() || "",
  );
  const mutation = useMutation<
    InventoryItem,
    Error,
    InventoryItemCreate | InventoryItemUpdate
  >({
    mutationFn: (payload) =>
      item
        ? inventoryApi<InventoryItem>(
            `/inventory/items/${encodeURIComponent(item.id)}`,
            { method: "PATCH", body: JSON.stringify(payload) },
          )
        : inventoryApi<InventoryItem>("/inventory/items", {
            method: "POST",
            body: JSON.stringify(payload),
          }),
    onSuccess: async (savedItem) => {
      await queryClient.invalidateQueries({ queryKey: ["inventory-items"] });
      await queryClient.invalidateQueries({
        queryKey: ["inventory-item", savedItem.id],
      });
      navigate(`/inventory/${encodeURIComponent(savedItem.id)}`);
    },
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fields = {
      name: name.trim(),
      unit,
      reorder_point: reorderPoint === "" ? null : Number(reorderPoint),
    };
    mutation.mutate(item ? fields : { id: id.trim(), ...fields });
  }

  return (
    <section className="workspace-panel inventory-form-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">
            {item ? `Item ${item.id}` : "Materials register"}
          </p>
          <h2>{item ? "Edit inventory item" : "Create inventory item"}</h2>
        </div>
      </div>
      <form className="inventory-form" onSubmit={submit}>
        <div className="form-grid">
          {!item && (
            <label className="form-field">
              <span>Item ID</span>
              <input
                autoComplete="off"
                required
                value={id}
                onChange={(event) => setId(event.target.value)}
              />
            </label>
          )}
          <label className="form-field">
            <span>Name</span>
            <input
              required
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
          </label>
          <label className="form-field">
            <span>Unit of measure</span>
            <select
              value={unit}
              onChange={(event) => setUnit(event.target.value as InventoryUnit)}
            >
              {units.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="form-field">
            <span>Reorder point</span>
            <input
              min="0"
              step="any"
              type="number"
              value={reorderPoint}
              onChange={(event) => setReorderPoint(event.target.value)}
            />
          </label>
        </div>
        {mutation.error && <ItemError message={mutation.error.message} />}
        <div className="form-actions">
          <Link
            className="button button-quiet"
            to={
              item ? `/inventory/${encodeURIComponent(item.id)}` : "/inventory"
            }
          >
            Cancel
          </Link>
          <button
            className="button button-primary"
            type="submit"
            disabled={mutation.isPending}
          >
            {mutation.isPending
              ? "Saving..."
              : item
                ? "Save changes"
                : "Create item"}
          </button>
        </div>
      </form>
    </section>
  );
}

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
