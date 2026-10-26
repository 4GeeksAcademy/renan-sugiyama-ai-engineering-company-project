import { useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  inventoryApi,
  type InventoryItem,
  type InventoryItemCreate,
  type InventoryItemUpdate,
  type InventoryUnit,
} from "../api/inventoryClient";
import { ItemError } from "./inventoryItemHelpers";

const units: InventoryUnit[] = [
  "unit",
  "pack",
  "box",
  "ream",
  "roll",
  "liter",
  "kg",
];

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
