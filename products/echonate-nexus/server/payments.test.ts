import { describe, it, expect } from "vitest";
import { PRODUCTS, getProduct, formatPrice, getSubscriptionProducts, getOneTimeProducts } from "./products";

describe("Products Configuration", () => {
  it("should have all required products defined", () => {
    expect(PRODUCTS).toBeDefined();
    expect(Object.keys(PRODUCTS).length).toBeGreaterThan(0);
  });

  it("should have valid product structure", () => {
    for (const product of Object.values(PRODUCTS)) {
      expect(product.id).toBeDefined();
      expect(product.name).toBeDefined();
      expect(product.description).toBeDefined();
      expect(typeof product.price).toBe("number");
      expect(product.price).toBeGreaterThanOrEqual(0);
      expect(product.currency).toBe("usd");
      expect(["subscription", "one_time"]).toContain(product.type);
    }
  });

  it("should have pro and enterprise products", () => {
    expect(PRODUCTS.PRO_MONTHLY).toBeDefined();
    expect(PRODUCTS.ENTERPRISE).toBeDefined();
  });

  it("should get product by id", () => {
    const product = getProduct("pro_monthly");
    expect(product).toBeDefined();
    expect(product?.name).toBe("Pro Signal Access");
  });

  it("should return undefined for unknown product", () => {
    const product = getProduct("unknown_product");
    expect(product).toBeUndefined();
  });

  it("should format price correctly", () => {
    expect(formatPrice(4900)).toBe("$49.00");
    expect(formatPrice(49900)).toBe("$499.00");
    expect(formatPrice(0)).toBe("$0.00");
    expect(formatPrice(100)).toBe("$1.00");
  });
});

describe("Payment Flow", () => {
  it("should have correct price for pro tier", () => {
    expect(PRODUCTS.PRO_MONTHLY.price).toBe(4900); // $49.00 in cents
  });

  it("should have correct price for enterprise tier", () => {
    expect(PRODUCTS.ENTERPRISE.price).toBe(49900); // $499.00 in cents
  });

  it("should have subscription type for monthly products", () => {
    expect(PRODUCTS.PRO_MONTHLY.type).toBe("subscription");
    expect(PRODUCTS.ENTERPRISE.type).toBe("subscription");
  });

  it("should get subscription products", () => {
    const subscriptions = getSubscriptionProducts();
    expect(subscriptions.length).toBeGreaterThan(0);
    expect(subscriptions.every(p => p.type === "subscription")).toBe(true);
  });

  it("should get one-time products", () => {
    const oneTime = getOneTimeProducts();
    expect(oneTime.length).toBeGreaterThan(0);
    expect(oneTime.every(p => p.type === "one_time")).toBe(true);
  });
});
