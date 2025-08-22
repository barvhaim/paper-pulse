"""Pipeline state definition for paper-pulse workflow."""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class PipelineState(TypedDict):
    """State object that flows through the pipeline nodes."""

    # Input
    user_preferences: Dict[str, Any]
    date_filter: Optional[datetime]

    # Paper Discovery output
    discovered_papers: Optional[List[Dict[str, Any]]]

    # Content Extraction output
    extracted_contents: Optional[Dict[str, Dict[str, Any]]]  # paper_url -> content

    # Research Analyzer output
    analyses: Optional[Dict[str, Dict[str, Any]]]  # paper_url -> analysis

    # Delivery output
    delivery_content: Optional[Dict[str, Any]]
    delivery_status: Optional[Dict[str, Any]]

    # Metadata
    pipeline_id: str
    start_time: Optional[datetime]
    current_node: Optional[str]
    errors: Optional[List[Dict[str, Any]]]


class SinglePaperState(TypedDict):
    """State for processing a single paper through extraction and analysis."""

    # Paper data
    paper: Dict[str, Any]

    # Processing results
    extracted_content: Optional[Dict[str, Any]]
    analysis: Optional[Dict[str, Any]]

    # Metadata
    pipeline_id: str
    paper_index: int
    errors: Optional[List[Dict[str, Any]]]
