export async function checkBackendHealth() {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/health/");
    const data = await res.json();
    return data;
  } catch (err) {
    console.error("Backend unreachable:", err);
    return { status: "error" };
  }
}
