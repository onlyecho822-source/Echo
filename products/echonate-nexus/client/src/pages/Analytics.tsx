import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  BarChart3, 
  Zap, 
  ArrowLeft,
  Loader2,
  TrendingUp,
  TrendingDown,
  Target,
  Activity,
  PieChart,
  LineChart
} from "lucide-react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";

// Signal type colors
const typeColors: Record<string, string> = {
  seismic: "#ef4444",
  health: "#22c55e",
  sentiment: "#3b82f6",
  solar: "#f59e0b",
  forex: "#8b5cf6",
  crypto: "#06b6d4",
  geopolitical: "#ec4899",
};

export default function Analytics() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  
  const { data: stats, isLoading: statsLoading } = trpc.signals.stats.useQuery();
  const { data: accuracy, isLoading: accuracyLoading } = trpc.accuracy.byType.useQuery();

  const isLoading = authLoading || statsLoading || accuracyLoading;

  // Calculate chart data
  const typeDistribution = useMemo(() => {
    if (!stats?.byType) return [];
    return Object.entries(stats.byType).map(([type, count]) => ({
      type,
      count: count as number,
      color: typeColors[type] || "#6b7280",
      percentage: stats.total > 0 ? ((count as number) / stats.total * 100).toFixed(1) : "0",
    }));
  }, [stats]);

  const accuracyData = useMemo(() => {
    if (!accuracy) return [];
    return accuracy.map(a => ({
      type: a.signalType,
      accuracy: parseFloat(a.currentAccuracy || "0.5") * 100,
      total: a.totalSignals || 0,
      correct: a.correctSignals || 0,
      lower: parseFloat(a.confidenceLower || "0.025") * 100,
      upper: parseFloat(a.confidenceUpper || "0.975") * 100,
      color: typeColors[a.signalType] || "#6b7280",
    }));
  }, [accuracy]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

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
          <Link href="/dashboard">
            <Button variant="ghost" className="gap-2">
              <ArrowLeft className="w-4 h-4" /> Back to Dashboard
            </Button>
          </Link>
        </div>
      </nav>

      <main className="container py-8 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-primary" />
            Signal Analytics
          </h1>
          <p className="text-muted-foreground mt-2">
            Performance metrics and accuracy tracking with Bayesian confidence intervals.
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                  <Activity className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stats?.total || 0}</p>
                  <p className="text-sm text-muted-foreground">Total Signals</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                  <Target className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {stats?.accuracy ? (stats.accuracy * 100).toFixed(1) : "N/A"}%
                  </p>
                  <p className="text-sm text-muted-foreground">Overall Accuracy</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stats?.evaluated || 0}</p>
                  <p className="text-sm text-muted-foreground">Evaluated</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <PieChart className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{typeDistribution.length}</p>
                  <p className="text-sm text-muted-foreground">Signal Types</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Signal Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="w-5 h-5" />
                Signal Distribution
              </CardTitle>
              <CardDescription>Breakdown by signal type</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {typeDistribution.map(({ type, count, color, percentage }) => (
                  <div key={type} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: color }}
                        />
                        <span className="capitalize font-medium">{type}</span>
                      </div>
                      <span className="text-muted-foreground">
                        {count} ({percentage}%)
                      </span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all"
                        style={{ 
                          width: `${percentage}%`,
                          backgroundColor: color,
                        }}
                      />
                    </div>
                  </div>
                ))}
                {typeDistribution.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    No signal data available
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Accuracy by Type (Bayesian) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Accuracy by Type
              </CardTitle>
              <CardDescription>
                Bayesian posterior estimates with 95% confidence intervals
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {accuracyData.map(({ type, accuracy, total, correct, lower, upper, color }) => (
                  <div key={type} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: color }}
                        />
                        <span className="capitalize font-medium">{type}</span>
                      </div>
                      <div className="text-right">
                        <span className="font-semibold">{accuracy.toFixed(1)}%</span>
                        <span className="text-xs text-muted-foreground ml-2">
                          ({correct}/{total})
                        </span>
                      </div>
                    </div>
                    {/* Confidence interval visualization */}
                    <div className="relative h-6 bg-muted rounded-full overflow-hidden">
                      {/* Confidence interval range */}
                      <div 
                        className="absolute h-full opacity-30"
                        style={{ 
                          left: `${lower}%`,
                          width: `${upper - lower}%`,
                          backgroundColor: color,
                        }}
                      />
                      {/* Point estimate */}
                      <div 
                        className="absolute h-full w-1 rounded-full"
                        style={{ 
                          left: `${accuracy}%`,
                          backgroundColor: color,
                        }}
                      />
                      {/* Labels */}
                      <div className="absolute inset-0 flex items-center justify-between px-2 text-xs">
                        <span className="text-muted-foreground">{lower.toFixed(0)}%</span>
                        <span className="text-muted-foreground">{upper.toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
                {accuracyData.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    No accuracy data available yet. Outcomes need to be recorded.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Methodology Card */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Bayesian Accuracy Methodology</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-invert max-w-none">
            <p className="text-muted-foreground">
              Our accuracy metrics use <strong>Bayesian inference</strong> with a Beta-Binomial model. 
              Each signal type starts with a uniform prior (Beta(1,1)) and updates as outcomes are recorded.
              The displayed accuracy is the <strong>posterior mean</strong> (α / (α + β)), and the confidence 
              interval represents the 95% credible interval from the posterior distribution.
            </p>
            <p className="text-muted-foreground mt-4">
              This approach provides several advantages over simple accuracy percentages:
            </p>
            <ul className="text-muted-foreground list-disc list-inside mt-2 space-y-1">
              <li>Accounts for uncertainty when sample sizes are small</li>
              <li>Naturally shrinks toward 50% with limited data (regularization)</li>
              <li>Confidence intervals narrow as more data is collected</li>
              <li>Resistant to overfitting on small samples</li>
            </ul>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
