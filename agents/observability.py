import time
from datetime import datetime
from typing import Dict, Any

class AgentObservability:
    
    def __init__(self):
        self.traces = []
    
    def log_agent_start(self, agent_name: str, input_data: Dict[str, Any]) -> float:
        start_time = time.time()
        trace = {
            "agent": agent_name,
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "input_preview": str(input_data)[:100],
            "start_time": start_time
        }
        self.traces.append(trace)
        return start_time
    
    def log_agent_end(self, agent_name: str, start_time: float, 
                      output_data: Dict[str, Any], tokens: int = 0, error: str = None):
        latency = time.time() - start_time
        trace = {
            "agent": agent_name,
            "status": "completed" if not error else "failed",
            "timestamp": datetime.now().isoformat(),
            "latency_seconds": round(latency, 2),
            "tokens_used": tokens,
            "output_preview": str(output_data)[:100] if output_data else None,
            "error": error
        }
        self.traces.append(trace)
        return trace
    
    def get_summary(self):
        total_latency = sum(t.get('latency_seconds', 0) for t in self.traces)
        total_tokens = sum(t.get('tokens_used', 0) for t in self.traces)
        errors = [t for t in self.traces if t.get('error')]
        
        return {
            "total_agents_executed": len([t for t in self.traces if t['status'] == 'started']),
            "total_latency_seconds": round(total_latency, 2),
            "total_tokens_used": total_tokens,
            "error_count": len(errors),
            "errors": errors,
            "detailed_trace": self.traces
        }