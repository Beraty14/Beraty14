#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestration compiler for ProfileOS.
Runs plugin data fetchers, triggers SVG rendering, compiles README.md.
"""

import os
import sys
import json
import re
from datetime import datetime

# Import local rendering functions
from render_svgs import flatten_dict, render_template

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    templates_dir = os.path.join(base_dir, "templates")
    readme_path = os.path.join(base_dir, "README.md")
    
    print("========================================")
    print("ProfileOS Compilation Pipeline Initialized")
    print("========================================")

    # 1. Execute live stats plugin first (GitHub API fetch)
    sys.path.insert(0, os.path.join(base_dir, "plugins"))
    try:
        import github_stats
        print("Executing Plugin: plugins/github_stats.py...")
        github_stats.main()
    except Exception as e:
        print(f"Warning: Failed to execute github_stats plugin: {e}", file=sys.stderr)

    # 2. Execute SVG Asset Rendering Engine
    try:
        import render_svgs
        print("Executing Rendering Engine: scripts/render_svgs.py...")
        render_svgs.main()
    except Exception as e:
        print(f"Error executing render_svgs: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Load variables map for Markdown compilation
    manifest_path = os.path.join(base_dir, "manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    theme_file = os.path.join(base_dir, manifest.get("theme", "themes/slate.json"))
    with open(theme_file, "r", encoding="utf-8") as f:
        theme_data = json.load(f)

    with open(os.path.join(data_dir, "static.json"), "r", encoding="utf-8") as f:
        static_data = json.load(f)
    with open(os.path.join(data_dir, "semi_dynamic.json"), "r", encoding="utf-8") as f:
        semi_dynamic_data = json.load(f)
    
    dynamic_file = os.path.join(data_dir, "dynamic.json")
    if os.path.exists(dynamic_file):
        with open(dynamic_file, "r", encoding="utf-8") as f:
            dynamic_data = json.load(f)
    else:
        dynamic_data = {"repos": 0, "followers": 0, "stars": 0, "contributions": 1420}

    # 4. Build flat variables map
    variables = {}
    variables.update(flatten_dict(theme_data))
    variables.update(flatten_dict(static_data, prefix="profile"))
    variables.update(flatten_dict(semi_dynamic_data))
    variables.update(flatten_dict(dynamic_data, prefix="dynamic"))
    
    # Inject current timestamp for build signatures
    variables["build_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    variables["cache_buster"] = str(int(datetime.now().timestamp()))

    # 5. Compile README.md from template
    readme_template_path = os.path.join(templates_dir, "README.template.md")
    if not os.path.exists(readme_template_path):
        print(f"Error: README template not found at {readme_template_path}", file=sys.stderr)
        sys.exit(1)

    with open(readme_template_path, "r", encoding="utf-8") as f:
        readme_template = f.read()

    print("Compiling final markdown document...")
    compiled_readme = render_template(readme_template, variables)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(compiled_readme)
    
    print(f"Successfully compiled ProfileOS landing page: {readme_path}")
    print("========================================")
    print("Compilation Complete: System Clean.")
    print("========================================")

if __name__ == "__main__":
    main()
