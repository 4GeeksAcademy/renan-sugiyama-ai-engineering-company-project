import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  inventoryApi,
  InventoryApiError,
  type InventoryItemList,
  type InventoryMovement,
  type InventoryMovementCreate,
  type InventoryMovementType,
} from "../api/inventoryClient";

const movementTypes: { value: InventoryMovementType; label: string }[] = [
  { value: "incoming_stock", label: "Incoming stock" },
  { value: "outgoing_stock", label: "Outgoing stock" },
  { value: "stock_adjustment", label: "Stock adjustment" },
];

function localDateTimeValue(): string {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

export function InventoryMovementPage() {
  const queryClient = useQueryClient();
  const [itemId, setItemId] = useState("");
  const [type, setType] = useState<InventoryMovementType>("incoming_stock");
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState("");
  const [recordedAt, setRecordedAt] = useState(localDateTimeValue);
  const [direction, setDirection] = useState<"increase" | "decrease">(
    "increase",
  );
  const itemsQuery = useQuery({
    queryKey: ["inventory-items"],
    queryFn: () => inventoryApi<InventoryItemList>("/inventory/items"),
  });
  const selectedItem = itemsQuery.data?.items.find(
    (item) => item.id === itemId,
  );
  const mutation = useMutation<
    InventoryMovement,
    Error,
    InventoryMovementCreate
  >({
    mutationFn: (payload) =>
      inventoryApi<InventoryMovement>("/inventory/movements", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: async (movement) => {
      await queryClient.invalidateQueries({ queryKey: ["inventory-items"] });
      await queryClient.invalidateQueries({
        queryKey: ["inventory-item", movement.item_id],
      });
      setQuantity("");
      setReason("");
      setRecordedAt(localDateTimeValue());
    },
  });

  const fieldErrors =
    mutation.error instanceof InventoryApiError
      ? mutation.error.fieldErrors
      : {};

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedItem) return;
    const payload: InventoryMovementCreate = {
      item_id: itemId,
      type,
      quantity: Number(quantity),
      reason: reason.trim(),
      recorded_at: new Date(recordedAt).toISOString(),
      unit: selectedItem.unit,
      direction: type === "stock_adjustment" ? direction : null,
    };
    mutation.mutate(payload);
  }

  function clearFeedback() {
    mutation.reset();
  }

  return (
    <section className="workspace-panel inventory-form-panel movement-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Stock history</p>
          <h2>Register inventory movement</h2>
        </div>
      </div>
      {itemsQuery.isLoading ? (
        <div className="loading-state">Loading inventory items...</div>
      ) : itemsQuery.error ? (
        <div className="inventory-form movement-form">
          <p className="inventory-error" role="alert">
            {itemsQuery.error.message}
          </p>
        </div>
      ) : itemsQuery.data?.items.length === 0 ? (
        <div className="inventory-empty">
          <p>Create an inventory item before registering a movement.</p>
          <Link className="button button-primary" to="/new">
            Create inventory item
          </Link>
        </div>
      ) : (
        <form className="inventory-form movement-form" onSubmit={submit}>
          {mutation.isSuccess && (
            <p className="movement-success" role="status">
              Movement recorded for {selectedItem?.name || "the selected item"}.
            </p>
          )}
          <div className="form-grid">
            <label className="form-field">
              <span>Inventory item</span>
              <select
                required
                value={itemId}
                aria-invalid={Boolean(fieldErrors.item_id)}
                aria-describedby={
                  fieldErrors.item_id ? "movement-item-error" : undefined
                }
                onChange={(event) => {
                  setItemId(event.target.value);
                  clearFeedback();
                }}
              >
                <option value="" disabled>
                  Select an item
                </option>
                {itemsQuery.data?.items.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name} ({item.id})
                  </option>
                ))}
              </select>
              {fieldErrors.item_id && (
                <small id="movement-item-error" className="field-error">
                  {fieldErrors.item_id}
                </small>
              )}
            </label>
            <label className="form-field">
              <span>Movement type</span>
              <select
                value={type}
                aria-invalid={Boolean(fieldErrors.type)}
                aria-describedby={
                  fieldErrors.type ? "movement-type-error" : undefined
                }
                onChange={(event) => {
                  setType(event.target.value as InventoryMovementType);
                  clearFeedback();
                }}
              >
                {movementTypes.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {fieldErrors.type && (
                <small id="movement-type-error" className="field-error">
                  {fieldErrors.type}
                </small>
              )}
            </label>
            {type === "stock_adjustment" && (
              <label className="form-field">
                <span>Adjustment direction</span>
                <select
                  value={direction}
                  aria-invalid={Boolean(fieldErrors.direction)}
                  aria-describedby={
                    fieldErrors.direction
                      ? "movement-direction-error"
                      : undefined
                  }
                  onChange={(event) => {
                    setDirection(event.target.value as "increase" | "decrease");
                    clearFeedback();
                  }}
                >
                  <option value="increase">Increase stock</option>
                  <option value="decrease">Decrease stock</option>
                </select>
                {fieldErrors.direction && (
                  <small id="movement-direction-error" className="field-error">
                    {fieldErrors.direction}
                  </small>
                )}
              </label>
            )}
            <label className="form-field">
              <span>Quantity</span>
              <input
                required
                min="0.000001"
                step="any"
                type="number"
                value={quantity}
                aria-invalid={Boolean(fieldErrors.quantity)}
                aria-describedby={
                  fieldErrors.quantity ? "movement-quantity-error" : undefined
                }
                onChange={(event) => {
                  setQuantity(event.target.value);
                  clearFeedback();
                }}
              />
              {fieldErrors.quantity && (
                <small id="movement-quantity-error" className="field-error">
                  {fieldErrors.quantity}
                </small>
              )}
            </label>
            <label className="form-field">
              <span>Item unit</span>
              <input
                readOnly
                value={selectedItem?.unit || ""}
                placeholder="Select an item"
              />
              {fieldErrors.unit && (
                <small className="field-error">{fieldErrors.unit}</small>
              )}
            </label>
            <label className="form-field">
              <span>Recorded at</span>
              <input
                required
                type="datetime-local"
                value={recordedAt}
                aria-invalid={Boolean(fieldErrors.recorded_at)}
                aria-describedby={
                  fieldErrors.recorded_at
                    ? "movement-recorded-at-error"
                    : undefined
                }
                onChange={(event) => {
                  setRecordedAt(event.target.value);
                  clearFeedback();
                }}
              />
              {fieldErrors.recorded_at && (
                <small id="movement-recorded-at-error" className="field-error">
                  {fieldErrors.recorded_at}
                </small>
              )}
            </label>
            <label className="form-field movement-reason">
              <span>Reason</span>
              <textarea
                required
                rows={3}
                value={reason}
                aria-invalid={Boolean(fieldErrors.reason)}
                aria-describedby={
                  fieldErrors.reason ? "movement-reason-error" : undefined
                }
                onChange={(event) => {
                  setReason(event.target.value);
                  clearFeedback();
                }}
              />
              {fieldErrors.reason && (
                <small id="movement-reason-error" className="field-error">
                  {fieldErrors.reason}
                </small>
              )}
            </label>
          </div>
          {mutation.error && (
            <p className="inventory-error" role="alert">
              {mutation.error.message}
            </p>
          )}
          <div className="form-actions">
            <Link className="button button-quiet" to="/">
              Cancel
            </Link>
            <button
              className="button button-primary"
              type="submit"
              disabled={mutation.isPending || !selectedItem}
            >
              {mutation.isPending ? "Recording..." : "Record movement"}
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
