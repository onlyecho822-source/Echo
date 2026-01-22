import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  Shield, 
  BarChart3,
  Globe,
  Heart,
  Sun,
  DollarSign,
  Bitcoin,
  AlertTriangle,
  ArrowRight,
  Check
} from "lucide-react";
import { getLoginUrl } from "@/const";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";

const signalTypes = [
  { icon: Activity, name: "Seismic", description: "Earthquake → Insurance correlation", color: "text-orange-400" },
  { icon: Heart, name: "Health", description: "Disease data → Pharma signals", color: "text-red-400" },
  { icon: TrendingUp, name: "Sentiment", description: "Reddit/WSB → Volatility prediction", color: "text-green-400" },
  { icon: Sun, name: "Solar", description: "Climate data → Energy stocks", color: "text-yellow-400" },
  { icon: DollarSign, name: "Forex", description: "Currency movements → ETF signals", color: "text-blue-400" },
  { icon: Bitcoin, name: "Crypto", description: "BTC/ETH → COIN/MSTR correlation", color: "text-purple-400" },
];

const pricingTiers = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Get started with delayed signals",
    features: [
      "Last 7 days of signals",
      "24-hour delay",
      "Basic dashboard",
      "Email required",
    ],
    cta: "Get Started",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$49",
    period: "/month",
    description: "Real-time signals for serious traders",
    features: [
      "Real-time alerts",
      "Full signal history",
      "Confidence scores",
      "API access (100/day)",
      "Priority support",
    ],
    cta: "Start Pro Trial",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "$199",
    period: "/month",
    description: "For funds and institutions",
    features: [
      "Everything in Pro",
      "Custom signals",
      "Unlimited API",
      "Webhooks",
      "Dedicated support",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
];

