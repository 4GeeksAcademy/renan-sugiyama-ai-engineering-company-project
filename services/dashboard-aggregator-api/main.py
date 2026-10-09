from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Nexova Dashboard Aggregator API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4173", "http://127.0.0.1:4173"],
    allow_methods=["GET"],
)

DASHBOARD = {
    "metrics": [
        {
            "label": "Support SLA compliance",
            "value": "76%",
            "delta": "Target 90%",
            "tone": "warning",
        },
        {
            "label": "CRM adoption",
            "value": "40%",
            "delta": "Record upkeep",
            "tone": "critical",
        },
        {
            "label": "Average resolution time",
            "value": "48h",
            "delta": "Target 24h",
            "tone": "critical",
        },
        {
            "label": "Weekly operational risk",
            "value": "12",
            "delta": "Escalations",
            "tone": "warning",
        },
    ],
    "panels": [
        {
            "title": "Support outsourcing",
            "badge": "SLA risk",
            "badgeClass": "critical",
            "metricLabel": "SLA compliance",
            "metricValue": "76%",
            "progress": 76,
            "alerts": [
                "Backlog is concentrated in chat and email channels.",
                "Seven tickets are above target and need reassignment.",
                "Knowledge base coverage is still uneven across teams.",
            ],
        },
        {
            "title": "Sales pipeline",
            "badge": "Follow-up",
            "badgeClass": "warning",
            "metricLabel": "CRM updates",
            "metricValue": "40%",
            "progress": 40,
            "alerts": [
                "Only 40% of SDRs maintain CRM records consistently.",
                "Follow-up delays remain the main reason for lost opportunities.",
                "Inactive deals need intervention before next week.",
            ],
        },
        {
            "title": "Training programmes",
            "badge": "Engagement",
            "badgeClass": "positive",
            "metricLabel": "Completion rate",
            "metricValue": "68%",
            "progress": 68,
            "alerts": [
                "Training catalogue needs better discoverability and segmentation.",
                "Enrolment flow is still manual and spreadsheet-based.",
                "Most learners are requesting more role-specific programmes.",
            ],
        },
        {
            "title": "Internal HR",
            "badge": "Coverage",
            "badgeClass": "warning",
            "metricLabel": "Onboarding completion",
            "metricValue": "82%",
            "progress": 82,
            "alerts": [
                "Holiday and absence requests still rely on manual email workflows.",
                "Onboarding tasks remain fragmented across teams.",
                "Performance review tracking is not centralised yet.",
            ],
        },
    ],
}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/dashboard")
def dashboard() -> dict:
    return DASHBOARD