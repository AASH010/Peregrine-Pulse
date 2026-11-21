// Dashboard skeleton (tasks DSH-01 to DSH-06). Screens are placeholders until their tasks are done.
const SCREENS = [
  { id: "DSH-02", name: "Emergency Simulation", purpose: "Create a simulated emergency: type, capability, network condition." },
  { id: "DSH-03", name: "Risk Assessment", purpose: "Level, confidence, explanation and recommended action." },
  { id: "DSH-04", name: "Responder Selection", purpose: "Candidates, criteria, exclusions and the selected entity." },
  { id: "DSH-05", name: "Acknowledgment & Escalation", purpose: "Simulate acknowledgment or failure and observe the alternative." },
  { id: "DSH-06", name: "Incident Timeline", purpose: "Evidence-backed stages, transport path and SIMULATED badges." },
];

export default function App() {
  return (
    <main className="page">
      <header>
        <h1>PeregrinePulse Dashboard</h1>
        <p className="notice" role="note">
          Prototype skeleton. Everything shown in this dashboard is simulated and must not be relied upon in a real
          emergency.
        </p>
      </header>
      <section aria-labelledby="planned">
        <h2 id="planned">Planned screens</h2>
        <ul className="cards">
          {SCREENS.map((screen) => (
            <li key={screen.id} className="card">
              <span className="badge">{screen.id}</span>
              <h3>{screen.name}</h3>
              <p>{screen.purpose}</p>
              <span className="badge badge-simulated">SIMULATED</span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
