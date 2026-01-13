import json
import os
import requests
import time
from pathlib import Path
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
            journal = p['bib'].get('journal', p['bib'].get('conference', ''))
            impact_factor = ""
            issn = ""
            
            try:
                r = requests.get(f"https://api.crossref.org/works?query.title={title}&rows=1", timeout=10)
                if r.status_code == 200:
                    items = r.json()['message']['items']
                    if items: 
                        crossref_data = items[0]
                        doi = crossref_data.get('DOI', '')
                        # Get journal name from CrossRef if not found in Scholar
                        if not journal and 'container-title' in crossref_data:
                            journal = crossref_data['container-title'][0] if isinstance(crossref_data['container-title'], list) else crossref_data['container-title']
                        # Get ISSN for impact factor lookup
                        if 'ISSN' in crossref_data:
                            issn = crossref_data['ISSN'][0] if isinstance(crossref_data['ISSN'], list) else crossref_data['ISSN']
            except (requests.RequestException, KeyError, ValueError) as e:
                print(f"CrossRef lookup failed for '{title[:50]}': {e}")
            
            # Get journal metrics (CiteScore) from Elsevier Serial Title API using ISSN
            elsevier_key = os.getenv("ELSEVIER_API_KEY")
            if issn and elsevier_key:
                try:
                    headers = {
                        'X-ELS-APIKey': elsevier_key,
                        'Accept': 'application/json'
                    }
                    r = requests.get(
                        f"https://api.elsevier.com/content/serial/title/issn/{issn}",
                        headers=headers,
                        timeout=10
                    )
                    if r.status_code == 200:
                        data = r.json().get('serial-metadata-response', {})
                        entries = data.get('entry', [])
                        if entries:
                            entry = entries[0]
                            cs_info = entry.get('citeScoreYearInfoList', {})
                            # Try the current metric first
                            cs_value = cs_info.get('citeScoreCurrentMetric')
                            cs_year = cs_info.get('citeScoreCurrentMetricYear')
                            if cs_value:
                                impact_factor = f"CiteScore ({cs_year}): {cs_value}"
                            else:
                                # Fallback: check year-specific list
                                year_info = cs_info.get('citeScoreYearInfo', [])
                                if year_info:
                                    latest = year_info[0]
                                    if 'citeScore' in latest and 'year' in latest:
                                        impact_factor = f"CiteScore ({latest['year']}): {latest['citeScore']}"
                            # If CiteScore missing, try SNIP/SJR
                            if not impact_factor:
                                snip = entry.get('SNIPList', {}).get('SNIP', [{}])[0].get('$') if isinstance(entry.get('SNIPList', {}).get('SNIP'), list) else None
                                sjr = entry.get('SJRList', {}).get('SJR', [{}])[0].get('$') if isinstance(entry.get('SJRList', {}).get('SJR'), list) else None
                                if snip:
                                    impact_factor = f"SNIP: {snip}"
                                elif sjr:
                                    impact_factor = f"SJR: {sjr}"
                    else:
                        print(f"Elsevier API returned status {r.status_code} for ISSN {issn}")
                except (requests.RequestException, KeyError, ValueError) as e:
                    print(f"Elsevier lookup failed for ISSN {issn}: {e}")

            data_to_save.append({
                "title": title,
                "authors": p['bib'].get('author', ''),
                "year": p['bib'].get('pub_year', ''),
                "journal": journal if journal else 'Unknown',
                "impact_factor": impact_factor,
                "doi": doi,
                "citations": p.get('num_citations', 0)
            })
            print(f"Processed: {title[:50]}...")
            time.sleep(1) # Small delay to be polite to Google
        except Exception as e:
            print(f"Skipping a publication due to error: {e}")

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    output_file = script_dir / 'assets' / 'publications.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=4)
    print(f"Success! {output_file} updated.")

if __name__ == "__main__":
    update_data()