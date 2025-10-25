"""
Quick Brand Reputation Demo - Tests the running backend API
"""

import requests
import json
import time
from datetime import datetime

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_section(text):
    """Print a section header"""
    print("\n" + "-"*70)
    print(f"  {text}")
    print("-"*70)

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("✅ Backend Status: HEALTHY")
            print(f"   Database: {health.get('database', 'unknown')}")
            print(f"   Timestamp: {health.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"⚠️ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running!")
        print("   Please start the backend first:")
        print("   cd backend")
        print('   & "..\\.\\.venv\\Scripts\\python.exe" main.py')
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

def get_system_status():
    """Get detailed system status"""
    try:
        response = requests.get("http://localhost:8000/autonomous/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print_section("SYSTEM STATUS")
            print(f"Autonomous Mode: {status.get('autonomous_mode', 'unknown').upper()}")
            
            if 'orchestrator' in status:
                orch = status['orchestrator']
                if orch.get('initialized'):
                    print(f"Orchestrator: ✅ INITIALIZED")
                    if 'status' in orch and isinstance(orch['status'], dict):
                        agents = orch['status'].get('registered_agents', [])
                        print(f"Registered Agents: {len(agents)}")
                        for agent in agents:
                            print(f"  • {agent.get('agent_id', 'unknown')} - {', '.join(agent.get('capabilities', []))}")
            return True
        return False
    except Exception as e:
        print(f"⚠️ Could not get system status: {e}")
        return False

def trigger_brand_analysis(brand_name="Google"):
    """Trigger a brand reputation analysis"""
    print_section(f"TRIGGERING BRAND ANALYSIS: {brand_name}")
    print(f"⏳ Starting analysis... (this may take 15-30 seconds)")
    print(f"   The AI orchestrator will:")
    print(f"   1. Collect mentions from available sources")
    print(f"   2. Analyze sentiment and engagement")
    print(f"   3. Detect any issues or opportunities")
    print(f"   4. Generate recommendations\n")
    
    try:
        # Trigger autonomous cycle
        response = requests.post("http://localhost:8000/autonomous/trigger", timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print_section("ANALYSIS RESULTS")
            
            if result.get('success'):
                print("✅ Analysis Status: SUCCESS\n")
                
                # Parse and display the result
                if 'result' in result and isinstance(result['result'], dict):
                    analysis = result['result']
                    
                    # Display execution summary
                    if 'executed_plan' in analysis:
                        print("📋 Execution Plan:")
                        for i, step in enumerate(analysis['executed_plan'], 1):
                            status = "✅" if step.get('success') else "⚠️"
                            print(f"   {status} Step {i}: {step.get('description', 'Completed')}")
                        print()
                    
                    # Display agents used
                    if 'agents_used' in analysis:
                        print(f"🤖 Agents Involved: {', '.join(analysis['agents_used'])}\n")
                    
                    # Display main result/analysis
                    if 'result' in analysis:
                        print("📊 DETAILED ANALYSIS:")
                        print("-"*70)
                        result_text = analysis['result']
                        if isinstance(result_text, str):
                            # Format the output nicely
                            lines = result_text.split('\n')
                            for line in lines:
                                if line.strip():
                                    print(f"   {line}")
                        else:
                            print(json.dumps(result_text, indent=2))
                        print("-"*70)
                    
                    # Display recommendations
                    if 'recommendations' in analysis:
                        print("\n💡 RECOMMENDATIONS:")
                        for i, rec in enumerate(analysis['recommendations'], 1):
                            print(f"   {i}. {rec}")
                    
                    # Display success rate
                    if 'success_rate' in analysis:
                        rate = analysis['success_rate'] * 100
                        print(f"\n📈 Success Rate: {rate:.1f}%")
                
                print(f"\n⏱️ Completed at: {result.get('timestamp', 'unknown')}")
                
            else:
                print("⚠️ Analysis completed with issues")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
            
            return True
            
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out (analysis may still be running)")
        print("   Check the backend logs for status")
        return False
    except Exception as e:
        print(f"❌ Error triggering analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_demo():
    """Run the complete demo"""
    print_header("BRAND REPUTATION ANALYSIS DEMO")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Using: Multi-Agent AI System with LLM Orchestration")
    print("Note: Demo uses mock data (no expensive API keys required)")
    
    # Step 1: Check backend
    print_section("STEP 1: Checking Backend Status")
    if not check_backend_health():
        return
    
    time.sleep(1)
    
    # Step 2: Get system status
    print_section("STEP 2: Getting System Information")
    get_system_status()
    
    time.sleep(1)
    
    # Step 3: Run analysis
    print_section("STEP 3: Running Brand Reputation Analysis")
    success = trigger_brand_analysis("Google")
    
    # Final message
    print_header("DEMO COMPLETE")
    if success:
        print("✅ Brand reputation analysis completed successfully!")
        print("\n📚 Additional Resources:")
        print("   • API Docs: http://localhost:8000/docs")
        print("   • Health Check: http://localhost:8000/health")
        print("   • System Status: http://localhost:8000/autonomous/status")
        print("\n💡 You can also analyze different brands by modifying the script")
    else:
        print("⚠️ Analysis encountered some issues")
        print("   Check the backend logs for more details")
    
    print()

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
