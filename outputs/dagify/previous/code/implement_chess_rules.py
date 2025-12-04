from ._implement_chess_rules.review_official_chess_rules import review_official_chess_rules
from ._implement_chess_rules.implement_castling_rules import implement_castling_rules
from ._implement_chess_rules.implement_pawn_promotion_rules import implement_pawn_promotion_rules
from ._implement_chess_rules.implement_checkmate_conditions import implement_checkmate_conditions
from ._implement_chess_rules.verify_chess_implementation import verify_chess_implementation
from ._implement_chess_rules.compile_supported_moves import compile_supported_moves
from ._implement_chess_rules.extract_checkmate_conditions import extract_checkmate_conditions
from ._implement_chess_rules.generate_implementation_notes import generate_implementation_notes

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Review the official chess rules and regulations to ensure understanding of
#   the requirements.
#   Reason: This step is necessary to ensure that the implementation accurately
#           reflects the official rules.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Consult a chess reference guide and review the rules.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Implement castling rules, including king-side and queen-side castling.
#   Reason: Castling is a special move that allows the king to move three squares
#           towards a rook.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a state machine to track the king's and rook's positions.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Implement pawn promotion rules, including promotion to queen, rook, bishop,
#   and knight.
#   Reason: Pawn promotion is a critical aspect of chess, allowing pawns to become more
#           powerful pieces.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a promotion queue to track pawns that are eligible for promotion.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Implement checkmate conditions, including check, checkmate, and stalemate.
#   Reason: Checkmate is the ultimate goal of chess, and the implementation must
#           accurately reflect the conditions.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Use a state machine to track the king's position and detect checkmate
#           conditions.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Verify the implementation using a chess reference guide.
#   Reason: Verification is critical to ensure that the implementation accurately
#           reflects the official rules.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Consult a chess reference guide and test the implementation.
# -- END PRD --



class ChooseChessEngineOutput(BaseModel):
    """Pydantic model for choose_chess_engine node outputs."""
    chosen_engine: str = Field(..., description="The name of the selected chess engine")
    key_features: List[str] = Field(..., description="A list of key features supported by the chosen chess engine")
    supported_features: List[bool] = Field(..., description="A list of boolean values indicating whether each of the required features is supported by the chosen engine")
    engine_rating: int = Field(..., description="The Elo rating of the chosen chess engine")


class DesignChessBoardOutput(BaseModel):
    """Pydantic model for design_chess_board node outputs."""
    board_design_description: str = Field(..., description="Description of the chess board design")
    key_elements: str = Field(..., description="List of key elements in the chess board design")
    mockup_image: str = Field(..., description="Mockup image of the chess board design (represented as a string for simplicity)")
    design_meets_requirements: bool = Field(..., description="Whether the design meets the user requirements")


class ImplementChessRulesOutput(BaseModel):
    """Pydantic model for implement_chess_rules node outputs."""
    chess_rules_implemented: bool = Field(..., description="Whether the official chess rules have been successfully implemented.")
    rules_verification_status: str = Field(..., description="Status of the rules verification process using a chess reference guide.")
    supported_moves: List[str] = Field(..., description="List of supported chess moves, including castling, pawn promotion, and en passant.")
    checkmate_conditions: List[str] = Field(..., description="List of conditions that lead to checkmate.")
    implementation_notes: str = Field(..., description="Any additional notes or comments regarding the implementation of chess rules.")


def implement_chess_rules(choose_chess_engine_input: ChooseChessEngineOutput, design_chess_board_input: DesignChessBoardOutput, **kwargs) -> ImplementChessRulesOutput:
    """Enforce the official chess rules and regulations.

    Args:
        choose_chess_engine_input: Input from the 'choose_chess_engine' node.
        design_chess_board_input: Input from the 'design_chess_board' node.
        **kwargs: Additional keyword arguments.

    Returns:
        ImplementChessRulesOutput: Object containing outputs for this node.
    """
    # Review official chess rules and regulations
    official_rules: dict = review_official_chess_rules()
    
    # Implement castling rules for both king-side and queen-side
    castling_implementation: dict = implement_castling_rules(
        engine_features=choose_chess_engine_input.key_features,
        board_design=design_chess_board_input.board_design_description
    )
    
    # Implement pawn promotion rules for all piece types
    promotion_implementation: dict = implement_pawn_promotion_rules(
        supported_pieces=["queen", "rook", "bishop", "knight"]
    )
    
    # Implement checkmate, check, and stalemate conditions
    checkmate_implementation: dict = implement_checkmate_conditions(
        engine_rating=choose_chess_engine_input.engine_rating
    )
    
    # Verify implementation using chess reference guide
    verification_result: dict = verify_chess_implementation(
        rules=official_rules,
        castling=castling_implementation,
        promotion=promotion_implementation,
        checkmate=checkmate_implementation
    )
    
    # Compile supported moves list
    supported_moves_list: List[str] = compile_supported_moves(
        castling=castling_implementation,
        promotion=promotion_implementation,
        basic_moves=official_rules
    )
    
    # Extract checkmate conditions
    checkmate_conditions_list: List[str] = extract_checkmate_conditions(
        checkmate_impl=checkmate_implementation
    )
    
    # Generate implementation notes
    notes: str = generate_implementation_notes(
        engine_name=choose_chess_engine_input.chosen_engine,
        board_requirements=design_chess_board_input.design_meets_requirements,
        verification=verification_result
    )
    
    return ImplementChessRulesOutput(
        chess_rules_implemented=verification_result["success"],
        rules_verification_status=verification_result["status"],
        supported_moves=supported_moves_list,
        checkmate_conditions=checkmate_conditions_list,
        implementation_notes=notes
    )