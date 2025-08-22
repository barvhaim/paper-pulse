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
class UserProfile:
    """User profile information from HuggingFace API."""

    avatar_url: Optional[str] = None
    fullname: Optional[str] = None
    username: Optional[str] = None
    user_type: Optional[str] = None
    follower_count: Optional[int] = None


@dataclass
class UserPermissions:
    """User permissions from HuggingFace API."""

    is_pro: Optional[bool] = None
    is_hf: Optional[bool] = None
    is_hf_admin: Optional[bool] = None
    is_mod: Optional[bool] = None


@dataclass
class User:
    """User information from HuggingFace API."""

    id: str
    profile: Optional[UserProfile] = None
    permissions: Optional[UserPermissions] = None


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
class PaperMetadata:
    """Media, links and submission metadata for a paper."""

    media_urls: List[str] = field(default_factory=list)
    project_page: Optional[str] = None
    github_repo: Optional[str] = None
    thumbnail: Optional[str] = None
    github_stars: Optional[int] = None


@dataclass
class PaperEngagement:
    """Community engagement data for a paper."""

    upvotes: int = 0
    num_comments: int = 0
    discussion_id: Optional[str] = None


@dataclass
class PaperSubmission:
    """Paper submission information."""

    submitted_by: Optional[User] = None
    submitted_on_daily_by: Optional[User] = None
    submitted_on_daily_at: Optional[str] = None
    is_author_participating: Optional[bool] = None


@dataclass
class AIContent:
    """AI-generated content for a paper."""

    ai_summary: Optional[str] = None
    ai_keywords: List[str] = field(default_factory=list)


@dataclass
class PaperCore:
    """Core paper information."""

    id: str
    title: str
    authors: List[Author]
    summary: str
    published_at: Optional[str] = None


@dataclass
class ProcessingInfo:
    """Processing information for a paper."""

    discovered_at: datetime = field(default_factory=datetime.now)
    status: ProcessingStatus = ProcessingStatus.DISCOVERED


@dataclass
class Paper:  # pylint: disable=too-many-public-methods
    """Core paper metadata and information aligned with HuggingFace API."""

    # Core information
    core: PaperCore

    # Grouped metadata
    metadata: PaperMetadata = field(default_factory=PaperMetadata)
    engagement: PaperEngagement = field(default_factory=PaperEngagement)
    submission: PaperSubmission = field(default_factory=PaperSubmission)
    ai_content: AIContent = field(default_factory=AIContent)

    # Processing metadata
    processing: ProcessingInfo = field(default_factory=ProcessingInfo)

    @property
    def author_list(self) -> str:
        """Get formatted author list string."""
        author_names = [author.name for author in self.core.authors]
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
        return f"https://huggingface.co/papers/{self.core.id}"

    @property
    def abstract(self) -> str:
        """Get abstract for backward compatibility."""
        return self.core.summary

    @property
    def published_date(self) -> Optional[datetime]:
        """Get published date as datetime for backward compatibility."""
        if self.core.published_at:
            try:
                return datetime.fromisoformat(
                    self.core.published_at.replace("Z", "+00:00")
                )
            except ValueError:
                return None
        return None

    def update_status(self, status: ProcessingStatus) -> None:
        """Update the processing status."""
        self.processing.status = status

    # Core field backward compatibility properties
    @property
    def id(self) -> str:
        """Get paper ID for backward compatibility."""
        return self.core.id

    @property
    def title(self) -> str:
        """Get title for backward compatibility."""
        return self.core.title

    @property
    def authors(self) -> List[Author]:
        """Get authors for backward compatibility."""
        return self.core.authors

    @property
    def summary(self) -> str:
        """Get summary for backward compatibility."""
        return self.core.summary

    @property
    def published_at(self) -> Optional[str]:
        """Get published at for backward compatibility."""
        return self.core.published_at

    @property
    def discovered_at(self) -> datetime:
        """Get discovered at for backward compatibility."""
        return self.processing.discovered_at

    @property
    def status(self) -> ProcessingStatus:
        """Get processing status for backward compatibility."""
        return self.processing.status

    # Backward compatibility properties for nested fields
    @property
    def media_urls(self) -> List[str]:
        """Get media URLs for backward compatibility."""
        return self.metadata.media_urls

    @property
    def project_page(self) -> Optional[str]:
        """Get project page for backward compatibility."""
        return self.metadata.project_page

    @property
    def github_repo(self) -> Optional[str]:
        """Get GitHub repo for backward compatibility."""
        return self.metadata.github_repo

    @property
    def thumbnail(self) -> Optional[str]:
        """Get thumbnail for backward compatibility."""
        return self.metadata.thumbnail

    @property
    def github_stars(self) -> Optional[int]:
        """Get GitHub stars for backward compatibility."""
        return self.metadata.github_stars

    @property
    def upvotes(self) -> int:
        """Get upvotes for backward compatibility."""
        return self.engagement.upvotes

    @property
    def num_comments(self) -> int:
        """Get number of comments for backward compatibility."""
        return self.engagement.num_comments

    @property
    def discussion_id(self) -> Optional[str]:
        """Get discussion ID for backward compatibility."""
        return self.engagement.discussion_id

    @property
    def ai_summary(self) -> Optional[str]:
        """Get AI summary for backward compatibility."""
        return self.ai_content.ai_summary

    @property
    def ai_keywords(self) -> List[str]:
        """Get AI keywords for backward compatibility."""
        return self.ai_content.ai_keywords

    @property
    def submitted_by(self) -> Optional[User]:
        """Get submitted by user for backward compatibility."""
        return self.submission.submitted_by

    @property
    def submitted_on_daily_by(self) -> Optional[User]:
        """Get submitted on daily by user for backward compatibility."""
        return self.submission.submitted_on_daily_by

    @property
    def submitted_on_daily_at(self) -> Optional[str]:
        """Get submitted on daily at for backward compatibility."""
        return self.submission.submitted_on_daily_at

    @property
    def is_author_participating(self) -> Optional[bool]:
        """Get is author participating for backward compatibility."""
        return self.submission.is_author_participating


@dataclass
class ResearchAnalysis:
    """LLM analysis results for a research paper."""

    paper_url: str

    # Core analysis components
    tldr: str
    key_contributions: List[str]
    technical_insights: List[str]
