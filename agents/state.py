from typing import TypedDict, List, Annotated, Literal
from langchain.schema import Document
from datetime import datetime
import operator

class ResearchNote(TypedDict):
    content: str
    source: str
    chunk_id: str
    page: int
    confidence: float

class ActionItem(TypedDict):
    task: str
    owner: str
    due_date: str
    confidence: Literal["High", "Medium", "Low"]

class AgentState(TypedDict):
    user_query: str
    output_mode: Literal["executive", "analyst"]
    
    execution_plan: str
    research_queries: List[str]
    
    research_notes: Annotated[List[ResearchNote], operator.add]
    retrieved_documents: List[Document]
    
    executive_summary: str
    email_draft: str
    action_items: List[ActionItem]
    
    verification_status: str
    hallucination_flags: List[str]
    missing_evidence: List[str]

    agent_trace: Annotated[List[dict], operator.add]
    current_agent: str
    error_log: Annotated[List[str], operator.add]
    
    timestamp: str
    total_tokens: int
    total_latency: float