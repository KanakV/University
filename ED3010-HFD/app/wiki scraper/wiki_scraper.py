import requests
import time
import json
import os
import re
import argparse
from urllib.parse import quote
from bs4 import BeautifulSoup

WIKI_BASE = "https://en.wikipedia.org/wiki/"
# wiki_scraper.py (Modified)
...
PLOTS_DIR = os.path.join(os.getcwd(), "data", "plots") # Changed: Output to data/plots

# Add more realistic headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

def fetch_page(title):
    url = WIKI_BASE + "List_of_" + quote(title.replace(" ", "_")) + "_episodes"
    print(url)
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.text, url

def get_episode_links(html):
    soup = BeautifulSoup(html, "html.parser")
    episodes = []
    
    # Look for episode tables - Wikipedia typically uses these classes for episode lists
    tables = soup.find_all("table", class_=["wikiepisodetable", "wikitable plainrowheaders", "wikitable", "wikitable plainrowheaders wikiepisodetable"])
    # print(tables)
    for table in tables:
        # Find all rows except the header
        rows = table.find_all('tr')[1:]
        
        for row in rows:
            # Look for episode title in different possible locations
            title_cell = None
            
            # Check "Title" column (usually marked with class="summary")
            title_cell = row.find('td', class_='summary') or row.find('th', class_='summary')
            
            # If not found, try looking for any cell with an episode link
            if not title_cell:
                for cell in row.find_all(['td', 'th']):
                    if cell.find('a'):
                        title_cell = cell
                        break
            
            if title_cell:
                link = title_cell.find('a')
                if link and link.get('href', '').startswith('/wiki/'):
                    # Clean up the title
                    title = link.get('title', link.text.strip())
                    
                    # Some episodes have season and episode numbers in cells
                    season_cell = row.find('td', class_='vevent')
                    if season_cell:
                        episode_no = season_cell.text.strip()
                        if episode_no:
                            title = f"{episode_no} - {title}"
                    
                    episodes.append({
                        'title': title,
                        'url': 'https://en.wikipedia.org' + link['href']
                    })
    
    # Remove duplicates while preserving order
    seen = set()
    unique_episodes = []
    for ep in episodes:
        if ep['url'] not in seen:
            seen.add(ep['url'])
            unique_episodes.append(ep)
    
    # print(unique_episodes)
    return unique_episodes

def extract_plot(source):
    """
    If source is a BeautifulSoup Tag for an <tr class="expand-child">, extract the
    shortSummaryText from td.description > div.shortSummaryText.
    If source is a <tr> main row, this function will try to find the corresponding
    expand-child sibling and extract from there. Returns {'title':..., 'plot':...}.
    """
    # Normalize to Tag/soup
    if isinstance(source, (str, bytes)):
        soup = BeautifulSoup(source, "html.parser")
        # no reliable title from a plain string here
        return {'title': None, 'plot': None}
    else:
        tag = source

    title = None
    plot = None

    # Try to get title from a summary cell in the current row (if present)
    summary_td = tag.find('td', class_='summary') or tag.find('th', class_='summary')
    if summary_td:
        for a in summary_td.find_all('a'):
            a.replace_with(a.get_text())
        for sup in summary_td.find_all('sup'):
            sup.decompose()
        title = summary_td.get_text(separator=" ", strip=True)

    # If this tag is an expand-child, extract directly
    classes = tag.get('class', []) or []
    if 'expand-child' in classes:
        desc_td = tag.find('td', class_='description')
        if desc_td:
            div = desc_td.find('div', class_='shortSummaryText')
            if div:
                for sup in div.find_all('sup'):
                    sup.decompose()
                for a in div.find_all('a'):
                    a.replace_with(a.get_text())
                plot = div.get_text(separator=" ", strip=True)
        return {'title': title, 'plot': plot}

    # Otherwise, look for the next sibling expand-child row (common pattern)
    next_tr = tag.find_next_sibling()
    checked = 0
    while next_tr and checked < 6:  # guard against long searches
        nclasses = next_tr.get('class', []) or []
        if 'expand-child' in nclasses:
            desc_td = next_tr.find('td', class_='description')
            if desc_td:
                div = desc_td.find('div', class_='shortSummaryText')
                if div:
                    for sup in div.find_all('sup'):
                        sup.decompose()
                    for a in div.find_all('a'):
                        a.replace_with(a.get_text())
                    plot = div.get_text(separator=" ", strip=True)
            break
        # stop if we hit another main episode row
        if 'vevent' in nclasses:
            break
        next_tr = next_tr.find_next_sibling()
        checked += 1

    # If still no plot, do a conservative page-level fallback (as before)
    if not plot and hasattr(tag, 'find_all'):
        page_divs = tag.find_all('div', class_='shortSummaryText')
        if page_divs:
            texts = []
            for div in page_divs:
                for sup in div.find_all('sup'):
                    sup.decompose()
                for a in div.find_all('a'):
                    a.replace_with(a.get_text())
                t = div.get_text(separator=" ", strip=True)
                if t:
                    texts.append(t)
            plot = " ".join(texts) if texts else None

    return {'title': title, 'plot': plot}

