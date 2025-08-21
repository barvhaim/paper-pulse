"""Utility functions for agent processing."""

import logging
from typing import Any
from beeai_framework.logger import Logger
from beeai_framework.emitter import EventMeta
from beeai_framework.errors import FrameworkError

logger = Logger("agent-utils", level=logging.DEBUG)


def process_agent_events(data: Any, event: EventMeta) -> None:
    """Process agent events and log appropriately"""

    if event.name == "error":
        logger.info("Agent 🤖: %s", FrameworkError.ensure(data.error).explain())
    elif event.name == "retry":
        logger.info("Agent 🤖: Retrying the action...")
    elif event.name == "update":
        logger.info("Agent(%s) 🤖: %s", data.update.key, data.update.parsed_value)
    elif event.name == "start":
        logger.info("Agent 🤖: Starting new iteration")
    elif event.name == "success":
        logger.info("Agent 🤖: Success")
