from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from state import AgentState
from observability import AgentObservability
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class VerifierAgent:
    """Checks for hallucinations, missing evidence, contradictions"""
    
    def __init__(self, observability: AgentObservability):
        self.llm = ChatAnthropic(
            model=os.getenv("MODEL_NAME", "claude-sonnet-4-20250514"),
            temperature=0,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.obs = observability
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a fact-checking verification agent.

Your job is to verify that all claims in the deliverables are supported by the research notes.

Check for:
1. **Hallucinations**: Claims not found in any research note
2. **Missing Evidence**: Important topics mentioned but not backed by sources
3. **Contradictions**: Claims that conflict with research findings
4. **Unsupported Statistics**: Numbers/percentages without source citations

For each issue found, provide:
- The specific claim
- Why it's problematic
- What evidence is missing

Be thorough but fair. If everything is properly supported, say "VERIFIED: All claims supported."
"""),
            ("human", """Research Notes:
{research_notes}

Executive Summary:
{summary}

Email Draft:
{email}

Action Items:
{actions}

Verify all content above.""")
        ])
    
    def verify(self, state: AgentState) -> AgentState:
        """Verify deliverables against research notes"""
        start_time = self.obs.log_agent_start("Verifier", {
            "summary_length": len(state.get("executive_summary", "")),
            "notes_count": len(state["research_notes"])
        })
        
        try:
            # Format inputs
            notes_text = "\n\n".join([
                f"{i+1}. {note['content'][:200]}...\n   Source: {note['source']}, {note['chunk_id']}"
                for i, note in enumerate(state["research_notes"][:10])
            ])
            
            actions_text = "\n".join([
                f"- {action['task']} (Owner: {action['owner']})"
                for action in state["action_items"]
            ])
            
            response = self.llm.invoke(
                self.prompt.format_messages(
                    research_notes=notes_text,
                    summary=state["executive_summary"],
                    email=state["email_draft"],
                    actions=actions_text
                )
            )
            
            content = response.content
            
            # Parse verification results
            if "VERIFIED: All claims supported" in content:
                state["verification_status"] = "PASSED"
                state["hallucination_flags"] = []
                state["missing_evidence"] = []
            else:
                state["verification_status"] = "ISSUES_FOUND"
                state["hallucination_flags"] = self._extract_issues(content, "Hallucination")
                state["missing_evidence"] = self._extract_issues(content, "Missing Evidence")
            
            state["current_agent"] = "Verifier"
            
            # Get token usage
            usage = response.response_metadata.get('usage', {})
            tokens = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            
            self.obs.log_agent_end("Verifier", start_time, {
                "status": state["verification_status"],
                "issues_found": len(state["hallucination_flags"]) + len(state["missing_evidence"])
            }, tokens=tokens)
            
            return state
            
        except Exception as e:
            self.obs.log_agent_end("Verifier", start_time, None, error=str(e))
            state["error_log"].append(f"Verifier error: {str(e)}")
            return state
    
    def _extract_issues(self, text: str, issue_type: str) -> list:
        """Extract specific types of issues from verification report"""
        issues = []
        lines = text.split('\n')
        
        in_section = False
        for line in lines:
            if issue_type.lower() in line.lower():
                in_section = True
                continue
            
            if in_section:
                if line.strip() and line.strip()[0] in ['-', '*', '•', '1', '2', '3', '4', '5']:
                    issues.append(line.strip().lstrip('-*•0123456789. ').strip())
                elif line.strip() and not line[0].isspace() and line.strip()[0].isupper():
                    in_section = False
        
        return issues