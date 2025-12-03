import { z } from "zod";

export const zGenerate = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  niche: z.string().min(3, "Niche must be at least 3 characters"),
  audience: z.string().min(3, "Audience must be at least 3 characters"),
  format: z.string().min(3, "Format must be at least 3 characters")
});

export const zRegister = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters")
});

export const zLogin = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required")
});
