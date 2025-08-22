"""Data models for research papers and related processing results."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class ProcessingStatus(Enum):
    """Status of paper processing through the pipeline."""

    DISCOVERED = "discovered"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass
class Paper:
    """Core paper metadata and information."""

    title: str
    authors: List[str]
    abstract: str
    url: str
    published_date: Optional[datetime]

    # Processing metadata
    discovered_at: datetime = field(default_factory=datetime.now)
    status: ProcessingStatus = ProcessingStatus.DISCOVERED

    @property
    def author_list(self) -> str:
        """Get formatted author list string."""
        if len(self.authors) == 1:
            return self.authors[0]
        elif len(self.authors) == 2:
            return f"{self.authors[0]} and {self.authors[1]}"
        elif len(self.authors) > 2:
            return f"{self.authors[0]} et al."
        return ""

    def update_status(self, status: ProcessingStatus) -> None:
        """Update the processing status."""
        self.status = status


@dataclass
class ResearchAnalysis:
    """LLM analysis results for a research paper."""

    paper_url: str

    # Core analysis components
    tldr: str
    key_contributions: List[str]
    technical_insights: List[str]
