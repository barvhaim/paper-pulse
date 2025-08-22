"""Example agent implementation using the BeeAI framework."""

import asyncio
import logging
from dotenv import load_dotenv
from beeai_framework.tools.weather import OpenMeteoTool
from backend.agents.base import BaseAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExampleAgent(BaseAgent):
    """Example agent that demonstrates weather querying capabilities."""

    def __init__(self):
        tools = [OpenMeteoTool()]
        super().__init__(name="ExampleAgent", tools=tools, model_name="llama3.1:8b")


if __name__ == "__main__":
    agent = ExampleAgent()
    logger.info("Agent created: %s", agent.name)
    # Example usage of the agent can be added here
    output = asyncio.run(agent.run(prompt="What is the weather like in New York City?"))
    logger.info("Agent response: %s", output)
