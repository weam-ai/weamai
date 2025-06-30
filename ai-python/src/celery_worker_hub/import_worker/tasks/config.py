class SUM_MEMORY_LIMIT:
    MAX_TOKEN_LIMIT = 10000

class ImportChatConfig:
    SUCCESS_TITLE = "Chat Import Successful"
    SUCCESS_BODY = "{count} chats have been successfully imported from {source} into the {brain_name} Brain.Check them out now!"
    FAILURE_TITLE = "Chat Import Failed"
    FAILURE_BODY = ("Your selected source ({source}) and the uploaded file do not match. "
        "Please verify that you have selected the correct source code and uploaded the appropriate file for '{brain_name}' Brain, then try again.")