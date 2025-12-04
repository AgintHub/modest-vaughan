# -- PRD --
# 1. BULLET: Retrieve the chosen chess engine details from the output of the
#   'choose_chess_engine' node.
#   Reason: To ensure that the correct chess engine is integrated with the application.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Access the 'chosen_engine' and 'key_features' fields from the
#           'choose_chess_engine' node's output.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Retrieve the designed user interface details from the output of the
#   'add_user_interface' node.
#   Reason: To ensure that the chess engine is integrated with the correct user
#           interface.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Access the 'ui_components', 'layout_description', and 'validation_passed'
#           fields from the 'add_user_interface' node's output.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Use the chess engine's API to integrate it with the user interface.
#   Reason: To enable seamless interaction between the engine and the UI.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Utilize the chess engine's API documentation to implement the integration.
#           Handle errors and exceptions properly.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Verify the correct functioning of chess moves and rules.
#   Reason: To ensure that the integration is successful and the chess engine is
#           working correctly.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Implement test cases to verify the correctness of chess moves and rules.
#           Use a chess reference guide to validate the results.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Document the integration process and any issues encountered.
#   Reason: To facilitate debugging and future maintenance.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Keep a record of the integration process, including any challenges faced
#           and solutions implemented.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class ChooseChessEngineOutput(BaseModel):
    """Pydantic model for choose_chess_engine node outputs."""
    chosen_engine: str = Field(..., description="The name of the selected chess engine")
    key_features: List[str] = Field(..., description="A list of key features supported by the chosen chess engine")
    supported_features: List[bool] = Field(..., description="A list of boolean values indicating whether each of the required features is supported by the chosen engine")
    engine_rating: int = Field(..., description="The Elo rating of the chosen chess engine")


class AddUserInterfaceOutput(BaseModel):
    """Pydantic model for add_user_interface node outputs."""
    ui_components: List[str] = Field(..., description="List of UI components such as buttons, menus, and tooltips.")
    layout_description: str = Field(..., description="Brief textual description of the overall UI layout.")
    validation_passed: bool = Field(..., description="Whether the UI design meets UX guidelines.")
    accessibility_score: int = Field(..., description="Accessibility score ranging from 0 (poor) to 100 (excellent).")
    user_feedback_summary: str = Field(..., description="Summary of user feedback on the UI design.")


class IntegrateChessEngineOutput(BaseModel):
    """Pydantic model for integrate_chess_engine node outputs."""
    integration_status: bool = Field(..., description="Whether the integration was successful")
    chess_engine_used: str = Field(..., description="The name of the chess engine used for integration")
    issues_encountered: List[str] = Field(..., description="List of issues encountered during integration")
    verification_result: bool = Field(..., description="Whether the verification of chess moves and rules was successful")


def integrate_chess_engine(choose_chess_engine_input: ChooseChessEngineOutput, add_user_interface_input: AddUserInterfaceOutput, **kwargs) -> IntegrateChessEngineOutput:
    """Integrate the selected chess engine with the application.

    Args:
        choose_chess_engine_input: Input from the 'choose_chess_engine' node.
        add_user_interface_input: Input from the 'add_user_interface' node.
        **kwargs: Additional keyword arguments.

    Returns:
        IntegrateChessEngineOutput: Object containing outputs for this node.
    """
    # Retrieve chosen chess engine details
    chosen_engine: str = choose_chess_engine_input.chosen_engine
    key_features: List[str] = choose_chess_engine_input.key_features
    
    # Retrieve user interface details
    ui_components: List[str] = add_user_interface_input.ui_components
    layout_description: str = add_user_interface_input.layout_description
    validation_passed: bool = add_user_interface_input.validation_passed
    
    # Initialize integration tracking
    issues_encountered: List[str] = []
    
    # Use chess engine API to integrate with UI
    integration_successful: bool = integrate_engine_with_ui(
        engine_name=chosen_engine,
        engine_features=key_features,
        ui_components=ui_components,
        layout_description=layout_description
    )
    
    # Handle integration errors and exceptions
    if not integration_successful:
        integration_errors: List[str] = handle_integration_errors(
            engine=chosen_engine,
            ui_validation=validation_passed
        )
        issues_encountered.extend(integration_errors)
    
    # Verify chess moves and rules functionality
    verification_passed: bool = verify_chess_functionality(
        engine_name=chosen_engine,
        integrated_ui=ui_components
    )
    
    if not verification_passed:
        verification_issues: List[str] = analyze_verification_failures(
            engine=chosen_engine
        )
        issues_encountered.extend(verification_issues)
    
    # Document integration process and issues
    document_integration_process(
        engine_name=chosen_engine,
        integration_status=integration_successful,
        verification_status=verification_passed,
        issues=issues_encountered
    )
    
    return IntegrateChessEngineOutput(
        integration_status=integration_successful,
        chess_engine_used=chosen_engine,
        issues_encountered=issues_encountered,
        verification_result=verification_passed
    )