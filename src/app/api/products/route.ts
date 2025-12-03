import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import prisma from "@/lib/prisma";

export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const products = await prisma.product.findMany({
      where: { userId: (session.user as any).id },
      orderBy: { createdAt: "desc" }
    });

    return NextResponse.json({ products });

  } catch (err: any) {
    console.error("Products fetch error:", err);
    return NextResponse.json({
      error: err.message || "Failed to fetch products"
    }, { status: 500 });
  }
}
