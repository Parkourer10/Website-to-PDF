import requests
from bs4 import BeautifulSoup
from pdf import generate_webpage_pdfs
import os
from config import (BASE_URL,
                    BATCH_SIZE,
                    NUM_CORES,
                    )

def scrape_pages(base_url, output_file):
    all_pages = set()
    to_visit = [base_url]
    visited = set()

    print(f"Starting to archive {base_url}")
    
    with open(output_file, 'w') as f:
        try:
            while to_visit:
                current_url = to_visit.pop(0)
                
                if current_url in visited:
                    continue
                    
                visited.add(current_url)
                
                print(f"Page: {current_url}")
                
                try:
                    response = requests.get(current_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        if href:
                            if href.startswith('/') and ':' not in href and '?' not in href:
                                full_url = base_url.rstrip('/') + href
                                if full_url not in visited and full_url not in to_visit:
                                    all_pages.add(full_url)
                                    to_visit.append(full_url)
                                    
                                    f.write(full_url + '\n')
                                    f.flush()
                
                except requests.RequestException as e:
                    print(f"Error! {current_url}: {e}")
                    continue
        
        except KeyboardInterrupt:
            print("\Interrupted")
    
    print(f"\nFound {len(all_pages)} pages.")
    print(f"Links saved to {output_file}")

if __name__ == "__main__":
    OUTPUT_FILE= 'webpages.txt' #please do not change this.

    if not os.path.exists(OUTPUT_FILE):
        scrape_pages(BASE_URL, OUTPUT_FILE)
        generate_webpage_pdfs(OUTPUT_FILE, batch_size=BATCH_SIZE, num_cores=NUM_CORES)
    else:
        generate_webpage_pdfs(OUTPUT_FILE, batch_size=BATCH_SIZE, num_cores=NUM_CORES)
        
