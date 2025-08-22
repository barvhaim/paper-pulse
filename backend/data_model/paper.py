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
class User:
    """User information from HuggingFace API."""

    id: str
    avatar_url: Optional[str] = None
    fullname: Optional[str] = None
    username: Optional[str] = None
    user_type: Optional[str] = None
    is_pro: Optional[bool] = None
    is_hf: Optional[bool] = None
    is_hf_admin: Optional[bool] = None
    is_mod: Optional[bool] = None
    follower_count: Optional[int] = None


@dataclass
class Author:
    """Author information from HuggingFace API."""

    id: str
    name: str
    user: Optional[User] = None
    status: Optional[str] = None
    status_last_changed_at: Optional[str] = None
    hidden: Optional[bool] = None


@dataclass
class Paper:
    """Core paper metadata and information aligned with HuggingFace API."""

    # Core paper information
    id: str
    title: str
    authors: List[Author]
    summary: str
    published_at: Optional[str] = None
    submitted_on_daily_at: Optional[str] = None

    # Media and links
    media_urls: List[str] = field(default_factory=list)
    project_page: Optional[str] = None
    github_repo: Optional[str] = None
    thumbnail: Optional[str] = None

    # Community engagement
    upvotes: int = 0
    num_comments: int = 0
    discussion_id: Optional[str] = None

    # AI-generated content
    ai_summary: Optional[str] = None
    ai_keywords: List[str] = field(default_factory=list)

    # GitHub integration
    github_stars: Optional[int] = None

    # Submission information
    submitted_by: Optional[User] = None
    submitted_on_daily_by: Optional[User] = None
    is_author_participating: Optional[bool] = None

    # Processing metadata
    discovered_at: datetime = field(default_factory=datetime.now)
    status: ProcessingStatus = ProcessingStatus.DISCOVERED

    @property
    def author_list(self) -> str:
        """Get formatted author list string."""
        author_names = [author.name for author in self.authors]
        if len(author_names) == 1:
            return author_names[0]
        if len(author_names) == 2:
            return f"{author_names[0]} and {author_names[1]}"
        if len(author_names) > 2:
            return f"{author_names[0]} et al."
        return ""

    @property
    def url(self) -> str:
        """Get paper URL for backward compatibility."""
        return f"https://huggingface.co/papers/{self.id}"

    @property
    def abstract(self) -> str:
        """Get abstract for backward compatibility."""
        return self.summary

    @property
    def published_date(self) -> Optional[datetime]:
        """Get published date as datetime for backward compatibility."""
        if self.published_at:
            try:
                return datetime.fromisoformat(self.published_at.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

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
