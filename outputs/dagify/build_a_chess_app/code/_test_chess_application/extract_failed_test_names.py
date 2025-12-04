# -- PRD --
# 1. BULLET: The shim function needs to parse the input test results string and identify
#   the failed test names.
#   Reason: The test results string contains information about the test execution,
#           including the names of failed tests.
#   Impact: The shim function will be able to extract the failed test names, which will
#           be used to generate a test summary report.
#   Complexity: MEDIUM
#   Method: The shim function can use regular expressions or string parsing techniques
#           to extract the failed test names from the input string.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: The shim function needs to handle different formats of the input test results
#   string.
#   Reason: The input test results string may have different formats depending on the
#           test framework used.
#   Impact: The shim function will be able to handle different formats of the input
#           test results string, making it more robust.
#   Complexity: HIGH
#   Method: The shim function can use machine learning or natural language processing
#           techniques to identify the failed test names in different
#           formats.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: The shim function needs to return a list of failed test names.
#   Reason: The test summary report requires a list of failed test names.
#   Impact: The shim function will be able to provide the required information for the
#           test summary report.
#   Complexity: LOW
#   Method: The shim function can simply return a list of failed test names in the
#           required format.
# -- END PRD --

from typing import List


def extract_failed_test_names(results: str) -> List[str]:
    """
    Extracts a list of failed test names from the test results.

    Args:
        results: Input parameter of type str

    Returns:
        List[str]: Output of type List[str]
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
