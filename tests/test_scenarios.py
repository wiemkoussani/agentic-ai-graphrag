"""Test scenarios for evaluating the Agentic AI system."""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_db.client import Neo4jClient
from agent.graphrag import GraphRAGPipeline
from agent.agent import AgenticAI


class TestScenarios:
    """Test scenarios for system evaluation."""
    
    def __init__(self):
        self.client = Neo4jClient()
        self.graphrag = GraphRAGPipeline(self.client)
        self.agent = AgenticAI(self.graphrag)
        self.results = []
    
    def run_test(self, scenario_name: str, query: str, expected_tools: list = None):
        """Run a single test scenario."""
        print(f"\n{'='*60}")
        print(f"Test: {scenario_name}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            result = self.agent.query(query)
            elapsed_time = time.time() - start_time
            
            # Check if expected tools were used
            tools_match = True
            if expected_tools:
                tools_used = set(result.get("tools_used", []))
                expected_set = set(expected_tools)
                tools_match = expected_set.issubset(tools_used)
            
            test_result = {
                "scenario": scenario_name,
                "query": query,
                "response": result.get("response", ""),
                "tools_used": result.get("tools_used", []),
                "expected_tools": expected_tools,
                "tools_match": tools_match,
                "latency": elapsed_time,
                "steps": len(result.get("steps", [])),
                "success": True
            }
            
            print(f"✅ Response received in {elapsed_time:.2f}s")
            print(f"Tools used: {result.get('tools_used', [])}")
            print(f"Response preview: {result.get('response', '')[:200]}...")
            
            if expected_tools:
                if tools_match:
                    print(f"✅ Expected tools used correctly")
                else:
                    print(f"⚠️  Expected tools: {expected_tools}, Got: {result.get('tools_used', [])}")
            
            self.results.append(test_result)
            return test_result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ Error: {str(e)}")
            
            test_result = {
                "scenario": scenario_name,
                "query": query,
                "error": str(e),
                "latency": elapsed_time,
                "success": False
            }
            
            self.results.append(test_result)
            return test_result
    
    def run_all_tests(self):
        """Run all test scenarios."""
        print("\n" + "="*60)
        print("🧪 Running Test Scenarios")
        print("="*60)
        
        # Test Scenario 1: Graph Query - Actor Information
        self.run_test(
            "Graph Query - Actor Information",
            "Who acted in Inception?",
            expected_tools=["graph_query"]
        )
        
        # Test Scenario 2: Graph Query - Director Relationships
        self.run_test(
            "Graph Query - Director Relationships",
            "What films did Christopher Nolan direct?",
            expected_tools=["graph_query"]
        )
        
        # Test Scenario 3: Graph Query - Genre Information
        self.run_test(
            "Graph Query - Genre Information",
            "What genres does Breaking Bad belong to?",
            expected_tools=["graph_query"]
        )
        
        # Test Scenario 4: Calculator Tool
        self.run_test(
            "Calculator Tool",
            "Calculate 125 * 47 + 892",
            expected_tools=["calculator"]
        )
        
        # Test Scenario 5: Complex Multi-Tool Query
        self.run_test(
            "Complex Multi-Tool Query",
            "Who acted in Inception? Also calculate 15 to the power of 3.",
            expected_tools=["graph_query", "calculator"]
        )
        
        # Test Scenario 6: Graph Traversal
        self.run_test(
            "Graph Traversal",
            "Which actors worked together?",
            expected_tools=["graph_query"]
        )
        
        # Test Scenario 7: Film Details Query
        self.run_test(
            "Film Details Query",
            "What are the details of The Matrix?",
            expected_tools=["graph_query"]
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("📊 Test Summary")
        print("="*60)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get("success", False))
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%")
        
        if successful_tests > 0:
            avg_latency = sum(r.get("latency", 0) for r in self.results if r.get("success")) / successful_tests
            print(f"Average Latency: {avg_latency:.2f}s")
        
        # Tool usage statistics
        all_tools = []
        for result in self.results:
            if result.get("success"):
                all_tools.extend(result.get("tools_used", []))
        
        if all_tools:
            from collections import Counter
            tool_counts = Counter(all_tools)
            print("\nTool Usage:")
            for tool, count in tool_counts.items():
                print(f"  {tool}: {count} times")
        
        # Detailed results
        print("\n" + "="*60)
        print("Detailed Results")
        print("="*60)
        
        for i, result in enumerate(self.results, 1):
            status = "✅" if result.get("success") else "❌"
            print(f"\n{i}. {status} {result['scenario']}")
            print(f"   Query: {result['query']}")
            if result.get("success"):
                print(f"   Tools: {result.get('tools_used', [])}")
                print(f"   Latency: {result.get('latency', 0):.2f}s")
            else:
                print(f"   Error: {result.get('error', 'Unknown')}")
    
    def close(self):
        """Close connections."""
        self.client.close()


def main():
    """Main function to run tests."""
    tester = TestScenarios()
    
    try:
        tester.run_all_tests()
    finally:
        tester.close()


if __name__ == "__main__":
    main()



