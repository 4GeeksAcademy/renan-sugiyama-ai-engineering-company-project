type Metric = {
  label: string;
  value: string;
  delta: string;
  tone: "positive" | "warning" | "critical";
};

type DepartmentPanel = {
  title: string;
  badge: string;
  badgeClass: "positive" | "warning" | "critical";
  metricLabel: string;
  metricValue: string;
  progress: number;
  alerts: string[];
};

const metrics: Metric[] = [
  {
    label: "Support SLA compliance",
    value: "76%",
    delta: "Target 90%",
    tone: "warning",
  },
  {
    label: "CRM adoption",
    value: "40%",
    delta: "Record upkeep",
    tone: "critical",
  },
  {
    label: "Average resolution time",
    value: "48h",
    delta: "Target 24h",
    tone: "critical",
  },
  {
    label: "Weekly operational risk",
    value: "12",
    delta: "Escalations",
    tone: "warning",
  },
];

const panels: DepartmentPanel[] = [
  {
    title: "Support outsourcing",
    badge: "SLA risk",
    badgeClass: "critical",
    metricLabel: "SLA compliance",
    metricValue: "76%",
    progress: 76,
    alerts: [
      "Backlog is concentrated in chat and email channels.",
      "Seven tickets are above target and need reassignment.",
      "Knowledge base coverage is still uneven across teams.",
    ],
  },
  {
    title: "Sales pipeline",
    badge: "Follow-up",
    badgeClass: "warning",
    metricLabel: "CRM updates",
    metricValue: "40%",
    progress: 40,
    alerts: [
      "Only 40% of SDRs maintain CRM records consistently.",
      "Follow-up delays remain the main reason for lost opportunities.",
      "Inactive deals need intervention before next week.",
    ],
  },
  {
    title: "Training programmes",
    badge: "Engagement",
    badgeClass: "positive",
    metricLabel: "Completion rate",
    metricValue: "68%",
    progress: 68,
    alerts: [
      "Training catalogue needs better discoverability and segmentation.",
      "Enrolment flow is still manual and spreadsheet-based.",
      "Most learners are requesting more role-specific programmes.",
    ],
  },
  {
    title: "Internal HR",
    badge: "Coverage",
    badgeClass: "warning",
    metricLabel: "Onboarding completion",
    metricValue: "82%",
    progress: 82,
    alerts: [
      "Holiday and absence requests still rely on manual email workflows.",
      "Onboarding tasks remain fragmented across teams.",
      "Performance review tracking is not centralised yet.",
    ],
  },
];

function App() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brandMark">N</div>
          <div>
            <div className="brandTitle">Nexova</div>
            <div className="brandSubtitle">Operations</div>
          </div>
        </div>

        <nav className="nav" aria-label="Dashboard navigation">
          <span className="navLabel">Overview</span>
          <a className="active" href="#">
            Dashboard
          </a>
          <a href="#">Support</a>
          <a href="#">Sales</a>
          <a href="#">Training</a>
          <a href="#">HR</a>
        </nav>

        <div className="statusCard">
          <span className="statusDot" />
          <div>
            <strong>Operations status</strong>
            <small>Needs attention</small>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <div className="eyebrow">Executive view</div>
            <h1>Performance dashboard</h1>
          </div>
          <button className="ctaButton">Generate report</button>
        </header>

        <section className="metricsGrid">
          {metrics.map((metric) => (
            <article key={metric.label} className="metricCard">
              <div className="metricHeader">
                <span>{metric.label}</span>
                <span className={`metricTone ${metric.tone}`}>
                  {metric.delta}
                </span>
              </div>
              <div className="metricValue">{metric.value}</div>
            </article>
          ))}
        </section>

        <section className="contentGrid">
          {panels.map((panel) => (
            <article key={panel.title} className="panel">
              <div className="panelHeader">
                <h2>{panel.title}</h2>
                <span className={`chip ${panel.badgeClass}`}>
                  {panel.badge}
                </span>
              </div>

              <div className="progressBlock">
                <div className="progressMeta">
                  <span>{panel.metricLabel}</span>
                  <strong>{panel.metricValue}</strong>
                </div>
                <div className="progressTrack">
                  <div
                    className={`progressFill ${panel.badgeClass}`}
                    style={{ width: `${panel.progress}%` }}
                  />
                </div>
              </div>

              <ul className="alertList">
                {panel.alerts.map((alert) => (
                  <li key={alert}>{alert}</li>
                ))}
              </ul>
            </article>
          ))}
        </section>
      </main>
    </div>
  );
}

export default App;
