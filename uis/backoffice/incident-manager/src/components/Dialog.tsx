import { useNavigate } from "react-router-dom";
import type { ReactNode } from "react";

export function Dialog({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  return (
    <div className="modal-backdrop">
      <section className="modal" role="dialog" aria-modal="true">
        <button
          className="modal-close"
          type="button"
          onClick={() => navigate(-1)}
          aria-label="Close"
        >
          ×
        </button>
        {children}
      </section>
    </div>
  );
}
