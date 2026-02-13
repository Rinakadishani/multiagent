from graph import HealthcareMultiAgentSystem

print("=" * 80)
print("TESTING EXECUTIVE VS ANALYST MODE")
print("=" * 80)

system = HealthcareMultiAgentSystem()

query = "How can hospitals improve medication adherence for chronic disease patients?"

print("\n\n" + "-" * 40)
print("EXECUTIVE MODE")
print("-" * 40)
exec_result = system.run(query, output_mode="executive")

print("\n📋 Executive Summary:")
print(exec_result["executive_summary"][:300] + "...")

print("\n📧 Email (first 200 chars):")
print(exec_result["email_draft"][:200] + "...")

print("\n\n" + "-" * 40)
print("ANALYST MODE")
print("-" * 40)


system.obs = system.obs.__class__()

analyst_result = system.run(query, output_mode="analyst")

print("\nAnalyst Summary:")
print(analyst_result["executive_summary"][:300] + "...")

print("\n Email (first 200 chars):")
print(analyst_result["email_draft"][:200] + "...")

# Compare
print("\n" + "=" * 80)
print(" COMPARISON")
print("=" * 80)
print(f"Executive Summary Length: {len(exec_result['executive_summary'])} chars")
print(f"Analyst Summary Length: {len(analyst_result['executive_summary'])} chars")
print(f"Executive Actions: {len(exec_result['action_items'])}")
print(f"Analyst Actions: {len(analyst_result['action_items'])}")