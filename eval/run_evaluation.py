import json
import sys
import os
from datetime import datetime
import pandas as pd
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / 'agents'))

from graph import HealthcareMultiAgentSystem

def run_evaluation():
    """Run all test queries and collect results"""
    
    with open('test_queries_short.json', 'r') as f:
        test_queries = json.load(f)
    
    system = HealthcareMultiAgentSystem()
    results = []
    
    print("=" * 80)
    print("STARTING EVALUATION")
    print("=" * 80)
    print(f"Total queries: {len(test_queries)}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Processing {test['id']}: {test['query'][:60]}...")
        
        try:
            system = HealthcareMultiAgentSystem()
            
            result = system.run(test['query'], test['mode'])
            
            eval_result = {
                "query_id": test['id'],
                "query": test['query'],
                "mode": test['mode'],
                "status": "SUCCESS",
                "verification_status": result['verification_status'],
                "summary_length": len(result['executive_summary'].split()),
                "summary_chars": len(result['executive_summary']),
                "action_items_count": len(result['action_items']),
                "sources_count": len(result['sources']),
                "latency_seconds": result['observability']['total_latency_seconds'],
                "tokens_used": result['observability']['total_tokens_used'],
                "error_count": result['observability']['error_count'],
                "hallucinations": len(result['hallucinations']),
                "missing_evidence": len(result['missing_evidence']),
                "agents_executed": result['observability']['total_agents_executed']
            }
            
            print(f"  Status: {eval_result['status']}")
            print(f"  Verification: {eval_result['verification_status']}")
            print(f"  Latency: {eval_result['latency_seconds']}s")
            print(f"  Tokens: {eval_result['tokens_used']}")
            
        except Exception as e:
            eval_result = {
                "query_id": test['id'],
                "query": test['query'],
                "mode": test['mode'],
                "status": "FAILED",
                "error": str(e)
            }
            print(f"  Status: FAILED")
            print(f"  Error: {str(e)[:100]}")
        
        results.append(eval_result)

    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f'eval_results_{timestamp}.csv'
    df.to_csv(csv_file, index=False)
    

    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Queries: {len(results)}")
    
    success_results = [r for r in results if r['status'] == 'SUCCESS']
    print(f"Successful: {len(success_results)}")
    print(f"Failed: {len(results) - len(success_results)}")
    
    if success_results:
        print(f"\nPERFORMANCE METRICS (Successful queries only)")
        print("-" * 80)
        
        avg_latency = sum(r['latency_seconds'] for r in success_results) / len(success_results)
        avg_tokens = sum(r['tokens_used'] for r in success_results) / len(success_results)
        
        print(f"Average Latency: {avg_latency:.2f}s")
        print(f"Average Tokens: {avg_tokens:.0f}")
        print(f"Total Tokens Used: {sum(r['tokens_used'] for r in success_results):,}")
        print(f"Estimated Cost: ${sum(r['tokens_used'] for r in success_results) * 0.000003:.4f}")
        
        verified = sum(1 for r in success_results if r['verification_status'] == 'PASSED')
        print(f"\nVerification PASSED: {verified}/{len(success_results)} ({verified/len(success_results)*100:.1f}%)")
        
        with_issues = sum(1 for r in success_results if r.get('hallucinations', 0) > 0 or r.get('missing_evidence', 0) > 0)
        print(f" Queries with Issues: {with_issues}/{len(success_results)}")
        
        print(f"\n OUTPUT QUALITY")
        print("-" * 80)
        avg_summary_words = sum(r['summary_length'] for r in success_results) / len(success_results)
        avg_actions = sum(r['action_items_count'] for r in success_results) / len(success_results)
        avg_sources = sum(r['sources_count'] for r in success_results) / len(success_results)
        
        print(f"Average Summary Length: {avg_summary_words:.0f} words")
        print(f"Average Action Items: {avg_actions:.1f}")
        print(f"Average Sources Cited: {avg_sources:.1f}")
        
        exec_results = [r for r in success_results if r['mode'] == 'executive']
        analyst_results = [r for r in success_results if r['mode'] == 'analyst']
        
        if exec_results and analyst_results:
            print(f"\nMODE COMPARISON")
            print("-" * 80)
            exec_avg_words = sum(r['summary_length'] for r in exec_results) / len(exec_results)
            analyst_avg_words = sum(r['summary_length'] for r in analyst_results) / len(analyst_results)
            
            print(f"Executive Mode Avg Summary: {exec_avg_words:.0f} words")
            print(f"Analyst Mode Avg Summary: {analyst_avg_words:.0f} words")
    
    print(f"\nResults saved to: {csv_file}")
    print("=" * 80)
    
    return df

if __name__ == "__main__":
    print("\nWARNING: This will take 10-15 minutes and cost ~$1.00 in API credits")
    response = input("Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        run_evaluation()
    else:
        print("Evaluation cancelled.")