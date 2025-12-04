from ._test_chess_application.create_comprehensive_test_plan import create_comprehensive_test_plan
from ._test_chess_application.generate_test_cases import generate_test_cases
from ._test_chess_application.execute_test_cases import execute_test_cases
from ._test_chess_application.analyze_test_results import analyze_test_results
from ._test_chess_application.fix_bugs_and_retest import fix_bugs_and_retest
from ._test_chess_application.generate_test_summary_report import generate_test_summary_report
from ._test_chess_application.determine_overall_test_status import determine_overall_test_status
from ._test_chess_application.extract_failed_test_names import extract_failed_test_names
from ._test_chess_application.count_total_bugs import count_total_bugs

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Develop a comprehensive test plan that covers all aspects of the chess
#   application, including game setup, moves, checks, and draws.
#   Reason: A thorough test plan ensures that all critical components of the
#           application are tested.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a structured testing approach, such as black-box testing, to ensure
#           that the application's functionality is thoroughly verified.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Create test cases for each scenario, including valid and invalid inputs, to
#   ensure that the application behaves correctly in different situations.
#   Reason: Test cases help to identify specific bugs and inconsistencies in the
#           application.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a testing framework, such as JUnit or PyUnit, to create and execute
#           test cases.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Execute the test cases and record the results, including any failures or
#   errors.
#   Reason: Executing test cases helps to identify bugs and inconsistencies in the
#           application.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use a testing framework to execute test cases and report results.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Analyze the test results to identify bugs and inconsistencies, and prioritize
#   them for fixing.
#   Reason: Analyzing test results helps to identify the most critical issues that need
#           to be addressed.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a bug tracking system, such as JIRA or Bugzilla, to prioritize and
#           track bugs.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Fix the identified bugs and inconsistencies, and re-run the test cases to
#   ensure that the issues are resolved.
#   Reason: Fixing bugs and inconsistencies ensures that the application is stable and
#           functions correctly.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a debugging tool, such as a debugger or print statements, to identify
#           and fix the root cause of the issue.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Generate a test summary report that includes the test results, bugs
#   identified, and recommendations for future improvements.
#   Reason: A test summary report provides a comprehensive overview of the testing
#           process and results.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use a reporting tool, such as a spreadsheet or document template, to
#           generate the test summary report.
# -- END PRD --



class IntegrateChessEngineOutput(BaseModel):
    """Pydantic model for integrate_chess_engine node outputs."""
    integration_status: bool = Field(..., description="Whether the integration was successful")
    chess_engine_used: str = Field(..., description="The name of the chess engine used for integration")
    issues_encountered: List[str] = Field(..., description="List of issues encountered during integration")
    verification_result: bool = Field(..., description="Whether the verification of chess moves and rules was successful")


class AddUserInterfaceOutput(BaseModel):
    """Pydantic model for add_user_interface node outputs."""
    ui_components: List[str] = Field(..., description="List of UI components such as buttons, menus, and tooltips.")
    layout_description: str = Field(..., description="Brief textual description of the overall UI layout.")
    validation_passed: bool = Field(..., description="Whether the UI design meets UX guidelines.")
    accessibility_score: int = Field(..., description="Accessibility score ranging from 0 (poor) to 100 (excellent).")
    user_feedback_summary: str = Field(..., description="Summary of user feedback on the UI design.")


class TestChessApplicationOutput(BaseModel):
    """Pydantic model for test_chess_application node outputs."""
    test_passed: bool = Field(..., description="True if all tests pass without critical failures; otherwise false.")
    total_tests_run: int = Field(..., description="Total number of individual test cases executed.")
    failed_test_names: List[str] = Field(..., description="List of names or identifiers of test cases that failed.")
    bug_count: int = Field(..., description="Number of bugs or inconsistencies discovered during testing.")
    test_summary: str = Field(..., description="Brief textual summary of testing results, including key findings and recommendations.")


def test_chess_application(integrate_chess_engine_input: IntegrateChessEngineOutput, add_user_interface_input: AddUserInterfaceOutput, **kwargs) -> TestChessApplicationOutput:
    """Verify the correct functioning of the chess application.

    Args:
        integrate_chess_engine_input: Input from the 'integrate_chess_engine' node.
        add_user_interface_input: Input from the 'add_user_interface' node.
        **kwargs: Additional keyword arguments.

    Returns:
        TestChessApplicationOutput: Object containing outputs for this node.
    """
    # Develop comprehensive test plan covering all aspects of chess application
    test_plan: List[str] = create_comprehensive_test_plan(
        engine_status=integrate_chess_engine_input.integration_status,
        ui_components=add_user_interface_input.ui_components
    )
    
    # Create test cases for each scenario including valid and invalid inputs
    test_cases: List[dict] = generate_test_cases(
        test_plan=test_plan,
        engine_name=integrate_chess_engine_input.chess_engine_used,
        ui_validation=add_user_interface_input.validation_passed
    )
    
    # Execute test cases and record results
    test_results: dict = execute_test_cases(
        test_cases=test_cases,
        engine_verification=integrate_chess_engine_input.verification_result
    )
    
    # Analyze test results to identify bugs and inconsistencies
    bug_analysis: dict = analyze_test_results(
        results=test_results,
        engine_issues=integrate_chess_engine_input.issues_encountered
    )
    
    # Fix identified bugs and re-run failed tests
    fixed_results: dict = fix_bugs_and_retest(
        bug_analysis=bug_analysis,
        original_results=test_results
    )
    
    # Generate test summary report
    summary_report: str = generate_test_summary_report(
        results=fixed_results,
        bugs_found=bug_analysis,
        ui_accessibility_score=add_user_interface_input.accessibility_score
    )
    
    # Extract final metrics for output
    final_test_status: bool = determine_overall_test_status(results=fixed_results)
    total_tests: int = len(test_cases)
    failed_tests: List[str] = extract_failed_test_names(results=fixed_results)
    total_bugs: int = count_total_bugs(bug_analysis=bug_analysis)
    
    return TestChessApplicationOutput(
        test_passed=final_test_status,
        total_tests_run=total_tests,
        failed_test_names=failed_tests,
        bug_count=total_bugs,
        test_summary=summary_report
    )