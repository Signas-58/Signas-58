import os
import re
import json
import urllib.request
import urllib.error
import random
from datetime import datetime, timezone

# Configuration
USERNAME = "Signas-58"
README_PATH = "README.md"

def get_public_repos():
    """Fetch the number of public repositories using the public GitHub API."""
    url = f"https://api.github.com/users/{USERNAME}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("public_repos")
    except Exception as e:
        print(f"Error fetching public repos: {e}")
        return None

def get_private_repos(token):
    """Fetch the total number of private repositories using the authenticated user endpoint."""
    if not token:
        return None
    url = "https://api.github.com/user"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {token}")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            # For personal accounts, total_private_repos or owned_private_repos works
            return data.get("total_private_repos") or data.get("owned_private_repos")
    except Exception as e:
        print(f"Error fetching private repos: {e}")
        return None

def parse_current_stats(content):
    """Parse existing repository stats from README to serve as fallback values."""
    public_match = re.search(r"Public%20Repos-(\d+)", content)
    private_match = re.search(r"Private%20Repos-(\d+)", content)
    
    current_public = int(public_match.group(1)) if public_match else 42
    current_private = int(private_match.group(1)) if private_match else 29
    return current_public, current_private

def get_daily_quote():
    """Fetch a random tech/programming quote from ZenQuotes or fallback list."""
    url = "https://zenquotes.io/api/random"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("q"), data[0].get("a")
    except Exception as e:
        print(f"Error fetching quote from API: {e}")
    
    # Fallback to local curated quotes
    fallback_quotes = [
        {"q": "Talk is cheap. Show me the code.", "a": "Linus Torvalds"},
        {"q": "Programs must be written for people to read, and only incidentally for machines to execute.", "a": "Harold Abelson"},
        {"q": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "a": "Martin Fowler"},
        {"q": "First, solve the problem. Then, write the code.", "a": "John Johnson"},
        {"q": "Experience is the name everyone gives to their mistakes.", "a": "Oscar Wilde"},
        {"q": "Code is like humor. When you have to explain it, it’s bad.", "a": "Cory House"},
        {"q": "Simplicity is the soul of efficiency.", "a": "Austin Freeman"},
        {"q": "Make it work, make it right, make it fast.", "a": "Kent Beck"},
        {"q": "Before software can be reusable it first has to be usable.", "a": "Ralph Johnson"},
        {"q": "Optimism is a occupational hazard of programming: feedback is the treatment.", "a": "Kent Beck"}
    ]
    quote = random.choice(fallback_quotes)
    return quote["q"], quote["a"]

def replace_section(content, start_tag, end_tag, replacement):
    """Replace content between start and end tags (inclusive of tags)."""
    start_idx = content.find(start_tag)
    end_idx = content.find(end_tag)
    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        print(f"Warning: Tags {start_tag} and/or {end_tag} not found or malformed.")
        return content
    return (
        content[:start_idx + len(start_tag)]
        + "\n"
        + replacement
        + "\n"
        + content[end_idx:]
    )

def main():
    if not os.path.exists(README_PATH):
        print(f"Error: {README_PATH} not found.")
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Get fallbacks
    fallback_public, fallback_private = parse_current_stats(content)

    # 1. Fetch updated repo counts
    token = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
    
    public_repos = get_public_repos()
    if public_repos is None:
        public_repos = fallback_public
        print(f"Using fallback public repos: {public_repos}")
    else:
        print(f"Fetched public repos: {public_repos}")

    private_repos = get_private_repos(token)
    if private_repos is None:
        private_repos = fallback_private
        print(f"Using fallback private repos: {private_repos}")
    else:
        print(f"Fetched private repos: {private_repos}")

    # 2. Fetch daily quote
    quote_text, quote_author = get_daily_quote()
    print(f"Selected Quote: '{quote_text}' - {quote_author}")

    # 3. Format replacement contents
    stats_replacement = (
        f'<p align="center">\n'
        f'  <img src="https://img.shields.io/badge/Public%20Repos-{public_repos}-00F7FF?style=for-the-badge&logo=github&logoColor=black"/>\n'
        f'  <img src="https://img.shields.io/badge/Private%20Repos-{private_repos}-00F7FF?style=for-the-badge&logo=github&logoColor=black"/>\n'
        f'</p>'
    )
    
    quote_replacement = (
        f'> "{quote_text}"\n'
        f'> — *{quote_author}*'
    )

    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    update_replacement = f"*Last Updated: {current_date}*"

    # 4. Perform replacements
    content = replace_section(content, "<!-- STATS_SECTION_START -->", "<!-- STATS_SECTION_END -->", stats_replacement)
    content = replace_section(content, "<!-- QUOTE_SECTION_START -->", "<!-- QUOTE_SECTION_END -->", quote_replacement)
    content = replace_section(content, "<!-- UPDATE_SECTION_START -->", "<!-- UPDATE_SECTION_END -->", update_replacement)

    # 5. Write back to README.md
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("README.md updated successfully!")

if __name__ == "__main__":
    main()
