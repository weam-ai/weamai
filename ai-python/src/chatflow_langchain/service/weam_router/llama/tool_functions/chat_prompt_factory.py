from typing  import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from src.prompts.langchain.llama.tool_selection_prompt import tool_selection_prompt
from src.logger.default_logger import logger

def create_chat_prompt(
    history=None,
    general_system_template=tool_selection_prompt, 
    general_user_template=None, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    history.insert(0, SystemMessage(general_system_template))
    if additional_prompt:
        general_user_template=additional_prompt+general_user_template
    
    history.append(HumanMessage(general_user_template))
    
    logger.info("Created chat prompt document.")
    return history

