import asyncio
import time
import logging
from typing import Dict, Any
from shared.schemas import AIProcessRequest, AIProcessResponse
from ai_core.agents.query_classifier import QueryClassifierAgent
from ai_core.agents.retriever_agent import RetrieverAgent
from ai_core.agents.reasoning_agent import ReasoningAgent

logger = logging.getLogger(__name__)

class MultiAgentPipeline:
    """
    Orchestrates the 5 AI agents.
    Executes sequential tasks (Rewrite -> Retrieve -> Reason)
    and parallel tasks (Validate + Explain).
    """

    def __init__(self):
        self.classifier = QueryClassifierAgent()
        self.retriever = RetrieverAgent()
        self.reasoner = ReasoningAgent()

    async def process(self, request: AIProcessRequest) -> AIProcessResponse:
        logger.info(f"Starting pipeline for query: '{request.query}'")
        agent_trace = {}
        
        try:
            # 1. Query Classifier (LLM Call 1)
            t0 = time.time()
            classification = await self.classifier.execute(request.query)
            category = classification.get("category", "GENERAL")
            rewritten_query = classification.get("rewritten_query", request.query)
            agent_trace["Classifier"] = {
                "time_ms": int((time.time()-t0)*1000), 
                "output": f"Category: {category} | Rewritten: {rewritten_query}"
            }
            
            # Short-circuit for CASUAL chat to save LLM/FAISS credits
            if category == "CASUAL":
                return AIProcessResponse(
                    answer="Hello! I am the CrisisBridge AI safety assistant. I can help you with emergency procedures, safety protocols, and general facility guidance. How can I assist you today?",
                    sources=[],
                    confidence=1.0,
                    explanation="Detected as casual chat.",
                    rewritten_query=request.query,
                    agent_trace=agent_trace
                )
            
            # 2. Retriever (Local Vector Search - No LLM Call)
            t0 = time.time()
            retrieval_result = await self.retriever.execute(rewritten_query)
            context = retrieval_result["context"]
            sources = retrieval_result["sources"]
            agent_trace["Retriever"] = {
                "time_ms": int((time.time()-t0)*1000), 
                "output": f"Retrieved {len(sources)} sources."
            }
            
            # 3. Reasoning (LLM Call 2)
            t0 = time.time()
            answer = await self.reasoner.execute(rewritten_query, context)
            agent_trace["Reasoning"] = {
                "time_ms": int((time.time()-t0)*1000), 
                "output": answer[:100] + ("..." if len(answer) > 100 else "")
            }
            
            return AIProcessResponse(
                answer=answer,
                sources=sources,
                confidence=0.9 if category == "GENERAL" else 0.95, 
                explanation=f"Response generated based on safety protocols (Category: {category}).",
                rewritten_query=rewritten_query,
                agent_trace=agent_trace
            )
            
        except Exception as e:
            logger.error(f"Pipeline failure: {str(e)}", exc_info=True)
            return AIProcessResponse(
                answer="I encountered an error processing your request. If this is a life-threatening emergency, please dial 911 or contact the front desk (0) immediately.",
                sources=[],
                confidence=0.0,
                explanation=f"Pipeline error: {str(e)}",
                agent_trace=agent_trace
            )
