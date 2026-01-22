/**
 * Echo Signal Detector - Product Definitions
 * 
 * Centralized product and pricing configuration for Stripe integration.
 * These map to Stripe Products/Prices created in the dashboard.
 */

export const PRODUCTS = {
  // One-time purchase: Alternative Data Intelligence Framework
  FRAMEWORK: {
    id: 'framework',
    name: 'Alternative Data Intelligence Framework',
    description: 'Complete autonomous data collection and signal detection system',
    type: 'one_time' as const,
    price: 29700, // $297.00 in cents
    currency: 'usd',
    features: [
      '5 autonomous data collection agents',
      'Correlation detection engine',
      '14+ free data sources',
      'Production database schema',
      'Backtesting framework',
      'Full documentation',
      'MIT license - commercial use allowed',
    ],
  },

  // Subscription: Pro Signal Access
  PRO_MONTHLY: {
    id: 'pro_monthly',
    name: 'Pro Signal Access',
    description: 'Real-time signals with email alerts',
    type: 'subscription' as const,
    interval: 'month' as const,
    price: 4900, // $49.00/month in cents
    currency: 'usd',
    features: [
      'Real-time signal access (no delay)',
      'Email alerts on new signals',
      'Signal confidence scores',
      'Historical performance data',
      'Priority support',
    ],
  },

  // Subscription: Pro Annual (discounted)
  PRO_ANNUAL: {
    id: 'pro_annual',
    name: 'Pro Signal Access (Annual)',
    description: 'Real-time signals with email alerts - save 20%',
    type: 'subscription' as const,
    interval: 'year' as const,
    price: 47000, // $470.00/year in cents (save ~$118)
    currency: 'usd',
    features: [
      'Everything in Pro Monthly',
      'Save 20% vs monthly',
      'Annual billing',
    ],
  },

  // Subscription: Enterprise
  ENTERPRISE: {
    id: 'enterprise',
    name: 'Enterprise Signal Access',
    description: 'Full API access with custom integrations',
    type: 'subscription' as const,
    interval: 'month' as const,
    price: 49900, // $499.00/month in cents
    currency: 'usd',
    features: [
      'Everything in Pro',
      'API access (1000 calls/day)',
      'Custom signal types',
      'Webhook delivery',
      'Dedicated support',
      'Custom integrations',
    ],
  },
} as const;

export type ProductId = keyof typeof PRODUCTS;
export type Product = typeof PRODUCTS[ProductId];

/**
 * Get product by ID
 */
export function getProduct(id: string): Product | undefined {
  return Object.values(PRODUCTS).find(p => p.id === id);
}

/**
 * Get all subscription products
 */
export function getSubscriptionProducts(): Product[] {
  return Object.values(PRODUCTS).filter(p => p.type === 'subscription');
}

/**
 * Get all one-time products
 */
export function getOneTimeProducts(): Product[] {
  return Object.values(PRODUCTS).filter(p => p.type === 'one_time');
}

/**
 * Format price for display
 */
export function formatPrice(priceInCents: number, currency: string = 'usd'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency.toUpperCase(),
  }).format(priceInCents / 100);
}
