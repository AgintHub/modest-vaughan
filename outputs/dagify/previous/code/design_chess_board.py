from ._design_chess_board.determine_color_scheme_from_engine import determine_color_scheme_from_engine
from ._design_chess_board.select_piece_designs_from_engine import select_piece_designs_from_engine
from ._design_chess_board.analyze_user_requirements import analyze_user_requirements
from ._design_chess_board.design_board_layout import design_board_layout
from ._design_chess_board.create_board_mockup import create_board_mockup
from ._design_chess_board.generate_design_description import generate_design_description
from ._design_chess_board.describe_key_elements import describe_key_elements
from ._design_chess_board.verify_design_requirements import verify_design_requirements

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Retrieve the chosen chess engine's name and key features from the
#   choose_chess_engine node's output
#   Reason: To incorporate the chosen engine's capabilities into the board design
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use the chosen engine's name to determine the preferred color scheme and
#           piece designs, and incorporate its key features into the
#           board's layout and functionality
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Determine the user requirements for the chess board design based on the
#   choose_chess_engine node's output
#   Reason: To ensure the design meets the user's needs and expectations
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Analyze the user requirements gathered during the choose_chess_engine
#           node's execution and identify the key elements that must be
#           included in the board design
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Create a simple mockup of the chess board design using a graphic design tool
#   Reason: To visualize the design and identify potential issues
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a graphic design tool to create a mockup of the chess board,
#           incorporating the chosen engine's name, key features, and user
#           requirements
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Describe the key elements of the chess board design
#   Reason: To provide a clear understanding of the design's components and
#           functionality
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Write a detailed description of the key elements, including the board's
#           layout, piece designs, and any notable features or
#           functionalities
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Verify that the design meets the user requirements
#   Reason: To ensure the design is satisfactory and functional
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Compare the design to the user requirements and verify that all necessary
#           elements are included and functional
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


def design_chess_board(choose_chess_engine_input: ChooseChessEngineOutput, **kwargs) -> DesignChessBoardOutput:
    """Create a visually appealing chess board design.

    Args:
        choose_chess_engine_input: Input from the 'choose_chess_engine' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DesignChessBoardOutput: Object containing outputs for this node.
    """
    # Retrieve engine information and features
    engine_name: str = choose_chess_engine_input.chosen_engine
    engine_features: List[str] = choose_chess_engine_input.key_features
    
    # Determine color scheme and piece designs based on chosen engine
    color_scheme: str = determine_color_scheme_from_engine(engine_name=engine_name)
    piece_designs: str = select_piece_designs_from_engine(engine_name=engine_name)
    
    # Analyze user requirements from engine selection
    user_requirements: List[str] = analyze_user_requirements(engine_output=choose_chess_engine_input)
    
    # Create board layout incorporating engine features
    board_layout: str = design_board_layout(features=engine_features, requirements=user_requirements)
    
    # Generate mockup using graphic design tool
    mockup_data: str = create_board_mockup(
        color_scheme=color_scheme,
        piece_designs=piece_designs,
        layout=board_layout,
        engine_name=engine_name
    )
    
    # Describe key elements of the design
    design_description: str = generate_design_description(
        color_scheme=color_scheme,
        piece_designs=piece_designs,
        layout=board_layout,
        engine_features=engine_features
    )
    
    key_elements_description: str = describe_key_elements(
        layout=board_layout,
        pieces=piece_designs,
        features=engine_features
    )
    
    # Verify design meets user requirements
    requirements_met: bool = verify_design_requirements(
        design_elements=key_elements_description,
        user_requirements=user_requirements,
        mockup=mockup_data
    )
    
    return DesignChessBoardOutput(
        board_design_description=design_description,
        key_elements=key_elements_description,
        mockup_image=mockup_data,
        design_meets_requirements=requirements_met
    )