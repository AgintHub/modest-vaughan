from ._add_user_interface.conduct_user_research import conduct_user_research
from ._add_user_interface.create_wireframes_and_prototypes import create_wireframes_and_prototypes
from ._add_user_interface.extract_ui_components import extract_ui_components
from ._add_user_interface.generate_layout_description import generate_layout_description
from ._add_user_interface.validate_ui_design import validate_ui_design
from ._add_user_interface.calculate_accessibility_score import calculate_accessibility_score
from ._add_user_interface.test_ui_with_users import test_ui_with_users
from ._add_user_interface.iterate_ui_design import iterate_ui_design
from ._add_user_interface.summarize_user_feedback import summarize_user_feedback
from ._add_user_interface.determine_validation_status import determine_validation_status

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Conduct user research to gather requirements for the UI design
#   Reason: This step ensures that the UI design meets the needs and expectations of
#           the target users
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use online surveys, user interviews, and competitor analysis to gather
#           requirements
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Create wireframes and prototypes of the UI design
#   Reason: This step allows for visualization and testing of the UI design
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use design tools such as Figma, Sketch, or Adobe XD to create wireframes
#           and prototypes
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Validate the UI design using UX guidelines and heuristics
#   Reason: This step ensures that the UI design meets established UX principles and
#           guidelines
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use UX guidelines such as Nielsen's heuristics, WCAG 2.1, and Material
#           Design principles to evaluate the UI design
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Test the UI design with a small group of users and gather feedback
#   Reason: This step ensures that the UI design is user-friendly and meets the needs
#           of the target users
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use usability testing methods such as user testing, A/B testing, and
#           heatmap analysis to gather feedback
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Iterate on the UI design based on user feedback and testing results
#   Reason: This step ensures that the UI design is refined and improved based on user
#           feedback and testing results
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use design tools and UX principles to iterate on the UI design and make
#           improvements
# -- END PRD --



class ImplementChessRulesOutput(BaseModel):
    """Pydantic model for implement_chess_rules node outputs."""
    chess_rules_implemented: bool = Field(..., description="Whether the official chess rules have been successfully implemented.")
    rules_verification_status: str = Field(..., description="Status of the rules verification process using a chess reference guide.")
    supported_moves: List[str] = Field(..., description="List of supported chess moves, including castling, pawn promotion, and en passant.")
    checkmate_conditions: List[str] = Field(..., description="List of conditions that lead to checkmate.")
    implementation_notes: str = Field(..., description="Any additional notes or comments regarding the implementation of chess rules.")


class DesignChessBoardOutput(BaseModel):
    """Pydantic model for design_chess_board node outputs."""
    board_design_description: str = Field(..., description="Description of the chess board design")
    key_elements: str = Field(..., description="List of key elements in the chess board design")
    mockup_image: str = Field(..., description="Mockup image of the chess board design (represented as a string for simplicity)")
    design_meets_requirements: bool = Field(..., description="Whether the design meets the user requirements")


class AddUserInterfaceOutput(BaseModel):
    """Pydantic model for add_user_interface node outputs."""
    ui_components: List[str] = Field(..., description="List of UI components such as buttons, menus, and tooltips.")
    layout_description: str = Field(..., description="Brief textual description of the overall UI layout.")
    validation_passed: bool = Field(..., description="Whether the UI design meets UX guidelines.")
    accessibility_score: int = Field(..., description="Accessibility score ranging from 0 (poor) to 100 (excellent).")
    user_feedback_summary: str = Field(..., description="Summary of user feedback on the UI design.")


def add_user_interface(implement_chess_rules_input: ImplementChessRulesOutput, design_chess_board_input: DesignChessBoardOutput, **kwargs) -> AddUserInterfaceOutput:
    """Design an intuitive and user-friendly interface for the application.

    Args:
        implement_chess_rules_input: Input from the 'implement_chess_rules' node.
        design_chess_board_input: Input from the 'design_chess_board' node.
        **kwargs: Additional keyword arguments.

    Returns:
        AddUserInterfaceOutput: Object containing outputs for this node.
    """
    # Conduct user research to gather UI requirements
    user_requirements: dict = conduct_user_research(
        surveys=True, 
        interviews=True, 
        competitor_analysis=True
    )
    
    # Create wireframes and prototypes based on chess rules and board design
    wireframes: dict = create_wireframes_and_prototypes(
        chess_rules=implement_chess_rules_input,
        board_design=design_chess_board_input,
        user_requirements=user_requirements
    )
    
    # Extract UI components from wireframes
    ui_components: List[str] = extract_ui_components(wireframes=wireframes)
    
    # Generate layout description
    layout_description: str = generate_layout_description(
        wireframes=wireframes,
        board_design=design_chess_board_input.board_design_description
    )
    
    # Validate UI design using UX guidelines and heuristics
    validation_results: dict = validate_ui_design(
        wireframes=wireframes,
        nielsen_heuristics=True,
        wcag_guidelines=True,
        material_design=True
    )
    
    # Calculate accessibility score
    accessibility_score: int = calculate_accessibility_score(
        validation_results=validation_results,
        wcag_compliance=True
    )
    
    # Test UI design with users and gather feedback
    user_feedback: dict = test_ui_with_users(
        wireframes=wireframes,
        usability_testing=True,
        ab_testing=True,
        heatmap_analysis=True
    )
    
    # Iterate on design based on feedback
    final_design: dict = iterate_ui_design(
        wireframes=wireframes,
        user_feedback=user_feedback,
        validation_results=validation_results
    )
    
    # Generate user feedback summary
    feedback_summary: str = summarize_user_feedback(user_feedback=user_feedback)
    
    # Determine if validation passed
    validation_passed: bool = determine_validation_status(
        validation_results=validation_results,
        accessibility_score=accessibility_score
    )
    
    return AddUserInterfaceOutput(
        ui_components=ui_components,
        layout_description=layout_description,
        validation_passed=validation_passed,
        accessibility_score=accessibility_score,
        user_feedback_summary=feedback_summary
    )