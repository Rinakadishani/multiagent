from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from state import AgentState
from observability import AgentObservability
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class PlannerAgent:
    
    def __init__(self, observability: AgentObservability):
        self.llm = ChatAnthropic(
            model=os.getenv("MODEL_NAME", "claude-sonnet-4-20250514"),
            temperature=0.2,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.obs = observability
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a strategic planning agent for healthcare analytics.

Your task is to:
1. Analyze the user's business request
2. Break it down into 3-5 specific research queries
3. Create a structured execution plan

Output Mode Context:
- Executive mode: Focus on high-level insights, strategic recommendations
- Analyst mode: Focus on detailed data, comprehensive analysis

Return your response in this exact format:

EXECUTION_PLAN:
[Your step-by-step plan]

RESEARCH_QUERIES:
1. [First specific query]
2. [Second specific query]
3. [Third specific query]
"""),
            ("human", "User Request: {query}\nOutput Mode: {mode}")
        ])
    
    def plan(self, state: AgentState) -> AgentState:
        start_time = self.obs.log_agent_start("Planner", {
            "query": state["user_query"],
            "mode": state["output_mode"]
        })
        
        try:
            response = self.llm.invoke(
                self.prompt.format_messages(
                    query=state["user_query"],
                    mode=state["output_mode"]
                )
            )
            
            content = response.content
            
            if "RESEARCH_QUERIES:" in content:
                plan_section = content.split("RESEARCH_QUERIES:")[0].replace("EXECUTION_PLAN:", "").strip()
                queries_section = content.split("RESEARCH_QUERIES:")[1].strip()
            else:
                plan_section = content
                queries_section = ""
            
            queries = []
            for line in queries_section.split("\n"):
                line = line.strip()
                if line and len(line) > 0 and line[0].isdigit():
                    if ". " in line:
                        query = line.split(". ", 1)[1]
                    else:
                        query = line
                    queries.append(query.strip())
            
            state["execution_plan"] = plan_section
            state["research_queries"] = queries
            state["current_agent"] = "Planner"
            
            usage = response.response_metadata.get('usage', {})
            tokens = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            
            self.obs.log_agent_end("Planner", start_time, {
                "plan_length": len(plan_section),
                "query_count": len(queries)
            }, tokens=tokens)
            
            return state
            
        except Exception as e:
            self.obs.log_agent_end("Planner", start_time, None, error=str(e))
            state["error_log"].append(f"Planner error: {str(e)}")
            return state