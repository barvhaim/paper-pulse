"""Base agent class for standardized multi-agent architecture."""

from abc import ABC
from typing import List, Optional
import logging
from beeai_framework.agents import AgentExecutionConfig
from beeai_framework.agents.react import ReActAgent
from beeai_framework.tools.tool import Tool
from beeai_framework.memory import TokenMemory
from beeai_framework.emitter import EmitterOptions
from backend.llm import get_llm_client
from backend.common.utils import process_agent_events


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""

    def __init__(
        self,
        name: str,
        tools: List[Tool],
        model_name: str = "llama3.1:8b",
        execution_config: Optional[AgentExecutionConfig] = None,
    ):
        """Initialize the base agent.

        Args:
            name: Agent name for identification
            tools: List of tools available to the agent
            model_name: LLM model to use
            execution_config: Custom execution configuration
        """
        self.name = name
        self.tools = tools
        self.llm = get_llm_client(model_name=model_name)
        self.agent = self._create_agent()
        self.execution_config = execution_config or self._default_execution_config()
        self.logger = logging.getLogger(f"agent.{name}")

    def _create_agent(self) -> ReActAgent:
        """Create and configure the ReActAgent with tools and LLM."""
        return ReActAgent(llm=self.llm, tools=self.tools, memory=TokenMemory(self.llm))

    @staticmethod
    def _default_execution_config() -> AgentExecutionConfig:
        """Provide default execution configuration."""
        return AgentExecutionConfig(
            max_retries_per_step=6, total_max_retries=10, max_iterations=20
        )

    async def run(self, prompt: str) -> str:
        """Run the agent with a given prompt.

        Args:
            prompt: Input prompt for the agent

        Returns:
            Agent response text
        """
        self.logger.info("Starting agent execution: %s", self.name)

        response = await self.agent.run(
            prompt=prompt,
            execution=self.execution_config,
        ).on("*", process_agent_events, EmitterOptions(match_nested=False))

        self.logger.info("Agent execution completed: %s", self.name)
        return response.result.text

    @property
    def agent_type(self) -> str:
        """Return the agent type for identification."""
        return self.__class__.__name__
