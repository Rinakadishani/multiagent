from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from state import AgentState, ResearchNote
from observability import AgentObservability
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retrieval.vector_store import HealthcareVectorStore

class ResearchAgent:
    
    def __init__(self, observability: AgentObservability):
        self.llm = ChatAnthropic(
            model=os.getenv("MODEL_NAME", "claude-sonnet-4-20250514"),
            temperature=0.1,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.obs = observability
        self.vector_store = HealthcareVectorStore(persist_directory="../chroma_db")
        self.vector_store.load_vectorstore()
        
        self.synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research synthesis agent.

Analyze the retrieved documents and extract key findings that answer the research query.
For each finding:
- State it clearly and concisely
- Note which document it came from
- Be honest: if the documents don't contain relevant information, say "Not found in sources"."""),
            ("human", """Research Query: {query}

Retrieved Documents:
{documents}

Extract 2-3 key findings with sources.""")
        ])
    
    def research(self, state: AgentState) -> AgentState:
        start_time = self.obs.log_agent_start("Research", {
            "queries": state["research_queries"]
        })
        
        try:
            all_notes = []
            total_tokens = 0
            
            for query in state["research_queries"]:
                results = self.vector_store.similarity_search(query, k=4)
                
                doc_text = "\n\n---\n\n".join([
                    f"Document: {doc.metadata['doc_name']}\n"
                    f"Page: {doc.metadata.get('page', 'N/A')}\n"
                    f"Chunk ID: {doc.metadata['chunk_id']}\n"
                    f"Content: {doc.page_content}"
                    for doc, score in results
                ])
                
                response = self.llm.invoke(
                    self.synthesis_prompt.format_messages(
                        query=query,
                        documents=doc_text
                    )
                )
                
                usage = response.response_metadata.get('usage', {})
                tokens = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                total_tokens += tokens
                
                for doc, score in results:
                    note: ResearchNote = {
                        "content": response.content[:500],
                        "source": doc.metadata['doc_name'],
                        "chunk_id": doc.metadata['chunk_id'],
                        "page": doc.metadata.get('page', 0),
                        "confidence": 1.0 - min(score / 2.0, 1.0)
                    }
                    all_notes.append(note)
            
            state["research_notes"] = all_notes
            state["current_agent"] = "Research"
            
            self.obs.log_agent_end("Research", start_time, {
                "notes_created": len(all_notes)
            }, tokens=total_tokens)
            
            return state
            
        except Exception as e:
            self.obs.log_agent_end("Research", start_time, None, error=str(e))
            state["error_log"].append(f"Research error: {str(e)}")
            return state