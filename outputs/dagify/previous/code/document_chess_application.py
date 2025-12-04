from ._document_chess_application.analyze_chess_engine_features import analyze_chess_engine_features
from ._document_chess_application.analyze_test_results import analyze_test_results
from ._document_chess_application.create_user_manual_outline import create_user_manual_outline
from ._document_chess_application.write_user_manual_content import write_user_manual_content
from ._document_chess_application.create_api_documentation import create_api_documentation
from ._document_chess_application.extract_api_endpoints import extract_api_endpoints
from ._document_chess_application.review_documentation import review_documentation
from ._document_chess_application.generate_version_identifier import generate_version_identifier
from ._document_chess_application.publish_documentation import publish_documentation

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Review the output from the integrate_chess_engine node to understand the
#   chess engine used and its key features.
#   Reason: This step ensures that the documentation is accurate and relevant to the
#           integrated chess engine.
#   Impact: LOW
#   Complexity: LOW
#   Method: Analyze the output from integrate_chess_engine, focusing on the chess
#           engine used and its features.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Review the output from the test_chess_application node to identify areas that
#   require detailed documentation.
#   Reason: This step helps to prioritize documentation efforts and ensure that
#           critical areas are covered.
#   Impact: LOW
#   Complexity: LOW
#   Method: Examine the test results from test_chess_application, noting any issues or
#           areas that require clarification.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Create an outline for the user manual, including sections for Setup, Rules,
#   Features, and FAQ.
#   Reason: A well-structured outline ensures that the user manual is comprehensive and
#           easy to follow.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a standard documentation template and include sections for game setup,
#           rules, features, and frequently asked questions.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Write detailed content for each section of the user manual, using clear and
#   concise language.
#   Reason: Clear documentation is essential for users to understand and effectively
#           use the chess application.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Use a collaborative documentation tool and involve subject matter experts
#           to ensure accuracy and clarity.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Create API documentation that outlines the available functions and methods,
#   including request and response formats.
#   Reason: Accurate API documentation is crucial for developers to integrate with the
#           chess application.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Use API documentation tools and follow standard API documentation
#           guidelines, such as OpenAPI or Swagger.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Review and revise the user manual and API documentation to ensure accuracy,
#   completeness, and consistency.
#   Reason: Thorough review and revision ensure that the documentation is reliable and
#           effective.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Conduct a thorough review of the documentation, involving subject matter
#           experts and stakeholders to validate accuracy and completeness.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Publish the user manual and API documentation in a accessible format, such as
#   a web portal or documentation repository.
#   Reason: Accessible documentation ensures that users and developers can easily find
#           and use the information they need.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use a documentation hosting platform, such as GitHub Pages or Read the
#           Docs, to publish and share the documentation.
# -- END PRD --



class TestChessApplicationOutput(BaseModel):
    """Pydantic model for test_chess_application node outputs."""
    test_passed: bool = Field(..., description="True if all tests pass without critical failures; otherwise false.")
    total_tests_run: int = Field(..., description="Total number of individual test cases executed.")
    failed_test_names: List[str] = Field(..., description="List of names or identifiers of test cases that failed.")
    bug_count: int = Field(..., description="Number of bugs or inconsistencies discovered during testing.")
    test_summary: str = Field(..., description="Brief textual summary of testing results, including key findings and recommendations.")


class IntegrateChessEngineOutput(BaseModel):
    """Pydantic model for integrate_chess_engine node outputs."""
    integration_status: bool = Field(..., description="Whether the integration was successful")
    chess_engine_used: str = Field(..., description="The name of the chess engine used for integration")
    issues_encountered: List[str] = Field(..., description="List of issues encountered during integration")
    verification_result: bool = Field(..., description="Whether the verification of chess moves and rules was successful")


class DocumentChessApplicationOutput(BaseModel):
    """Pydantic model for document_chess_application node outputs."""
    user_manual_sections: List[str] = Field(..., description="Sections included in the user manual, such as Setup, Rules, Features, FAQ.")
    api_endpoints: List[str] = Field(..., description="List of API endpoints with their HTTP methods.")
    manual_version: str = Field(..., description="Version identifier of the user manual.")
    api_version: str = Field(..., description="Version identifier of the API documentation.")
    is_manual_complete: bool = Field(..., description="Whether the user manual has been fully written.")
    is_api_documented: bool = Field(..., description="Whether the API documentation has been fully written.")


def document_chess_application(test_chess_application_input: TestChessApplicationOutput, integrate_chess_engine_input: IntegrateChessEngineOutput, **kwargs) -> DocumentChessApplicationOutput:
    """Create a comprehensive user manual and API documentation for the chess application.

    Args:
        test_chess_application_input: Input from the 'test_chess_application' node.
        integrate_chess_engine_input: Input from the 'integrate_chess_engine' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DocumentChessApplicationOutput: Object containing outputs for this node.
    """
    # Review chess engine output to understand features and capabilities
    engine_analysis: dict = analyze_chess_engine_features(
        engine_name=integrate_chess_engine_input.chess_engine_used,
        integration_status=integrate_chess_engine_input.integration_status,
        verification_result=integrate_chess_engine_input.verification_result
    )
    
    # Review test results to identify documentation priorities
    test_analysis: dict = analyze_test_results(
        test_passed=test_chess_application_input.test_passed,
        failed_tests=test_chess_application_input.failed_test_names,
        bug_count=test_chess_application_input.bug_count,
        test_summary=test_chess_application_input.test_summary
    )
    
    # Create user manual outline with standard sections
    manual_outline: List[str] = create_user_manual_outline(
        engine_features=engine_analysis,
        test_insights=test_analysis
    )
    
    # Write detailed content for each section of the user manual
    manual_content: dict = write_user_manual_content(
        outline=manual_outline,
        engine_info=engine_analysis,
        test_info=test_analysis
    )
    
    # Generate API documentation with endpoints and methods
    api_documentation: dict = create_api_documentation(
        chess_engine=integrate_chess_engine_input.chess_engine_used,
        engine_features=engine_analysis
    )
    
    # Extract API endpoints list from documentation
    api_endpoints_list: List[str] = extract_api_endpoints(api_docs=api_documentation)
    
    # Review and revise documentation for accuracy and completeness
    review_results: dict = review_documentation(
        manual_content=manual_content,
        api_docs=api_documentation,
        engine_analysis=engine_analysis
    )
    
    # Generate version identifiers for documentation
    manual_version: str = generate_version_identifier(doc_type="user_manual")
    api_version: str = generate_version_identifier(doc_type="api_documentation")
    
    # Publish documentation to accessible format
    publication_status: dict = publish_documentation(
        manual_content=manual_content,
        api_docs=api_documentation,
        manual_version=manual_version,
        api_version=api_version
    )
    
    # Determine completion status based on review and publication
    is_manual_complete: bool = review_results.get("manual_complete", False) and publication_status.get("manual_published", False)
    is_api_documented: bool = review_results.get("api_complete", False) and publication_status.get("api_published", False)
    
    return DocumentChessApplicationOutput(
        user_manual_sections=manual_outline,
        api_endpoints=api_endpoints_list,
        manual_version=manual_version,
        api_version=api_version,
        is_manual_complete=is_manual_complete,
        is_api_documented=is_api_documented
    )