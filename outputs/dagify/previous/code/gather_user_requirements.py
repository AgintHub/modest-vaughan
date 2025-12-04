from ._gather_user_requirements.collect_chess_app_reviews import collect_chess_app_reviews
from ._gather_user_requirements.collect_user_feedback import collect_user_feedback
from ._gather_user_requirements.apply_nlp_processing import apply_nlp_processing
from ._gather_user_requirements.perform_sentiment_analysis import perform_sentiment_analysis
from ._gather_user_requirements.analyze_user_feedback import analyze_user_feedback
from ._gather_user_requirements.extract_features_from_analysis import extract_features_from_analysis
from ._gather_user_requirements.categorize_features import categorize_features
from ._gather_user_requirements.apply_prioritization_matrix import apply_prioritization_matrix
from ._gather_user_requirements.select_top_features import select_top_features
from ._gather_user_requirements.assign_feature_priorities import assign_feature_priorities
from ._gather_user_requirements.summarize_user_feedback import summarize_user_feedback

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Conduct a thorough analysis of online reviews and user feedback on existing
#   chess applications to identify common complaints and desired features.
#   Reason: This approach provides valuable insights into user needs and preferences.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use natural language processing (NLP) techniques to analyze text data from
#           online reviews and user feedback. Apply sentiment analysis to
#           identify positive and negative sentiments.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Identify and categorize desired features into functional and non-functional
#   requirements.
#   Reason: This approach helps to prioritize features based on user needs.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use a feature categorization framework to group similar features together.
#           Apply a prioritization matrix to rank features based on their
#           importance and feasibility.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Select the top 5 required features based on their priority and importance.
#   Reason: This approach ensures that the most critical features are addressed.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use a decision-making framework to select the top 5 features. Apply a
#           weighted scoring model to evaluate features based on their
#           priority and importance.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Assign priorities to each feature based on their importance and feasibility.
#   Reason: This approach ensures that features are implemented in the correct order.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use a prioritization framework to assign priorities to each feature. Apply
#           a numerical scale (e.g., 1-5) to represent the priority level.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Summarize the user feedback and reviews analyzed to determine required
#   features.
#   Reason: This approach provides context and justification for the selected features.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use a text summarization technique to summarize the user feedback and
#           reviews. Apply a qualitative analysis approach to identify key
#           themes and insights.
# -- END PRD --



class GatherUserRequirementsOutput(BaseModel):
    """Pydantic model for gather_user_requirements node outputs."""
    required_features: List[str] = Field(..., description="List of the top 5 required features for the chess application")
    feature_priorities: List[int] = Field(..., description="List of priorities for each feature, with 1 being the highest priority")
    user_feedback_summary: str = Field(..., description="Summary of user feedback and reviews analyzed to determine required features")


def gather_user_requirements(general_input: str, **kwargs) -> GatherUserRequirementsOutput:
    """Collect user feedback and identify key features for the chess application.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        GatherUserRequirementsOutput: Object containing outputs for this node.
    """
    # Conduct thorough analysis of online reviews and user feedback
    raw_reviews_data: List[str] = collect_chess_app_reviews(sources=["app_stores", "forums", "social_media"])
    user_feedback_data: List[str] = collect_user_feedback(sources=["surveys", "support_tickets", "community_posts"])
    
    # Apply NLP techniques and sentiment analysis
    processed_reviews: List[dict] = apply_nlp_processing(text_data=raw_reviews_data)
    sentiment_analysis_results: dict = perform_sentiment_analysis(processed_data=processed_reviews)
    feedback_analysis_results: dict = analyze_user_feedback(feedback_data=user_feedback_data)
    
    # Identify and extract features from analysis
    extracted_features: List[str] = extract_features_from_analysis(
        reviews_analysis=sentiment_analysis_results,
        feedback_analysis=feedback_analysis_results
    )
    
    # Categorize features into functional and non-functional requirements
    categorized_features: dict = categorize_features(
        features=extracted_features,
        framework="functional_nonfunctional"
    )
    
    # Apply prioritization matrix to rank features
    prioritized_features: List[dict] = apply_prioritization_matrix(
        categorized_features=categorized_features,
        criteria=["importance", "feasibility", "user_impact"]
    )
    
    # Select top 5 features using decision-making framework
    top_features: List[str] = select_top_features(
        prioritized_features=prioritized_features,
        count=5,
        method="weighted_scoring"
    )
    
    # Assign numerical priorities to selected features
    feature_priorities: List[int] = assign_feature_priorities(
        features=top_features,
        scale_range=(1, 5),
        priority_framework="importance_feasibility"
    )
    
    # Generate summary of user feedback and reviews
    feedback_summary: str = summarize_user_feedback(
        reviews_data=raw_reviews_data,
        feedback_data=user_feedback_data,
        analysis_results=sentiment_analysis_results,
        method="qualitative_analysis"
    )
    
    return GatherUserRequirementsOutput(
        required_features=top_features,
        feature_priorities=feature_priorities,
        user_feedback_summary=feedback_summary
    )