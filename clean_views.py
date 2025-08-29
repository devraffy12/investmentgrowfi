#!/usr/bin/env python
"""
Clean up corrupted Django dashboard code from views.py
"""

import os

def clean_views_file():
    views_path = r"c:\Users\raffy\OneDrive\Desktop\investment\myproject\views.py"
    
    # Read the file
    with open(views_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the lines to keep
    cleaned_lines = []
    skip_mode = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Start skipping at the corrupted section after investment_plans_proper
        if line_num >= 1279 and 'Calculate' in line and line.strip().startswith('#'):
            skip_mode = True
            print(f"Starting skip at line {line_num}: {line.strip()}")
            continue
            
        # Stop skipping when we hit a proper function definition
        if skip_mode and line.strip().startswith('@login_required'):
            next_line = lines[i+1] if i+1 < len(lines) else ""
            if 'def investment_plans(request):' in next_line:
                skip_mode = False
                print(f"Stopping skip at line {line_num}: {line.strip()}")
        
        # Keep the line if we're not in skip mode
        if not skip_mode:
            cleaned_lines.append(line)
        else:
            print(f"Skipping line {line_num}: {line.strip()}")
    
    # Write back the cleaned file
    with open(views_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"✅ Cleaned views.py - removed {len(lines) - len(cleaned_lines)} lines")
    print(f"Original: {len(lines)} lines -> Cleaned: {len(cleaned_lines)} lines")

if __name__ == "__main__":
    clean_views_file()
