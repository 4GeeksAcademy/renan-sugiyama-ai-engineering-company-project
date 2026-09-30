import SiteHeader from "../components/SiteHeader";
import HeroSection from "../components/HeroSection";
import "./HomePage.css";

const services = [
  {
    title: "Executive search",
    description:
      "Targeted hiring strategies for leadership and specialist roles across critical business functions.",
    badge: "Talent selection",
  },
  {
    title: "Customer support outsourcing",
    description:
      "Operational support teams trained for service quality, faster resolution times, and stronger SLA performance.",
    badge: "Operations",
  },
  {
    title: "Corporate training",
    description:
      "Leadership and soft-skills programmes designed for team growth, engagement, and business performance.",
    badge: "Learning",
  },
];

const metrics = [
  { value: "12 years", label: "of market experience" },
  { value: "40+", label: "recruitment specialists" },
  { value: "30", label: "support agents in delivery" },
  { value: "24h", label: "average service response target" },
];

const advantages = [
  "AI-enabled workflows that remove repetitive manual work.",
  "Better commercial visibility with live operating metrics and reporting.",
  "Scalable service delivery across recruiting, support, and training.",
  "Human-centred execution grounded in real operational needs.",
];

function HomePage() {
  return (
    <>
      <SiteHeader />

      <main>
        <HeroSection />

        <section id="services" className="sectionWrap">
          <div className="container">
            <span className="eyebrow">What we do</span>
            <div className="sectionHeader">
              <h2 className="sectionTitle">
                Business capability across the full talent lifecycle.
              </h2>
              <p className="sectionIntro">
                We combine consulting, operational execution, and technology to
                help mid-sized companies attract the right talent, train teams
                effectively, and deliver support at scale.
              </p>
            </div>

            <div className="serviceGrid">
              {services.map((service) => (
                <article key={service.title} className="card serviceCard">
                  <span className="serviceBadge">{service.badge}</span>
                  <h3>{service.title}</h3>
                  <p>{service.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="solutions" className="sectionWrap altSection">
          <div className="container">
            <span className="eyebrow">Why Nexova</span>
            <div className="sectionHeader narrow">
              <h2 className="sectionTitle">
                Operational clarity for companies that need to grow without
                losing control.
              </h2>
            </div>

            <div className="metricsGrid">
              {metrics.map((metric) => (
                <div key={metric.label} className="card metricCard">
                  <div className="metricValue">{metric.value}</div>
                  <div className="metricLabelText">{metric.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="impact" className="sectionWrap">
          <div className="container highlightRow">
            <div>
              <span className="eyebrow">Built for scale</span>
              <h2 className="sectionTitle">
                From manual work to a measurable operating system.
              </h2>
            </div>

            <ul className="advantageList">
              {advantages.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </section>
      </main>

      <footer id="contact" className="siteFooter">
        <div className="container footerBlock card">
          <div>
            <span className="eyebrow">Let’s build the next chapter</span>
            <h2 className="sectionTitle smallTitle">
              Nexova helps businesses grow through better talent operations.
            </h2>
          </div>

          <div className="footerActions">
            <a className="primaryButton" href="mailto:hello@nexova.solutions">
              hello@nexova.solutions
            </a>
            <a className="secondaryButton" href="tel:+34900000000">
              +34 900 000 000
            </a>
          </div>
        </div>
      </footer>
    </>
  );
}

export default HomePage;
