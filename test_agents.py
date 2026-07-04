"""
Quick test script to verify all agents are working before launching the UI.
Run: python test_agents.py
"""
from agents.orchestrator import OrchestratorAgent

def test_all_agents():
    print("=" * 60)
    print("KrishiMind — Agent Test Suite")
    print("=" * 60)

    orchestrator = OrchestratorAgent()

    test_cases = [
        {
            "label": "Weather Agent",
            "query": "Will it rain this week? Should I irrigate my fields?",
            "context": {"state": "Maharashtra", "season": "kharif", "soil_type": "black soil"}
        },
        {
            "label": "Crop Advisory Agent",
            "query": "Which crop should I grow in loamy soil this kharif season?",
            "context": {"state": "Punjab", "season": "kharif", "soil_type": "loamy"}
        },
        {
            "label": "Market Price Agent",
            "query": "What is the current price of onion? Should I sell now?",
            "context": {"state": "Maharashtra", "crop": "onion", "season": "rabi"}
        },
        {
            "label": "Pest & Disease Agent",
            "query": "My wheat leaves are turning yellow with orange spots. What is this?",
            "context": {"state": "Punjab", "crop": "wheat", "season": "rabi"}
        },
        {
            "label": "Multi-Agent (Weather + Crop)",
            "query": "Given this week's weather, should I sow cotton now?",
            "context": {"state": "Gujarat", "season": "kharif", "soil_type": "black soil"}
        },
    ]

    for i, tc in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {tc['label']}")
        print(f"Query: {tc['query']}")
        print("-" * 40)
        result = orchestrator.run(tc["query"], tc["context"])
        print(f"Agents used: {result['agents_used']}")
        print(f"Response:\n{result['final_response']}")
        print("=" * 60)

if __name__ == "__main__":
    test_all_agents()
