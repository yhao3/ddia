#!/usr/bin/env python3
"""
Convert Markdown files to Obsidian-flavored Markdown format.
Transformations:
1. Image embeds: ![](./path) -> ![[path]]
2. Internal heading links: [text](#heading) -> [[#heading|text]]
3. Cross-chapter links: [text](./chN#heading) -> [[chN#heading|text]]
4. Figure references with links: [圖 X-Y](./v1/path.png) -> [[v1/path.png|圖 X-Y]]
5. HTML font tags: <font color="...">text</font> -> ==text==
"""

import re
import os
from pathlib import Path

def convert_image_embeds(content: str) -> str:
    """Convert ![](./path) to ![[path]]"""
    # Match ![alt](./path) where alt can be empty
    pattern = r'!\[([^\]]*)\]\(\./([^)]+)\)'
    def replace(m):
        alt = m.group(1)
        path = m.group(2)
        if alt:
            return f'![[{path}|{alt}]]'
        return f'![[{path}]]'
    return re.sub(pattern, replace, content)

def convert_internal_heading_links(content: str) -> str:
    """Convert [text](#heading) to [[#heading|text]]"""
    # Only match links starting with # (same file headings)
    pattern = r'\[([^\]]+)\]\(#([^)]+)\)'
    def replace(m):
        text = m.group(1)
        heading = m.group(2)
        return f'[[#{heading}|{text}]]'
    return re.sub(pattern, replace, content)

def convert_cross_chapter_links(content: str) -> str:
    """Convert [text](./chN#heading) or [text](./chN) to [[chN#heading|text]] or [[chN|text]]"""
    # Match links to other files (./filename or ./filename#heading)
    pattern = r'\[([^\]]+)\]\(\./([^)]+)\)'
    def replace(m):
        text = m.group(1)
        path = m.group(2)
        # All relative links become wikilinks, including image references
        return f'[[{path}|{text}]]'
    return re.sub(pattern, replace, content)

def convert_font_tags(content: str) -> str:
    """Convert <font color="...">text</font> to ==text=="""
    pattern = r'<font[^>]*>([^<]+)</font>'
    def replace(m):
        text = m.group(1)
        return f'=={text}=='
    return re.sub(pattern, replace, content)

def process_file(filepath: Path) -> tuple[bool, int]:
    """Process a single markdown file and return (modified, change_count)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    content = original

    # Apply transformations in order
    content = convert_image_embeds(content)
    content = convert_internal_heading_links(content)
    content = convert_cross_chapter_links(content)
    content = convert_font_tags(content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Count changes (rough estimate)
        changes = 0
        changes += len(re.findall(r'!\[\[', content)) - len(re.findall(r'!\[\[', original))
        changes += len(re.findall(r'\[\[#', content)) - len(re.findall(r'\[\[#', original))
        changes += len(re.findall(r'\[\[ch', content)) - len(re.findall(r'\[\[ch', original))
        changes += len(re.findall(r'==', content)) - len(re.findall(r'==', original))

        return True, abs(changes) // 2 if changes > 0 else 1

    return False, 0

def main():
    base_dir = Path(__file__).parent
    md_files = list(base_dir.glob('*.md'))

    total_modified = 0
    total_changes = 0

    for filepath in sorted(md_files):
        modified, changes = process_file(filepath)
        if modified:
            total_modified += 1
            total_changes += changes
            print(f"✓ {filepath.name}: {changes} changes")
        else:
            print(f"  {filepath.name}: no changes")

    print(f"\nSummary: Modified {total_modified} files with approximately {total_changes} changes")

if __name__ == '__main__':
    main()