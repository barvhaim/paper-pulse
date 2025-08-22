"""LangGraph workflow definition for the paper-pulse pipeline."""

from langgraph.graph import StateGraph
from backend.pipeline.state import PipelineState, SinglePaperState
from backend.pipeline.nodes import (
    paper_discovery_node,
    map_extraction_node,
    process_single_paper_node,
    extract_single_paper_node,
    analyze_single_paper_node,
    collect_results_node,
    delivery_node,
)
from backend.pipeline.node_types import (
    PAPER_DISCOVERY_NODE,
    MAP_EXTRACTION_NODE,
    PROCESS_SINGLE_PAPER_NODE,
    EXTRACT_SINGLE_PAPER_NODE,
    ANALYZE_SINGLE_PAPER_NODE,
    COLLECT_RESULTS_NODE,
    DELIVERY_NODE,
)


def build_single_paper_subgraph():
    """Build subgraph for processing a single paper."""
    subgraph = StateGraph(SinglePaperState)

    # Add single paper processing nodes
    subgraph.add_node(EXTRACT_SINGLE_PAPER_NODE, extract_single_paper_node)
    subgraph.add_node(ANALYZE_SINGLE_PAPER_NODE, analyze_single_paper_node)

    # Set entry point and edges
    subgraph.set_entry_point(EXTRACT_SINGLE_PAPER_NODE)
    subgraph.add_edge(EXTRACT_SINGLE_PAPER_NODE, ANALYZE_SINGLE_PAPER_NODE)
    subgraph.set_finish_point(ANALYZE_SINGLE_PAPER_NODE)

    return subgraph.compile()


def build_graph():
    """Build and compile the paper-pulse workflow graph."""
    # Main pipeline graph
    flow = StateGraph(PipelineState)

    # Add pipeline nodes
    flow.add_node(PAPER_DISCOVERY_NODE, paper_discovery_node)
    flow.add_node(MAP_EXTRACTION_NODE, map_extraction_node)
    flow.add_node(PROCESS_SINGLE_PAPER_NODE, process_single_paper_node)
    flow.add_node(COLLECT_RESULTS_NODE, collect_results_node)
    flow.add_node(DELIVERY_NODE, delivery_node)

    # Set the entry point
    flow.set_entry_point(PAPER_DISCOVERY_NODE)

    return flow.compile()
