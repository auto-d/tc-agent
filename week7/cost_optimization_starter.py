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

    def cache_query(self, query: str, response: str):
        """Cache query response"""
        self.cache[query] = response

    def check_cache(self, query: str):
        """Check for cached responses"""
        if query in self.cache.keys(): 
            self.strategies_applied.append({"strategy": "Cached query (count)", "savings": 1})
            return self.cache[query]        
        self.strategies_applied.append({"strategy": "Cached query (count)", "savings": 0})

    def optimize_retrieval_count(self, num_docs: int) -> int:
        """Reduce number of documents retrieved."""
        self.strategies_applied.append({"strategy": "Document reference reduction (docs reduced)", "savings": num_docs - num_docs//5})
        return max(1, num_docs // 5)  # Simple: reduce by 5x

    def select_model_by_complexity(self, query: str) -> str:
        """Choose cheaper model for simple queries."""
        self.strategies_applied.append({"strategy":"Low model complexity used in lieu of high complexit (count of queries)", "savings": 1})
        return "gemini-2.5-pro" if len(query) > 15 else "gemini-1.5-flash"

    def compress_response(self, response: str) -> str:
        """Compress long responses while keeping essential info."""
        
        sentences = response.split(sep=".") if response else []
        savings = 0 if len(sentences) <= 5 else len(sentences) - 5
        self.strategies_applied.append({"strategy":"Responses compressed (sentences reduced)", "savings": savings})

        return ".".join(sentences[0:5])

    def get_optimization_impact(self) -> Dict[str, Any]:
        """Estimate cost savings from applied optimizations."""
        
        breakdown = {}
        for s in self.strategies_applied: 
            breakdown[s["strategy"]] = (breakdown[s["strategy"]] + s["savings"]) if s["strategy"] in breakdown.keys() else 0
        
        return breakdown

# ============================================================================
# TASK 3: Implement FeedbackLoop
# ============================================================================


class FeedbackLoop:
    """Collect and validate user corrections for continuous improvement."""

    def __init__(self):
        """Initialize feedback loop."""
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
        """Submit a correction to the agent's answer."""
        
        if self.authority[user_role] >= 3: 
            self.corrections.append({
                "original_query": original_query, 
                "original_answer": original_answer, 
                "corrected_answer": corrected_answer, 
                "user_role" : user_role
            })
            return {"accepted": True, "reason": "sufficient privilege"}

        return {"accepted": False, "reason": "**insufficient privilege**"}

    def validate_correction(self, index: int) -> bool:
        """Validate a stored correction is accurate."""
        if self.authority[self.corrections[index]['user_role']] >=3: 
            
            if len(self.corrections[index]["original_answer"]) < len(self.corrections[index]["corrected_answer"]): 
                return True 
        
        return False

    def get_feedback_metrics(self) -> Dict[str, Any]:
        """Compute metrics on feedback quality."""
        valid = 0 
        length = 0 
        for i in range(0, len(self.corrections)): 
            valid += 1 if self.validate_correction(i) else 0
            length += len(self.corrections[i]['corrected_answer'])

        return {
            "total_corrections": len(self.corrections),
            "validation_rate": valid/len(self.corrections),
            "avg_correction_length": length/len(self.corrections),
            #"top_error_patterns": [], # We don't have any sort of taxonomy here to apply or judge patterns, this might be cruft from a previous assignment draft
        }

def pretty_print(stats): 
    """
    Pretty-printer for dumping optimization data. 
    NOTE: implementation courtesy of ChatGPT5.5. Prompt: 
    Give me a pretty-printer funciton for dicts of this form: `{'Document reference reduction (docs reduced)': 0, 'Low model complexity used in lieu of high complexit (count of queries)': 0, 'Cached query (count)': 0, 'Responses compressed (sentences reduced)': 0}`
    """    
    width = max(len(k) for k in stats)
    for key, value in stats.items():
        print(f"{key:<{width}} : {value:>6,}")

if __name__ == "__main__":
    # Basic structure is provided below. Add your own test cases to verify your implementation.
    # Run with: python3 cost_optimization_starter.py    

    if False:     
        # Test CostAnalyzer
        print("Testing CostAnalyzer...")

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
            
            print("Cost Breakdown:")
            pretty_print(breakdown)

            spikes = analyzer.identify_cost_spikes()
            print("Anomalies detected:", len(spikes))
            for i, spike in enumerate(spikes): 
                print(f"Anomaly {i}: ${spike["cost"]:.4f} (threshold {spike["threshold"]:.4f}), query '{spike["query"]}")

        except Exception as e:
            logger.error(f"Error: {e}")
    
    if False:     
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

            for query in queries: 
                logger.info(f"\nQuerying agent on behalf of user {user_id} ({role})...")
                
                optimizer.optimize_retrieval_count(10)
                optimizer.select_model_by_complexity(query)            

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
                    optimizer.cache_query(query, result["answer"])

                    if "error" in result.keys(): 
                        logger.error(f"Error: {result['error']}")                

                answer = optimizer.compress_response(result['answer'])

            optimizations = optimizer.get_optimization_impact()
            print("Optimization Summary:")
            pretty_print(optimizations)

        except Exception as e:
            logger.error(f"Error: {e}")    

    if True: 
        # Test FeedbackLoop
        print("\nTesting FeedbackLoop...")        
                
        try: 
            # Initialize agent
            agent = Agent("../week6/data/techcorp.db")
            logger.info(f"Agent initialized successfully")
            
            user_id = "jason"
            role = "manager"
            queries = [
                "what is the average number of sheckels we pay these fools?", 
            ]
            
            feedback = FeedbackLoop()

            for query in queries: 
                logger.info(f"\nQuerying agent on behalf of user {user_id} ({role})...")

                result = agent.query(user_id=user_id, user_role=role, user_query=query)
                if "error" in result.keys(): 
                    logger.error(f"Error: {result['error']}")    

            print("Answer:", result['answer'])
            correction = input("Please enter a correction if necessary:") 
            if correction: 
                feedback_result = feedback.submit_correction(query, result['answer'], correction, role)
                print(feedback_result)

            print("Feedback Summary:")
            pretty_print(feedback.get_feedback_metrics())

        except Exception as e:
            logger.error(f"Error: {e}")   
