"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Register() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      setLoading(true);
      setError("");

      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Registration failed");
      }

      router.push("/auth/login");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
            Create Account
          </h1>
          <p className="text-zinc-400">Join Product Bloom today</p>
        </div>

        <form onSubmit={onSubmit} className="card space-y-4">
          <input
            type="email"
            className="input"
            placeholder="Email"
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            required
          />
          <input
            type="password"
            className="input"
            placeholder="Password (min 8 characters)"
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            required
          />

          {error && (
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-4 text-red-400">
              {error}
            </div>
          )}

          <button type="submit" className="btn" disabled={loading}>
            {loading ? "Creating account..." : "Register"}
          </button>

          <p className="text-center text-zinc-400 text-sm">
            Already have an account?{" "}
            <a href="/auth/login" className="text-purple-400 hover:text-purple-300">
              Sign in
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
