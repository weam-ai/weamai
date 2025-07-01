class OPENAIMODEL:
      GPT_35='gpt-3.5-turbo'
      GPT_4o_MINI ='gpt-4.1-mini'
class REFORMED_QUERY:
      QUERY_LIMIT_CHECK=5000
      REFORMED_QUERY_LIMIT=5000
class QUOTES:
      UNWANTED_QUOTES =["'''", '"""', '"', "'", '`','’', '‘','“','‘']

class ANTHROPICMODEL:
      claude_sonnet_3_5='claude-3-5-sonnet-latest'
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
        "default": [
            "Oops! There's a Glitch",
            "Whoops! Something's Off",
            "Oops! We Need a Moment",
            "Wait Up! Just a Moment",
            "Oops! Technical Hiccup",
            "Oops! We're on the Case"
        ]
    }