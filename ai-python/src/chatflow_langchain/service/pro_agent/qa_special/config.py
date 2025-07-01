class ChatHistoryConfig:
    MAX_TOKEN_LIMIT = 10000
    TOP_K = 18

class BatchConfig:
    BATCH_SIZE = 18
    CHECKLIST_PATH="./src/chatflow_langchain/service/pro_agent/qa_special/data/checklist.json"
    PAGESPEED_PATH="./src/chatflow_langchain/service/pro_agent/qa_special/data/pageSpeedChecklist.json"
    BATCH_TOKEN_LIMIT = 9_00_000
    MAX_SOURCE_LIMIT = 1_000_000
  