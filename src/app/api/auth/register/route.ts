import { NextRequest, NextResponse } from "next/server";
import prisma from "@/lib/prisma";
import bcrypt from "bcryptjs";
import { zRegister } from "@/utils/validators";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const parsed = zRegister.parse(body);

    const existing = await prisma.user.findUnique({
      where: { email: parsed.email }
    });

    if (existing) {
      return NextResponse.json({
        error: "Email already registered"
      }, { status: 400 });
    }

    const hashed = await bcrypt.hash(parsed.password, 10);

    const user = await prisma.user.create({
      data: {
        email: parsed.email,
        password: hashed
      }
    });

    return NextResponse.json({
      success: true,
      user: { id: user.id, email: user.email }
    });

  } catch (err: any) {
    console.error("Registration error:", err);
    return NextResponse.json({
      error: err.message || "Registration failed"
    }, { status: 500 });
  }
}
