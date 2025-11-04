
import { useEffect, useState } from "react";
import { checkBackendHealth } from "../utils/api";

export default function Dashboard() {
  const [health, setHealth] = useState("checking...");

  useEffect(() => {
    checkBackendHealth().then((res) => setHealth(res.status));
  }, []);

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Dashboard</h1>
      <p>Backend status: <strong>{health}</strong></p>
    </div>
  );
}
