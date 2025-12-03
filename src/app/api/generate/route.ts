import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import prisma from "@/lib/prisma";
import { generateProduct } from "@/lib/openai";
import { zGenerate } from "@/utils/validators";

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await req.json();
    const parsed = zGenerate.parse(body);

    const content = await generateProduct(parsed);

    const product = await prisma.product.create({
      data: {
        ...parsed,
        content: content || "",
        userId: (session.user as any).id
      },
    });

    return NextResponse.json({ success: true, product });

  } catch (err: any) {
    console.error("Generation error:", err);
    return NextResponse.json({
      error: err.message || "Generation failed"
    }, { status: 500 });
  }
}
