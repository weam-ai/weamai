# Define a custom output parser
from langchain_core.output_parsers import BaseOutputParser
from src.chatflow_langchain.service.gemini.title.utils import remove_all_quotes,remove_title_and_colon
import re
class TitleOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        # Assuming the generated title is the first line of the output
        try:
            text=text.replace("title:","").strip()
            text =text.replace("title","").strip()
            text= remove_all_quotes(text)
            text=remove_title_and_colon(text)
            text = re.sub(r"json\s*[{:\n]*", "", text).strip()  # Remove "json", "{", ":", and newlines
            text = re.sub(r"\n?}$", "", text)
        except Exception as e:
            text="New Chat"
        return text