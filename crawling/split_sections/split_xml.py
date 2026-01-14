import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import random
import time
import os
import glob

page_configs = {
    "https://www.pennmedicine.org/updates/blogs/musculoskeletal-and-rheumatology/2017/december/5-ergonomic-tips-to-help-with-back-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nccih.nih.gov/health/tips/things-to-know-about-massage-therapy-for-health-purposes": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nccih.nih.gov/health/tips/things-to-know-about-chronic-low-back-pain-and-complementary-health-approaches": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://handsdownbetter.org/about-chiropractic/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.cdc.gov/female-blood-disorders/about/heavy-menstrual-bleeding.html": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/menstruation/conditioninfo": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://acl.gov/about-acl/about-national-institute-disability-independent-living-and-rehabilitation-research": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/diseases-conditions/adenomyosis/symptoms-causes/syc-20369138?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/healthy-lifestyle/adult-health/in-depth/office-ergonomics/art-20046169?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/amenorrhea": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nationaljewish.org/conditions/health-information/exercise-and-weight/exercise-at-home/axial-extension?modal=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://ors.od.nih.gov/sr/dohs/HealthAndWellness/Ergonomics/Pages/spine.aspx": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.cdc.gov/nchs/products/databriefs/db415.htm": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/diseases-conditions/back-pain/symptoms-causes/syc-20369906?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.ninds.nih.gov/health-information/disorders/back-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.acog.org/womens-health/faqs/back%20pain%20during%20pregnancy": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/diseases-conditions/back-pain/in-depth/back-surgery/art-20048274?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nccih.nih.gov/health/black-cohosh": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.fda.gov/medical-devices/home-health-and-consumer-devices/brochure-home-healthcare-medical-devices-checklist": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.healthinaging.org/tools-and-tips/caregiver-guide-mobility-problems": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.amputation.research.va.gov/Prosthetic_Engineering/Prosthetic_Engineering_Overview.asp": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/tests-procedures/chiropractic-adjustment/about/pac-20393513?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nccih.nih.gov/health/chiropractic-in-depth": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.niams.nih.gov/health-topics/back-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.heart.org/en/health-topics/cardiac-rehab/getting-physically-active/common-problems-and-solutions-for-being-physically-active": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.osha.gov/etools/computer-workstations/positions": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/diseases-conditions/menorrhagia/symptoms-causes/syc-20352829?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://health.clevelandclinic.org/heres-how-to-set-up-your-office-to-avoid-aches-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nhlbi.nih.gov/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://orthoinfo.aaos.org/en/recovery/hip-conditioning-program/hip-pdf/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.niams.nih.gov/health-topics/hip-replacement-surgery": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.pcf.org/about-prostate-cancer/prostate-cancer-side-effects/hormone-therapy-side-effects/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/rehabtech/conditioninfo/help": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/menstruation/conditioninfo/diagnosed": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.ismrm.org/resources/information-for-patients/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://familydoctor.org/lifting-safety-tips-to-help-prevent-back-injuries/?adfree=true": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://familydoctor.org/symptom/lower-back-pain/?adfree=true": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://familydoctor.org/condition/low-back-pain/?adfree=true": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://familydoctor.org/magnetic-resonance-imaging-mri/?adfree=true": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.acatoday.org/patients/posture/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://newsinhealth.nih.gov/2018/10/managing-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/diseases-conditions/menopause/expert-answers/hormone-replacement-therapy/faq-20058499?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/diseases-conditions/menstrual-cramps/symptoms-causes/syc-20374938?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.womenshealth.gov/menstrual-cycle": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://youngwomenshealth.org/guides/menstrual-cramps/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.fda.gov/medical-devices/metal-metal-hip-implants/metal-metal-hip-implants-information-patients": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.fda.gov/radiation-emitting-products/medical-imaging/mri-magnetic-resonance-imaging": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nccih.nih.gov/research/statistics/nhis/2017": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.niaaa.nih.gov/publications/brochures-and-fact-sheets/using-alcohol-to-relieve-your-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.cdc.gov/overdose-prevention/hcp/clinical-care/nonopioid-therapies-for-pain-management.html": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.amputee-coalition.org/resources/thrive-as-prosthesis-users/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.merckmanuals.com/home/special-subjects/limb-prosthetics/overview-of-limb-prosthetics": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.merckmanuals.com/home/brain,-spinal-cord,-and-nerve-disorders/pain/overview-of-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.merckmanuals.com/home/fundamentals/rehabilitation/overview-of-rehabilitation": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.ninds.nih.gov/health-information/disorders/pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.painconsortium.nih.gov/health-information/pain-condition-resources": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.painconsortium.nih.gov/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.healthinaging.org/a-z-topic/pain-management/lifestyle": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.asahq.org/madeforthismoment/pain-management/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.healthinaging.org/a-z-topic/pain-management": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nia.nih.gov/health/pain/pain-you-can-get-help": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://newsinhealth.nih.gov/2019/08/period-problems": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://familydoctor.org/condition/piriformis-syndrome/?adfree=true": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.ninds.nih.gov/health-information/disorders/piriformis-syndrome": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/healthy-lifestyle/pregnancy-week-by-week/in-depth/pregnancy/art-20046080?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://orthoinfo.aaos.org/en/recovery/preventing-blood-clots-after-orthopaedic-surgery-video/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.spine.org/KnowYourBack/Prevention/Exercise/Strengthening": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://doctorsthatdo.osteopathic.org/prevention-treatment-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://health.gov/myhealthfinder/healthy-living/safety/prevent-back-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.verywellhealth.com/how-to-lift-2548509": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.amputee-coalition.org/resources/prosthetic-faqs-for-the-new-amputee/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.cdc.gov/mmwr/volumes/68/wr/mm685152a5.htm": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/tests-procedures/radiofrequency-neurotomy/about/pac-20394931?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nibib.nih.gov/science-education/science-topics/rehabilitation-engineering": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/rehabtech": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://newsinhealth.nih.gov/2022/01/retraining-brain-treat-chronic-back-pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/diseases-conditions/sciatica/symptoms-causes/syc-20377435?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nationaljewish.org/conditions/health-information/exercise-and-weight/exercise-at-home/shoulder-blade-squeeze?modal=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.ninds.nih.gov/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://familydoctor.org/condition/somatic-symptom-and-related-disorders/?adfree=true": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.ninds.nih.gov/health-information/disorders/spinal-cord-infarction": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nccih.nih.gov/health/spinal-manipulation-what-you-need-to-know": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://orthoinfo.aaos.org/en/recovery/spine-conditioning-program/spine-conditioning-program-pdf/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.christopherreeve.org/todays-care/living-with-paralysis/lifestyle/how-to-stay-healthy-on-the-road/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://youngwomenshealth.org/guides/tampons/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.ninds.nih.gov/health-information/disorders/tarlov-cysts": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.foothealthfacts.org/article/that-pain-in-your-back-could-be-linked-to-your-fee": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.fda.gov/consumers/consumer-updates/facts-tampons-and-how-use-them-safely": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.amputee-coalition.org/resources/the-wonderful-world-of-cosmesis/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.cancer.org/cancer/types/prostate-cancer/treating/recurrence.html": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.spine.org/KnowYourBack/Treatments/Assessment-Tools/Radiographic-Assessment-Back-Pain": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.spine.org/KnowYourBack/Treatments/Injection-Treatments-for-Spinal-Pain/Epidural-Steroid-Injections": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://familydoctor.org/vertebroplasty-for-spine-fracture-pain/?adfree=true": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/menstruation/conditioninfo/irregularities": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/rehabtech/conditioninfo/device": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/rehabtech/conditioninfo/use": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/menstruation/conditioninfo/treatments": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/amenorrhea/conditioninfo/treatments": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.nichd.nih.gov/health/topics/menstruation/conditioninfo/causes": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.aota.org/about/what-is-ot": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.amputee-coalition.org/resources/when-to-replace-a-prosthesis/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.mayoclinic.org/healthy-lifestyle/womens-health/in-depth/menstrual-cycle/art-20047186?p=1": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.cdc.gov/workplacehealthpromotion/health-strategies/musculoskeletal-disorders/index.html": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    },
    "https://www.caryortho.com/workplace-ergonomics-posture-and-back-pain/": {
        "section_container": "article",
        "title_tag": "h1",
        "content_tags": ["p"]
    }
}


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

        sections = []
        for section in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            section_title = section.get_text(separator=' ', strip=True)
            section_content = ""
            sibling = section.find_next_sibling()
            while sibling and sibling.name not in ['h1', 'h2', 'h3', 'h4']:
                section_content += sibling.get_text(separator=' ', strip=True) + " "
                sibling = sibling.find_next_sibling()
            sections.append((section_title, section_content.strip()))

        return main_title, main_content, sections
    
    except Exception as e:
        print(f"Error scraping URL {url}: {e}")
        return None, None, []

def update_xml_with_sections(xml_string, url):
    # Parse the existing XML
    root = ET.fromstring(xml_string)

    # Re-crawl the URL to get the latest content
    main_title, main_content, sections = scrape_page(url)

    if main_title and main_content and sections:
        # Clear the existing content
        content_element = root.find('.//content')
        if content_element is not None:
            content_element.clear()

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
        return xml_string

def process_xml_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    xml_files = glob.glob(os.path.join(input_folder, "*.xml"))

    for xml_file in xml_files:
        with open(xml_file, 'r', encoding='utf-8') as file:
            xml_string = file.read()

        # Extract URL from the XML file
        root = ET.fromstring(xml_string)
        url_element = root.find('.//url')
        if url_element is not None and url_element.text:
            url = url_element.text
            updated_xml = update_xml_with_sections(xml_string, url)

            # Write the updated XML to the output folder
            output_file_path = os.path.join(
                output_folder, os.path.basename(xml_file))
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(updated_xml)
            print(f"Processed {xml_file} -> {output_file_path}")
        else:
            print(f"URL not found in {xml_file}")

input_folder = "data"
output_folder = "split_data"
process_xml_files(input_folder, output_folder)