export default function Home() {
  const { user, isAuthenticated } = useAuth();
  const { data: stats } = trpc.signals.stats.useQuery();

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border/50 bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
              <Zap className="w-5 h-5 text-primary" />
            </div>
            <span className="font-semibold text-lg">Echo Signal</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/pricing" className="text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
            {isAuthenticated ? (
              <Link href="/dashboard">
                <Button>Dashboard</Button>
              </Link>
            ) : (
              <a href={getLoginUrl()}>
                <Button>Sign In</Button>
              </a>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container py-20 md:py-32">
        <div className="max-w-4xl mx-auto text-center">
          <Badge variant="secondary" className="mb-4">
            <Activity className="w-3 h-3 mr-1" />
            {stats?.total || 0} signals detected
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            Cross-Domain Market Signals
            <span className="text-primary"> Delivered</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Detect market-moving patterns from seismic activity, health data, social sentiment, 
            and climate signals. Alternative data correlation for $49/month.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {isAuthenticated ? (
              <Link href="/dashboard">
                <Button size="lg" className="gap-2">
                  View Signals <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            ) : (
              <a href={getLoginUrl()}>
                <Button size="lg" className="gap-2">
                  Start Free <ArrowRight className="w-4 h-4" />
                </Button>
              </a>
            )}
            <Link href="/pricing">
              <Button size="lg" variant="outline">
                View Pricing
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Live Signal Preview */}
      <section className="container py-16">
        <div className="max-w-5xl mx-auto">
          <Card className="bg-card/50 border-border/50 overflow-hidden">
            <CardHeader className="border-b border-border/50">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Live Signal Feed</CardTitle>
                  <CardDescription>Real-time cross-domain correlation detection</CardDescription>
                </div>
                <Badge variant="outline" className="gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  Live
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {/* Example signals */}
              <div className="divide-y divide-border/50">
                <SignalRow 
                  type="SEISMIC"
                  direction="bearish"
                  title="M6.2 Earthquake Detected — Japan"
                  target="TRV, ALL"
                  confidence={0.72}
                  time="2 hours ago"
                />
                <SignalRow 
                  type="SENTIMENT"
                  direction="bullish"
                  title="WSB Sentiment Ratio: 4.37 (Extreme)"
                  target="VIX, UVXY"
                  confidence={0.65}
                  time="15 min ago"
                />
                <SignalRow 
                  type="HEALTH"
                  direction="neutral"
                  title="COVID Critical Cases: 34,794"
                  target="PFE, JNJ"
                  confidence={0.58}
                  time="1 hour ago"
                />
              </div>
              <div className="p-4 bg-muted/30 text-center">
                <p className="text-sm text-muted-foreground">
                  Free tier shows signals with 24h delay. 
                  <a href={getLoginUrl()} className="text-primary hover:underline ml-1">
                    Upgrade for real-time access →
                  </a>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Signal Types */}
      <section className="container py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Six Signal Domains</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            We correlate alternative data from six distinct domains to detect market-moving patterns 
            before they appear in traditional data sources.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {signalTypes.map((signal) => (
            <Card key={signal.name} className="bg-card/50 border-border/50 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg bg-muted flex items-center justify-center ${signal.color}`}>
                    <signal.icon className="w-5 h-5" />
                  </div>
                  <CardTitle className="text-lg">{signal.name}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{signal.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section className="container py-16" id="pricing">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Simple Pricing</h2>
          <p className="text-muted-foreground">
            Start free. Upgrade when you need real-time signals.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {pricingTiers.map((tier) => (
            <Card 
              key={tier.name} 
              className={`bg-card/50 border-border/50 ${tier.highlighted ? 'border-primary ring-1 ring-primary' : ''}`}
            >
              <CardHeader>
                <CardTitle>{tier.name}</CardTitle>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-bold">{tier.price}</span>
                  <span className="text-muted-foreground">{tier.period}</span>
                </div>
                <CardDescription>{tier.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-primary" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                <a href={getLoginUrl()}>
                  <Button className="w-full" variant={tier.highlighted ? "default" : "outline"}>
                    {tier.cta}
                  </Button>
                </a>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Disclaimer */}
      <section className="container py-16">
        <Card className="bg-muted/30 border-border/50 max-w-3xl mx-auto">
          <CardContent className="p-6">
            <div className="flex gap-4">
              <AlertTriangle className="w-6 h-6 text-yellow-500 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold mb-2">Risk Disclosure</h3>
                <p className="text-sm text-muted-foreground">
                  Echo Signal Detector provides informational signals only. Signals are based on 
                  historical correlations that may not persist. Past performance does not guarantee 
                  future results. This is not financial advice. Trade at your own risk. Signal 
                  accuracy is not guaranteed. The service may experience downtime.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8">
        <div className="container">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-primary" />
              <span className="font-semibold">Echo Signal Detector</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2026 Echo Signal. Not financial advice.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function SignalRow({ 
  type, 
  direction, 
  title, 
  target, 
  confidence, 
  time 
}: { 
  type: string;
  direction: "bullish" | "bearish" | "neutral";
  title: string;
  target: string;
  confidence: number;
  time: string;
}) {
  const directionColors = {
    bullish: "text-green-400",
    bearish: "text-red-400",
    neutral: "text-blue-400",
  };
  
  const DirectionIcon = direction === "bullish" ? TrendingUp : direction === "bearish" ? TrendingDown : Activity;

  return (
    <div className={`p-4 hover:bg-muted/30 transition-colors signal-${direction}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className={`mt-1 ${directionColors[direction]}`}>
            <DirectionIcon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="outline" className="text-xs">{type}</Badge>
              <span className="text-xs text-muted-foreground">{time}</span>
            </div>
            <p className="font-medium">{title}</p>
            <p className="text-sm text-muted-foreground">Target: {target}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium">{(confidence * 100).toFixed(0)}%</div>
          <div className="text-xs text-muted-foreground">confidence</div>
        </div>
      </div>
    </div>
  );
}
