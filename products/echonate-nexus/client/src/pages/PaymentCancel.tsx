import { Link } from "wouter";
import { XCircle, ArrowLeft, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function PaymentCancel() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="max-w-lg w-full">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-yellow-500/20 rounded-full flex items-center justify-center mb-4">
            <XCircle className="w-10 h-10 text-yellow-500" />
          </div>
          <CardTitle className="text-2xl">Payment Cancelled</CardTitle>
          <CardDescription>
            Your payment was not completed. No charges have been made.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm text-muted-foreground">
              If you experienced any issues during checkout, please try again or contact our support team.
            </p>
          </div>

          <div className="flex flex-col gap-3">
            <Button asChild className="w-full">
              <Link href="/pricing">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Return to Pricing
              </Link>
            </Button>
            <Button variant="outline" asChild className="w-full">
              <Link href="/">
                <HelpCircle className="w-4 h-4 mr-2" />
                Contact Support
              </Link>
            </Button>
          </div>

          <p className="text-xs text-center text-muted-foreground">
            Need help? Email support@echosignal.io
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
