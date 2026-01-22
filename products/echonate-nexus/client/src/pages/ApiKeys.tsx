import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Key, 
  Zap, 
  ArrowLeft,
  Loader2,
  Plus,
  Copy,
  Trash2,
  Check,
  AlertTriangle,
  Clock,
  Activity
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
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";

export default function ApiKeys() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [newKeyName, setNewKeyName] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  
  const { data: subscription, isLoading: subLoading } = trpc.subscription.current.useQuery(
    undefined,
    { enabled: isAuthenticated }
  );
  
  const { data: apiKeys, isLoading, refetch } = trpc.apiKeys.list.useQuery(
    undefined,
    { enabled: isAuthenticated }
  );

  const createMutation = trpc.apiKeys.create.useMutation({
    onSuccess: (data) => {
      setNewlyCreatedKey(data.key);
      setNewKeyName("");
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const revokeMutation = trpc.apiKeys.revoke.useMutation({
    onSuccess: () => {
      toast.success("API key revoked");
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleCreateKey = () => {
    if (!newKeyName.trim()) {
      toast.error("Please enter a key name");
      return;
    }
    createMutation.mutate({ name: newKeyName });
  };

  const handleCopyKey = async () => {
    if (newlyCreatedKey) {
      await navigator.clipboard.writeText(newlyCreatedKey);
      setCopied(true);
      toast.success("API key copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleCloseDialog = () => {
    setIsCreateOpen(false);
    setNewlyCreatedKey(null);
    setCopied(false);
  };

  const isPro = subscription?.tier === "pro" || subscription?.tier === "enterprise";

  if (authLoading || isLoading || subLoading) {
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
            <CardDescription>Please log in to manage your API keys.</CardDescription>
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
              <Key className="w-8 h-8 text-primary" />
              API Keys
            </h1>
            <p className="text-muted-foreground mt-2">
              Manage your API keys for programmatic access to signals.
            </p>
          </div>
          {isPro && (
            <Dialog open={isCreateOpen} onOpenChange={(open) => {
              if (!open) handleCloseDialog();
              else setIsCreateOpen(true);
            }}>
              <DialogTrigger asChild>
                <Button className="gap-2">
                  <Plus className="w-4 h-4" /> Create Key
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>
                    {newlyCreatedKey ? "API Key Created" : "Create API Key"}
                  </DialogTitle>
                  <DialogDescription>
                    {newlyCreatedKey 
                      ? "Copy your API key now. You won't be able to see it again."
                      : "Create a new API key for programmatic access."
                    }
                  </DialogDescription>
                </DialogHeader>
                
                {newlyCreatedKey ? (
                  <div className="space-y-4 pt-4">
                    <Alert variant="destructive">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertTitle>Important</AlertTitle>
                      <AlertDescription>
                        This is the only time you'll see this key. Copy it now and store it securely.
                      </AlertDescription>
                    </Alert>
                    <div className="flex gap-2">
                      <Input
                        value={newlyCreatedKey}
                        readOnly
                        className="font-mono text-sm"
                      />
                      <Button onClick={handleCopyKey} variant="outline">
                        {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </Button>
                    </div>
                    <Button className="w-full" onClick={handleCloseDialog}>
                      Done
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4 pt-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Key Name</Label>
                      <Input
                        id="name"
                        placeholder="e.g., Production Server"
                        value={newKeyName}
                        onChange={(e) => setNewKeyName(e.target.value)}
                      />
                    </div>
                    <Button 
                      className="w-full" 
                      onClick={handleCreateKey}
                      disabled={createMutation.isPending}
                    >
                      {createMutation.isPending ? (
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      ) : null}
                      Create API Key
                    </Button>
                  </div>
                )}
              </DialogContent>
            </Dialog>
          )}
        </div>

        {/* Upgrade notice for free users */}
        {!isPro && (
          <Alert className="mb-6">
            <Key className="h-4 w-4" />
            <AlertTitle>API Access Requires Pro</AlertTitle>
            <AlertDescription>
              Upgrade to Pro or Enterprise to get API access for programmatic signal retrieval.
              <Link href="/pricing">
                <Button variant="link" className="px-2 h-auto">
                  View Plans →
                </Button>
              </Link>
            </AlertDescription>
          </Alert>
        )}

        {/* API Documentation */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>API Documentation</CardTitle>
            <CardDescription>Quick reference for using the signals API</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Base URL</h4>
              <code className="bg-muted px-3 py-1 rounded text-sm">
                {window.location.origin}/api/v1
              </code>
            </div>
            <div>
              <h4 className="font-medium mb-2">Authentication</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Include your API key in the Authorization header:
              </p>
              <code className="bg-muted px-3 py-1 rounded text-sm block">
                Authorization: Bearer echo_your_api_key_here
              </code>
            </div>
            <div>
              <h4 className="font-medium mb-2">Endpoints</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">GET</Badge>
                  <code className="bg-muted px-2 py-0.5 rounded">/signals</code>
                  <span className="text-muted-foreground">- List signals</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">GET</Badge>
                  <code className="bg-muted px-2 py-0.5 rounded">/signals/:id</code>
                  <span className="text-muted-foreground">- Get signal details</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">GET</Badge>
                  <code className="bg-muted px-2 py-0.5 rounded">/signals/stats</code>
                  <span className="text-muted-foreground">- Get signal statistics</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Keys List */}
        {isPro && (
          <Card>
            <CardHeader>
              <CardTitle>Your API Keys</CardTitle>
              <CardDescription>
                {apiKeys?.length || 0} active key{(apiKeys?.length || 0) !== 1 ? "s" : ""}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!apiKeys || apiKeys.length === 0 ? (
                <div className="text-center py-8">
                  <Key className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No API keys yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Create your first API key to start using the API.
                  </p>
                  <Button onClick={() => setIsCreateOpen(true)}>
                    <Plus className="w-4 h-4 mr-2" /> Create Key
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {apiKeys.map((key) => (
                    <div
                      key={key.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{key.name}</span>
                          <code className="text-xs bg-muted px-2 py-0.5 rounded">
                            {key.keyPrefix}...
                          </code>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            Created {new Date(key.createdAt).toLocaleDateString()}
                          </span>
                          {key.lastUsedAt && (
                            <span className="flex items-center gap-1">
                              <Activity className="w-3 h-3" />
                              Last used {new Date(key.lastUsedAt).toLocaleDateString()}
                            </span>
                          )}
                          <span>{key.usageCount || 0} requests</span>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-destructive hover:text-destructive"
                        onClick={() => {
                          if (confirm("Revoke this API key? This cannot be undone.")) {
                            revokeMutation.mutate({ id: key.id });
                          }
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
