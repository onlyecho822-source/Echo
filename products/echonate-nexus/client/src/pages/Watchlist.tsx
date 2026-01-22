import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Eye, 
  Zap, 
  ArrowLeft,
  Loader2,
  Plus,
  X,
  Trash2,
  Bell,
  BellOff,
  Edit2,
  Check
} from "lucide-react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";

export default function Watchlist() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [newWatchlistName, setNewWatchlistName] = useState("");
  const [newWatchlistDesc, setNewWatchlistDesc] = useState("");
  const [newTicker, setNewTicker] = useState("");
  const [selectedWatchlist, setSelectedWatchlist] = useState<number | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  
  const { data: watchlists, isLoading, refetch } = trpc.watchlists.list.useQuery(
    undefined,
    { enabled: isAuthenticated }
  );

  const createMutation = trpc.watchlists.create.useMutation({
    onSuccess: () => {
      toast.success("Watchlist created");
      setNewWatchlistName("");
      setNewWatchlistDesc("");
      setIsCreateOpen(false);
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const deleteMutation = trpc.watchlists.delete.useMutation({
    onSuccess: () => {
      toast.success("Watchlist deleted");
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const addTickerMutation = trpc.watchlists.addTicker.useMutation({
    onSuccess: () => {
      toast.success("Ticker added");
      setNewTicker("");
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const removeTickerMutation = trpc.watchlists.removeTicker.useMutation({
    onSuccess: () => {
      toast.success("Ticker removed");
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const updateMutation = trpc.watchlists.update.useMutation({
    onSuccess: () => {
      toast.success("Watchlist updated");
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleCreateWatchlist = () => {
    if (!newWatchlistName.trim()) {
      toast.error("Please enter a watchlist name");
      return;
    }
    createMutation.mutate({
      name: newWatchlistName,
      description: newWatchlistDesc || undefined,
    });
  };

  const handleAddTicker = (watchlistId: number) => {
    if (!newTicker.trim()) {
      toast.error("Please enter a ticker symbol");
      return;
    }
    addTickerMutation.mutate({
      watchlistId,
      ticker: newTicker.toUpperCase(),
    });
  };

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>Please log in to manage your watchlists.</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/">
              <Button className="w-full">Go to Home</Button>
            </Link>
          </CardContent>
        </Card>
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

      <main className="container py-8 max-w-4xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Eye className="w-8 h-8 text-primary" />
              Watchlists
            </h1>
            <p className="text-muted-foreground mt-2">
              Track specific tickers and receive alerts when signals match.
            </p>
          </div>
          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="w-4 h-4" /> New Watchlist
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Watchlist</DialogTitle>
                <DialogDescription>
                  Create a new watchlist to track specific tickers.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 pt-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    placeholder="e.g., Tech Stocks"
                    value={newWatchlistName}
                    onChange={(e) => setNewWatchlistName(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description (optional)</Label>
                  <Textarea
                    id="description"
                    placeholder="What's this watchlist for?"
                    value={newWatchlistDesc}
                    onChange={(e) => setNewWatchlistDesc(e.target.value)}
                  />
                </div>
                <Button 
                  className="w-full" 
                  onClick={handleCreateWatchlist}
                  disabled={createMutation.isPending}
                >
                  {createMutation.isPending ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : null}
                  Create Watchlist
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Watchlists */}
        {!watchlists || watchlists.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Eye className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No watchlists yet</h3>
              <p className="text-muted-foreground mb-4">
                Create your first watchlist to start tracking specific tickers.
              </p>
              <Button onClick={() => setIsCreateOpen(true)}>
                <Plus className="w-4 h-4 mr-2" /> Create Watchlist
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {watchlists.map((watchlist) => (
              <Card key={watchlist.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {watchlist.name}
                        {watchlist.alertOnSignal ? (
                          <Bell className="w-4 h-4 text-primary" />
                        ) : (
                          <BellOff className="w-4 h-4 text-muted-foreground" />
                        )}
                      </CardTitle>
                      {watchlist.description && (
                        <CardDescription>{watchlist.description}</CardDescription>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          updateMutation.mutate({
                            id: watchlist.id,
                            alertOnSignal: !watchlist.alertOnSignal,
                          });
                        }}
                      >
                        {watchlist.alertOnSignal ? (
                          <Bell className="w-4 h-4" />
                        ) : (
                          <BellOff className="w-4 h-4" />
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-destructive hover:text-destructive"
                        onClick={() => {
                          if (confirm("Delete this watchlist?")) {
                            deleteMutation.mutate({ id: watchlist.id });
                          }
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Tickers */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {((watchlist.tickers as string[]) || []).map((ticker) => (
                      <Badge
                        key={ticker}
                        variant="secondary"
                        className="flex items-center gap-1 px-3 py-1"
                      >
                        {ticker}
                        <button
                          className="ml-1 hover:text-destructive"
                          onClick={() => {
                            removeTickerMutation.mutate({
                              watchlistId: watchlist.id,
                              ticker,
                            });
                          }}
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </Badge>
                    ))}
                    {((watchlist.tickers as string[]) || []).length === 0 && (
                      <span className="text-sm text-muted-foreground">
                        No tickers added yet
                      </span>
                    )}
                  </div>

                  {/* Add ticker */}
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add ticker (e.g., AAPL)"
                      value={selectedWatchlist === watchlist.id ? newTicker : ""}
                      onChange={(e) => {
                        setSelectedWatchlist(watchlist.id);
                        setNewTicker(e.target.value.toUpperCase());
                      }}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          handleAddTicker(watchlist.id);
                        }
                      }}
                      className="max-w-[200px]"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleAddTicker(watchlist.id)}
                      disabled={addTickerMutation.isPending}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Min confidence */}
                  <div className="mt-4 text-sm text-muted-foreground">
                    Min confidence: {Math.round(parseFloat(watchlist.minConfidence || "0.70") * 100)}%
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
