from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from datetime import date

import requests
from bs4 import BeautifulSoup


# Paste the stable Statistik Austria page URL here once you have it.
SOURCE_PAGE_URL = "https://www.statistik.at/statistiken/tourismus-und-verkehr/fahrzeuge/kfz-neuzulassungen"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

USER_AGENT = (
    "PKW_Neuzulassungsdaten_nach_Krafstoffart/0.1 "
    "(Manuelles Monatliches Datendownload; Kontakt: Peer Szczepaniak, peer.szczepan@students.boku.ac.at, Universität für Bodenkultur Wien)"
)

REQUEST_TIMEOUT_SECONDS = 30

ALLOWED_EXTENSIONS = (".ods")

german_month_names = {
    1: "jänner",
    2: "februar",
    3: "märz",
    4: "april",
    5: "mai",
    6: "juni",
    7: "juli",
    8: "august",
    9: "september",
    10: "oktober",
    11: "november",
    12: "dezember",
}
today = date.today()
current_year = str(today.year)
current_month = today.month
current_month_conv = german_month_names[current_month]

RELEVANT_KEYWORDS = [
    "kfz",
    "neuzulassungen",
    "bundesland"
    "kraftstoffart",
    "energiequelle",
    "bundesland",
    "Kraftfahrzeuge",
    current_year,
    current_month_conv
]

@dataclass
class CandidateLink:
    url: str
    text: str
    filename: str
    score: int

def fetch_page(url: str) -> str:
    '''
    Takes given Webpage URL, downloads HTML and checks if website exists.
    USER_AGENT identifies, who is sending the request to the website. 
    '''

    headers = {"User-Agent": USER_AGENT} #When making request to website, identifies as research project (see above)

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit(f"ERROR: Could not load source page: {exc}") from exc

    return response.text

def find_download_links(html: str, base_url: str) -> list[CandidateLink]:
    
    '''
    Looks at every link on the given page (here: Statistik Austria page).
    Keeps and extracts all links that point to .ods files.
    Calls score_link definiiton to score files based on relevance.
    Returns list of possile download candidates.
    DOES NOT download yet.

    '''
    
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[CandidateLink] = []

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        absolute_url = urljoin(base_url, href)

        if not has_allowed_extension(absolute_url):
            continue

        text = link.get_text(" ", strip=True)
        filename = filename_from_url(absolute_url)

        score = score_link(text=text, filename=filename, url=absolute_url)

        candidates.append(
            CandidateLink(
                url=absolute_url,
                text=text,
                filename=filename,
                score=score,
            )
        )

    # Remove duplicates while preserving the best score per URL.
    deduped: dict[str, CandidateLink] = {}
    for candidate in candidates:
        existing = deduped.get(candidate.url)
        if existing is None or candidate.score > existing.score:
            deduped[candidate.url] = candidate

    return list(deduped.values())

def score_link(text: str, filename: str, url: str) -> int:

    '''
    Checks for keywords (defined above). Returns score based on keywords.
    '''
    haystack = f"{text} {filename} {url}".lower()
    filename_lower = filename.lower() #everyhting in lowercase for better comparision

    score = 0

    for keyword in RELEVANT_KEYWORDS:
        if keyword in haystack:
            score += 10

    return score

def has_allowed_extension(url: str) -> bool:
    path = urlparse(url).path.lower()
    return path.endswith(ALLOWED_EXTENSIONS)

def filename_from_url(url: str) -> str:
    path = urlparse(url).path
    filename = Path(unquote(path)).name

    if not filename:
        raise ValueError(f"Could not determine filename from URL: {url}")

    return sanitize_filename(filename)

def sanitize_filename(filename: str) -> str:
    """
    Keep the Statistik Austria filename recognizable, but remove unsafe path characters.
    Do not change file contents.
    """
    filename = filename.replace("/", "_").replace("\\", "_")
    filename = re.sub(r"\s+", "_", filename)
    return filename

def select_best_candidate(candidates: list[CandidateLink]) -> CandidateLink:
    """
    Select the strongest candidate.

    Sorting rules:
    1. Highest relevance score
    2. Filename descending, which often picks newer dated filenames
    3. URL descending as a fallback
    """
    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.score,
            candidate.filename.lower(),
            candidate.url.lower(),
        ),
        reverse=True,
    )[0]

def print_candidate_summary(candidates: list[CandidateLink]) -> None:
    print("Candidate links:")

    for candidate in sorted(candidates, key=lambda c: c.score, reverse=True):
        label = candidate.text or "(no link text)"
        print(f"  - score={candidate.score} file={candidate.filename}")
        print(f"    text={label}")
        print(f"    url={candidate.url}")
        print()

def download_file(url: str, output_path: Path) -> None:
    headers = {"User-Agent": USER_AGENT}

    try:
        with requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
            stream=True,
        ) as response:
            response.raise_for_status()

            temporary_path = output_path.with_suffix(output_path.suffix + ".part")

            with temporary_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)

            temporary_path.rename(output_path)

    except requests.RequestException as exc:
        raise SystemExit(f"ERROR: Could not download file: {exc}") from exc
    except OSError as exc:
        raise SystemExit(f"ERROR: Could not save file: {exc}") from exc

def main() -> None:

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


    # ---------------
    # 1. Check if page exists
    # ---------------

    print()
    print(f"Source page checked: {SOURCE_PAGE_URL}")
    print()

    html = fetch_page(SOURCE_PAGE_URL)

    # ------------------
    # 2. Print all possible download files, score them and select the best
    # ------------------
    candidates = find_download_links(html, SOURCE_PAGE_URL)

    print(f"Download links found: {len(candidates)}")
    print()

    if not candidates:
        print("ERROR: No .ods or .xlsx download links found on the source page.")
        sys.exit(1)

    print_candidate_summary(candidates)

    selected = select_best_candidate(candidates)

    print(f"Selected download URL: {selected.url}")
    print()
    
    # -----------------
    # 3. Download best scored file if already exists, skip
    # -----------------
    output_path = RAW_DATA_DIR / selected.filename
    print(f"Output file path: {output_path}")
    print()

    if output_path.exists():
        print("Result: skipped")
        print("Reason: file already exists, raw data was not overwritten.")
        return

    download_file(selected.url, output_path)

    print("Result: downloaded")
    print(f"Saved new raw file: {output_path}")
    print()

if __name__ == "__main__":
    main()