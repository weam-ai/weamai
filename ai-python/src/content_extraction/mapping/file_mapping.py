from dotenv import load_dotenv
from src.content_extraction.text.extractor_base import TextExtractor
from src.content_extraction.text.doc_extractor import *
from src.content_extraction.text.pdf_extractor import *
from src.content_extraction.text.textfile_extractor import *
from src.content_extraction.text.excel_extractor import * 
from src.content_extraction.text.csv_extractor import *
from src.content_extraction.text.old_excel_extractor import *
from src.content_extraction.text.eml_extractor import *
from src.content_extraction.text.php_extractor import *
from src.content_extraction.text.javascript_extractor import *
from src.content_extraction.text.css_extractor import *
from src.content_extraction.text.html_extractor import *
from src.content_extraction.text.sql_extractor import *
from src.content_extraction.text.py_extractor import *
from src.content_extraction.text.json_extractor import *

from src.logger.default_logger import logger

load_dotenv()

# Define the default mapping of file types to their default extractors
default_extractors = {
    "s3_pdf": S3PDFTextExtractor,
    "s3_docx": S3DOCXTextExtractor,
    "s3_doc":S3DOCTextExtractor,
    "s3_text": S3TextFileExtractor,
    "s3_txt":S3TextFileExtractor,
    "s3_xlsx": S3ExcelExtractor,
    "s3_csv": S3CSVExtractor,
    "s3_xls": OldS3ExcelExtractor,
    "s3_eml": S3EMLExtractor,
    "s3_php": S3PHPExtractor,
    "s3_js": S3JSExtractor,
    "s3_css": S3CSSExtractor,
    "s3_html": S3HTMLExtractor,
    "s3_htm": S3HTMLExtractor,
    "s3_sql": S3SQLExtractor,
    "s3_py": S3PythonExtractor,
    "s3_json": S3JSONExtractor,

    "pdf": PDFTextExtractor,
    "doc": DOCTextExtractor,
    "docx": DOCXTextExtractor,
    "text": TextFileExtractor,
    "txt":TextFileExtractor,
    'xlsx': ExcelExtractor,
    'csv': CSVExtractor,
    'xls': OldExcelExtractor,
    'eml': EMLExtractor,
    "php": PHPExtractor,
    "js": JSExtractor,
    "css": CSSExtractor,
    "html": HTMLExtractor,
    "htm": HTMLExtractor,
    "sql": SQLExtractor,
    "py": PythonExtractor,
    "json": JSONExtractor,

    "localstack_pdf": LSTACKPDFTextExtractor,
    "localstack_docx": LSTACKDOCXTextExtractor,
    "localstack_doc": LSTACKDOCTextExtractor,
    "localstack_text": LSTACKTextFileExtractor,
    "localstack_txt": LSTACKTextFileExtractor,
    "localstack_xlsx": LSTACKExcelExtractor,
    "localstack_csv": LSTACKCSVExtractor,
    "localstack_xls": OldLSTACKExcelExtractor,
    "localstack_eml": LSTACKEMLExtractor,
    "localstack_php": LSTACKPHPExtractor,
    "localstack_js": LSTACKJSExtractor,
    "localstack_css": LSTACKCSSExtractor,
    "localstack_html": LSTACKHTMLExtractor,
    "localstack_htm": LSTACKHTMLExtractor,
    "localstack_sql": LSTACKSQLExtractor,
    "localstack_py": LSTACKPythonExtractor,
    "localstack_json": LSTACKJSONExtractor,

    "minio_pdf":MINIOPDFTextExtractor,
    "minio_docx": MINIODOCXTextExtractor,
    "minio_doc": MINIODOCTextExtractor,
    "minio_text": MINIOTextFileExtractor,
    "minio_txt": MINIOTextFileExtractor,
    "minio_xlsx": MINIOExcelExtractor,
    "minio_csv": MINIOCSVExtractor,
    "minio_xls": OldMINIOExcelExtractor,
    "minio_eml": MINIOEMLExtractor,
    "minio_php": MINIOPHPExtractor,
    "minio_js": MINIOJSExtractor,
    "minio_css": MINIOCSSExtractor,
    "minio_html": MINIOHTMLExtractor,
    "minio_htm": MINIOHTMLExtractor,
    "minio_sql": MINIOSQLExtractor,
    "minio_py": MINIOPythonExtractor,
    "minio_json": MINIOJSONExtractor,

}

# Define the default file_map structure
default_file_map = lambda file_type: {
    "url": {
        "s3_url": default_extractors[f"s3_{file_type}"],  # Placeholder for actual S3 extractor
        "public_url": default_extractors[file_type],
        "localstack": default_extractors[f"localstack_{file_type}"],
        "minio":default_extractors[f"minio_{file_type}"]

    },
    "local_file": default_extractors[file_type]
}

def is_url_type(source:str='url')->bool:
    # Check if the 'file_map' corresponds to a 'url_type'

    if 'url' in source:
        return True
    elif 'localstack' in source or 'minio' in source:
        return True
    elif 'file' in source:
        return False
    else:
        logger.error(f"Invalid source type provided: {source}")
        raise ValueError("Invalid file type or map configuration")



def get_extractor(file_type: str, source: str, extractors: dict = default_extractors, file_map_creator: callable = default_file_map):
    # Generate the file_map using the provided file_map_creator function
    extractor = None
 
    
    try:
        # Generate the file_map using the provided file_map_creator function
        file_map = file_map_creator(file_type)
        logger.info(f"File map generated for file type '{file_type}': {file_map}")

    except Exception as e:
        logger.error(f"Error creating file map for file type '{file_type}': {e}")
        # Handle any exception raised by file_map_creator or printing file_type
        raise Exception(f"Error in file_map creation or printing file type: {e}")

    try:
        # Check if the source type is from a URL and handle accordingly
        if source in file_map['url']:
            # For URL sources, fetch the appropriate extractor from the file_map
            extractor_info = file_map['url'][source]
            # If the extractor info turns out to be a class name in string form, fetch the class from globals
            extractor = globals().get(extractor_info, extractors[file_type]) if isinstance(extractor_info, TextExtractor) else extractor_info
        elif source == "local_file":
            # For local files, directly use the extractor based on the file type
            extractor = extractors[file_type]
        else:
            logger.error(f"Unsupported source type '{source}'")
            # Raise an error if an unsupported source is provided
            raise ValueError(f"Unsupported source type: {source}")
        
        logger.info(f"Extractor selected: {extractor} for file type '{file_type}' and source '{source}'")

    except KeyError as e:
        # Handle the case where a key does not exist in the dictionary
        raise KeyError(f"Missing key in file map or extractors: {e}")

    # Ensure the selected extractor is a subclass of TextExtractor for consistency and safety
    if not issubclass(extractor, TextExtractor):
        logger.error(f"Invalid extractor type '{extractor}' for file type '{file_type}'")
        raise TypeError(f"The selected extractor is not a valid TextExtractor for file type: {file_type}")
    
    return extractor


