"""
Zapier Integration Tester
Tests webhook connectivity and payload delivery
"""

import requests
import json
from datetime import datetime
import sys

class ZapierTester:
    """Test Zapier webhooks with structured payloads"""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def test_connection(self, test_name="basic_test"):
        """Send test payload to Zapier webhook"""
        payload = {
            "event": "zapier_test",
            "test_name": test_name,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "sovereign_os",
            "data": {
                "status": "testing_connection",
                "message": "If you receive this, Zapier integration is working!"
            }
        }
        
        print(f"\n🔄 Testing webhook: {self.webhook_url[:50]}...")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            result = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_text": response.text[:200],  # First 200 chars
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if result["success"]:
                print("✅ SUCCESS! Webhook triggered successfully.")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text[:100]}")
            else:
                print(f"❌ FAILED! Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
            
            return result
            
        except requests.exceptions.Timeout:
            print("❌ TIMEOUT! Webhook took too long to respond.")
            return {"success": False, "error": "timeout"}
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR! Could not reach webhook.")
            return {"success": False, "error": "connection_error"}
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_feedback_os_payload(self):
        """Test with Feedback OS style payload"""
        payload = {
            "event": "feedback_checkin",
            "timestamp": datetime.utcnow().isoformat(),
            "checkin_type": "morning",
            "data": {
                "energy": 8,
                "focus": 7,
                "mood": 8,
                "notes": "Test check-in from automation"
            }
        }
        
        print("\n🧪 Testing Feedback OS payload format...")
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            success = response.status_code == 200
            print("✅ Feedback OS format accepted!" if success else "❌ Feedback OS format failed!")
            
            return {
                "success": success,
                "status_code": response.status_code,
                "payload_type": "feedback_os"
            }
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}


def load_config():
    """Load webhook URLs from config file"""
    try:
        with open("zapier_config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("\n⚠️  Config file not found!")
        print("Creating zapier_config.json template...")
        
        template = {
            "zapier_webhooks": {
                "feedback_os": "PASTE_YOUR_WEBHOOK_URL_HERE",
                "alerts": "PASTE_YOUR_ALERTS_WEBHOOK_HERE",
                "logging": "PASTE_YOUR_LOGGING_WEBHOOK_HERE"
            },
            "notes": "Replace the placeholder URLs with actual webhook URLs from your Zaps"
        }
        
        with open("zapier_config.json", "w") as f:
            json.dump(template, f, indent=2)
        
        print("✅ Template created! Edit zapier_config.json and run again.\n")
        return None


def main():
    """Main test routine"""
    print("\n" + "="*60)
    print("ZAPIER INTEGRATION TESTER")
    print("="*60)
    
    # Load config
    config = load_config()
    if not config:
        sys.exit(1)
    
    webhooks = config.get("zapier_webhooks", {})
    
    # Test feedback_os webhook if configured
    feedback_webhook = webhooks.get("feedback_os", "")
    
    if not feedback_webhook or feedback_webhook == "PASTE_YOUR_WEBHOOK_URL_HERE":
        print("\n⚠️  No webhook URL configured!")
        print("Edit zapier_config.json and add your webhook URL.")
        sys.exit(1)
    
    # Run tests
    tester = ZapierTester(feedback_webhook)
    
    print("\n📋 TEST 1: Basic Connection")
    print("-" * 60)
    result1 = tester.test_connection("basic_connectivity")
    
    print("\n📋 TEST 2: Feedback OS Payload")
    print("-" * 60)
    result2 = tester.test_feedback_os_payload()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Basic Test: {'✅ PASS' if result1['success'] else '❌ FAIL'}")
    print(f"Feedback OS Test: {'✅ PASS' if result2['success'] else '❌ FAIL'}")
    print("\nNext steps:")
    if result1['success'] and result2['success']:
        print("✅ All tests passed! Zapier integration is working.")
        print("✅ You can now connect Feedback OS to Zapier automation.")
    else:
        print("❌ Some tests failed. Check:")
        print("   1. Webhook URL is correct")
        print("   2. Zap is turned ON")
        print("   3. Internet connection is working")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
