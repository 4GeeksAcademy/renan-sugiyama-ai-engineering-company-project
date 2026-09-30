import "./SiteHeader.css";

function SiteHeader() {
  return (
    <header className="siteHeader">
      <div className="container siteHeaderInner">
        <div className="brandWrap">
          <div className="brandMark">N</div>
          <div>
            <div className="brandName">Nexova</div>
            <div className="brandSub">Solutions</div>
          </div>
        </div>

        <nav className="mainNav" aria-label="Main navigation">
          <a href="#services">Services</a>
          <a href="#solutions">Solutions</a>
          <a href="#impact">Impact</a>
          <a href="#contact">Contact</a>
        </nav>

        <a className="primaryButton headerButton" href="#contact">
          Talk to us
        </a>
      </div>
    </header>
  );
}

export default SiteHeader;
