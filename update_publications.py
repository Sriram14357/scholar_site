import json
import requests
from scholarly import scholarly, ProxyGenerator

def update_data():
    # Set up a ProxyGenerator object to use free proxies
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)
    print("Fetching data for ID: _-tb2Y8AAAAJ...")
    search_query = scholarly.search_author_id('_-tb2Y8AAAAJ')
    author = scholarly.fill(search_query)
    
    data_to_save = []
    for pub in author['publications'][:20]: # Limits to top 20 for speed
        p = scholarly.fill(pub)
        title = p['bib'].get('title', '')
        
        # CrossRef DOI Lookup
        doi = ""
        try:
            r = requests.get(f"https://api.crossref.org/works?query.title={title}&rows=1")
            if r.status_code == 200:
                items = r.json()['message']['items']
                if items: doi = items[0].get('DOI', '')
        except: pass

        data_to_save.append({
            "title": title,
            "authors": p['bib'].get('author', ''),
            "year": p['bib'].get('pub_year', ''),
            "journal": p['bib'].get('journal', p['bib'].get('conference', 'Unknown')),
            "doi": doi,
            "citations": p.get('num_citations', 0)
        })

    with open('assets/publications.json', 'w') as f:
        json.dump(data_to_save, f, indent=4)
    print("Success! assets/publications.json updated.")

if __name__ == "__main__":
    update_data()