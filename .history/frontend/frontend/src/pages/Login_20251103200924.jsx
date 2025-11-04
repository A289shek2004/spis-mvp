
import { useState } from "react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Logging in with ${username}`);
  };

  return (
    <div style={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center", background: "#f5f5f5" }}>
      <form
        onSubmit={handleSubmit}
        style={{ background: "#fff", padding: "30px", borderRadius: "8px", width: "300px", boxShadow: "0 0 10px rgba(0,0,0,0.1)" }}
      >
        <h2 style={{ textAlign: "center" }}>Login</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ width: "100%", margin: "10px 0", padding: "10px" }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ width: "100%", margin: "10px 0", padding: "10px" }}
        />
        <button type="submit" style={{ width: "100%", padding: "10px", background: "#ddd", border: "none" }}>
          Login
        </button>
      </form>
    </div>
  );
}
