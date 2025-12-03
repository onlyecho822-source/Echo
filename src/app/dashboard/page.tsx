import { redirect } from "next/navigation";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import prisma from "@/lib/prisma";

export default async function Dashboard() {
  const session = await getServerSession(authOptions);

  if (!session?.user) {
    redirect("/auth/login");
  }

  const products = await prisma.product.findMany({
    where: { userId: (session.user as any).id },
    orderBy: { createdAt: "desc" }
  });

  return (
    <div className="min-h-screen p-10">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
            Your Products
          </h1>
          <p className="text-zinc-400">
            {products.length} product{products.length !== 1 ? "s" : ""} generated
          </p>
        </div>

        {products.length === 0 ? (
          <div className="card text-center py-16">
            <p className="text-zinc-400 text-lg mb-4">
              No products yet. Start by generating your first one!
            </p>
            <a href="/generate" className="btn inline-block max-w-xs mx-auto">
              Generate Product
            </a>
          </div>
        ) : (
          <div className="grid gap-6">
            {products.map(p => (
              <div key={p.id} className="card">
                <div className="mb-4">
                  <h2 className="text-2xl font-bold text-white mb-2">{p.title}</h2>
                  <div className="flex gap-3 text-sm text-zinc-400">
                    <span className="bg-purple-500/20 px-3 py-1 rounded-full border border-purple-500/30">
                      {p.niche}
                    </span>
                    <span className="bg-pink-500/20 px-3 py-1 rounded-full border border-pink-500/30">
                      {p.audience}
                    </span>
                    <span className="bg-blue-500/20 px-3 py-1 rounded-full border border-blue-500/30">
                      {p.format}
                    </span>
                  </div>
                </div>

                <div className="bg-black border border-zinc-800 rounded-lg p-6 overflow-auto max-h-96">
                  <pre className="text-sm text-zinc-300 whitespace-pre-wrap font-mono">
                    {p.content}
                  </pre>
                </div>

                <div className="mt-4 text-xs text-zinc-500">
                  Generated {new Date(p.createdAt).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
