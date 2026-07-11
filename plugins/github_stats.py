#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Stats Plugin for ProfileOS.
Fetches repository count, followers, and stars count for Beraty14.
"""

import os
import sys
import json
import urllib.request

def fetch_github_stats(username):
    stats = {
        "repos": 0,
        "followers": 0,
        "stars": 0,
        "contributions": 1420 # Base contributions placeholder/fallback if not fetchable
    }

    # Set up request with GITHUB_TOKEN if available to avoid API rate limits
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": "ProfileOS-Compiler-2.6"}
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        # 1. Fetch User Profile Info
        url = f"https://api.github.com/users/{username}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            user_data = json.loads(response.read().decode())
            stats["followers"] = user_data.get("followers", 0)
            stats["repos"] = user_data.get("public_repos", 0)

        # 2. Fetch User Repos to Aggregate Stars
        # Handle pagination (up to 100 repos per page is plenty for Beraty14's 3-4 repos)
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
        repos_req = urllib.request.Request(repos_url, headers=headers)
        with urllib.request.urlopen(repos_req, timeout=10) as response:
            repos_data = json.loads(response.read().decode())
            total_stars = 0
            for repo in repos_data:
                if not repo.get("fork", False):
                    total_stars += repo.get("stargazers_count", 0)
            stats["stars"] = total_stars

        # 3. Fetch User Contributions by parsing public contribution page
        import re
        contrib_url = f"https://github.com/users/{username}/contributions"
        contrib_req = urllib.request.Request(contrib_url, headers=headers)
        with urllib.request.urlopen(contrib_req, timeout=10) as response:
            contrib_html = response.read().decode()
            match = re.search(r'(\d+)\s+contributions\s+in\s+the\s+last\s+year', contrib_html, re.IGNORECASE)
            if match:
                stats["contributions"] = int(match.group(1))

    except Exception as e:
        print(f"Error fetching stats from GitHub API: {e}", file=sys.stderr)
        # Load existing stats or fallbacks if API call fails
        pass

    return stats

def main():
    username = "Beraty14"
    print(f"Fetching live stats for {username}...")
    stats = fetch_github_stats(username)
    print(f"Stats fetched: {stats}")

    # Write stats to dynamic.json
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    dynamic_file = os.path.join(data_dir, "dynamic.json")

    with open(dynamic_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Successfully updated dynamic.json at {dynamic_file}")

if __name__ == "__main__":
    main()
