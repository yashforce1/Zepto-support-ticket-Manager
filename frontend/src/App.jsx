import { useState } from "react";
import Analyze from "./pages/Analyze";
import Dashboard from "./pages/Dashboard";
import "./App.css";

function App() {
  const [tab, setTab] = useState("dashboard");

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark">Z</div>
          <div className="brand-text">
            <h1>Zepto Support AI</h1>
            <span className="brand-sub">AI-powered ticket triage &amp; resolution</span>
          </div>
        </div>
        <nav className="tab-nav">
          <button
            className={tab === "dashboard" ? "tab active" : "tab"}
            onClick={() => setTab("dashboard")}
          >
            Dashboard
          </button>
          <button
            className={tab === "analyze" ? "tab active" : "tab"}
            onClick={() => setTab("analyze")}
          >
            Analyze Ticket
          </button>
        </nav>
      </header>

      <main>
        {tab === "analyze" ? (
          <Analyze />
        ) : (
          <Dashboard onSimulate={() => setTab("analyze")} />
        )}
      </main>
    </div>
  );
}

export default App;