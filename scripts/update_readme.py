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

def get_recent_activity():
    """Fetch recent public GitHub events and format them as a markdown list."""
    url = f"https://api.github.com/users/{USERNAME}/events/public"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            events = json.loads(response.read().decode())
            activity_lines = []
            count = 0
            for event in events:
                if count >= 5:
                    break
                
                event_type = event.get("type")
                repo_name = event.get("repo", {}).get("name")
                repo_link = f"[{repo_name}](https://github.com/{repo_name})"
                
                if event_type == "PushEvent":
                    commits = event.get("payload", {}).get("commits", [])
                    num_commits = len(commits)
                    if num_commits == 0:
                        size = event.get("payload", {}).get("size")
                        if size is not None:
                            num_commits = size
                    
                    if num_commits > 0:
                        desc = f"📝 Pushed {num_commits} commit(s) to {repo_link}"
                        commit_msg = commits[0].get("message", "").split("\n")[0] if commits else ""
                        if commit_msg:
                            if len(commit_msg) > 60:
                                commit_msg = commit_msg[:57] + "..."
                            desc += f" (*\"{commit_msg}\"*)"
                    else:
                        desc = f"📝 Pushed to {repo_link}"
                    activity_lines.append(desc)
                    count += 1
                elif event_type == "PullRequestEvent":
                    action = event.get("payload", {}).get("action")
                    pr_title = event.get("payload", {}).get("pull_request", {}).get("title")
                    pr_url = event.get("payload", {}).get("pull_request", {}).get("html_url")
                    desc = f"🔓 {action.capitalize()} PR [{pr_title}]({pr_url}) in {repo_link}"
                    activity_lines.append(desc)
                    count += 1
                elif event_type == "IssuesEvent":
                    action = event.get("payload", {}).get("action")
                    issue_title = event.get("payload", {}).get("issue", {}).get("title")
                    issue_url = event.get("payload", {}).get("issue", {}).get("html_url")
                    desc = f"💬 {action.capitalize()} issue [{issue_title}]({issue_url}) in {repo_link}"
                    activity_lines.append(desc)
                    count += 1
                elif event_type == "CreateEvent":
                    ref_type = event.get("payload", {}).get("ref_type")
                    if ref_type == "repository":
                        desc = f"📁 Created new repository {repo_link}"
                        activity_lines.append(desc)
                        count += 1
                elif event_type == "WatchEvent":
                    desc = f"⭐ Starred repository {repo_link}"
                    activity_lines.append(desc)
                    count += 1
                    
            if not activity_lines:
                return "*No recent public activity.*"
            return "\n".join([f"- {line}" for line in activity_lines])
    except Exception as e:
        print(f"Error fetching recent activity: {e}")
        return "*Failed to load recent activity.*"

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

COUNTER_THEMES = [
    "https://count.getloli.com/get/@Signas-58?theme=moebooru",
    "https://anime-counter.lulushu.workers.dev/@Signas-58?theme=naruto",
    "https://anime-counter.lulushu.workers.dev/@Signas-58?theme=onepiece",
    "https://count.getloli.com/get/@Signas-58?theme=booru-helltaker",
    "https://count.getloli.com/get/@Signas-58?theme=gelbooru"
]

def rotate_counter_theme(content):
    """Rotate to the next theme from the user's 5 selected profile view counter themes."""
    if "<!-- COUNTER_SECTION_START -->" not in content or "<!-- COUNTER_SECTION_END -->" not in content:
        return content

    current_idx = -1
    for i, theme_url in enumerate(COUNTER_THEMES):
        if theme_url in content:
            current_idx = i
            break

    next_idx = (current_idx + 1) % len(COUNTER_THEMES)
    next_url = COUNTER_THEMES[next_idx]
    print(f"Rotating counter theme to index {next_idx}: {next_url}")

    replacement = (
        f'<p align="center">\n'
        f'  <img src="{next_url}" alt="Profile Views Counter" />\n'
        f'</p>'
    )
    return replace_section(content, "<!-- COUNTER_SECTION_START -->", "<!-- COUNTER_SECTION_END -->", replacement)

def main():
    if not os.path.exists(README_PATH):
        print(f"Error: {README_PATH} not found.")
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Rotate counter theme across the 5 selected themes
    content = rotate_counter_theme(content)

    # Get fallbacks
    fallback_public, fallback_private = parse_current_stats(content)

    # 1. Fetch updated repo counts
    if "<!-- STATS_SECTION_START -->" in content:
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

        stats_replacement = (
            f'<p align="center">\n'
            f'  <img src="https://img.shields.io/badge/Public%20Repos-{public_repos}-00F7FF?style=for-the-badge&logo=github&logoColor=black"/>\n'
            f'  <img src="https://img.shields.io/badge/Private%20Repos-{private_repos}-00F7FF?style=for-the-badge&logo=github&logoColor=black"/>\n'
            f'</p>'
        )
        content = replace_section(content, "<!-- STATS_SECTION_START -->", "<!-- STATS_SECTION_END -->", stats_replacement)

    # 2. Fetch daily quote
    if "<!-- QUOTE_SECTION_START -->" in content:
        quote_text, quote_author = get_daily_quote()
        print(f"Selected Quote: '{quote_text}' - {quote_author}")
        quote_replacement = (
            f'> "{quote_text}"\n'
            f'> — *{quote_author}*'
        )
        content = replace_section(content, "<!-- QUOTE_SECTION_START -->", "<!-- QUOTE_SECTION_END -->", quote_replacement)

    # 3. Update timestamp
    if "<!-- UPDATE_SECTION_START -->" in content:
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        update_replacement = f"*Last Updated: {current_date}*"
        content = replace_section(content, "<!-- UPDATE_SECTION_START -->", "<!-- UPDATE_SECTION_END -->", update_replacement)

    # 4. Fetch recent activity
    if "<!-- ACTIVITY_SECTION_START -->" in content:
        activity_replacement = get_recent_activity()
        content = replace_section(content, "<!-- ACTIVITY_SECTION_START -->", "<!-- ACTIVITY_SECTION_END -->", activity_replacement)

    # 5. Write back to README.md
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("README.md updated successfully!")

if __name__ == "__main__":
    main()
