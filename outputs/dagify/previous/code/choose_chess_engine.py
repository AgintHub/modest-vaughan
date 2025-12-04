from ._choose_chess_engine.research_chess_engines import research_chess_engines
from ._choose_chess_engine.evaluate_engine_performance import evaluate_engine_performance
from ._choose_chess_engine.select_best_engine import select_best_engine
from ._choose_chess_engine.verify_engine_features import verify_engine_features
from ._choose_chess_engine.get_engine_key_features import get_engine_key_features
from ._choose_chess_engine.get_engine_elo_rating import get_engine_elo_rating

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Research and identify potential chess engines that meet the user requirements
#   Reason: This step is necessary to ensure that the chosen engine meets the user's
#           needs
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use online research, review articles, and chess engine documentation to
#           identify potential engines
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Evaluate the features and performance of each potential chess engine
#   Reason: This step is necessary to determine which engine best meets the user
#           requirements
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use benchmarks, performance metrics, and feature lists to evaluate each
#           engine
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Select the chess engine that best meets the user requirements
#   Reason: This step is necessary to ensure that the chosen engine meets the user's
#           needs
#   Impact: HIGH
#   Complexity: LOW
#   Method: Compare the features and performance of each engine and select the best one
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Verify that the chosen engine supports the required features
#   Reason: This step is necessary to ensure that the chosen engine meets the user
#           requirements
#   Impact: HIGH
#   Complexity: LOW
#   Method: Check the engine's documentation and feature list to verify that it
#           supports the required features
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Retrieve the Elo rating of the chosen chess engine
#   Reason: This step is necessary to provide a measure of the engine's performance
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Look up the engine's Elo rating in a reliable chess engine rating database
#           or documentation
# -- END PRD --



class GatherUserRequirementsOutput(BaseModel):
    """Pydantic model for gather_user_requirements node outputs."""
    required_features: List[str] = Field(..., description="List of the top 5 required features for the chess application")
    feature_priorities: List[int] = Field(..., description="List of priorities for each feature, with 1 being the highest priority")
    user_feedback_summary: str = Field(..., description="Summary of user feedback and reviews analyzed to determine required features")


class ChooseChessEngineOutput(BaseModel):
    """Pydantic model for choose_chess_engine node outputs."""
    chosen_engine: str = Field(..., description="The name of the selected chess engine")
    key_features: List[str] = Field(..., description="A list of key features supported by the chosen chess engine")
    supported_features: List[bool] = Field(..., description="A list of boolean values indicating whether each of the required features is supported by the chosen engine")
    engine_rating: int = Field(..., description="The Elo rating of the chosen chess engine")


def choose_chess_engine(gather_user_requirements_input: GatherUserRequirementsOutput, **kwargs) -> ChooseChessEngineOutput:
    """Select a reliable chess engine for the application.

    Args:
        gather_user_requirements_input: Input from the 'gather_user_requirements' node.
        **kwargs: Additional keyword arguments.

    Returns:
        ChooseChessEngineOutput: Object containing outputs for this node.
    """
    # Research and identify potential chess engines that meet user requirements
    potential_engines: List[str] = research_chess_engines(
        required_features=gather_user_requirements_input.required_features,
        feature_priorities=gather_user_requirements_input.feature_priorities
    )
    
    # Evaluate features and performance of each potential chess engine
    engine_evaluations: List[dict] = evaluate_engine_performance(
        engines=potential_engines,
        required_features=gather_user_requirements_input.required_features
    )
    
    # Select the best chess engine based on evaluation results
    best_engine: str = select_best_engine(
        evaluations=engine_evaluations,
        feature_priorities=gather_user_requirements_input.feature_priorities
    )
    
    # Verify that the chosen engine supports the required features
    feature_support_verification: List[bool] = verify_engine_features(
        engine_name=best_engine,
        required_features=gather_user_requirements_input.required_features
    )
    
    # Get key features supported by the chosen engine
    engine_key_features: List[str] = get_engine_key_features(
        engine_name=best_engine
    )
    
    # Retrieve the Elo rating of the chosen chess engine
    engine_elo_rating: int = get_engine_elo_rating(
        engine_name=best_engine
    )
    
    return ChooseChessEngineOutput(
        chosen_engine=best_engine,
        key_features=engine_key_features,
        supported_features=feature_support_verification,
        engine_rating=engine_elo_rating
    )