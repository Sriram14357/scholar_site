import json
import requests
import time
from scholarly import scholarly

def update_data():
    print("Fetching data for ID: _-tb2Y8AAAAJ...")
    
    # Attempt to fetch with retries in case of temporary network blocks
    max_retries = 3
    author = None
    
    for i in range(max_retries):
        try:
            search_query = scholarly.search_author_id('_-tb2Y8AAAAJ')
            author = scholarly.fill(search_query)
            break 
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(5) # Wait before retrying

    if not author:
        print("Failed to fetch data after multiple attempts.")
        return

    data_to_save = []
    # Limit to top 20 to avoid triggering Google's bot detection
    for pub in author['publications'][:20]: 
        try:
            p = scholarly.fill(pub)
            title = p['bib'].get('title', '')
            
            # DOI Lookup via CrossRef
            doi = ""
            try:
                r = requests.get(f"https://api.crossref.org/works?query.title={title}&rows=1", timeout=10)
                if r.status_code == 200:
                    items = r.json()['message']['items']
                    if items: 
                        # Only take DOI if the title is a close match
                        doi = items[0].get('DOI', '')
            except: 
                pass

            data_to_save.append({
                "title": title,
                "authors": p['bib'].get('author', ''),
                "year": p['bib'].get('pub_year', ''),
                "journal": p['bib'].get('journal', p['bib'].get('conference', 'Unknown')),
                "doi": doi,
                "citations": p.get('num_citations', 0)
            })
            print(f"Processed: {title[:50]}...")
            time.sleep(1) # Small delay to be polite to Google
        except Exception as e:
            print(f"Skipping a publication due to error: {e}")

    with open('assets/publications.json', 'w') as f:
        json.dump(data_to_save, f, indent=4)
    print("Success! assets/publications.json updated.")

if __name__ == "__main__":
    update_data()