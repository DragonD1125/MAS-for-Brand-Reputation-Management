"""
Brand Reputation Analysis Demo Script
Uses free/mock data sources to demonstrate the system capabilities
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.orchestrator_llm import LangChainOrchestrator
from app.agents.data_collection_agent_llm import SmartDataCollectionAgent
from app.agents.alert_management_agent import AlertManagementAgent
from loguru import logger

async def run_demo_analysis(brand_name: str = "Tesla"):
    """Run a complete brand reputation analysis demo"""
    
    print("\n" + "="*60)
    print(f"  BRAND REPUTATION ANALYSIS DEMO")
    print(f"  Brand: {brand_name}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    try:
        # Initialize orchestrator
        print("🤖 Initializing AI Orchestrator...")
        orchestrator = LangChainOrchestrator("demo_orchestrator")
        await orchestrator.initialize_agent()
        print("✅ Orchestrator ready\n")
        
        # Initialize data collection agent
        print("📊 Initializing Data Collection Agent...")
        data_agent = SmartDataCollectionAgent("demo_data_collector")
        await data_agent.initialize_agent()
        await orchestrator.register_agent(data_agent)
        print("✅ Data agent ready\n")
        
        # Initialize alert agent
        print("🚨 Initializing Alert Management Agent...")
        alert_agent = AlertManagementAgent("demo_alert_manager")
        await alert_agent.initialize_agent()
        await orchestrator.register_agent(alert_agent)
        print("✅ Alert agent ready\n")
        
        print("-"*60)
        print("🔍 STARTING BRAND MONITORING ANALYSIS...")
        print("-"*60 + "\n")
        
        # Create strategic goal for the orchestrator
        strategic_goal = f"""
DEMO BRAND REPUTATION ANALYSIS FOR: {Google}

OBJECTIVE: Conduct a comprehensive brand reputation analysis to demonstrate system capabilities.

TASKS:
1. Collect brand mentions from available data sources (using mock data where APIs unavailable)
2. Analyze sentiment and engagement patterns
3. Identify any potential reputation issues or opportunities
4. Generate actionable insights and recommendations

AVAILABLE AGENTS:
- Smart Data Collection Agent: Can collect mentions from Twitter, Reddit, and News
- Alert Management Agent: Can detect crisis indicators and anomalies

EXPECTED OUTPUT:
- Summary of mentions found across platforms
- Sentiment analysis (positive/negative/neutral breakdown)
- Key themes and topics
- Engagement metrics
- Risk assessment
- Recommended actions

NOTE: This is a demo using mock/sample data to showcase system capabilities.
Twitter, Reddit, and Instagram APIs are not configured, so realistic mock data will be used.

Execute this analysis and provide a comprehensive report.
"""
        
        # Execute the strategic goal
        print("🧠 AI Orchestrator is analyzing the brand reputation...")
        print("   (This may take 15-30 seconds)\n")
        
        result = await orchestrator.execute_strategic_goal(strategic_goal)
        
        print("\n" + "="*60)
        print("  ANALYSIS COMPLETE")
        print("="*60 + "\n")
        
        if result.get("success"):
            print("✅ Status: SUCCESS\n")
            
            # Display execution details
            if "executed_plan" in result:
                print("📋 Execution Plan:")
                for i, step in enumerate(result["executed_plan"], 1):
                    print(f"   {i}. {step.get('description', 'Step executed')}")
                print()
            
            # Display agents involved
            if "agents_used" in result:
                print(f"🤖 Agents Involved: {', '.join(result['agents_used'])}\n")
            
            # Display main result
            if "result" in result:
                print("📊 ANALYSIS RESULTS:")
                print("-"*60)
                print(result["result"])
                print("-"*60)
            
            # Display recommendations
            if "recommendations" in result:
                print("\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(result["recommendations"], 1):
                    print(f"   {i}. {rec}")
        else:
            print(f"⚠️ Status: PARTIAL SUCCESS")
            print(f"   Message: {result.get('error', 'Unknown issue')}\n")
            
            if "result" in result:
                print("📊 Partial Results:")
                print(result["result"])
        
        print("\n" + "="*60)
        print("  DEMO COMPLETE")
        print("="*60 + "\n")
        
        # Cleanup
        await orchestrator.shutdown()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Error during demo: {e}\n")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Brand Reputation Analysis Demo")
    parser.add_argument(
        "--brand",
        type=str,
        default="Tesla",
        help="Brand name to analyze (default: Tesla)"
    )
    
    args = parser.parse_args()
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║  BRAND REPUTATION MANAGEMENT SYSTEM - DEMO MODE         ║")
    print("║  Multi-Agent AI Analysis System                         ║")
    print("╚" + "="*58 + "╝")
    
    # Run the demo
    asyncio.run(run_demo_analysis(args.brand))
    
    print("\n💡 TIP: Run with --brand 'YourBrand' to analyze a different brand")
    print("📚 Note: Using mock data for demo purposes (no API keys required)\n")

if __name__ == "__main__":
    main()
