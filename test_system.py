print("🧪 Testing CMHP Automation System")
print("=================================")

# Import modules
try:
    from health_tracker import health_tracker
    print("✅ Health tracker: Imported")
except:
    print("❌ Health tracker: Failed")

try:
    from financial_tracker import finances
    print("✅ Financial tracker: Imported")
except:
    print("❌ Financial tracker: Failed")

try:
    from alert_system import alerts
    print("✅ Alert system: Imported")
except:
    print("❌ Alert system: Failed")

try:
    from scheduler import scheduler
    print("✅ Scheduler: Imported")
except:
    print("❌ Scheduler: Failed")

print("\n📊 System Status:")
print(f"- Dashboard: https://regenesisart.github.io/cmhp-dashboard/")
print(f"- Agent: https://regenesis-agent-510958561702.us-central1.run.app/")
print(f"- eBay Approval: Pending (1-2 days)")
print(f"- Sprint Progress: 50% complete")
