class OPENAIMODEL:
      GPT_35='gpt-3.5-turbo'
      GPT_4o_MINI ='gpt-4.1-mini'
      GPT_4o="gpt-4.1"
class REFORMED_QUERY:
      QUERY_LIMIT_CHECK=5000
      REFORMED_QUERY_LIMIT=5000
class QUOTES:
      UNWANTED_QUOTES =["'''", '"""', '"', "'", '`','’', '‘','“','‘']

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
      "default": [
            "Oops! There's a Glitch",
            "Whoops! Something's Off",
            "Oops! We Need a Moment",
            "Wait Up! Just a Moment",
            "Oops! Technical Hiccup",
            "Oops! We're on the Case"
      ]
    }