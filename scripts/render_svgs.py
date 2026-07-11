#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVG Template Renderer for ProfileOS.
Loads theme tokens and data files, resolves placeholders, and writes final SVGs.
"""

import os
import json
import re

def flatten_dict(d, prefix=''):
    flat = {}
    if isinstance(d, dict):
        for k, v in d.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            flat.update(flatten_dict(v, new_prefix))
    elif isinstance(d, list):
        for idx, v in enumerate(d):
            new_prefix = f"{prefix}[{idx}]"
            flat.update(flatten_dict(v, new_prefix))
    else:
        flat[prefix] = str(d)
    return flat

def render_template(template_str, variables):
    # Matches placeholders like {profile.name} or {colors.bg_start}
    # CSS rules like { opacity: 0.25; } won't match as they are not keys in variables
    pattern = re.compile(r'\{([a-zA-Z0-9_\.\[\]\-]+)\}')
    
    def replacer(match):
        key = match.group(1)
        return variables.get(key, match.group(0))
        
    return pattern.sub(replacer, template_str)

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    themes_dir = os.path.join(base_dir, "themes")
    templates_dir = os.path.join(base_dir, "templates")
    assets_dir = os.path.join(base_dir, "assets")
    
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Load manifest and verify active theme
    manifest_path = os.path.join(base_dir, "manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    theme_file = os.path.join(base_dir, manifest.get("theme", "themes/slate.json"))
    with open(theme_file, "r", encoding="utf-8") as f:
        theme_data = json.load(f)

    # 2. Load data files
    with open(os.path.join(data_dir, "static.json"), "r", encoding="utf-8") as f:
        static_data = json.load(f)
    with open(os.path.join(data_dir, "semi_dynamic.json"), "r", encoding="utf-8") as f:
        semi_dynamic_data = json.load(f)
    
    # Pre-calculate progress widths for SVG bar rendering (total scale is 220px)
    for project in semi_dynamic_data.get("projects", []):
        progress = project.get("progress", 0)
        project["progress_width"] = str(int(220 * (progress / 100.0)))
    
    dynamic_file = os.path.join(data_dir, "dynamic.json")
    if os.path.exists(dynamic_file):
        with open(dynamic_file, "r", encoding="utf-8") as f:
            dynamic_data = json.load(f)
    else:
        dynamic_data = {"repos": 0, "followers": 0, "stars": 0, "contributions": 1420}

    # 3. Build flat variables map
    variables = {}
    variables.update(flatten_dict(theme_data))
    variables.update(flatten_dict(static_data, prefix="profile"))
    variables.update(flatten_dict(semi_dynamic_data))
    variables.update(flatten_dict(dynamic_data, prefix="dynamic"))

    # 4. Render and compile each SVG widget template
    widgets = manifest.get("widgets", [])
    print(f"Starting SVG compilation for widgets: {widgets}...")

    for widget in widgets:
        template_name = f"{widget}.template.svg"
        template_path = os.path.join(templates_dir, template_name)
        
        if not os.path.exists(template_path):
            print(f"Warning: Template not found: {template_path}")
            continue
            
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        rendered_content = render_template(template_content, variables)
        # Convert double curly braces (escaped for format() originally) to single braces for valid CSS
        rendered_content = rendered_content.replace("{{", "{").replace("}}", "}")
        
        output_path = os.path.join(assets_dir, f"{widget}_v26.svg")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_content)
        print(f"Compiled: {output_path}")

    # 5. Compile individual project cards dynamically
    project_card_template_path = os.path.join(templates_dir, "project_card.template.svg")
    if os.path.exists(project_card_template_path):
        with open(project_card_template_path, "r", encoding="utf-8") as f:
            card_template = f.read()
        for project in semi_dynamic_data.get("projects", []):
            proj_title = project.get("title").lower()
            # Build variables map for this specific project card
            card_variables = {}
            card_variables.update(flatten_dict(theme_data))
            card_variables.update(flatten_dict(project, prefix="project"))
            
            rendered_card = render_template(card_template, card_variables)
            rendered_card = rendered_card.replace("{{", "{").replace("}}", "}")
            
            output_card_path = os.path.join(assets_dir, f"project_{proj_title}_v26.svg")
            with open(output_card_path, "w", encoding="utf-8") as f:
                f.write(rendered_card)
            print(f"Compiled Project Card: {output_card_path}")

    print("SVG rendering engine execution complete.")

if __name__ == "__main__":
    main()
