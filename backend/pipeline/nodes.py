"""Pipeline nodes implementation for paper-pulse workflow."""

import logging
import requests
from datetime import datetime
from typing import List, Dict, Any
from langgraph.graph import END
from langgraph.types import Command, Send

from backend.pipeline.state import PipelineState, SinglePaperState
from backend.pipeline.node_types import (
    MAP_EXTRACTION_NODE,
    PROCESS_SINGLE_PAPER_NODE,
    EXTRACT_SINGLE_PAPER_NODE,
    ANALYZE_SINGLE_PAPER_NODE,
    COLLECT_RESULTS_NODE,
    DELIVERY_NODE,
)
from backend.data_model.paper import (
    Paper,
    Author,
    User,
    UserProfile,
    UserPermissions,
    PaperCore,
    PaperMetadata,
    PaperEngagement,
    PaperSubmission,
    AIContent,
)


def _fetch_daily_papers(limit: int = 20) -> List[Paper]:
    """
    Fetch papers from Hugging Face daily papers API.

    Args:
        limit: Maximum number of papers to fetch

    Returns:
        List of Paper objects
    """
    base_url = "https://huggingface.co/api/daily_papers"
    params = {}

    if limit:
        params["limit"] = limit

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        papers_data = response.json()

        # Convert API response to Paper objects
        papers = []
        for item in papers_data:
            if "paper" in item:
                paper_data = item["paper"]

                # Create Author objects
                authors = []
                for author_data in paper_data.get("authors", []):
                    user = None
                    if author_data.get("user"):
                        user_data = author_data["user"]
                        profile = UserProfile(
                            avatar_url=user_data.get("avatarUrl"),
                            fullname=user_data.get("fullname"),
                            username=user_data.get("user"),
                            user_type=user_data.get("type"),
                            follower_count=user_data.get("followerCount"),
                        )
                        permissions = UserPermissions(
                            is_pro=user_data.get("isPro"),
                            is_hf=user_data.get("isHf"),
                            is_hf_admin=user_data.get("isHfAdmin"),
                            is_mod=user_data.get("isMod"),
                        )
                        user = User(
                            id=user_data.get("_id", ""),
                            profile=profile,
                            permissions=permissions,
                        )

                    author = Author(
                        id=author_data.get("_id", ""),
                        name=author_data.get("name", "Unknown"),
                        user=user,
                        status=author_data.get("status"),
                        status_last_changed_at=author_data.get("statusLastChangedAt"),
                        hidden=author_data.get("hidden"),
                    )
                    authors.append(author)

                # Create User objects for submission info
                submitted_by = None
                if paper_data.get("submittedBy"):
                    sb_data = paper_data["submittedBy"]
                    profile = UserProfile(
                        avatar_url=sb_data.get("avatarUrl"),
                        fullname=sb_data.get("fullname"),
                        username=sb_data.get("name"),
                        user_type=sb_data.get("type"),
                        follower_count=sb_data.get("followerCount"),
                    )
                    permissions = UserPermissions(
                        is_pro=sb_data.get("isPro"),
                        is_hf=sb_data.get("isHf"),
                        is_hf_admin=sb_data.get("isHfAdmin"),
                        is_mod=sb_data.get("isMod"),
                    )
                    submitted_by = User(
                        id=sb_data.get("_id", ""),
                        profile=profile,
                        permissions=permissions,
                    )

                submitted_on_daily_by = None
                if paper_data.get("submittedOnDailyBy"):
                    sodb_data = paper_data["submittedOnDailyBy"]
                    profile = UserProfile(
                        avatar_url=sodb_data.get("avatarUrl"),
                        fullname=sodb_data.get("fullname"),
                        username=sodb_data.get("user"),
                        user_type=sodb_data.get("type"),
                    )
                    submitted_on_daily_by = User(
                        id=sodb_data.get("_id", ""),
                        profile=profile,
                    )

                # Create Paper object with nested structure
                core = PaperCore(
                    id=paper_data.get("id", ""),
                    title=paper_data.get("title", ""),
                    authors=authors,
                    summary=paper_data.get("summary", ""),
                    published_at=paper_data.get("publishedAt"),
                )

                metadata = PaperMetadata(
                    media_urls=paper_data.get("mediaUrls", []),
                    project_page=paper_data.get("projectPage"),
                    github_repo=paper_data.get("githubRepo"),
                    thumbnail=paper_data.get("thumbnail"),
                    github_stars=paper_data.get("githubStars"),
                )

                engagement = PaperEngagement(
                    upvotes=paper_data.get("upvotes", 0),
                    num_comments=paper_data.get("numComments", 0),
                    discussion_id=paper_data.get("discussionId"),
                )

                submission = PaperSubmission(
                    submitted_by=submitted_by,
                    submitted_on_daily_by=submitted_on_daily_by,
                    submitted_on_daily_at=paper_data.get("submittedOnDailyAt"),
                    is_author_participating=paper_data.get("isAuthorParticipating"),
                )

                ai_content = AIContent(
                    ai_summary=paper_data.get("ai_summary"),
                    ai_keywords=paper_data.get("ai_keywords", []),
                )

                paper = Paper(
                    core=core,
                    metadata=metadata,
                    engagement=engagement,
                    submission=submission,
                    ai_content=ai_content,
                )
                papers.append(paper)

        return papers

    except requests.RequestException as e:
        logging.error(f"Failed to fetch papers from Hugging Face API: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error processing papers data: {str(e)}")
        return []


