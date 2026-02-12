from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from state import AgentState, ActionItem
from observability import AgentObservability
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class WriterAgent:
    
    def __init__(self, observability: AgentObservability):
        self.llm = ChatAnthropic(
            model=os.getenv("MODEL_NAME", "claude-sonnet-4-20250514"),
            temperature=0.3,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.obs = observability
        
        self.executive_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an executive report writer for healthcare leadership.

Create outputs for C-suite executives who need:
- Strategic insights, not technical details
- Clear business impact and ROI
- Actionable recommendations
- Concise, professional tone

Use the research notes provided, cite sources properly."""),
            ("human", self._get_writer_template())
        ])
        
        self.analyst_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a healthcare data analyst report writer.

Create outputs for analysts and data teams who need:
- Detailed findings with statistical context
- Comprehensive methodology notes
- Technical accuracy and depth
- All relevant data points and trends

Use the research notes provided, cite sources properly."""),
            ("human", self._get_writer_template())
        ])
    
    def _get_writer_template(self) -> str:
        return """User Request: {query}

Execution Plan: {plan}

Research Notes:
{research_notes}

Create the following deliverables:

1. EXECUTIVE SUMMARY (max 150 words)
[Write concise summary here]

2. CLIENT-READY EMAIL
Subject: [Write subject line]
[Write professional email body]

3. ACTION ITEMS
Provide 3-5 action items in JSON format:
[{{"task": "...", "owner": "...", "due_date": "YYYY-MM-DD", "confidence": "High|Medium|Low"}}]

Cite sources as: [Source: DocumentName, Page X]"""
    
    def write(self, state: AgentState) -> AgentState:
        """Generate deliverables based on output mode"""
        start_time = self.obs.log_agent_start("Writer", {
            "mode": state["output_mode"],
            "research_notes_count": len(state["research_notes"])
        })
        
        try:

            notes_text = "\n\n".join([
                f"Finding {i+1}:\n{note['content']}\n"
                f"[Source: {note['source']}, Page {note['page']}, {note['chunk_id']}]"
                for i, note in enumerate(state["research_notes"][:10])
            ])
            
            prompt = self.executive_prompt if state["output_mode"] == "executive" else self.analyst_prompt
            
            response = self.llm.invoke(
                prompt.format_messages(
                    query=state["user_query"],
                    plan=state["execution_plan"],
                    research_notes=notes_text
                )
            )
            
            content = response.content
            
            summary = self._extract_section(content, "EXECUTIVE SUMMARY", "CLIENT-READY EMAIL")
            email = self._extract_section(content, "CLIENT-READY EMAIL", "ACTION ITEMS")
            actions_text = self._extract_section(content, "ACTION ITEMS", "---END---")
            
            action_items = self._parse_actions(actions_text)
            
            state["executive_summary"] = summary.strip()
            state["email_draft"] = email.strip()
            state["action_items"] = action_items
            state["current_agent"] = "Writer"
            
            usage = response.response_metadata.get('usage', {})
            tokens = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            
            self.obs.log_agent_end("Writer", start_time, {
                "summary_length": len(summary),
                "email_length": len(email),
                "action_count": len(action_items)
            }, tokens=tokens)
            
            return state
            
        except Exception as e:
            self.obs.log_agent_end("Writer", start_time, None, error=str(e))
            state["error_log"].append(f"Writer error: {str(e)}")
            return state
    
    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> str:
        """Extract text between two markers"""
        try:
            start_idx = text.find(start_marker)
            end_idx = text.find(end_marker) if end_marker != "---END---" else len(text)
            
            if start_idx == -1:
                return ""
            
            section = text[start_idx + len(start_marker):end_idx]
            return section.strip()
        except:
            return ""
    
    def _parse_actions(self, actions_text: str) -> list:
        try:
            start = actions_text.find('[')
            end = actions_text.rfind(']') + 1
            
            if start != -1 and end > start:
                json_str = actions_text[start:end]
                actions = json.loads(json_str)
                
                validated = []
                for action in actions:
                    if all(k in action for k in ["task", "owner", "due_date", "confidence"]):
                        validated.append(action)
                
                return validated if validated else self._create_default_actions()
            
            return self._create_default_actions()
        except:
            return self._create_default_actions()
    
    def _create_default_actions(self):
        return [
            {
                "task": "Review research findings and recommendations",
                "owner": "Healthcare Team Lead",
                "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "confidence": "High"
            }
        ]