import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re
import PyPDF2
import os
import random, time


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

    session = requests.Session()
    response = session.get(url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Decompose headers, footers, navs, and sidebars
    for tag in ['header', 'footer', 'nav', 'aside']:
        for element in soup.find_all(tag):
            element.decompose()
            time.sleep(random.uniform(1, 3))

    # Remove scripts and styles
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
        time.sleep(random.uniform(1, 3))    

    
    # Extract main content
    main_content = ""
    main_title = "No Title"

    # Expanded list of possible containers
    possible_containers = [
        'article', 'article__body', 'main', 'section', 'div#content', 'div.content', 'div.leftSubpage', 'div#main', 'div.main-content',
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
            main_content += main_section.get_text(separator='\n', strip=True) + "\n"

    time.sleep(random.uniform(1, 3))    


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


    image_urls = []
    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('src')
        if img_url and not img_url.startswith(('data:image', 'javascript')):
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = os.path.join(url, img_url)
            image_urls.append(img_url)
    
    # Introduce random delay between requests
    time.sleep(random.uniform(1, 3))

    return main_title, main_content.strip(), image_urls

def extract_pdf(file):

    full_text = ''
    try:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            full_text = full_text + " " + text
    except PyPDF2.errors.PdfReadError:
        # Handle the error (log, skip processing, etc.)
        print(f"Error: EOF marker not found for file: {file}")
    return full_text

def create_element_with_text(tag, text):
    element = ET.Element(tag)
    element.text = text.strip()
    return element

def save_to_xml(data, output_folder_path, filename):
    root = ET.Element("page")
    root.append(create_element_with_text("title", data[1]))
    root.append(create_element_with_text("url", data[2]))
    root.append(create_element_with_text("content", data[0]))

    images_element = ET.SubElement(root, "images")
    for img_url in data[3]:
        img_element = create_element_with_text("image", img_url)
        images_element.append(img_element)

    xml_str = ET.tostring(root, encoding='utf-8')

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    with open(os.path.join(output_folder_path, filename), "wb") as f:
        f.write(xml_str)

def sanitize_filename(title):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', title)

def main():
    urls = [
        'https://www.cdc.gov/nchs/products/databriefs/db415.htm',
        'https://www.cdc.gov/mmwr/volumes/68/wr/mm685152a5.htm',
        'https://www.cdc.gov/workplacehealthpromotion/health-strategies/musculoskeletal-disorders/index.html',
        'https://www.uclahealth.org/medical-services/spine/patient-resources/ergonomics-prolonged-sitting',
        'https://www.caryortho.com/workplace-ergonomics-posture-and-back-pain/',
        'https://health.clevelandclinic.org/heres-how-to-set-up-your-office-to-avoid-aches-pain',
        'https://ors.od.nih.gov/sr/dohs/HealthAndWellness/Ergonomics/Pages/spine.aspx',
        'https://www.verywellhealth.com/how-to-lift-2548509',
        'https://www.pennmedicine.org/updates/blogs/musculoskeletal-and-rheumatology/2017/december/5-ergonomic-tips-to-help-with-back-pain',
    ]

    output_folder_path = 'resources_list'
    docs = 0
    cpg_folder_path = "clinical_practice_guide"
    journal_folder_path = "journal_articles"

    for filename in os.listdir(cpg_folder_path):
        if filename.endswith('.pdf'):
            docs+=1
            file_path = os.path.join(cpg_folder_path, filename)
            print(f"Extracting text from PDF: {file_path}")
            content = extract_pdf(file_path)
            sanitized_title = sanitize_filename(os.path.splitext(filename)[0])
        filename = f"cpg_{sanitized_title}.xml"
        save_to_xml([content, sanitized_title, file_path, []], output_folder_path, filename.replace(r"__","_"))
        print(f"Saved data to {filename}")

    for url in urls:
            print(f"Scraping URL: {url}")
            docs += 1
            main_title, content, image_urls = scrape_page(url)
            sanitized_title = sanitize_filename(main_title)
            filename = f"{sanitized_title}.xml"
            save_to_xml([content, main_title, url, image_urls], output_folder_path, filename.replace(r"__","_"))
            print(f"Saved data to {filename}")

    for filename in os.listdir(journal_folder_path):
        if filename.endswith('.pdf'):
            docs+=1
            file_path = os.path.join(journal_folder_path, filename)
            print(f"Extracting text from PDF: {file_path}")
            content = extract_pdf(file_path)
            sanitized_title = sanitize_filename(os.path.splitext(filename)[0])
        filename = f"{sanitized_title}.xml"
        save_to_xml([content, sanitized_title, file_path, []], output_folder_path, filename.replace(r"__","_"))
        print(f"Saved data to {filename}")


    print("Total number of documents: ", docs)

if __name__ == "__main__":
    main()
