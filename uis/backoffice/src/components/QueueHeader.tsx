import { useUiStore } from "../store/uiStore";
import { FilterSelect } from "./FilterSelect";
import type { Catalogs } from "../types";

export function QueueHeader({ catalogs }: { catalogs: Catalogs }) {
  const filters = useUiStore((state) => state.filters);
  const setFilter = useUiStore((state) => state.setFilter);
  const clearFilters = useUiStore((state) => state.clearFilters);
  return (
    <>
      <div className="panel-header">
        <div>
          <p className="eyebrow">Live queue</p>
          <h2>All incidents</h2>
        </div>
        <span className="result-count">Use filters to focus the queue</span>
      </div>
      <div className="filters" role="search">
        <label className="search-field">
          <span>⌕</span>
          <input
            value={filters.search}
            onChange={(event) => setFilter("search", event.target.value)}
            type="search"
            placeholder="Search title, description or reporter"
          />
        </label>
        <FilterSelect
          label="status"
          value={filters.status}
          options={catalogs.statuses}
          onChange={setFilter}
        />
        <FilterSelect
          label="severity"
          value={filters.severity}
          options={catalogs.severities}
          onChange={setFilter}
        />
        <FilterSelect
          label="responsible_area"
          value={filters.responsible_area}
          options={catalogs.responsible_areas}
          onChange={setFilter}
        />
        <button
          className="button button-quiet"
          type="button"
          onClick={clearFilters}
        >
          Clear
        </button>
      </div>
    </>
  );
}