def get_season_links(html):
    soup = BeautifulSoup(html, "html.parser")
    season_links = []
    
    # Find hatnote navigation links
    hatnotes = soup.find_all("div", class_="hatnote navigation-not-searchable")
    for hatnote in hatnotes:
        link = hatnote.find('a')
        if link and link.get('href', '').startswith('/wiki/'):
            season_links.append({
                'title': link.get('title', link.text.strip()),
                'url': 'https://en.wikipedia.org' + link['href']
            })
    
    return season_links

def parse_season_episodes(html, season_title):
    """
    Parse a season page HTML and return list of dicts:
    {'season': season_title, 'title': <episode title>, 'plot': <plot text>, 'url': <optional episode link>}
    This now uses main episode rows (vevent / module-episode-list-row) and finds the
    corresponding expand-child row to pull td.description > div.shortSummaryText.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Find main episode rows (vevent + module-episode-list-row)
    main_rows = []
    for tr in soup.find_all('tr'):
        classes = tr.get('class', []) or []
        if isinstance(classes, list) and 'vevent' in classes and 'module-episode-list-row' in classes:
            main_rows.append(tr)

    # fallback: any vevent rows
    if not main_rows:
        for tr in soup.find_all('tr', class_='vevent'):
            main_rows.append(tr)

    for main in main_rows:
        # Prefer title from td.summary
        summary_td = main.find('td', class_='summary') or main.find('th', class_='summary')
        title = None
        if summary_td:
            for a in summary_td.find_all('a'):
                a.replace_with(a.get_text())
            for sup in summary_td.find_all('sup'):
                sup.decompose()
            title = summary_td.get_text(separator=" ", strip=True)

        # Try to get a direct episode link for reference
        link = main.find('a', href=True)
        row_url = 'https://en.wikipedia.org' + link['href'] if link and link['href'].startswith('/wiki/') else None

        # Use extract_plot which will search for the expand-child sibling
        extracted = extract_plot(main)
        plot = extracted.get('plot') or None
        # if extract_plot didn't return title, keep earlier-detected title or link text
        if not title:
            title = extracted.get('title')
        if not title and link:
            title = link.get('title') or link.get_text(strip=True)

        if title or plot:
            results.append({
                'season': season_title,
                'title': title,
                'plot': plot,
                'url': row_url
            })

    return results

def get_series_plots(series_title, season_index=None):
    try:
        html, url = fetch_page(series_title)
        
        # First get season links
        season_links = get_season_links(html)
        print(f"\nFound {len(season_links)} season pages")
        # print(season_links)
        
        all_results = []
        # Process each season (or only the requested one)
        for idx, season in enumerate(season_links):
            if season_index is not None and idx != season_index:
                continue
            print(f"\nProcessing: {season['title']}")
            try:
                r = requests.get(season['url'], headers=HEADERS)
                r.raise_for_status()

                # Parse the season page directly to extract episode rows and plots
                season_episodes = parse_season_episodes(r.text, season['title'])
                print(f"  Found {len(season_episodes)} episodes on season page")
                all_results.extend(season_episodes)

                # Be nice to servers
                time.sleep(1)
                        
            except Exception as e:
                print(f"Error processing season {season['title']}: {str(e)}")
                time.sleep(5)  # Longer delay on error
                
        return all_results
    except Exception as e:
        print(f"Error processing series: {str(e)}")
        return []

def _sanitize_filename(name):
    # keep letters, numbers, dash and underscore
    safe = re.sub(r'[^A-Za-z0-9 _\-]+', '', name).strip().replace(' ', '_')
    return safe or "series"

def main():
    p = argparse.ArgumentParser(description="Extract plot summaries for TV series from Wikipedia")
    p.add_argument("series", nargs='?', help="TV series title (optional if using --names-file)")
    p.add_argument("--output", "-o", help="Output JSON file path. If --names-file is used and no --output given, creates per-series files.", default=None)
    p.add_argument("--season", "-s", type=int, help="Season number to process (1-based). For testing, use 1")
    p.add_argument("--names-file", "-n", help="Path to text file with series names (one per line). Default: names.txt", default=os.path.join("data", "show_names.txt")) # Changed: Input file is data/show_names.txt

    args = p.parse_args()

    # ensure plots directory exists
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # determine season index (0-based) if provided
    season_idx = None
    if args.season is not None:
        season_idx = max(0, args.season - 1)

    # helper to process one series and return results
    def process_one(series_name):
        print(f"\nFetching episode plots for: {series_name}")
        plots = get_series_plots(series_name, season_index=season_idx)

        # normalize series/season fields
        for ep in plots:
            ep['series'] = series_name
            if args.season is not None:
                ep['season'] = str(args.season)
            else:
                season_value = ep.get('season')
                season_str = ""
                if isinstance(season_value, str):
                    m = re.search(r'(\d+)', season_value)
                    season_str = m.group(1) if m else (re.findall(r'\d+', season_value)[0] if re.findall(r'\d+', season_value) else season_value)
                else:
                    season_str = str(season_value) if season_value is not None else ""
                ep['season'] = season_str

        return plots

    # If names file exists or user provided --names-file, run in loop over file
    if os.path.exists(args.names_file):
        with open(args.names_file, 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f if line.strip()]
        if not names:
            print(f"No series names found in {args.names_file}")
            return

        aggregate = [] if args.output else None
        for series_name in names:
            plots = process_one(series_name)

            if args.output:
                # aggregate all series into single file (will be saved in plots/)
                aggregate.extend(plots)
            else:
                # write per-series file into plots/
                safe = _sanitize_filename(series_name)
                out_path = os.path.join(PLOTS_DIR, f"{safe}_episode_plots.json")
                try:
                    with open(out_path, 'w', encoding='utf-8') as of:
                        json.dump(plots, of, indent=2, ensure_ascii=False)
                        of.flush()
                        os.fsync(of.fileno())
                    print(f"Saved {len(plots)} items for '{series_name}' -> {out_path}")
                except Exception as e:
                    print(f"Failed to save for '{series_name}': {e}")

            # be polite to servers between series
            time.sleep(2)

        if aggregate is not None:
            try:
                # save aggregated results into plots/ using basename of provided output
                out_name = os.path.basename(args.output) if args.output else "all_episode_plots.json"
                out_path = os.path.join(PLOTS_DIR, out_name)
                with open(out_path, 'w', encoding='utf-8') as of:
                    json.dump(aggregate, of, indent=2, ensure_ascii=False)
                    of.flush()
                    os.fsync(of.fileno())
                print(f"Saved aggregated results -> {out_path}")
            except Exception as e:
                print(f"Failed to save aggregated output: {e}")

    else:
        # No names file: require series positional argument
        if not args.series:
            print("No series provided and names file not found. Provide a series name or create names.txt.")
            return

        plots = process_one(args.series)
        out_name = os.path.basename(args.output) if args.output else "episode_plots.json"
        out_path = os.path.join(PLOTS_DIR, out_name)
        try:
            with open(out_path, 'w', encoding='utf-8') as of:
                json.dump(plots, of, indent=2, ensure_ascii=False)
                of.flush()
                os.fsync(of.fileno())
            print(f"Saved {len(plots)} items -> {out_path}")
        except Exception as e:
            print(f"Failed to save output: {e}")

if __name__ == "__main__":
    main()