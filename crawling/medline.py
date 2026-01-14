import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re
import PyPDF2
from io import BytesIO
import os
import random

def search_results(query):
    base_url = "https://wsearch.nlm.nih.gov/ws/query"
    params = {
        'db': 'healthTopics',
        'term': query,
        'retmax': '10'
    }
    response = requests.get(base_url, params=params)
    return response.text

def parse_search_results(xml_data):
    urls = []
    root = ET.fromstring(xml_data)
    for doc in root.findall(".//document"):
        url = doc.get('url')
        urls.append(url)
    return urls

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
        'Referer': 'http://example.com',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Decompose headers, footers, navs, and sidebars
    for tag in ['header', 'footer', 'nav', 'aside']:
        for element in soup.select(tag):
            element.decompose()

    toc_section = soup.find('section', id='toc-section')
    if toc_section:
        toc_section.decompose()

    
    # Remove scripts and styles
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    
    # Extract main content
    main_content = ""
    main_title = "No Title"

    # Expanded list of possible containers
    possible_containers = [
        'article', 'article__body', 'main', 'section', 'div#content', 'div.content', 'div#main', 
        'div#primary', 'div.entry-content', 'div.post-content', 'div.article-content', 
        'div.page-content', 'div.blog-post', 'div#article', 'div#post', 'div.story', 
        'div.text', 'div.body', 'div.main-body', 'div#body', 'div.content-area',
        'div#content-wrapper', 'div.container', 'div.inner-content', 'div#main-content',
        'div.content-main', 'div#content-area', 'div#page-body', 'div.page-body'
    ]

    # Loop through containers to find and extract main content
    for container in possible_containers:
        main_section = soup.select_one(container)
        if main_section:
            main_content += main_section.get_text(separator='\n', strip=True) + "\n"

    # Fallback if no main container is found
    if not main_content:
        main_content = soup.get_text(separator='\n', strip=True)

    # Extract main title (h1 tag)
    h1_tag = soup.find('h1')
    if h1_tag:
        main_title = h1_tag.get_text(strip=True)
    else:
        try:
            main_title = soup.title.text
        except Exception as e:
            print(f"Error: Title not found for URL: {url}, Error: {e}")

    return main_title, main_content.strip(), soup

def extract_pdf(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    full_text = ''
    
    # Check content type before processing as PDF
    if response.headers['Content-Type'] == "application/pdf":
        try:
            reader = PyPDF2.PdfReader(BytesIO(response.content))
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                full_text = full_text + " " + text
        except PyPDF2.errors.PdfReadError:
            # Handle the error (log, skip processing, etc.)
            print(f"Error: EOF marker not found for URL: {url}")
    else:
        print(f"Skipping non-PDF content: {url}")
    return full_text

def extract_links(soup):
    links = []
    # Exclude sections with IDs "cat_59_section" and "cat_27_section"
    excluded_ids = ["cat_59_section", "cat_27_section"]
    for section in soup.find_all('section', id=re.compile('^cat')):
        if section.get('id') not in excluded_ids:
            for link in section.find_all('a', href=True):
                if "salud" in link['href'] or "spanish" in link['href'] or '/es/' in link['href'] or 'espanol' in link['href'] or 'https://es.' in link['href']:
                    continue
                else:
                    links.append({'href': link['href']})
    return links

def create_element_with_text(tag, text):
    element = ET.Element(tag)
    element.text = text.strip()
    return element

def sanitize_filename(title):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', title)

def save_page_to_xml(data, output_folder_path, filename):
    root = ET.Element("page")
    root.append(create_element_with_text("title", data['title']))
    root.append(create_element_with_text("url", data['url']))
    root.append(create_element_with_text("content", data['content']))
    
    xml_str = ET.tostring(root, encoding='utf-8')
    
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    full_path = os.path.join(output_folder_path, filename)
    if os.path.exists(full_path):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(output_folder_path, f"{base}_{counter}{ext}")):
            counter += 1
        full_path = os.path.join(output_folder_path, f"{base}_{counter}{ext}")

    with open(full_path, "wb") as f:
        f.write(xml_str)



def main():
    queries = ["lower back pain", "physical therapy", "rehabilitation"]

    docs = 0
    output_folder_path = "medline_resources"

    for query in queries:
        print(f"Searching for {query}...")
        xml_data = search_results(query)
        urls = parse_search_results(xml_data)

        for url in urls:
            print(f"Scraping URL: {url}")
            docs += 1
            main_title, content, soup = scrape_page(url)
            page_info = {'title': main_title, 'url': url, 'content': content}
            page_filename = f"{sanitize_filename(main_title)}.xml"
            save_page_to_xml(page_info, output_folder_path, page_filename.replace(r"__","_"))
            print(f"Saved data to {page_filename}")

            links = extract_links(soup)

            for link_info in links:
                link = link_info['href']
                print(f"Scraping subpage URL: {link}")
                if link.endswith(('.pdf', '.ashx')):
                    sub_content = extract_pdf(link)
                    sub_title = "PDF Content"
                else:
                    sub_title, sub_content, _ = scrape_page(link)
                subpage_info = {'title': sub_title, 'url': link, 'content': sub_content}
                subpage_filename = f"{sanitize_filename(sub_title)}.xml"
                save_page_to_xml(subpage_info, output_folder_path, subpage_filename.replace(r"__","_"))
                print(f"Saved data to {subpage_filename}")
                docs += 1

    print("Total number of documents: ", docs)

if __name__ == "__main__":
    main()
