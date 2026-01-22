import { describe, it, expect, vi, beforeEach } from "vitest";
import { getProduct, PRODUCTS, formatPrice } from "./products";

describe("Stripe Products Configuration", () => {
  it("should have pro_monthly product defined", () => {
    const product = getProduct("pro_monthly");
    expect(product).toBeDefined();
    expect(product?.id).toBe("pro_monthly");
    expect(product?.price).toBe(4900);
    expect(product?.type).toBe("subscription");
  });

  it("should have enterprise product defined", () => {
    const product = getProduct("enterprise");
    expect(product).toBeDefined();
    expect(product?.id).toBe("enterprise");
    expect(product?.price).toBe(49900);
    expect(product?.type).toBe("subscription");
  });

  it("should have framework product defined", () => {
    const product = getProduct("framework");
    expect(product).toBeDefined();
    expect(product?.id).toBe("framework");
    expect(product?.price).toBe(29700);
    expect(product?.type).toBe("one_time");
  });

  it("should return undefined for non-existent product", () => {
    const product = getProduct("non_existent");
    expect(product).toBeUndefined();
  });

  it("should format price correctly", () => {
    expect(formatPrice(4900)).toBe("$49.00");
    expect(formatPrice(29700)).toBe("$297.00");
    expect(formatPrice(49900)).toBe("$499.00");
  });

  it("should have all required product fields", () => {
    Object.values(PRODUCTS).forEach(product => {
      expect(product.id).toBeDefined();
      expect(product.name).toBeDefined();
      expect(product.description).toBeDefined();
      expect(product.price).toBeGreaterThan(0);
      expect(product.currency).toBe("usd");
      expect(product.features).toBeInstanceOf(Array);
      expect(product.features.length).toBeGreaterThan(0);
    });
  });
});
