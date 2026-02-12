from state import AgentState
from observability import AgentObservability
from planner_agent import PlannerAgent
from research_agent import ResearchAgent
from writer_agent import WriterAgent
from verifier_agent import VerifierAgent

print("=" * 80)
print("TESTING ALL 4 AGENTS")
print("=" * 80)

obs = AgentObservability()
planner = PlannerAgent(obs)
researcher = ResearchAgent(obs)
writer = WriterAgent(obs)
verifier = VerifierAgent(obs)

state: AgentState = {
    "user_query": "What are the best practices for reducing hospital readmissions for diabetes patients?",
    "output_mode": "executive",
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
    "timestamp": "",
    "total_tokens": 0,
    "total_latency": 0.0
}

print("\n1/4 Running Planner Agent...")
state = planner.plan(state)
print(f"Plan created with {len(state['research_queries'])} queries")

print("\n2/4 Running Research Agent...")
state = researcher.research(state)
print(f"{len(state['research_notes'])} research notes created")

print("\n3/4 Running Writer Agent...")
state = writer.write(state)
print(f"Deliverables created:")
print(f"   - Summary: {len(state['executive_summary'])} chars")
print(f"   - Email: {len(state['email_draft'])} chars")
print(f"   - Actions: {len(state['action_items'])} items")

print("\n4/4 Running Verifier Agent...")
state = verifier.verify(state)
print(f"Verification: {state['verification_status']}")

print("\n" + "=" * 80)
print("FINAL DELIVERABLES")
print("=" * 80)

print("\nEXECUTIVE SUMMARY:")
print(state['executive_summary'])

print("\nEMAIL DRAFT:")
print(state['email_draft'])

print("\nACTION ITEMS:")
for i, action in enumerate(state['action_items'], 1):
    print(f"{i}. {action['task']}")
    print(f"   Owner: {action['owner']} | Due: {action['due_date']} | Confidence: {action['confidence']}")

print("\nVERIFICATION:")
print(f"Status: {state['verification_status']}")
if state['hallucination_flags']:
    print(f"Hallucinations: {len(state['hallucination_flags'])}")
if state['missing_evidence']:
    print(f"Missing Evidence: {len(state['missing_evidence'])}")

print("\n" + "=" * 80)
print("OBSERVABILITY")
print("=" * 80)
summary = obs.get_summary()
print(f"Total latency: {summary['total_latency_seconds']}s")
print(f"Total tokens: {summary['total_tokens_used']}")
print(f"Errors: {summary['error_count']}")

print("\n" + "=" * 80)
print("DAY 2 COMPLETE!")
print("=" * 80)