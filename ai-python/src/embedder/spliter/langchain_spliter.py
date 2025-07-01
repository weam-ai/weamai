from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.embedder.config import SpliterConfig
from langchain_text_splitters.base import TextSplitter
from typing import List
from src.embedder.spliter.config import ExcelConfigs

custom_text_splitter = RecursiveCharacterTextSplitter(
    # Set custom chunk size
    chunk_size = SpliterConfig.CHUNK_SIZE,
    chunk_overlap  = SpliterConfig.CHUNK_OVERLAP,
    # Use length of the text as the size measure
    length_function = len,
    # Use only "\n\n" as the separator
    separators=["\n\n", "\n", " ", ""]
)

class ExcelTextSplitter(TextSplitter):
    def __init__(self):
        pass
    def split_text(self, text: str) -> List[str]:
        chunks = [text[i:i + ExcelConfigs.CHUNK_SIZE] for i in range(0, len(text), ExcelConfigs.CHUNK_SIZE)]

        return chunks
    
excel_custom_splitter = ExcelTextSplitter()
spliter_map={
    "pdf":custom_text_splitter,
    "doc":custom_text_splitter,
    "docx":custom_text_splitter,
    "txt":custom_text_splitter,
    "text":custom_text_splitter,
    "csv":excel_custom_splitter,
    "xlsx":excel_custom_splitter,
    "xls":excel_custom_splitter,
    "eml":custom_text_splitter,
    "php":excel_custom_splitter,
    "js":excel_custom_splitter,
    "css":excel_custom_splitter,
    "html":excel_custom_splitter,
    "htm":excel_custom_splitter,
    "sql":excel_custom_splitter,
}