import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Settings as SettingsIcon, 
  Bell, 
  User, 
  CreditCard, 
  Shield,
  Zap,
  Mail,
  Activity,
  TrendingUp,
  Globe,
  Sun,
  Heart,
  MessageSquare,
  ArrowLeft,
  Loader2,
  Check,
  AlertTriangle
} from "lucide-react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { toast } from "sonner";

const SIGNAL_TYPES = [
  { key: "enableSeismic", label: "Seismic", icon: Activity, description: "Earthquake & geological events" },
  { key: "enableHealth", label: "Health", icon: Heart, description: "Disease outbreaks & health data" },
  { key: "enableSentiment", label: "Sentiment", icon: MessageSquare, description: "Social media & news sentiment" },
  { key: "enableSolar", label: "Solar", icon: Sun, description: "Solar activity & space weather" },
  { key: "enableForex", label: "Forex", icon: TrendingUp, description: "Currency market correlations" },
  { key: "enableCrypto", label: "Crypto", icon: Zap, description: "Cryptocurrency signals" },
  { key: "enableGeopolitical", label: "Geopolitical", icon: Globe, description: "Political & global events" },
] as const;

export default function Settings() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  
  // Alert preferences state
  const [alertPrefs, setAlertPrefs] = useState({
    enableSeismic: true,
    enableHealth: true,
    enableSentiment: true,
    enableSolar: true,
    enableForex: true,
    enableCrypto: true,
    enableGeopolitical: true,
    minConfidence: 0.6,
    emailEnabled: true,
    emailAddress: "",
    digestFrequency: "instant" as "instant" | "hourly" | "daily",
  });
  
  // Fetch alert preferences
  const { data: preferences, isLoading: prefsLoading } = trpc.alerts.preferences.useQuery(
    undefined,
    { enabled: isAuthenticated }
  );
  
  // Fetch subscription
  const { data: subscription } = trpc.subscription.current.useQuery(
    undefined,
    { enabled: isAuthenticated }
  );
  
  // Update mutation
  const updatePrefs = trpc.alerts.updatePreferences.useMutation({
    onSuccess: () => {
      toast.success("Settings saved successfully");
      setIsSaving(false);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to save settings");
      setIsSaving(false);
    },
  });
  
  // Sync preferences from server
  useEffect(() => {
    if (preferences) {
      setAlertPrefs({
        enableSeismic: preferences.enableSeismic ?? true,
        enableHealth: preferences.enableHealth ?? true,
        enableSentiment: preferences.enableSentiment ?? true,
        enableSolar: preferences.enableSolar ?? true,
        enableForex: preferences.enableForex ?? true,
        enableCrypto: preferences.enableCrypto ?? true,
        enableGeopolitical: preferences.enableGeopolitical ?? true,
        minConfidence: parseFloat(String(preferences.minConfidence ?? "0.6")),
        emailEnabled: preferences.emailEnabled ?? true,
        emailAddress: preferences.emailAddress ?? user?.email ?? "",
        digestFrequency: (preferences.digestFrequency as "instant" | "hourly" | "daily") ?? "instant",
      });
    }
  }, [preferences, user?.email]);
  
  const handleSave = () => {
    setIsSaving(true);
    updatePrefs.mutate({
      ...alertPrefs,
      minConfidence: alertPrefs.minConfidence.toFixed(2),
    });
  };
  
  const handleToggleSignal = (key: string) => {
    setAlertPrefs(prev => ({
      ...prev,
      [key]: !prev[key as keyof typeof prev],
    }));
  };
  
  if (authLoading || prefsLoading) {
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
            <CardDescription>Please log in to access your settings.</CardDescription>
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <SettingsIcon className="w-8 h-8 text-primary" />
            Settings
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage your account, alert preferences, and subscription.
          </p>
        </div>

        <Tabs defaultValue="alerts" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="alerts" className="gap-2">
              <Bell className="w-4 h-4" /> Alerts
            </TabsTrigger>
            <TabsTrigger value="account" className="gap-2">
              <User className="w-4 h-4" /> Account
            </TabsTrigger>
            <TabsTrigger value="subscription" className="gap-2">
              <CreditCard className="w-4 h-4" /> Plan
            </TabsTrigger>
          </TabsList>

          {/* Alert Preferences Tab */}
          <TabsContent value="alerts" className="space-y-6">
            {/* Signal Types */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-primary" />
                  Signal Types
                </CardTitle>
                <CardDescription>
                  Choose which types of signals you want to receive alerts for.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {SIGNAL_TYPES.map(({ key, label, icon: Icon, description }) => (
                  <div 
                    key={key}
                    className="flex items-center justify-between p-3 rounded-lg border border-border/50 hover:border-border transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Icon className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{label}</p>
                        <p className="text-sm text-muted-foreground">{description}</p>
                      </div>
                    </div>
                    <Switch
                      checked={alertPrefs[key as keyof typeof alertPrefs] as boolean}
                      onCheckedChange={() => handleToggleSignal(key)}
                    />
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Confidence Threshold */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-primary" />
                  Confidence Threshold
                </CardTitle>
                <CardDescription>
                  Only receive alerts for signals above this confidence level.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Minimum Confidence</span>
                    <Badge variant="secondary" className="text-lg px-3">
                      {Math.round(alertPrefs.minConfidence * 100)}%
                    </Badge>
                  </div>
                  <Slider
                    value={[alertPrefs.minConfidence * 100]}
                    onValueChange={([value]) => setAlertPrefs(prev => ({ ...prev, minConfidence: value / 100 }))}
                    min={30}
                    max={95}
                    step={5}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>30% (More signals)</span>
                    <span>95% (High confidence only)</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Email Notifications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-primary" />
                  Email Notifications
                </CardTitle>
                <CardDescription>
                  Configure how you receive signal alerts via email.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Enable Email Alerts</p>
                    <p className="text-sm text-muted-foreground">Receive signal alerts in your inbox</p>
                  </div>
                  <Switch
                    checked={alertPrefs.emailEnabled}
                    onCheckedChange={(checked) => setAlertPrefs(prev => ({ ...prev, emailEnabled: checked }))}
                  />
                </div>
                
                {alertPrefs.emailEnabled && (
                  <>
                    <Separator />
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="your@email.com"
                        value={alertPrefs.emailAddress}
                        onChange={(e) => setAlertPrefs(prev => ({ ...prev, emailAddress: e.target.value }))}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Alert Frequency</Label>
                      <Select
                        value={alertPrefs.digestFrequency}
                        onValueChange={(value: "instant" | "hourly" | "daily") => 
                          setAlertPrefs(prev => ({ ...prev, digestFrequency: value }))
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="instant">Instant (Real-time)</SelectItem>
                          <SelectItem value="hourly">Hourly Digest</SelectItem>
                          <SelectItem value="daily">Daily Summary</SelectItem>
                        </SelectContent>
                      </Select>
                      <p className="text-xs text-muted-foreground">
                        {alertPrefs.digestFrequency === "instant" && "Receive alerts immediately when signals are detected"}
                        {alertPrefs.digestFrequency === "hourly" && "Receive a summary of signals every hour"}
                        {alertPrefs.digestFrequency === "daily" && "Receive a daily digest of all signals"}
                      </p>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Save Button */}
            <div className="flex justify-end">
              <Button onClick={handleSave} disabled={isSaving} className="gap-2">
                {isSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Check className="w-4 h-4" />
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          </TabsContent>

          {/* Account Tab */}
          <TabsContent value="account" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5 text-primary" />
                  Account Information
                </CardTitle>
                <CardDescription>
                  Your account details and profile information.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                    <User className="w-8 h-8 text-primary" />
                  </div>
                  <div>
                    <p className="text-xl font-semibold">{user?.name || "User"}</p>
                    <p className="text-muted-foreground">{user?.email || "No email set"}</p>
                  </div>
                </div>
                
                <Separator />
                
                <div className="grid gap-4">
                  <div className="flex justify-between items-center py-2">
                    <span className="text-muted-foreground">User ID</span>
                    <code className="bg-muted px-2 py-1 rounded text-sm">{user?.id}</code>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-muted-foreground">Role</span>
                    <Badge variant={user?.role === "admin" ? "default" : "secondary"}>
                      {user?.role || "user"}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-muted-foreground">Login Method</span>
                    <span className="text-sm">{user?.loginMethod || "OAuth"}</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-muted-foreground">Member Since</span>
                    <span className="text-sm">
                      {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : "N/A"}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Data & Privacy */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-primary" />
                  Data & Privacy
                </CardTitle>
                <CardDescription>
                  Manage your data and privacy settings.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    Your data is stored securely and never shared with third parties. 
                    Signal detection data is anonymized and used only to improve our algorithms.
                  </p>
                </div>
                <Button variant="outline" className="w-full" onClick={() => toast.info("Feature coming soon")}>
                  Export My Data
                </Button>
                <Button variant="destructive" className="w-full" onClick={() => toast.info("Please contact support to delete your account")}>
                  Delete Account
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Subscription Tab */}
          <TabsContent value="subscription" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="w-5 h-5 text-primary" />
                  Current Plan
                </CardTitle>
                <CardDescription>
                  Your subscription status and billing information.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 bg-primary/5 rounded-lg border border-primary/20">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-xl font-bold capitalize">{subscription?.tier || "Free"}</h3>
                      <Badge variant={subscription?.status === "active" ? "default" : "secondary"}>
                        {subscription?.status || "Active"}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {subscription?.tier === "free" 
                        ? "7-day delayed signals with basic access"
                        : subscription?.tier === "pro"
                        ? "Real-time signals with full history"
                        : "Enterprise access with API & webhooks"
                      }
                    </p>
                  </div>
                  {subscription?.tier === "free" && (
                    <Link href="/pricing">
                      <Button>Upgrade</Button>
                    </Link>
                  )}
                </div>
                
                {subscription?.tier !== "free" && (
                  <>
                    <Separator />
                    <div className="grid gap-4">
                      {subscription?.currentPeriodStart && (
                        <div className="flex justify-between items-center py-2">
                          <span className="text-muted-foreground">Current Period Start</span>
                          <span className="text-sm">
                            {new Date(subscription.currentPeriodStart).toLocaleDateString()}
                          </span>
                        </div>
                      )}
                      {subscription?.currentPeriodEnd && (
                        <div className="flex justify-between items-center py-2">
                          <span className="text-muted-foreground">Next Billing Date</span>
                          <span className="text-sm">
                            {new Date(subscription.currentPeriodEnd).toLocaleDateString()}
                          </span>
                        </div>
                      )}
                    </div>
                    <Button variant="outline" className="w-full" onClick={() => toast.info("Please contact support to manage your subscription")}>
                      Manage Subscription
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Plan Comparison */}
            <Card>
              <CardHeader>
                <CardTitle>Plan Features</CardTitle>
                <CardDescription>
                  Compare what's included in each plan.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  {/* Free */}
                  <div className={`p-4 rounded-lg border ${subscription?.tier === "free" ? "border-primary bg-primary/5" : "border-border"}`}>
                    <h4 className="font-semibold mb-2">Free</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> 7-day signal history
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> 24h delay
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> Basic dashboard
                      </li>
                    </ul>
                  </div>
                  
                  {/* Pro */}
                  <div className={`p-4 rounded-lg border ${subscription?.tier === "pro" ? "border-primary bg-primary/5" : "border-border"}`}>
                    <h4 className="font-semibold mb-2">Pro - $49/mo</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> Real-time signals
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> Full history
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> Email alerts
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> API access
                      </li>
                    </ul>
                  </div>
                  
                  {/* Enterprise */}
                  <div className={`p-4 rounded-lg border ${subscription?.tier === "enterprise" ? "border-primary bg-primary/5" : "border-border"}`}>
                    <h4 className="font-semibold mb-2">Enterprise - $199/mo</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> Everything in Pro
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> Custom signals
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> Webhooks
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-primary" /> Dedicated support
                      </li>
                    </ul>
                  </div>
                </div>
                
                {subscription?.tier === "free" && (
                  <div className="mt-6 text-center">
                    <Link href="/pricing">
                      <Button size="lg" className="gap-2">
                        <Zap className="w-4 h-4" />
                        View Full Pricing
                      </Button>
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Risk Disclaimer */}
            <Card className="border-yellow-500/20 bg-yellow-500/5">
              <CardContent className="pt-6">
                <div className="flex gap-3">
                  <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-muted-foreground">
                    <p className="font-medium text-foreground mb-1">Risk Disclaimer</p>
                    <p>
                      Echo Signal Detector provides informational signals only. We are not registered 
                      investment advisors. Past performance does not guarantee future results. 
                      Always do your own research and consult qualified professionals before making 
                      investment decisions.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
