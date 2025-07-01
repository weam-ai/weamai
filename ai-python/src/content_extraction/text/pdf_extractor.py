from src.content_extraction.text.extractor_base import TextExtractor
from PyPDF2 import PdfReader
from typing import Union, List
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
import time
from src.logger.default_logger import logger

class PDFTextExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from a PDF content, can return either all text at once or page-by-page."""
        start_time = time.time()  # Start timing

        pdf_reader = PdfReader(self.content)
        pages_text = [page.extract_text() if page.extract_text() else "" for page in pdf_reader.pages]

        if page_wise:
            result = pages_text  # Return list of page-wise texts
        else:
            result = ' '.join(pages_text)  # Return single string for all text

        end_time = time.time()  # End timing
        logger.info(
            f"Time taken to extract text from PDF: {end_time - start_time} seconds",
            extra={"tags": {"method": "PDFTextExtractor.extract_text"}}
        )
        return result


class S3PDFTextExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from PDF, appending hyperlinks immediately after the linked word."""
        import pymupdf
       
        start_time = time.time()
        doc = pymupdf.open(stream=self.content, filetype="pdf")
        result_pages = []

        for page in doc:
            words = page.get_text("words")
            links = page.get_links()
            
            page_text = []
            
            for word in words:
                word_rect = pymupdf.Rect(word[:4])
                text = word[4]
                
                # Check if this word has a hyperlink
                for link in links:
                    if 'uri' in link and word_rect.intersects(link['from']):
                        text = f"{text}({link['uri']})"
                        break
                
                
                page_text.append(text)
            result_pages.append(" ".join(page_text))



        doc.close()
        del doc
        end_time = time.time()
        logger.info(f"Time taken to extract text from PDF: {end_time - start_time} seconds",extra={"tags": {"method": "S3PDFTextExtractor.extract_text"}})
        return result_pages if page_wise else ' '.join(result_pages)
    






class LSTACKPDFTextExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from PDF, appending hyperlinks immediately after the linked word."""
        import pymupdf
       
        start_time = time.time()
        doc = pymupdf.open(stream=self.content, filetype="pdf")
        result_pages = []

        for page in doc:
            words = page.get_text("words")
            links = page.get_links()
            
            page_text = []
            
            for word in words:
                word_rect = pymupdf.Rect(word[:4])
                text = word[4]
                
                # Check if this word has a hyperlink
                for link in links:
                    if 'uri' in link and word_rect.intersects(link['from']):
                        text = f"{text}({link['uri']})"
                        break
                
                
                page_text.append(text)
            result_pages.append(" ".join(page_text))



        doc.close()
        del doc
        end_time = time.time()
        logger.info(f"Time taken to extract text from PDF: {end_time - start_time} seconds",extra={"tags": {"method": "LSTACKPDFTextExtractor.extract_text"}})
        return result_pages if page_wise else ' '.join(result_pages)
    

class MINIOPDFTextExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from PDF, appending hyperlinks immediately after the linked word."""
        import pymupdf
       
        start_time = time.time()
        doc = pymupdf.open(stream=self.content, filetype="pdf")
        result_pages = []

        for page in doc:
            words = page.get_text("words")
            links = page.get_links()
            
            page_text = []
            
            for word in words:
                word_rect = pymupdf.Rect(word[:4])
                text = word[4]
                
                # Check if this word has a hyperlink
                for link in links:
                    if 'uri' in link and word_rect.intersects(link['from']):
                        text = f"{text}({link['uri']})"
                        break
                
                
                page_text.append(text)
            result_pages.append(" ".join(page_text))



        doc.close()
        del doc
        end_time = time.time()
        logger.info(f"Time taken to extract text from PDF: {end_time - start_time} seconds",extra={"tags": {"method": "MINIOPDFTextExtractor.extract_text"}})
        return result_pages if page_wise else ' '.join(result_pages)