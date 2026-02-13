from langgraph.graph import StateGraph, END
from state import AgentState
from planner_agent import PlannerAgent
from research_agent import ResearchAgent
from writer_agent import WriterAgent
from verifier_agent import VerifierAgent
from observability import AgentObservability
from typing import Literal
from datetime import datetime

class HealthcareMultiAgentSystem:
    """Complete multi-agent system using LangGraph"""
    
    def __init__(self):
        self.obs = AgentObservability()
        
        self.planner = PlannerAgent(self.obs)
        self.researcher = ResearchAgent(self.obs)
        self.writer = WriterAgent(self.obs)
        self.verifier = VerifierAgent(self.obs)
        
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Construct the agent workflow graph"""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("planner", self.planner.plan)
        workflow.add_node("researcher", self.researcher.research)
        workflow.add_node("writer", self.writer.write)
        workflow.add_node("verifier", self.verifier.verify)
        
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "writer")
        workflow.add_edge("writer", "verifier")
        workflow.add_edge("verifier", END)
        
        return workflow
    
    def run(self, user_query: str, output_mode: str = "executive") -> dict:

        initial_state: AgentState = {
            "user_query": user_query,
            "output_mode": output_mode,
            "execution_plan": "",
            "research_queries": [],
            "research_notes": [],
            "retrieved_documents": [],
            "executive_summary": "",
            "email_draft": "",
            "action_items": [],
            "verification_status": "",
            "hallucination_flags": [],
            "missing_evidence": [],
            "agent_trace": [],
            "current_agent": "",
            "error_log": [],
            "timestamp": datetime.now().isoformat(),
            "total_tokens": 0,
            "total_latency": 0.0
        }
        
        print("=" * 80)
        print("HEALTHCARE MULTI-AGENT COPILOT")
        print("=" * 80)
        print(f"Query: {user_query}")
        print(f"Mode: {output_mode}")
        print("=" * 80)
        
        final_state = self.app.invoke(initial_state)
        
        obs_summary = self.obs.get_summary()
        
        output = {
            "user_query": final_state["user_query"],
            "output_mode": final_state["output_mode"],
            "timestamp": final_state["timestamp"],

            "executive_summary": final_state["executive_summary"],
            "email_draft": final_state["email_draft"],
            "action_items": final_state["action_items"],
            
            "sources": self._compile_sources(final_state["research_notes"]),
            
            "verification_status": final_state["verification_status"],
            "hallucinations": final_state["hallucination_flags"],
            "missing_evidence": final_state["missing_evidence"],
            
            "observability": obs_summary,
            
            "errors": final_state["error_log"]
        }
        
        return output
    
    def _compile_sources(self, research_notes: list) -> list:
        sources_dict = {}
        
        for note in research_notes:
            key = note['source']
            if key not in sources_dict:
                sources_dict[key] = {
                    "document": note['source'],
                    "pages": set(),
                    "chunks": []
                }
            
            sources_dict[key]["pages"].add(note['page'])
            sources_dict[key]["chunks"].append(note['chunk_id'])
        
        sources = []
        for doc, info in sources_dict.items():
            sources.append({
                "document": doc,
                "pages": sorted(list(info["pages"])),
                "chunk_count": len(info["chunks"])
            })
        
        return sources


def main():
    system = HealthcareMultiAgentSystem()
    
    result = system.run(
        user_query="What are evidence-based strategies to reduce 30-day readmissions for heart failure patients?",
        output_mode="executive"
    )
    
    print("\n" + "=" * 80)
    print("DELIVERABLES")
    print("=" * 80)
    
    print("\nEXECUTIVE SUMMARY")
    print("-" * 80)
    print(result["executive_summary"])
    
    print("\nEMAIL DRAFT")
    print("-" * 80)
    print(result["email_draft"])
    
    print("\nACTION ITEMS")
    print("-" * 80)
    for i, action in enumerate(result["action_items"], 1):
        print(f"{i}. {action['task']}")
        print(f"   Owner: {action['owner']} | Due: {action['due_date']} | Confidence: {action['confidence']}")
    
    print("\nSOURCES")
    print("-" * 80)
    for source in result["sources"]:
        print(f"• {source['document']}")
        print(f"  Pages: {source['pages']} | Chunks: {source['chunk_count']}")
    
    print("\nVERIFICATION")
    print("-" * 80)
    print(f"Status: {result['verification_status']}")
    if result['hallucinations']:
        print(f"Hallucinations found: {len(result['hallucinations'])}")
        for h in result['hallucinations']:
            print(f"   - {h}")
    if result['missing_evidence']:
        print(f"Missing evidence: {len(result['missing_evidence'])}")
        for m in result['missing_evidence']:
            print(f"   - {m}")
    if not result['hallucinations'] and not result['missing_evidence']:
        print("All claims verified")
    
    print("\nOBSERVABILITY")
    print("-" * 80)
    obs = result["observability"]
    print(f"Total Latency: {obs['total_latency_seconds']}s")
    print(f"Total Tokens: {obs['total_tokens_used']}")
    print(f"Agents Executed: {obs['total_agents_executed']}")
    print(f"Errors: {obs['error_count']}")
    
    print("\n" + "=" * 80)
    print("SYSTEM TEST COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()