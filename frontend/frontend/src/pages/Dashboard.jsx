export default function Dashboard() {
  const user = localStorage.getItem("token");

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-green-50">
      <h1 className="text-3xl font-bold mb-4 text-green-700">Welcome to SPIS Dashboard</h1>
      <p className="text-gray-600">You are logged in ✅</p>
      <button
        onClick={() => {
          localStorage.removeItem("token");
          window.location.href = "/login";
        }}
        className="mt-6 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
      >
        Logout
      </button>
    </div>
  );
}