def paper_discovery_node(state: PipelineState) -> Command:
    """
    Discover papers from Hugging Face based on user preferences.

    Fetches papers from configured sources, (TO-DO filters by categories and keywords),
    and updates state with discovered papers.
    """
    logging.info(f"Starting paper discovery for pipeline {state['pipeline_id']}")

    # Get user preferences for filtering
    settings = state.get("settings", {})
    limit = settings.get("limit", 10)

    logging.info(f"Fetching papers with limit={limit}")

    papers = _fetch_daily_papers(limit=limit)

    if not papers:
        logging.warning("No papers fetched from Hugging Face API")
        return Command(goto=END, update={"error": "No papers fetched"})

    logging.info("Paper discovery completed - proceeding to map extraction")

    return Command(goto=MAP_EXTRACTION_NODE, update={"discovered_papers": papers})


def map_extraction_node(state: PipelineState) -> Command:
    """
    Map each discovered paper to individual extraction processing.

    Uses Send commands to process papers in parallel via subgraph invocation.
    """
    logging.info(f"Mapping papers for extraction in pipeline {state['pipeline_id']}")

    if not state.get("discovered_papers"):
        logging.info("No papers discovered - proceeding to delivery")
        return Command(goto=DELIVERY_NODE, update={"processing_complete": True})

    paper_count = len(state["discovered_papers"])
    logging.info(
        f"Mapping {paper_count} papers for parallel processing via Send commands"
    )

    # Create Send commands for parallel processing
    send_commands = []
    for idx, paper in enumerate(state["discovered_papers"]):
        paper_state = {
            "paper": paper,
            "paper_index": idx,
            "pipeline_id": state["pipeline_id"],
            "extracted_content": None,
            "analysis": None,
            "errors": None,
        }
        send_commands.append(Send(PROCESS_SINGLE_PAPER_NODE, paper_state))

    logging.info(f"Created {len(send_commands)} Send commands for parallel processing")

    return Command(goto=send_commands, update={"parallel_processing_started": True})


def process_single_paper_node(state: SinglePaperState) -> Command:
    """
    Process a single paper by invoking the subgraph.

    This node receives Send commands and invokes the subgraph for isolated processing.
    """
    from backend.pipeline.graph import build_single_paper_subgraph

    paper = state["paper"]
    paper_index = state["paper_index"]
    pipeline_id = state["pipeline_id"]

    logging.info(
        f"[Pipeline {pipeline_id}] [Paper {paper_index}] Processing paper via subgraph: {paper.title}"
    )

    # Build and invoke the subgraph
    subgraph = build_single_paper_subgraph()
    result = subgraph.invoke(state)

    logging.info(
        f"[Pipeline {pipeline_id}] [Paper {paper_index}] Subgraph processing completed"
    )

    # Create unique keys to avoid conflicts when updating main state
    result_key = f"paper_result_{paper_index}_{pipeline_id.replace('-', '_')}"

    return Command(goto=COLLECT_RESULTS_NODE, update={result_key: result})


def extract_single_paper_node(state: SinglePaperState) -> Command:
    """
    Extract content from a single paper using Docling.

    TODO: Implement single paper extraction logic
    - Download PDF for this paper
    - Parse with Docling
    - Extract structured content
    - Handle figures, tables, equations
    """
    paper = state["paper"]
    paper_index = state["paper_index"]
    pipeline_id = state["pipeline_id"]

    if hasattr(paper, "title"):
        paper_title = paper.title
        paper_id = paper.id
        author_list = paper.author_list
    else:
        paper_title = paper.get("title", "Unknown")
        paper_id = paper.get("id", "unknown")
        author_list = "Unknown authors"

    logging.info(
        f"[Pipeline {pipeline_id}] [Paper {paper_index}] Starting extraction for: {paper_title}"
    )
    logging.info(f"[Pipeline {pipeline_id}] [Paper {paper_index}] Paper ID: {paper_id}")
    logging.info(
        f"[Pipeline {pipeline_id}] [Paper {paper_index}] Authors: {author_list}"
    )

    # TODO: Add single paper extraction implementation
    # extracted_content = extract_paper_content(state["paper"])
    extracted_content = {
        "status": "extracted",
        "content": "placeholder",
        "paper_id": paper_id,
        "extraction_timestamp": datetime.now().isoformat(),
    }

    logging.info(
        f"[Pipeline {pipeline_id}] [Paper {paper_index}] Content extraction completed - proceeding to analysis"
    )

    return Command(
        goto=ANALYZE_SINGLE_PAPER_NODE, update={"extracted_content": extracted_content}
    )


