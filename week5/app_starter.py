"""
Week 5: Agent Architecture Starter Template

Build an AI agent that answers TechCorp questions using:
- Gemini 2.5 Pro LLM (free tier via Google AI API)
- SQLite database queries
- Policy document retrieval

Complete the TODO sections marked below.
"""

import json
import sqlite3
from typing import Dict, Any
import google.genai as genai
from google.genai import types
import logging
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


# TASK 1: Implement the Tool base class


class Tool:
    """Base class for tools the agent can call."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.schema = None

    def execute(self, **kwargs) -> str:
        """Execute the tool.
        """
        raise NotImplementedError
    
    def get_tool_schema(self) -> str: 
        """Generalize the tool schema definition"""
        return json.dumps(self.schema) if self.schema is not None else ""

# TASK 2: Implement EmployeeLookupTool


class EmployeeLookupTool(Tool):
    """Look up employee information from SQLite database."""

    def __init__(self, db_path: str):
        super().__init__("employee_lookup", "Find employee information by name or ID")
        self.db_path = db_path
        self.schema = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "The exact or approximate employee name. This cannot be used with any other query argument."
                    },
                    "employee_id": {
                        "type": "integer",
                        "description": "The employee ID. This cannot be used with any other query argument"
                    }
                },
                "required": []
            }
        }        
    
    def execute(self, employee_name: str = None, employee_id: str = None) -> str:
        """Look up employee by name or ID.

        Args:
            employee_name: Name to search for (partial match ok)
            employee_id: ID to search for (exact match)

        Returns:
            JSON string with employee info or error message
        """
        try:

            with sqlite3.connect(self.db_path) as conn: 
                cursor = conn.cursor()
                
                if employee_name is not None: 
                    cursor.execute("SELECT * FROM employees WHERE name LIKE ?", (f"%{employee_name}%",))
                    rows = cursor.fetchall()
                
                elif employee_id is not None: 
                    cursor.execute("SELECT * FROM employees WHERE id = ?", (int(employee_id),))
                    rows = cursor.fetchall()

                else: 
                    raise ValueError("No query criteria provided!")
                             
            return json.dumps(rows, indent=2) if len(rows) > 0 else "No employees found."

        except Exception as e:
            logger.error(f"Employee lookup error: {e}")
            return f"Error: {str(e)}"

# TASK 3: Implement PolicySearchTool


class PolicySearchTool(Tool):
    """Search policy documents by keyword."""

    def __init__(self):
        super().__init__("policy_search", "Search policy documents by keyword or topic")
        with open("data/documents.json") as f:
            self.documents = (json.load(f))
        
        self.schema = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A string to search for inside the policy library and meeting minutes. For example 'travel', 'layoffs', 'budget'."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of documents to return (default is 5)."
                    }
                },
                "required": ["query"]
            }
        }

    def execute(self, query: str, limit: int = 5) -> str:
        """Search policies by keyword.

        Args:
            query: Search term
            limit: Max results to return

        Returns:
            Formatted string with matching documents
        """
        try:
            
            matches = [doc for doc in self.documents if query.lower() in doc["content"].lower()]
            
            results = []
            if matches is not None: 
                for match in matches[0:limit]: 
                    results.append({ 
                        "document_title": match["title"],
                        "document_content": match["content"][0:500]
                        })

                return json.dumps(results)
                
            return "No matches found"
        
        except Exception as e:
            logger.error(f"Policy search error: {e}")
            return f"Error: {str(e)}"


# TASK 4: Implement ExpenseQueryTool


class ExpenseQueryTool(Tool):
    """Query expense policies and approval limits."""

    def __init__(self):
        super().__init__("expense_query", "Query expense approval limits by role")
        
        with open("data/policies.json") as f:
            self.policies = (json.load(f))

        self.schema = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "A specific employee role: ['ic1_ic2' | 'ic3' | 'manager' | 'director' | 'vp']."
                    }
                },
                "required": ["role"]
            }
        }

    def execute(self, role: str) -> str:
        """Query expense approval limit for a given role.

        Args:
            role: Employee role (ic1_ic2, ic3, manager, director, vp)

        Returns:
            String with approval limit for the given role
        """
        try:
            value = self.policies["expense"]["approval_limits"].get(role)
            return f"Approval limit for {role}: ${str(value)}" if value is not None else f"No matching limit found for {role}"

        except Exception as e:
            logger.error(f"Expense query error: {e}")
            return f"Error: {str(e)}"


# TASK 5: Implement the Agent class


class Agent:
    """AI agent that answers questions using Gemini LLM + tools."""

    def __init__(self, db_path: str, api_key: str = None):
        """Initialize the agent.

        Args:
            db_path: Path to SQLite database
            api_key: Google AI API key (or use GOOGLE_API_KEY env var)
        """
        self.db_path = db_path
        self.api_key = api_key or GOOGLE_API_KEY

        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not set. Get free key at: "
                "https://aistudio.google.com/app/apikey"
            )

        self.client = genai.Client(api_key=self.api_key)

        self.tools = {
            "employee_lookup": EmployeeLookupTool(db_path),
            "policy_search": PolicySearchTool(),
            "expense_query": ExpenseQueryTool(),
        }

        self.input_tokens = 0
        self.output_tokens = 0
        self.queries = 0

    def _build_system_prompt(self, user_role: str) -> str:
        """Build system prompt describing available tools.

        Returns:
            System prompt string
        """
        
        prompt = f""" 
        You are a helpful Tech Corp assistant equipped with tool calls that can be used to retrieve\
        information about company employees and policies. You are working with a user whose role is\
        {user_role}, and should tailor your responses according to that role. 
        """
        return prompt

    def query(self, user_query: str, user_role: str = "engineer") -> Dict[str, Any]:
        """Answer a question using LLM + tools.

        Args:
            user_query: The question to answer
            user_role: User's role (for access control in future weeks)

        Returns:
            Dict with keys:
            - "answer": str - the response
            - "tokens_used": int - total tokens
            - "cost": float - cost in dollars
            - "role": str - user role
        """
        logger.info(f"Processing query: {user_query}")

        # Build up the Gemini config object which carries necessary tool call and prompt context
        system_prompt = self._build_system_prompt(user_role)

        schemas = []
        for tool in self.tools.values(): 
            schemas.append(tool.schema) 

        tools = types.Tool(function_declarations=schemas)
        config = types.GenerateContentConfig(
            tools=[tools], 
            system_instruction=system_prompt)
        
        # Build our message content in the Gemini schema 
        content = [
            types.Content(
                role="user", 
                parts=[types.Part.from_text(text=user_query)]
            )
        ]
        
        # Request completion
        response = self.client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=content, 
            config=config)
        input_tokens, output_tokens = self._update_usage(response)

        # Process one or more tool calls if the model invoked 
        try: 
            if response.function_calls: 

                logger.info(f"Found tool calls ({len(response.function_calls)})..")
                for call in response.function_calls: 
                    
                    logger.info(f"Agent called: {call.name}")
                    for tool in self.tools.values(): 
                        if tool.name == call.name:                                                         
                            logger.info(f"Mapped to internal tool {tool.name} ({tool.description})")
                            
                            logger.info(f"Calling with arguments: {call.args}")
                            result = tool.execute(**call.args)
                            
                            # Stick gemini's response into our aggregate response so it has context for the 
                            # following results
                            content.append(response.candidates[0].content)

                            # ... and add our results
                            function_result = types.Part.from_function_response(
                                name=tool.name, 
                                response={"result": result})                            
                            content.append(types.Content(role="user", parts=[function_result]))
                            break 

                # Armed with responses to the function calls, request another completion (without tool 
                # calls equipped)
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=content, 
                    config=types.GenerateContentConfig(system_instruction=system_prompt))                            
                tool_input_tokens, tool_output_tokens = self._update_usage(response)
                input_tokens += tool_input_tokens
                output_tokens += tool_output_tokens

        except Exception as e: 
            logger.error(f"Unexpected error processing tool call! ({type(e)})")

        return {
            "answer": response.text,
            "tokens_used": input_tokens + output_tokens,
            "cost": self._estimate_query_cost(input_tokens, output_tokens),
            "role": user_role,
        }

    def _update_usage(self, response): 
        """Parse a response message to extract utilization and record, returning counters"""
        input = 0 
        output = 0 

        if response: 
            input = response.usage_metadata.prompt_token_count 
            output = response.usage_metadata.thoughts_token_count + response.usage_metadata.candidates_token_count

        self.input_tokens += input 
        self.output_tokens += output 
        self.queries += 1

        return input, output

    def _estimate_query_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on tokens.

        Gemini 2.5 Pro pricing:
        - Input: $1.25 per 1M tokens
        - Output: $10.0 per 1M tokens

        On the free tier, we prefer flash, thought don't actually get billed and instead 
        chip away at our quota
        - Input: $0.30
        - Output = $2.5
        """
        input_cost = (input_tokens / 1_000_000) * 0.3
        output_cost = (output_tokens / 1_000_000) * 2.5
        return input_cost + output_cost

    def get_metrics(self) -> Dict[str, Any]:
        """Return performance metrics.

        TODO: Return dict with:
        - total_queries: number of queries processed
        - total_tokens: cumulative tokens used
        - total_cost: cumulative cost in dollars
        - avg_cost_per_query: average cost per query
        """

        cost = self._estimate_query_cost(self.input_tokens, self.output_tokens)
        return {
            "total_queries": self.queries,
            "total_tokens": self.input_tokens + self.output_tokens,
            "total_cost": cost,
            "avg_cost_per_query": cost/self.queries if self.queries > 0 else 0,
        }


# TASK 6: Test your implementation

if __name__ == "__main__":
    """Quick test of agent functionality."""
    import sys

    try:
        # Initialize agent
        agent = Agent("data/techcorp.db")
        logger.info(f"Agent initialized successfully")

        # Test a query
        if len(sys.argv) != 2: 
            print("Usage: python app_starter.py <question>\n") 
            sys.exit(1) 
        
        query = sys.argv[1]
        logger.info(f"\nQuerying agent...")
        result = agent.query(query)

        print(f"Answer\n---------------------\n: {result['answer']}\n")
        logger.info(f"Tokens: {result['tokens_used']}")
        logger.info(f"Cost: ${result['cost']:.6f}")

        # Check metrics
        metrics = agent.get_metrics()
        logger.info(f"Metrics: {metrics}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
