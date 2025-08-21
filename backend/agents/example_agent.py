"""Example agent implementation using the BeeAI framework."""

import asyncio
import logging
from dotenv import load_dotenv
from beeai_framework.agents import AgentExecutionConfig
from beeai_framework.agents.react import ReActAgent
from beeai_framework.logger import Logger
from beeai_framework.emitter import EmitterOptions
from beeai_framework.tools.weather import OpenMeteoTool
from beeai_framework.memory import TokenMemory
from backend.llm import get_llm_client
from backend.common.utils import process_agent_events

# Load environment variables
load_dotenv()

# Configure logging
logger = Logger(__file__, level=logging.DEBUG)


class ExampleAgent:
    """Example agent that demonstrates weather querying capabilities."""

    def __init__(self):
        self.name = "ExampleAgent"
        self.llm = get_llm_client(model_name="llama3.1:8b")
        self.tools = [
            OpenMeteoTool(),
        ]
        self.agent = self._create_agent()
        self.execution_config = AgentExecutionConfig(
            max_retries_per_step=6, total_max_retries=10, max_iterations=20
        )

    def _create_agent(self) -> ReActAgent:
        """Create and configure the agent with tools and LLM"""
        return ReActAgent(llm=self.llm, tools=self.tools, memory=TokenMemory(self.llm))

    async def run(self, prompt: str) -> str:
        """Run the agent with a given query"""
        response = await self.agent.run(
            prompt=prompt,
            execution=self.execution_config,
        ).on("*", process_agent_events, EmitterOptions(match_nested=False))
        return response.result.text


if __name__ == "__main__":
    agent = ExampleAgent()
    logger.info("Agent created: %s", agent.name)
    # Example usage of the agent can be added here
    output = asyncio.run(agent.run(prompt="What is the weather like in New York City?"))
    logger.info("Agent response: %s", output)
