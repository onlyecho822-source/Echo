"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const [form, setForm] = useState({
    title: "",
    niche: "",
    audience: "",
    format: ""
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function generate() {
    try {
      setLoading(true);
      setError("");

      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Generation failed");
      }

      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-3xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
            Product Bloom Engine
          </h1>
          <p className="text-zinc-400 text-lg">
            Generate complete digital products with AI
          </p>
        </div>

        <div className="card space-y-4">
          <input
            className="input"
            placeholder="Product Title (e.g., 'Complete Fitness Guide')"
            value={form.title}
            onChange={e => setForm({ ...form, title: e.target.value })}
          />
          <input
            className="input"
            placeholder="Niche (e.g., 'Health & Wellness')"
            value={form.niche}
            onChange={e => setForm({ ...form, niche: e.target.value })}
          />
          <input
            className="input"
            placeholder="Target Audience (e.g., 'Busy professionals')"
            value={form.audience}
            onChange={e => setForm({ ...form, audience: e.target.value })}
          />
          <input
            className="input"
            placeholder="Format (e.g., 'PDF Guide', 'Video Course')"
            value={form.format}
            onChange={e => setForm({ ...form, format: e.target.value })}
          />

          {error && (
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-4 text-red-400">
              {error}
            </div>
          )}

          <button
            className="btn"
            onClick={generate}
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Product"}
          </button>
        </div>
      </div>
    </div>
  );
}
