"""
Week 7: Cost Optimization & Feedback Loop Starter Template

Implement three systems:
1. CostAnalyzer - analyze and track query costs
2. OptimizationStrategy - optimize costs through caching, model selection, etc.
3. FeedbackLoop - collect and validate user corrections
"""

import json
import logging
import statistics
from typing import Dict, List, Any
from datetime import datetime
from app_starter import Agent 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# TASK 1: Implement CostAnalyzer
# ============================================================================


class CostAnalyzer:
    """Analyze and track query costs by component."""

    def __init__(self):
        """Initialize cost analyzer"""
        self.query_history = []

    def record_query(self, query, metrics, error=False):
        """Record a query and its cost breakdown."""
        query_record = {
                "query_text": query, 
                "retrieval_cost": 0, #Free, all documents are local in our testing 
                "llm_cost": metrics['total_llm_cost'],
                "tool_cost": metrics['total_tool_cost'],
                "error_cost": metrics['total_cost'] if error else 0, 
                "total_cost": metrics['total_cost'],
                "timestamp": datetime.utcnow().isoformat()
            }
        self.query_history.append(query_record)

    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get breakdown of costs by component"""

        breakdown = {
            "retrieval_total": statistics.mean([x['retrieval_cost'] for x in self.query_history]),
            "llm_total": statistics.mean([x['llm_cost'] for x in self.query_history]),
            "tool_total": statistics.mean([x['tool_cost'] for x in self.query_history]),
            "error_total": statistics.mean([x['error_cost'] for x in self.query_history]),
            "query_count": len(self.query_history),
        }
        breakdown['total_daily'] = \
            breakdown["retrieval_total"] +\
            breakdown["llm_total"] +\
            breakdown["tool_total"] +\
            breakdown["error_total"]
        
        return breakdown

    def identify_cost_spikes(self) -> List[Dict]:
        """Identify unusually expensive queries."""
        breakdown = self.get_cost_breakdown()

        spikes = []
        
        costs = [x['total_cost'] for x in self.query_history]
        mean = statistics.mean(costs) 
        stdev = statistics.stdev(costs) if len(costs) > 1 else 0

        for x in self.query_history: 
            threshold = mean + 2*stdev
            if x['total_cost'] > threshold: 
                spikes.append({
                    "query": x["query"], 
                    "cost": x["total_cost"], 
                    "threshold": threshold 
                })

        return spikes

# ============================================================================
# TASK 2: Implement OptimizationStrategy
# ============================================================================


class OptimizationStrategy:
    """Optimize agent costs through multiple strategies."""

    def __init__(self):
        """Initialize optimization strategy."""
        self.cache = {}  # {query: response}
        self.strategies_applied = []

    def cache(self, query: str, response: str):
        """Cache query response"""
        self.cache[query] = response

    def check_cache(self, query: str):
        """Check for cached responses"""
        return self.cache[query] if query in self.cache.keys() else None

    def optimize_retrieval_count(self, num_docs: int) -> int:
        """Reduce number of documents retrieved.

        TODO: Reduce count intelligently
        - Input 15 docs → output 3 docs (top-k)
        - Reduces token cost

        Args:
            num_docs: original document count

        Returns:
            optimized document count
        """
        # TODO: implement
        return max(1, num_docs // 5)  # Simple: reduce by 5x

    def select_model_by_complexity(self, query: str) -> str:
        """Choose cheaper model for simple queries.

        TODO: Analyze query complexity
        - Simple queries ("What is X?") → gemini-1.5-flash (cheaper, faster)
        - Complex queries ("Analyze...", "Compare...", "Design...") → gemini-2.5-pro

        Args:
            query: user's question

        Returns:
            model name to use
        """
        # TODO: implement
        return "gemini-2.5-pro"

    def enable_response_compression(self, response: str) -> str:
        """Compress long responses while keeping essential info.

        TODO: Reduce response length
        1. Split into sentences
        2. Keep only first N essential sentences
        3. Return compressed response

        Args:
            response: original response

        Returns:
            compressed response
        """
        # TODO: implement
        return response

    def get_optimization_impact(self) -> Dict[str, Any]:
        """Estimate cost savings from applied optimizations.

        TODO: Return impact analysis:
        - total_savings_pct: estimated % cost reduction
        - strategies_applied: list of which strategies used
        - breakdown: savings estimate per strategy
        """
        # TODO: implement
        return {
            "total_savings_pct": 0.0,
            "strategies_applied": self.strategies_applied,
            "breakdown": {},
        }


# ============================================================================
# TASK 3: Implement FeedbackLoop
# ============================================================================


class FeedbackLoop:
    """Collect and validate user corrections for continuous improvement."""

    def __init__(self):
        """Initialize feedback loop.

        TODO: Initialize corrections list and validation rules
        """
        self.corrections = []
        # Authority hierarchy for role-based validation
        self.authority = {
            "engineer": 1,
            "hr": 2,
            "finance": 2,
            "manager": 3,
            "executive": 4,
        }

    def submit_correction(
        self,
        original_query: str,
        original_answer: str,
        corrected_answer: str,
        user_role: str,
    ) -> Dict[str, Any]:
        """Submit a correction to the agent's answer.

        TODO: Validate and store correction
        1. Check user_role has sufficient authority
        2. Check corrected_answer is detailed enough (longer than original)
        3. Store in corrections list
        4. Return acceptance status

        Args:
            original_query: the question
            original_answer: agent's incorrect answer
            corrected_answer: user's correction
            user_role: user's role (for authority check)

        Returns:
            {"accepted": True/False, "reason": "..."}
        """
        # TODO: implement
        return {"accepted": False, "reason": "TODO: implement validation"}

    def validate_correction(self, index: int) -> bool:
        """Validate a stored correction is accurate.

        TODO: Check correction quality:
        1. User role has sufficient authority (manager+, i.e. level 3 or above)
        2. Correction is more detailed than original
        3. Correction makes sense

        Args:
            index: index into corrections list

        Returns:
            True if correction is valid, False otherwise
        """
        # TODO: implement
        return False

    def get_feedback_metrics(self) -> Dict[str, Any]:
        """Compute metrics on feedback quality.

        TODO: Calculate:
        - total_corrections: number of corrections received
        - validation_rate: % of corrections that are valid
        - avg_correction_length: average length of corrections
        - top_error_patterns: most common mistakes corrected

        Returns:
            dict with feedback metrics
        """
        # TODO: implement
        return {
            "total_corrections": len(self.corrections),
            "validation_rate": 0.0,
            "avg_correction_length": 0.0,
            "top_error_patterns": [],
        }


if __name__ == "__main__":
    # Basic structure is provided below. Add your own test cases to verify your implementation.
    # Run with: python3 cost_optimization_starter.py

    # Test CostAnalyzer
    print("Testing CostAnalyzer...")

    if False:     
        try:        
            # Initialize agent
            agent = Agent("../week6/data/techcorp.db")
            logger.info(f"Agent initialized successfully")
            
            user_id = "jason"
            role = "hr"
            queries = [
                "how many brians work at the company?", 
                "what is the employee ID of Joshua Martin",
                "please fetch a list of email addresses for all employees with the surname 'Smith'"
            ]
            
            for query in queries: 
                logger.info(f"\nQuerying agent on behalf of user {user_id} ({role})...")
                result = agent.query(user_id=user_id, user_role=role, user_query=query)
                if "error" in result.keys(): 
                    logger.error(f"Error: {result['error']}")

                else: 
                    print(f"Answer\n---------------------\n: {result['answer']}\n")
                    logger.info(f"Tokens: {result['tokens_used']}")
                    logger.info(f"Cost: ${result['cost']:.6f}")

            # Check metrics
            metrics = agent.get_metrics()
            logger.info(f"Metrics: {metrics}")

            analyzer = CostAnalyzer()            
            analyzer.record_query(query, metrics)            
            breakdown = analyzer.get_cost_breakdown()
            print("Cost breakdown")
            print(breakdown)

            spikes = analyzer.identify_cost_spikes()
            print("Anomalies detected:", len(spikes))
            for i, spike in enumerate(spikes): 
                print(f"Anomaly {i}: ${spike["cost"]:.4f} (threshold {spike["threshold"]:.4f}), query '{spike["query"]}")

        except Exception as e:
            logger.error(f"Error: {e}")
    
    # Test OptimizationStrategy
    print("\nTesting OptimizationStrategy...")
         
    try: 
         # Initialize agent
        agent = Agent("../week6/data/techcorp.db")
        logger.info(f"Agent initialized successfully")
        
        user_id = "jason"
        role = "hr"
        queries = [
            "how many brians work at the company?", 
            "what is the employee ID of Joshua Martin",
            "please fetch a list of email addresses for all employees with the surname 'Smith'"
            "how many brians work at the company?", 
            "how many brians work at the company?", 
        ]
        
        optimizer = OptimizationStrategy()
        # TODO: test apply_caching, select_model_by_complexity, and optimize_retrieval_count

        for query in queries: 
            logger.info(f"\nQuerying agent on behalf of user {user_id} ({role})...")
            
            result = None
            response = optimizer.check_cache(query)
            if response: 
                result = {
                    "answer" : response, 
                    "tokens_used" : 0, 
                    "cost": 0, 
                    "role": role
                }
                print(f"Cache hit, using cached response (query: {query})")

            else:            
                result = agent.query(user_id=user_id, user_role=role, user_query=query)
                optimizer.cache(query, result["answer"])

                if "error" in result.keys(): 
                    logger.error(f"Error: {result['error']}")                

            print(f"Answer\n---------------------\n: {result['answer']}\n")
            logger.info(f"Tokens: {result['tokens_used']}")
            logger.info(f"Cost: ${result['cost']:.6f}")

    except Exception as e:
        logger.error(f"Error: {e}")    

    # Test FeedbackLoop
    print("\nTesting FeedbackLoop...")
    feedback = FeedbackLoop()
    # TODO: submit corrections with different roles and verify accepted/rejected correctly
