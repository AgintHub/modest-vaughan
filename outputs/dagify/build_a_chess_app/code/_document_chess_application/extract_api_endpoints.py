# -- PRD --
# 1. BULLET: The shim function needs to parse the API documentation to identify and
#   extract API endpoints.
#   Reason: The API endpoints are required for further processing and documentation
#           purposes.
#   Impact: Correct extraction of API endpoints will ensure accurate documentation and
#           usage of the API.
#   Complexity: MEDIUM
#   Method: Use regular expressions or a parsing library to identify patterns that
#           represent API endpoints in the documentation.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: The shim function should handle various formats of API documentation.
#   Reason: API documentation may come in different formats (e.g., JSON, YAML,
#           Markdown), and the shim needs to be able to handle them.
#   Impact: Support for multiple formats will increase the versatility and usability of
#           the shim function.
#   Complexity: HIGH
#   Method: Implement format detection and use format-specific parsers or converters to
#           standardize the documentation before extraction.
# -- END PRD --

from typing import List


def extract_api_endpoints(api_docs: str) -> List[str]:
    """
    Extracts a list of API endpoints from the provided API documentation.

    Args:
        api_docs: Input parameter of type str

    Returns:
        List[str]: Output of type List[str]
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
