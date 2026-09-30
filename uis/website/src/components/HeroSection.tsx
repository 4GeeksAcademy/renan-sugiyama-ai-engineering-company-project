import "./HeroSection.css";

function HeroSection() {
  return (
    <section className="heroSection">
      <div className="container heroGrid">
        <div className="heroCopy">
          <span className="eyebrow">AI Engineering for people operations</span>
          <h1>We help companies hire, train, and support talent at scale.</h1>
          <p>
            Nexova Solutions turns complex people operations into clear systems,
            measurable performance, and faster decision-making for modern
            businesses.
          </p>

          <div className="heroActions">
            <a className="primaryButton" href="#contact">
              Book a discovery call
            </a>
            <a className="secondaryButton" href="#services">
              Explore services
            </a>
          </div>

          <div className="heroMeta">
            <div>
              <strong>120+</strong>
              <span>People in operation</span>
            </div>
            <div>
              <strong>8M€</strong>
              <span>Annual revenue</span>
            </div>
            <div>
              <strong>2 offices</strong>
              <span>Valencia & Miami</span>
            </div>
          </div>
        </div>

        <div className="heroPanel card" aria-label="Nexova business overview">
          <div className="panelHeader">
            <span>Operational signal</span>
            <span className="signalPill">Live</span>
          </div>

          <div className="panelMetricRow">
            <div>
              <div className="metricLabel">SLA compliance</div>
              <div className="metricValue">92%</div>
            </div>
            <div className="metricDelta positive">+12.4%</div>
          </div>

          <div className="miniGrid">
            <div className="miniCard">
              <span className="miniLabel">Headcount</span>
              <strong>1,240</strong>
              <small>talent placements</small>
            </div>
            <div className="miniCard accent">
              <span className="miniLabel">Training</span>
              <strong>4.8k</strong>
              <small>learners engaged</small>
            </div>
          </div>

          <ul className="detailList">
            <li>Executive search and hiring operations</li>
            <li>Support outsourcing with SLA control</li>
            <li>Leadership and soft-skills training</li>
          </ul>
        </div>
      </div>
    </section>
  );
}

export default HeroSection;