def analyze_single_paper_node(state: SinglePaperState) -> Command:
    """
    Analyze extracted content from a single paper using LLM.

    TODO: Implement single paper analysis logic
    - Identify research problems
    - Extract key contributions
    - Analyze methodology
    - Generate executive summary
    """
    paper = state["paper"]
    paper_index = state["paper_index"]
    pipeline_id = state["pipeline_id"]
    extracted_content = state.get("extracted_content", {})

    if hasattr(paper, "title"):
        paper_title = paper.title
        paper_id = paper.id
        ai_summary = paper.ai_summary
        ai_keywords = paper.ai_keywords
    else:
        paper_title = paper.get("title", "Unknown")
        paper_id = paper.get("id", "unknown")
        ai_summary = paper.get("ai_summary")
        ai_keywords = paper.get("ai_keywords", [])

    logging.info(
        f"[Pipeline {pipeline_id}] [Paper {paper_index}] Starting analysis for: {paper_title}"
    )
    logging.info(
        f"[Pipeline {pipeline_id}] [Paper {paper_index}] Using extracted content from: {extracted_content.get('extraction_timestamp', 'unknown time')}"
    )
    if ai_summary:
        logging.info(
            f"[Pipeline {pipeline_id}] [Paper {paper_index}] AI Summary available: {ai_summary[:100]}..."
        )
    if ai_keywords:
        logging.info(
            f"[Pipeline {pipeline_id}] [Paper {paper_index}] AI Keywords: {', '.join(ai_keywords[:5])}"
        )

    # TODO: Add single paper analysis implementation
    # analysis = analyze_paper_content(state["extracted_content"])
    analysis = {
        "status": "analyzed",
        "paper_id": paper_id,
        "tldr": f"Analysis placeholder for {paper_title}",
        "key_contributions": [f"Contribution analysis for {paper_id}"],
        "technical_insights": [f"Technical insight for {paper_title}"],
        "analysis_timestamp": datetime.now().isoformat(),
    }

    logging.info(
        f"[Pipeline {pipeline_id}] [Paper {paper_index}] Analysis completed - proceeding to collect results"
    )

    return Command(goto=END, update={"analysis": analysis})


def collect_results_node(state: PipelineState) -> Command:
    """
    Collect results from all processed papers and merge into main pipeline state.

    This is the "reduce" step that aggregates all individual paper results.
    """
    pipeline_id = state.get("pipeline_id", "unknown")

    # Find all paper result keys in the state
    paper_results = {}
    for key, value in state.items():
        if key.startswith("paper_result_") and isinstance(value, dict):
            paper_results[key] = value

    paper_count = len(paper_results)
    logging.info(
        f"[Pipeline {pipeline_id}] Collecting results from {paper_count} papers"
    )

    # Aggregate results from all papers
    processed_papers = []
    extraction_results = {}
    analysis_results = {}

    for result_key, paper_result in paper_results.items():
        paper_idx = paper_result.get("paper_index", 0)
        paper = paper_result.get("paper")
        processed_papers.append(paper)

        # Log individual paper completion
        if hasattr(paper, "title"):
            paper_title = paper.title
        else:
            paper_title = paper.get("title", "Unknown") if paper else "Unknown"

        logging.info(
            f"[Pipeline {pipeline_id}] Collected results for paper {paper_idx}: {paper_title}"
        )

        if "extracted_content" in paper_result:
            extraction_results[paper_idx] = paper_result["extracted_content"]
            logging.info(
                f"[Pipeline {pipeline_id}] Paper {paper_idx}: Extraction completed at {paper_result['extracted_content'].get('extraction_timestamp', 'unknown time')}"
            )

        if "analysis" in paper_result:
            analysis_results[paper_idx] = paper_result["analysis"]
            logging.info(
                f"[Pipeline {pipeline_id}] Paper {paper_idx}: Analysis completed at {paper_result['analysis'].get('analysis_timestamp', 'unknown time')}"
            )

    logging.info(
        f"[Pipeline {pipeline_id}] Results collection completed - proceeding to delivery"
    )
    logging.info(
        f"[Pipeline {pipeline_id}] Summary: {len(extraction_results)} extractions, {len(analysis_results)} analyses"
    )

    return Command(
        goto=DELIVERY_NODE,
        update={
            "processed_papers": processed_papers,
            "extraction_results": extraction_results,
            "analysis_results": analysis_results,
            "processing_complete": True,
        },
    )


def delivery_node(state: PipelineState) -> Command:
    """
    Format and deliver research digest to Slack channels.

    TODO: Implement delivery logic
    - Format analysis results
    - Create Slack blocks
    - Send to configured channels
    - Update delivery status
    """
    logging.info(f"Starting delivery for pipeline {state['pipeline_id']}")

    # TODO: Add delivery implementation
    delivery_status = {
        "delivered_at": datetime.now().isoformat(),
        "status": "delivered",
        "channel_count": 1,
        "paper_count": len(state.get("processed_papers", [])),
    }

    logging.info(f"Delivery completed for pipeline {state['pipeline_id']}")

    return Command(goto=END, update={"delivery_status": delivery_status})
