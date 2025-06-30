class OPENAIMODEL:
      GPT_35='gpt-3.5-turbo'
      GPT_4o_MINI ='gpt-4.1-mini'
class TaskConfig:
      CHUNK_SIZE=12000
      CHUNK_OVERLAP=400
class SummaryConfig:
      FORBIDDEN_PROMPT="The website provided is not able to scrape due to the forbidden access."
      FORBIDDEN_CODE = "403"
      EMPTY_PROMPT = "We encountered an issue during the scraping process, and no data was returned from the requested website."
class MailConfig:
      SUCCESS_MAIL_SUBJECT="Your Custom Prompt is Ready!"
      SUCCESS_MAIL_BODY="Great news! Weam has successfully updated your saved prompt using the URL you provided."
      FAILURE_MAIL_SUBJECT="We encountered an issue while preparing the prompt."
      FAILURE_MAIL_BODY="Unfortunately, Weam was unable to update your saved prompt using the provided URL. We apologize for any inconvenience this may have caused."
class ANTHROPICMODEL:
      CLAUDE_SONNET_3_5='claude-3-5-sonnet-latest'