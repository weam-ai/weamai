from src.content_extraction.text.extractor_base import TextExtractor
from PyPDF2 import PdfReader
import pandas as pd
from tabulate import tabulate
from typing import Union, List
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
class CSVExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """
        Extracts text from a CSV content and converts it to a Markdown table format.
        Args:
            page_wise (bool): This parameter is not used in the current implementation. Defaults to False.
        Returns:
            Union[str, List[str]]: A string containing the Markdown table representation of the CSV content.
        """
   
        df = pd.read_csv(self.content)

        all_tables = ""
            

        df = df.dropna(axis=1, how="all")  # Drop columns with all NaN values
        df = df.fillna(value=" ")  # Replace NaN with spaces
        # Convert the DataFrame to a Markdown table
        markdown_table = tabulate(df,tablefmt="pipe")
        all_tables += markdown_table  # Add the table and spacing
            

        return all_tables


class S3CSVExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """
        Extracts text from a CSV content, returning it as a Markdown table.
        Args:
            page_wise (bool): This parameter is not used in the current implementation. Defaults to False.
        Returns:
            Union[str, List[str]]: A string containing the CSV content formatted as a Markdown table.
        """
        """Extracts text from a PDF content, can return either all text at once or page-by-page."""

        df = pd.read_csv(self.content,encoding_errors="ignore")

        all_tables = ""
            

        df = df.dropna(axis=1, how="all")  # Drop columns with all NaN values
        df = df.fillna(value=" ")  # Replace NaN with spaces
        # Convert the DataFrame to a Markdown table
        markdown_table = tabulate(df,tablefmt="pipe")
        all_tables += markdown_table  # Add the table and spacing
            
            
        return all_tables

class LSTACKCSVExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """
        Extracts text from a CSV content, returning it as a Markdown table.
        Args:
            page_wise (bool): This parameter is not used in the current implementation. Defaults to False.
        Returns:
            Union[str, List[str]]: A string containing the CSV content formatted as a Markdown table.
        """
        """Extracts text from a PDF content, can return either all text at once or page-by-page."""

        df = pd.read_csv(self.content,encoding_errors="ignore")

        all_tables = ""
            

        df = df.dropna(axis=1, how="all")  # Drop columns with all NaN values
        df = df.fillna(value=" ")  # Replace NaN with spaces
        # Convert the DataFrame to a Markdown table
        markdown_table = tabulate(df,tablefmt="pipe")
        all_tables += markdown_table  # Add the table and spacing
            
            
        return all_tables

class MINIOCSVExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """
        Extracts text from a CSV content, returning it as a Markdown table.
        Args:
            page_wise (bool): This parameter is not used in the current implementation. Defaults to False.
        Returns:
            Union[str, List[str]]: A string containing the CSV content formatted as a Markdown table.
        """
        """Extracts text from a PDF content, can return either all text at once or page-by-page."""

        df = pd.read_csv(self.content,encoding_errors="ignore")

        all_tables = ""
            

        df = df.dropna(axis=1, how="all")  # Drop columns with all NaN values
        df = df.fillna(value=" ")  # Replace NaN with spaces
        # Convert the DataFrame to a Markdown table
        markdown_table = tabulate(df,tablefmt="pipe")
        all_tables += markdown_table  # Add the table and spacing
            
            
        return all_tables