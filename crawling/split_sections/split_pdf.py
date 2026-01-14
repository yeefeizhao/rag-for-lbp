"""import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import random
import os

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    return random.choice(user_agents)

def scrape_page(url):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Referer': 'https://www.google.com/',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive'
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        soup = BeautifulSoup(response.content, 'html.parser')

        # Decompose headers, footers, navs, and sidebars
        for tag in ['header', 'footer', 'nav', 'aside']:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove scripts and styles
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Extract main content
        main_content = ""
        main_title = "No Title"

        # Expanded list of possible containers
        possible_containers = [
            'main', 'article', 'article__body', 'section', 'div#content', 'div.content', 'div.leftSubpage', 'div#main', 'div.main-content',
            'div#primary', 'div.entry-content', 'div.post-content', 'div.article-content',
            'div.page-content', 'div.blog-post', 'div#article', 'div#post', 'div.story',
            'div.text', 'div.body', 'div.main-body', 'div#body', 'div.content-area',
            'div#content-wrapper', 'div.container', 'div.inner-content', 'div#main-content',
            'div.content-main', 'div#content-area', 'div#page-body', 'div.page-body', 'main.content-primary'
        ]

        # Loop through containers to find and extract main content
        for container in possible_containers:
            main_section = soup.select_one(container)
            if main_section:
                main_content += main_section.get_text(
                    separator='\n', strip=True) + "\n"
                break

        # Fallback if no main container is found
        if not main_content:
            main_content = soup.get_text(separator='\n', strip=True)

        # Extract main title (h1 tag)
        h1_tag = soup.find('h1')
        if h1_tag:
            main_title = h1_tag.get_text(separator=' ', strip=True)
        else:
            try:
                main_title = soup.title.get_text(separator=' ', strip=True)
            except Exception as e:
                print(f"Error: Title not found for URL: {url}, Error: {e}")

        sections = soup.find_all('div', class_='section')  # Adjust the class as per the HTML structure of the page
        parsed_sections = []

        for section in sections:
            section_title = section.find('h2')  # Adjust the tag as per the HTML structure
            section_content = section.find_all(['p', 'ul', 'ol'])  # Adjust the tags as per the HTML structure
            title_text = section_title.get_text(strip=True) if section_title else "No Title"
            content_text = "\n".join([el.get_text() for el in section_content])

            parsed_sections.append((title_text, content_text))

        return main_title, main_content, parsed_sections
    
    except Exception as e:
        print(f"Error scraping URL {url}: {e}")
        return None, None, []

def update_xml_with_sections(url):
    # Parse the existing XML
    root = ET.Element("page")
    # Re-crawl the URL to get the latest content
    main_title, main_content, sections = scrape_page(url)

    if main_title and main_content and sections:
        # Clear the existing content
        content_element = ET.SubElement(root, 'content')

        # Add new sections to the XML
        for title, content in sections:
            section = ET.SubElement(content_element, 'section')
            section_title = ET.SubElement(section, 'sectionTitle')
            section_title.text = title
            section_content = ET.SubElement(section, 'sectionContent')
            section_content.text = content

        # Convert the updated XML tree back to a string
        updated_xml_string = ET.tostring(root, encoding='unicode')
        return updated_xml_string
    else:
        print(f"Failed to scrape or update XML for URL: {url}")
        return None

def process_xml_files(urls, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for url in urls:
        # Extract URL from the XML file
        if url is not None:
            updated_xml = update_xml_with_sections(url)

            if updated_xml is not None:
                # Write the updated XML to the output folder
                output_file_path = os.path.join(output_folder, "file.xml")
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(updated_xml)
                print(f"Processed {url} -> file.xml")
            else:
                print(f"Failed to update XML for URL: {url}")
        else:
            print(f"URL not found")

urls = [
    "https://www.jospt.org/doi/10.2519/jospt.2021.0304"
]
output_folder = "split_pdf"
process_xml_files(urls, output_folder)
"""

import fitz  # PyMuPDF
import xml.etree.ElementTree as ET
import os

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def parse_sections(text):
    lines = text.split('\n')
    sections = []
    current_section = None

    for line in lines:
        if line.strip() == '':
            continue
        if line.isupper() and len(line.split()) < 10:  # Assuming section titles are in uppercase
            if current_section:
                sections.append(current_section)
            current_section = {'title': line.strip(), 'content': ''}
        elif current_section:
            current_section['content'] += line.strip() + ' '
    
    if current_section:
        sections.append(current_section)
    
    return sections

def create_xml(title, url, sections):
    root = ET.Element("page")
    
    title_element = ET.SubElement(root, "title")
    title_element.text = title
    
    url_element = ET.SubElement(root, "url")
    url_element.text = url
    
    content_element = ET.SubElement(root, "content")
    
    for section in sections:
        section_element = ET.SubElement(content_element, "section")
        
        section_title_element = ET.SubElement(section_element, "sectionTitle")
        section_title_element.text = section['title']
        
        section_content_element = ET.SubElement(section_element, "sectionContent")
        section_content_element.text = section['content']
    
    return ET.ElementTree(root)

def main(pdf_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            text = extract_text_from_pdf(pdf_path)
            sections = parse_sections(text)
            
            title = pdf_file
            url = pdf_path
            
            xml_tree = create_xml(title, url, sections)
            xml_output_path = os.path.join(output_folder, pdf_file.replace('.pdf', '.xml'))
            xml_tree.write(xml_output_path)

# Example usage
pdf_folder = "crawling/clinical_practice_guide"
output_folder = "langchain/split_pdf"
main(pdf_folder, output_folder)
