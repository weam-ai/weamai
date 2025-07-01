from botocore.exceptions import NoCredentialsError
from bson import ObjectId
from src.aws.boto3_client import Boto3S3Client
from src.aws.localstack_client import LocalStackS3Client
from src.aws.minio_client import MinioClient
import pandas as pd
from src.logger.default_logger import logger
from fastapi import HTTPException, status
import requests
from bs4 import BeautifulSoup
import json
import os
import io
from src.aws.storageClient_service import ClientService
async def clean_list(items):
    seen = set()
    clean_items = []
    for item in items:
        item = item.strip()
        if item and item not in seen:
            clean_items.append(item)
            seen.add(item)
    clean_items = " ".join(clean_items)
    return clean_items

async def get_user_agents():
    """Function to return a list of user-agent strings and additional headers."""
    return [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4.1 Safari/605.1.15',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/89.0',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0; en-US; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        {
            'User-Agent': 'Opera/9.80 (Windows NT 6.0; U; en) Presto/2.12.388 Version/12.18',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Accept': 'text/html, application/xml;q=0.9, */*;q=0.8',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
    ]

async def web_scraping(url):
    try:
        user_agents = await get_user_agents()
        for headers in user_agents:
            html_content = requests.get(url, headers=headers, timeout=30)
            if html_content.status_code == 200:
                soup = BeautifulSoup(html_content.text, 'html.parser')
                print(f"Successfully fetched URL: {url} with User-Agent: {headers['User-Agent']}")
                # return soup
                break
            print(f"Received status code {html_content.status_code} for User-Agent: {headers['User-Agent']}")
        if html_content.status_code != 200:
            html_content.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL: {url} - {e}")


    try:
        lang = soup.html.get('lang')
   
    except Exception as e:
        print("Error extracting language for URL %s: %s", url, e)
        lang = None

    try:
        title = soup.title.string
    except Exception as e:
        print("Error extracting title for URL %s: %s", url, e)
        title = None

    try:
        meta = [f"{meta.get('name')}: {meta.get('content')}" for meta in soup.find_all('meta') if meta.get('name')]
 
    except Exception as e:
        print("Error extracting meta tags for URL %s: %s", url, e)
        meta = []

    try:
        img_tags = soup.find_all('img')
        image_list = []
        for img in img_tags:
            alt_text = img.get('alt', '')
            image_list.append(alt_text)
    except:
        print("Error extracting image information for URL %s: %s", url, e)
        image_list = []

    try:
        contacts = soup.find_all(
            ['address', 'a'], 
            string=lambda t: t and ('contact' in t.lower() or 'email' in t.lower() or 'phone' in t.lower())
        )
        contact_texts = [contact.get_text() for contact in contacts]
    except Exception as e:
        print("Error extracting contact information for URL %s: %s", url, e)
        contact_texts = []

    try:
        social_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(platform in href for platform in ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']):
                social_links.append(href)
  
    except Exception as e:
        print("Error extracting social media links for URL %s: %s", url, e)
        social_links = []

    try:
        nav_items = [nav.get_text() for nav in soup.find_all('nav')]
  
    except Exception as e:
        print("Error extracting navigation items for URL %s: %s", url, e)
        nav_items = []

    try:
        products = [prod.get_text() for prod in soup.find_all(['div', 'section'], class_=lambda x: x and 'product' in x.lower())]
  
    except Exception as e:
        print("Error extracting product information for URL %s: %s", url, e)
        products = []

    try:
        headings = [heading.get_text() for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    except Exception as e:
        print("Error extracting headings for URL %s: %s", url, e)
        headings = []

    try:
        footer = soup.body.find('footer')
        if footer:
            footer.extract()
        texts = [text.get_text() for text in soup.find_all('p')]
        filtered_texts = [text for text in texts if text.strip()]
      
    except Exception as e:
        print("Error extracting texts for URL %s: %s", url, e)
        filtered_texts = []

    # Footer
    try:
        footer_texts = []
        if footer:
            footer_texts = [text.get_text() for text in footer.find_all('p')]

    except Exception as e:
        print("Error extracting footer texts for URL %s: %s", url, e)
        footer_texts = []

    try:
        list_tags = soup.find_all(['ul', 'ol'])
        list_items = []
        for list_tag in list_tags:
            items = [li.get_text() for li in list_tag.find_all('li')]
            list_items.extend(items)
       
    except Exception as e:
        print("Error extracting list items for URL %s: %s", url, e)
        list_items = []

    page_analysis = {
        'language': lang,
        'title': title,
        'meta_tags': meta,
        'images':image_list,
        'contact_info': contact_texts,
        'social_links': social_links,
        'navigation': nav_items,
        'product_info': products,
        'headings': headings,
        'texts': filtered_texts,
        'footer': footer_texts,
        'lists': list_items
    }
    try:
        page_analysis['contact_info'] = await clean_list(page_analysis['contact_info'])
        page_analysis['social_links'] = await clean_list(page_analysis['social_links'])
        page_analysis['navigation'] = await clean_list(page_analysis['navigation'])
        page_analysis['product_info'] = await clean_list(page_analysis['product_info'])
        page_analysis['headings'] = await clean_list(page_analysis['headings'])
        page_analysis['texts'] = await clean_list(page_analysis['texts'])
        page_analysis['footer'] = await clean_list(page_analysis['footer'])
        page_analysis['lists'] = await clean_list(page_analysis['lists'])
        page_analysis['meta_tags'] = await clean_list(page_analysis['meta_tags'])
        page_analysis['images'] = await clean_list(page_analysis['images'])
        page_analysis = " ".join(f'{page}:{page_analysis[page]}' for page in page_analysis)
        
        # print("\ncompany summary :\n", company_summary)
        return page_analysis
        
    except Exception as e:
        print("Error cleaning or joining analysis data for URL %s: %s", url, e)
        return page_analysis

def parse_proposal_content(content):
    """Parse the OpenAI response into a dictionary"""
    try:
        # Clean the content string
        content = content.strip()
        # Remove any potential markdown code block markers
        content = content.replace("```json", "").replace("```", "")
        # Parse the JSON
        data = json.loads(content)
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing OpenAI response: {e}")
        print("Raw content received:", content)
        return None


class ProposalDocument:
    def __init__(self, doc):
        """Initialize with a docx Document object"""
        self.doc = doc

    def copy_formatting(self, source_run, target_run):
        """Copy formatting from source run to target run properly"""
        if source_run._element.rPr is None:
            return
        
        # Create new run properties if target doesn't have them
        if target_run._element.rPr is None:
            target_run._element.get_or_add_rPr()

        # Copy font properties directly
        target_run.font.name = source_run.font.name
        target_run.font.size = source_run.font.size
        target_run.font.bold = source_run.font.bold
        target_run.font.italic = source_run.font.italic
        target_run.font.underline = source_run.font.underline
        if source_run.font.color:
            target_run.font.color.rgb = source_run.font.color.rgb

    def replace_text_in_doc(self, placeholder, replacement):
        """Replace text while preserving formatting"""
        # Replace in paragraphs
        for paragraph in self.doc.paragraphs:
            if placeholder not in paragraph.text:
                continue

            # Store initial formatting
            format_run = None
            for run in paragraph.runs:
                if run.text.strip():
                    format_run = run
                    break

            if not format_run:
                continue

            # Get the full paragraph text and replace the placeholder
            full_text = paragraph.text
            new_text = full_text.replace(placeholder, str(replacement))

            # Clear the paragraph
            for run in paragraph.runs:
                run._element.getparent().remove(run._element)

            # Add the new text with preserved formatting
            new_run = paragraph.add_run(new_text)
            self.copy_formatting(format_run, new_run)

        # Replace in tables
        for table in self.doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if placeholder not in paragraph.text:
                            continue

                        # Store initial formatting
                        format_run = None
                        for run in paragraph.runs:
                            if run.text.strip():
                                format_run = run
                                break

                        if not format_run:
                            continue

                        # Get the full paragraph text and replace the placeholder
                        full_text = paragraph.text
                        new_text = full_text.replace(placeholder, str(replacement))

                        # Clear the paragraph
                        for run in paragraph.runs:
                            run._element.getparent().remove(run._element)

                        # Add the new text with preserved formatting
                        new_run = paragraph.add_run(new_text)
                        self.copy_formatting(format_run, new_run)

    def replace_placeholders(self, data):
        """Replace placeholders in the document with structured data"""
        # Add dollar sign to budget values before replacement
        # Project Overview replacements
        for key, value in data["project_overview"].items():
            self.replace_text_in_doc(f"{{{key}}}", str(value))

        # Debug print to check submission details


        # Explicitly handle userCompanyLocation first
        company_location = data["submission_details"].get("userCompanyLocation", "")

        self.replace_text_in_doc("{userCompanyLocation}", str(company_location))

        # Handle other submission details
        for key, value in data["submission_details"].items():
            if key != "userCompanyLocation":  # Skip as we already handled it
                self.replace_text_in_doc(f"{{{key}}}", str(value))


        # Company details replacements
        self.replace_text_in_doc("{userCompanySummary}", str(data["userCompanySummary"]))

        # Timeline replacements
        for key, value in data["timeline"].items():
            self.replace_text_in_doc(f"{{{key}}}", str(value))
        
        # Budget replacements
        for key, value in data["core_budget"].items():
            try:
                amount = float(str(value).replace('$', '').replace(',', ''))
                formatted_value = f"{amount:,.2f}"
            except (ValueError, AttributeError):
                formatted_value = value
            self.replace_text_in_doc(f"{{{key}}}", formatted_value)
        
        # Add-ons replacements
        for key, value in data["recommended_addons"].items():
            try:
                amount = float(str(value).replace('$', '').replace(',', ''))
                formatted_value = f"{amount:,.2f}"
            except (ValueError, AttributeError):
                formatted_value = value
            self.replace_text_in_doc(f"{{{key}}}", formatted_value)

        # Add total cost replacement
        for key, value in data["total_cost"].items():
            try:
                amount = float(str(value).replace('$', '').replace(',', ''))
                formatted_value = f"{amount:,.2f}"
            except (ValueError, AttributeError):
                formatted_value = value
            self.replace_text_in_doc(f"{{{key}}}", formatted_value)

async def upload_doc_to_s3(doc):
    """Uploads a Word document to an S3 bucket."""
    try:
        s3_folder = "web-proposal"
        filename = str(ObjectId()) + '.docx'  # Creates random file name
        s3_key = f"{s3_folder}/{filename}"
        doc_buffer = io.BytesIO()
        
        # Save the document to the in-memory buffer
        doc.save(doc_buffer)
        doc_buffer.seek(0)
        client_service = ClientService()
        s3_client = client_service.client_type.client
        bucket_name = client_service.client_type.bucket_name
        cdn_url = client_service.client_type.cdn_url
        s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=doc_buffer.getvalue())
        logger.info(f"Successfully uploaded to s3://{bucket_name}/{s3_key}")
        return cdn_url + "/" + s3_key
    except Exception as e:
        logger.error(
            f"Error uploading the document: {e}",
            extra={"tags": {"task_function": "upload_doc_to_s3"}}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
