import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, Zap, ArrowLeft, Loader2 } from "lucide-react";
import { Link } from "wouter";
import { getLoginUrl } from "@/const";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { toast } from "sonner";
import { useState } from "react";

export default function Pricing() {
  const { data: tiers } = trpc.subscription.tiers.useQuery();
  const { isAuthenticated, user } = useAuth();
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  
  const createCheckout = trpc.payments.createCheckout.useMutation({
    onSuccess: (data: { url: string | null }) => {
      toast.info("Redirecting to checkout...");
      if (data.url) window.open(data.url, "_blank");
      setLoadingTier(null);
    },
    onError: (error: { message?: string }) => {
      toast.error(error.message || "Failed to create checkout session");
      setLoadingTier(null);
    },
  });

  const handleUpgrade = (productId: string) => {
    if (!isAuthenticated) {
      window.location.href = getLoginUrl();
      return;
    }
    setLoadingTier(productId);
    createCheckout.mutate({ productId });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border/50 bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
              <Zap className="w-5 h-5 text-primary" />
            </div>
            <span className="font-semibold text-lg">Echo Signal</span>
          </Link>
          <Link href="/">
            <Button variant="ghost" className="gap-2">
              <ArrowLeft className="w-4 h-4" /> Back
            </Button>
          </Link>
        </div>
      </nav>

      <main className="container py-16">
        <div className="text-center mb-12">
          <Badge variant="secondary" className="mb-4">Pricing</Badge>
          <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Start free with delayed signals. Upgrade to Pro for real-time market intelligence.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {(tiers || []).map((tier, index) => {
            const isHighlighted = tier.id === "pro";
            const isLoading = loadingTier === tier.id;
            
            return (
              <Card 
                key={tier.id}
                className={`bg-card/50 border-border/50 relative ${
                  isHighlighted ? 'border-primary ring-2 ring-primary/20' : ''
                }`}
              >
                {isHighlighted && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground">Most Popular</Badge>
                  </div>
                )}
                <CardHeader className="text-center pb-2">
                  <CardTitle className="text-2xl">{tier.name}</CardTitle>
                  <div className="flex items-baseline justify-center gap-1 mt-4">
                    <span className="text-5xl font-bold">
                      ${tier.price}
                    </span>
                    {tier.price > 0 && (
                      <span className="text-muted-foreground">/month</span>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-4 mb-8">
                    {tier.features.map((feature: string) => (
                      <li key={feature} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  {tier.id === "free" ? (
                    isAuthenticated ? (
                      <Link href="/dashboard">
                        <Button className="w-full" variant="outline">
                          Go to Dashboard
                        </Button>
                      </Link>
                    ) : (
                      <a href={getLoginUrl()}>
                        <Button className="w-full" variant="outline">
                          Get Started Free
                        </Button>
                      </a>
                    )
                  ) : tier.id === "enterprise" ? (
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => handleUpgrade("enterprise")}
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        "Contact Sales"
                      )}
                    </Button>
                  ) : (
                    <Button 
                      className="w-full" 
                      variant={isHighlighted ? "default" : "outline"}
                      onClick={() => handleUpgrade("pro_monthly")}
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : isAuthenticated ? (
                        "Upgrade Now"
                      ) : (
                        "Start Pro Trial"
                      )}
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Test Mode Notice */}
        <div className="max-w-xl mx-auto mt-8 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-center">
          <p className="text-sm text-yellow-600 dark:text-yellow-400">
            <strong>Test Mode:</strong> Use card number <code className="bg-muted px-1 rounded">4242 4242 4242 4242</code> with any future expiry and CVC.
          </p>
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto mt-20">
          <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          
          <div className="space-y-6">
            <FaqItem 
              question="What is a signal?"
              answer="A signal is a detected correlation between alternative data (like earthquake activity, health data, or social sentiment) and potential market movements. Each signal includes a direction (bullish/bearish), confidence score, and rationale."
            />
            <FaqItem 
              question="How accurate are the signals?"
              answer="Signal accuracy varies by type and market conditions. We track and display historical accuracy for transparency. Past performance does not guarantee future results. Signals are informational only and not financial advice."
            />
            <FaqItem 
              question="What's the difference between Free and Pro?"
              answer="Free tier shows signals with a 24-hour delay and limited to the last 7 days. Pro tier provides real-time alerts, full history, detailed rationale, and API access for programmatic integration."
            />
            <FaqItem 
              question="Can I cancel anytime?"
              answer="Yes, you can cancel your subscription at any time. Your access continues until the end of your billing period."
            />
            <FaqItem 
              question="Is this financial advice?"
              answer="No. Echo Signal Detector provides informational signals only. We are not registered investment advisors. Always do your own research and consult qualified professionals before making investment decisions."
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8 mt-16">
        <div className="container text-center text-sm text-muted-foreground">
          © 2026 Echo Signal Detector. Not financial advice. Trade at your own risk.
        </div>
      </footer>
    </div>
  );
}

function FaqItem({ question, answer }: { question: string; answer: string }) {
  return (
    <div className="border-b border-border/50 pb-6">
      <h3 className="font-semibold mb-2">{question}</h3>
      <p className="text-muted-foreground">{answer}</p>
    </div>
  );
}
