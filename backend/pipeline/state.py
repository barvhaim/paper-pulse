"""Pipeline state definition for paper-pulse workflow."""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from backend.data_model.paper import Paper


class PipelineState(TypedDict):
    """State object that flows through the pipeline nodes."""

    # Input
    settings: Dict[str, Any]

    # Paper Discovery output
    discovered_papers: List[Paper]

    # Metadata
    pipeline_id: str
    start_time: Optional[datetime]
    error: Optional[str]


class SinglePaperState(TypedDict):
    """State for processing a single paper through extraction and analysis."""

    # Paper data
    paper: Paper

    # Processing results
    extracted_content: Optional[Dict[str, Any]]
    analysis: Optional[Dict[str, Any]]

    # Metadata
    pipeline_id: str
    paper_index: int
    errors: Optional[List[Dict[str, Any]]]
