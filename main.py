"""Main module entry point for paper-pulse application."""

import logging
import uuid
from datetime import datetime

from backend.pipeline.graph import build_graph
from backend.pipeline.state import PipelineState


def _setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )


def _initial_state() -> PipelineState:
    """Create a test pipeline state for demonstration."""
    return PipelineState(
        settings={"limit": 3},
        discovered_papers=[],
        pipeline_id=str(uuid.uuid4()),
        start_time=datetime.now(),
        error=None,
    )


def main():
    """Main function that runs the paper-pulse pipeline."""
    _setup_logging()

    logging.info("Starting Paper Pulse application")

    # Build the workflow graph
    graph = build_graph()

    # Create initial state
    initial_state = _initial_state()
    logging.info("Created pipeline with ID: %s", initial_state["pipeline_id"])

    # Run the workflow
    try:
        logging.info("Starting pipeline execution")
        result = graph.invoke(initial_state)
        logging.info("Pipeline execution completed successfully")

        # Log discovered papers for verification
        discovered_papers = result.get("discovered_papers", [])
        if discovered_papers:
            logging.info("Successfully discovered %d papers:", len(discovered_papers))
            for i, paper in enumerate(discovered_papers):
                if hasattr(paper, "title"):
                    # Paper object
                    logging.info("  %d. %s", i + 1, paper.title)
                    logging.info("      Authors: %s", paper.author_list)
                    logging.info("      Upvotes: %d", paper.upvotes)
                    if paper.ai_keywords:
                        logging.info(
                            "      Keywords: %s", ", ".join(paper.ai_keywords[:3])
                        )
                else:
                    # Fallback for dict
                    logging.info("  %d. %s", i + 1, paper.get("title", "No title"))

    except Exception as e:
        logging.error("Pipeline execution failed: %s", str(e))
        raise


if __name__ == "__main__":
    main()
