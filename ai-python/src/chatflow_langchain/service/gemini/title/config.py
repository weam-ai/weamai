class REFORMED_QUERY:
      QUERY_LIMIT_CHECK=5000
      REFORMED_QUERY_LIMIT=5000
class QUOTES:
      UNWANTED_QUOTES =["'''", '"""', '"', "'", '`','’', '‘','“','‘']

class GEMINIMODEL:
      gemini_1_5_flash_8b='gemini-2.0-flash'
class DEFAULT_TITLES:
    TITLES = {
        "NotFoundError": [
          "Connection Not Established",
          "Unable to Locate Server",
          "Connection Attempt Unsuccessful"
        ],
        "RateLimitError": [
          "Limit Reached",
          "Request Threshold Met"
        ],
        "APIStatusError": [
          "Service Status Check",
          "Service Response Pending"
        ],
        "LengthFinishReasonError": [
          "Request Length Exceeded Limit",
          "Request Size Beyond Limit",
          "Request Concluded Due to Length"
        ],
        "ContentFilterFinishReasonError": [
          "Content Filter Applied",
          "Request Screened for Content",
          "Request Restricted by Content Filter"
        ],
        "APITimeoutError": [
          "Connection Timing Out",
          "Response Pending Beyond Expected Time",
          "Request Time Threshold Reached"
        ],
        "APIConnectionError": [
          "Connection Attempt in Progress",
          "API Connection Pending",
          "Attempting to Reach the Server"
        ],
        "AuthenticationError": [
          "Authentication Required",
          "Identity Verification Needed",
          "Unable to Verify Identity",
          "Access Requires Authentication"
        ],
        "PermissionDeniedError": [
          "Access Not Granted",
          "Authorization Needed",
          "Insufficient Permissions",
          "Access Restricted",
          "Operation Requires Elevated Access"
        ],
        "APIError": [
          "Service Encountered an Issue",
          "Unexpected API Behavior",
          "API Encountered an Unexpected Condition",
          "Service Interaction Interrupted",
          "Anomaly Detected in API Response"
        ],
        "AnthropicError": [
          "Anthropic Service Encountered an Issue",
          "Unexpected Response from Anthropic API",
          "Issue in Communication with Anthropic",
          "Anthropic Request Could Not Be Processed",
          "Issue Detected in Anthropic Service",
          "Anthropic API Interaction Interrupted",
          "Service Behavior Requires Attention",
          "Unanticipated Outcome from Anthropic API",
          "Processing Error in Anthropic Service",
          "Anthropic Service Unavailable"
        ],
        "ResourceExhausted": [
          "Maximizing Resource Efficiency",
          "Resource Management in Progress",
          "Resource Optimization Underway",
          "Optimizing Resource Allocation",
          "Balancing Resource Load",
          "Resource Usage Over load"
        ],
        "GoogleAPICallError": [
          "Connecting to Google Services",
          "Synchronizing with Google for Better Access",
          "Establishing a Secure Link",
          "Synchronizing with Google API",
          "Preparing to Access Google Services"
        ],
        "GoogleAPIError": [
          "Enhancing Google Service Experience",
          "Refining Google API Integration",
          "Improving Google API Connectivity",
          "Refining Service Communication",
          "Upgrading Google Service Interaction"
        ],
        "GoogleGenerativeAIError": [
          "Crafting Tailored AI Responses",
          "Enhancing AI-Driven Experience",
          "Refining Generative AI Output",
          "Polishing AI-Generated Content"
        ],
        "default": [
            "Oops! There's a Glitch",
            "Whoops! Something's Off",
            "Oops! We Need a Moment",
            "Wait Up! Just a Moment",
            "Oops! Technical Hiccup",
            "Oops! We're on the Case"
        ]
    }