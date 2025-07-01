from src.content_extraction.text.extractor_base import TextExtractor
from PyPDF2 import PdfReader
import xlrd
xlrd.__version__ = "2.0.1" 
import pandas as pd
from tabulate import tabulate
from typing import Union, List
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
class OldExcelExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from a PDF content, can return either all text at once or page-by-page."""
        
# Load the Excel file
        # Create an ExcelFile object
        excel = pd.ExcelFile(self.content)

        # Initialize an empty string to hold all Markdown tables
        all_tables = ""

        # Loop through all sheets
        for sheet_name in excel.sheet_names:
            
            # Read the sheet into a DataFrame
            df = excel.parse(sheet_name)
            df = df.dropna(axis=1, how="all")  # Drop columns with all NaN values
            df = df.fillna(value=" ")  # Replace NaN with spaces
            
            # Convert the DataFrame to a Markdown table
            markdown_table = tabulate(df,tablefmt="pipe")
            
            # Add a section header and the table to the output
            all_tables += f"### Sheet: {sheet_name}\n"  # Add a header for the sheet
            all_tables += markdown_table  # Add the table and spacing
            

        return all_tables


class OldS3ExcelExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from a PDF content, can return either all text at once or page-by-page."""

        # Create an ExcelFile object
        excel = pd.ExcelFile(self.content)

        # Initialize an empty string to hold all Markdown tables
        all_tables = ""

        # Loop through all sheets
        for sheet_name in excel.sheet_names:
            
            # Read the sheet into a DataFrame
            df = excel.parse(sheet_name)
            df = df.dropna(axis=1, how="all")  # Drop columns with all NaN values
            df = df.fillna(value=" ")  # Replace NaN with spaces
            
            # Convert the DataFrame to a Markdown table
            markdown_table = tabulate(df,tablefmt="pipe")
            
            # Add a section header and the table to the output
            all_tables += f"### Sheet: {sheet_name}\n"  # Add a header for the sheet
            all_tables += markdown_table  # Add the table and spacing
            
        return all_tables
    
class OldLSTACKExcelExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from a PDF content, can return either all text at once or page-by-page."""

        # Create an ExcelFile object
        excel = pd.ExcelFile(self.content)

        # Initialize an empty string to hold all Markdown tables
        all_tables = ""

        # Loop through all sheets
        for sheet_name in excel.sheet_names:
            
            # Read the sheet into a DataFrame
            df = excel.parse(sheet_name)
            df = df.dropna(axis=1, how="all")  # Drop columns with all NaN values
            df = df.fillna(value=" ")  # Replace NaN with spaces
            
            # Convert the DataFrame to a Markdown table
            markdown_table = tabulate(df,tablefmt="pipe")
            
            # Add a section header and the table to the output
            all_tables += f"### Sheet: {sheet_name}\n"  # Add a header for the sheet
            all_tables += markdown_table  # Add the table and spacing
            
        return all_tables
    
class OldMINIOExcelExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from a PDF content, can return either all text at once or page-by-page."""

        # Create an ExcelFile object
        excel = pd.ExcelFile(self.content)

        # Initialize an empty string to hold all Markdown tables
        all_tables = ""

        # Loop through all sheets
        for sheet_name in excel.sheet_names:
            
            # Read the sheet into a DataFrame
            df = excel.parse(sheet_name)
            df = df.dropna(axis=1, how="all")  # Drop columns with all NaN values
            df = df.fillna(value=" ")  # Replace NaN with spaces
            
            # Convert the DataFrame to a Markdown table
            markdown_table = tabulate(df,tablefmt="pipe")
            
            # Add a section header and the table to the output
            all_tables += f"### Sheet: {sheet_name}\n"  # Add a header for the sheet
            all_tables += markdown_table  # Add the table and spacing
            
        return all_tables