import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  Settings,
  BarChart3,
  Bell,
  LogOut,
  Crown,
  Filter,
  Search,
  Download,
  Bookmark,
  BookmarkCheck,
  ExternalLink,
  RefreshCw,
  X,
  ChevronDown,
  Calendar,
  Eye,
  Key,
  Receipt
} from "lucide-react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useState, useMemo } from "react";
import { toast } from "sonner";

const signalTypeLabels: Record<string, string> = {
  seismic: "Seismic",
  health: "Health",
  sentiment: "Sentiment",
  solar: "Solar/Weather",
  forex: "Forex",
  crypto: "Crypto",
  geopolitical: "Geopolitical",
};

const signalTypeColors: Record<string, string> = {
  seismic: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  health: "bg-green-500/20 text-green-400 border-green-500/30",
  sentiment: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  solar: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  forex: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  crypto: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
  geopolitical: "bg-red-500/20 text-red-400 border-red-500/30",
};

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [selectedType, setSelectedType] = useState<string | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const [bookmarkedIds, setBookmarkedIds] = useState<Set<number>>(new Set());
  const [showFilters, setShowFilters] = useState(false);
  const [directionFilter, setDirectionFilter] = useState<string[]>(["bullish", "bearish", "neutral"]);
  const [minConfidence, setMinConfidence] = useState(0);
  
  const { data: signalsData, isLoading, refetch } = trpc.signals.list.useQuery({
    limit: 50,
    signalType: selectedType as any,
  });
  
  const { data: stats } = trpc.signals.stats.useQuery();
  const { data: subscription } = trpc.subscription.current.useQuery();

  const tier = signalsData?.tier || "free";
  const rawSignals = signalsData?.signals || [];
  
  // Apply client-side filters
  const signals = useMemo(() => {
    return rawSignals.filter(signal => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesSearch = 
          signal.title?.toLowerCase().includes(query) ||
          signal.summary?.toLowerCase().includes(query) ||
          signal.targetTicker?.toLowerCase().includes(query) ||
          signal.source?.toLowerCase().includes(query);
        if (!matchesSearch) return false;
      }
      
      // Direction filter
      if (!directionFilter.includes(signal.direction)) return false;
      
      // Confidence filter
      if (parseFloat(signal.confidence) < minConfidence / 100) return false;
      
      return true;
    });
  }, [rawSignals, searchQuery, directionFilter, minConfidence]);

  const toggleBookmark = (id: number) => {
    setBookmarkedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
        toast.success("Removed from bookmarks");
      } else {
        next.add(id);
        toast.success("Added to bookmarks");
      }
      return next;
    });
  };

  const exportSignals = () => {
    const data = signals.map(s => ({
      type: s.signalType,
      ticker: s.targetTicker,
      direction: s.direction,
      confidence: s.confidence,
      title: s.title,
      summary: s.summary,
      source: s.source,
      detectedAt: s.detectedAt
    }));
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `echo-signals-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Signals exported successfully");
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                <Zap className="w-5 h-5 text-primary" />
              </div>
              <span className="font-semibold text-lg">Echo Signal</span>
            </Link>
            <Badge variant={tier === "pro" ? "default" : tier === "enterprise" ? "default" : "secondary"}>
              {tier === "free" && "Free"}
              {tier === "pro" && <><Crown className="w-3 h-3 mr-1" /> Pro</>}
              {tier === "enterprise" && <><Crown className="w-3 h-3 mr-1" /> Enterprise</>}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={() => refetch()}>
              <RefreshCw className="w-5 h-5" />
            </Button>
            <Link href="/watchlist">
              <Button variant="ghost" size="icon" title="Watchlists">
                <Eye className="w-5 h-5" />
              </Button>
            </Link>
            <Link href="/analytics">
              <Button variant="ghost" size="icon" title="Analytics">
                <BarChart3 className="w-5 h-5" />
              </Button>
            </Link>
            <Link href="/api-keys">
              <Button variant="ghost" size="icon" title="API Keys">
                <Key className="w-5 h-5" />
              </Button>
            </Link>
            <Link href="/orders">
              <Button variant="ghost" size="icon" title="Orders">
                <Receipt className="w-5 h-5" />
              </Button>
            </Link>
            <Link href="/settings">
              <Button variant="ghost" size="icon" title="Settings">
                <Settings className="w-5 h-5" />
              </Button>
            </Link>
            <Button variant="ghost" size="icon" onClick={() => logout()} title="Logout">
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      <main className="container py-8">
        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard 
            title="Total Signals" 
            value={stats?.total || 0} 
            icon={Activity}
          />
          <StatCard 
            title="Accuracy" 
            value={`${((stats?.accuracy || 0) * 100).toFixed(1)}%`}
            icon={BarChart3}
            subtitle={`${stats?.evaluated || 0} evaluated`}
          />
          <StatCard 
            title="Your Tier" 
            value={tier.charAt(0).toUpperCase() + tier.slice(1)}
            icon={Crown}
          />
          <StatCard 
            title="Bookmarked" 
            value={bookmarkedIds.size}
            icon={Bookmark}
          />
        </div>

        {/* Upgrade Banner for Free Users */}
        {tier === "free" && (
          <Card className="mb-8 bg-primary/10 border-primary/30">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <p className="font-medium">You're viewing signals with 24h delay</p>
                <p className="text-sm text-muted-foreground">Upgrade to Pro for real-time alerts and API access</p>
              </div>
              <Link href="/pricing">
                <Button>Upgrade to Pro</Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {/* Search and Filters */}
        <Card className="mb-6 bg-card/50 border-border/50">
          <CardContent className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search signals by ticker, title, or source..."
                  className="pl-10 bg-muted/50"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              
              {/* Type Filter */}
              <select 
                className="bg-muted border border-border rounded-md px-3 py-2 text-sm min-w-[150px]"
                value={selectedType || ""}
                onChange={(e) => setSelectedType(e.target.value || undefined)}
              >
                <option value="">All Types</option>
                {Object.entries(signalTypeLabels).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
              
              {/* Advanced Filters Toggle */}
              <Button 
                variant="outline" 
                onClick={() => setShowFilters(!showFilters)}
                className="gap-2"
              >
                <Filter className="w-4 h-4" />
                Filters
                <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
              </Button>
              
              {/* Export */}
              <Button variant="outline" onClick={exportSignals} className="gap-2">
                <Download className="w-4 h-4" />
                Export
              </Button>
            </div>
            
            {/* Advanced Filters Panel */}
            {showFilters && (
              <div className="mt-4 pt-4 border-t border-border/50 grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Direction Filter */}
                <div>
                  <Label className="text-sm text-muted-foreground mb-2 block">Direction</Label>
                  <div className="flex gap-4">
                    {["bullish", "bearish", "neutral"].map(dir => (
                      <label key={dir} className="flex items-center gap-2 cursor-pointer">
                        <Checkbox
                          checked={directionFilter.includes(dir)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setDirectionFilter([...directionFilter, dir]);
                            } else {
                              setDirectionFilter(directionFilter.filter(d => d !== dir));
                            }
                          }}
                        />
                        <span className="text-sm capitalize">{dir}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                {/* Confidence Filter */}
                <div>
                  <Label className="text-sm text-muted-foreground mb-2 block">
                    Min Confidence: {minConfidence}%
                  </Label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={minConfidence}
                    onChange={(e) => setMinConfidence(parseInt(e.target.value))}
                    className="w-full accent-primary"
                  />
                </div>
                
                {/* Results Count */}
                <div className="flex items-end">
                  <p className="text-sm text-muted-foreground">
                    Showing {signals.length} of {rawSignals.length} signals
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Signal Feed */}
        <Card className="bg-card/50 border-border/50">
          <CardHeader className="border-b border-border/50">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Signal Feed</CardTitle>
                <CardDescription>
                  {tier === "free" ? "Delayed by 24 hours" : "Real-time signals"} • Click any signal for details
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-8 text-center text-muted-foreground">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
                Loading signals...
              </div>
            ) : signals.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                No signals match your filters. Try adjusting your search criteria.
              </div>
            ) : (
              <div className="divide-y divide-border/50">
                {signals.map((signal) => (
                  <SignalRow 
                    key={signal.id} 
                    signal={signal} 
                    isBookmarked={bookmarkedIds.has(signal.id)}
                    onBookmark={() => toggleBookmark(signal.id)}
                    onClick={() => setSelectedSignal(signal)}
                  />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>

      {/* Signal Detail Modal */}
      <Dialog open={!!selectedSignal} onOpenChange={() => setSelectedSignal(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          {selectedSignal && (
            <>
              <DialogHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <Badge className={signalTypeColors[selectedSignal.signalType]}>
                      {signalTypeLabels[selectedSignal.signalType]}
                    </Badge>
                    <DialogTitle className="mt-2">{selectedSignal.title}</DialogTitle>
                    <DialogDescription>{selectedSignal.summary}</DialogDescription>
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`text-lg px-3 py-1 ${
                      selectedSignal.direction === "bullish" ? "border-green-500/50 text-green-400" :
                      selectedSignal.direction === "bearish" ? "border-red-500/50 text-red-400" :
                      "border-blue-500/50 text-blue-400"
                    }`}
                  >
                    {selectedSignal.direction === "bullish" && <TrendingUp className="w-4 h-4 mr-1" />}
                    {selectedSignal.direction === "bearish" && <TrendingDown className="w-4 h-4 mr-1" />}
                    {selectedSignal.direction === "neutral" && <Activity className="w-4 h-4 mr-1" />}
                    {selectedSignal.direction.toUpperCase()}
                  </Badge>
                </div>
              </DialogHeader>
              
              <div className="space-y-6 mt-4">
                {/* Key Metrics */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-muted/50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-primary">
                      {(parseFloat(selectedSignal.confidence) * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-muted-foreground">Confidence</div>
                  </div>
                  <div className="bg-muted/50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold">
                      {(parseFloat(selectedSignal.strength) * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-muted-foreground">Strength</div>
                  </div>
                  <div className="bg-muted/50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-primary">
                      {selectedSignal.targetTicker || "—"}
                    </div>
                    <div className="text-xs text-muted-foreground">Target</div>
                  </div>
                </div>
                
                {/* Rationale */}
                <div>
                  <h4 className="font-medium mb-2">Analysis & Rationale</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {selectedSignal.rationale}
                  </p>
                </div>
                
                {/* Metadata */}
                <div>
                  <h4 className="font-medium mb-2">Signal Details</h4>
                  <div className="bg-muted/30 rounded-lg p-4 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Source</span>
                      <span className="flex items-center gap-1">
                        {selectedSignal.source}
                        {selectedSignal.sourceUrl && (
                          <a href={selectedSignal.sourceUrl} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Sector</span>
                      <span>{selectedSignal.targetSector || "—"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Detected</span>
                      <span>{new Date(selectedSignal.detectedAt).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Expires</span>
                      <span>{new Date(selectedSignal.expiresAt).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                
                {/* Raw Data (for Pro/Enterprise) */}
                {tier !== "free" && selectedSignal.rawData && (
                  <div>
                    <h4 className="font-medium mb-2">Raw Data</h4>
                    <pre className="bg-muted/30 rounded-lg p-4 text-xs overflow-x-auto">
                      {JSON.stringify(JSON.parse(selectedSignal.rawData), null, 2)}
                    </pre>
                  </div>
                )}
                
                {/* Actions */}
                <div className="flex gap-2 pt-4 border-t border-border/50">
                  <Button 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => {
                      toggleBookmark(selectedSignal.id);
                    }}
                  >
                    {bookmarkedIds.has(selectedSignal.id) ? (
                      <><BookmarkCheck className="w-4 h-4 mr-2" /> Bookmarked</>
                    ) : (
                      <><Bookmark className="w-4 h-4 mr-2" /> Bookmark</>
                    )}
                  </Button>
                  <Button 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => {
                      navigator.clipboard.writeText(JSON.stringify(selectedSignal, null, 2));
                      toast.success("Signal data copied to clipboard");
                    }}
                  >
                    Copy Data
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function StatCard({ 
  title, 
  value, 
  icon: Icon,
  subtitle 
}: { 
  title: string;
  value: string | number;
  icon: any;
  subtitle?: string;
}) {
  return (
    <Card className="bg-card/50 border-border/50">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-muted-foreground">{title}</span>
          <Icon className="w-4 h-4 text-muted-foreground" />
        </div>
        <div className="text-2xl font-bold">{value}</div>
        {subtitle && <div className="text-xs text-muted-foreground">{subtitle}</div>}
      </CardContent>
    </Card>
  );
}

function SignalRow({ 
  signal, 
  isBookmarked,
  onBookmark,
  onClick
}: { 
  signal: any;
  isBookmarked: boolean;
  onBookmark: () => void;
  onClick: () => void;
}) {
  const directionColors = {
    bullish: "text-green-400",
    bearish: "text-red-400",
    neutral: "text-blue-400",
  };
  
  const DirectionIcon = signal.direction === "bullish" ? TrendingUp : 
                        signal.direction === "bearish" ? TrendingDown : Activity;

  const timeAgo = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor(diff / (1000 * 60));
    
    if (hours > 24) return `${Math.floor(hours / 24)}d ago`;
    if (hours > 0) return `${hours}h ago`;
    return `${minutes}m ago`;
  };

  return (
    <div 
      className={`p-4 hover:bg-muted/30 transition-colors cursor-pointer signal-${signal.direction}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className={`mt-1 ${directionColors[signal.direction as keyof typeof directionColors]}`}>
            <DirectionIcon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge className={`text-xs ${signalTypeColors[signal.signalType]}`}>
                {signalTypeLabels[signal.signalType] || signal.signalType}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {timeAgo(signal.detectedAt)}
              </span>
              {isBookmarked && (
                <BookmarkCheck className="w-3 h-3 text-primary" />
              )}
            </div>
            <p className="font-medium">{signal.title}</p>
            <p className="text-sm text-muted-foreground line-clamp-1">{signal.summary}</p>
            {signal.targetTicker && (
              <p className="text-sm text-muted-foreground mt-1">
                Target: <span className="text-foreground font-medium">{signal.targetTicker}</span>
                {signal.targetSector && ` • ${signal.targetSector}`}
              </p>
            )}
          </div>
        </div>
        <div className="text-right flex-shrink-0 flex items-start gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => {
              e.stopPropagation();
              onBookmark();
            }}
          >
            {isBookmarked ? (
              <BookmarkCheck className="w-4 h-4 text-primary" />
            ) : (
              <Bookmark className="w-4 h-4" />
            )}
          </Button>
          <div>
            <div className="text-sm font-medium">
              {(parseFloat(signal.confidence) * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-muted-foreground">confidence</div>
            <Badge 
              variant="outline" 
              className={`mt-2 text-xs ${
                signal.direction === "bullish" ? "border-green-500/50 text-green-400" :
                signal.direction === "bearish" ? "border-red-500/50 text-red-400" :
                "border-blue-500/50 text-blue-400"
              }`}
            >
              {signal.direction.toUpperCase()}
            </Badge>
          </div>
        </div>
      </div>
    </div>
  );
}
