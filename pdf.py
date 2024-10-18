import os
import base64
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyPDF2 import PdfMerger, PdfReader
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from config import CHROME_DRIVER_PATH, PDF_OUTPUT_FILE, BATCH_SIZE, NUM_CORES
#TODO:
#Fix the progress bar.

def setup_driver():
    chrome_driver_path = CHROME_DRIVER_PATH  
    service = Service(chrome_driver_path)
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    
    #saving to pdf
    appstate = {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": ""
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
    options.add_experimental_option('prefs', {
        'printing.print_preview_sticky_settings.appState': appstate,
        'download.default_directory': os.path.abspath('pdfs')
    })
    
    return webdriver.Chrome(service=service, options=options)

def scroll_page(driver): #to load all imgs in the webpage!
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
    )
    driver.execute_script("""
        var imgs = document.getElementsByTagName('img');
        for (var i = 0; i < imgs.length; i++) {
            var img = imgs[i];
            var src = img.src;
            img.src = '';
            img.src = src;
        }
    """)
    
    #INSURING ALL IMGS ARE LOADED ! 
    time.sleep(10)


def generate_pdf(driver, website, pdf_path):
    try:
        driver.get(website)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        #lazy-loaded images loadin
        scroll_page(driver)
        print_options = {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True,
        }
        result = driver.execute_cdp_cmd('Page.printToPDF', print_options)
        with open(pdf_path, 'wb') as file:
            file.write(base64.b64decode(result['data']))
        if verify_pdf(pdf_path):
            print(f"Saved PDF: {pdf_path} for webpage {website}")
            return pdf_path
        else:
            os.remove(pdf_path)
            return None

    except Exception as e:
        print(f"Error capturing {website}: {e}")
        return None
    
def verify_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error verifying PDF {pdf_path}: {e}")
        return False

def process_batch(websites, start_idx, pdf_folder, pbar):
    driver = setup_driver()
    valid_pdfs = []
    for idx, website in enumerate(websites, start=start_idx):
        pdf_filename = f'page_{idx + 1}.pdf'
        pdf_path = os.path.join(pdf_folder, pdf_filename)
        result = generate_pdf(driver, website, pdf_path)
        if result:
            valid_pdfs.append(result)
        pbar.update(1)  #update the progress bar
    driver.quit()
    return valid_pdfs

def generate_webpage_pdfs(website_file, batch_size=BATCH_SIZE, num_cores=NUM_CORES):
    print(f"Using batch size of {batch_size} and {num_cores} cores")
    
    with open(website_file, 'r') as file:
        websites = [line.strip() for line in file.readlines() if line.strip()]

    pdf_folder = 'pdfs' #please do not change it. its not important
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)

    all_valid_pdfs = []
    
    
    with tqdm(total=len(websites), desc="Generating PDFs", unit="pdf") as pbar:
        with ThreadPoolExecutor(max_workers=num_cores) as executor:
            futures = []
            for i in range(0, len(websites), batch_size):
                batch = websites[i:i+batch_size]
                future = executor.submit(process_batch, batch, i, pdf_folder, pbar)
                futures.append(future)

            for future in as_completed(futures):
                all_valid_pdfs.extend(future.result())

    #combine all da pdfs
    output_pdf = PDF_OUTPUT_FILE
    merger = PdfMerger()
    for pdf_path in all_valid_pdfs:
        merger.append(pdf_path)

    merger.write(output_pdf)
    merger.close()

    #clean up
    for pdf_path in all_valid_pdfs:
        os.remove(pdf_path)
    os.rmdir(pdf_folder)

    print(f"Full website pdf created: {output_pdf}")
