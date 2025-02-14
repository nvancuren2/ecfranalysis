import json
import sqlite3
import os
import time

# Connect to the database (sections.db)
conn = sqlite3.connect("section_2_14.db")
cursor = conn.cursor()

# Create the agency_regulations table if it doesn't exist.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS agency_regulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        short_name TEXT,
        display_name TEXT,
        sortable_name TEXT,
        slug TEXT,
        regulation_count INTEGER
    )
''')
conn.commit()

def get_regulation_count(title_number, chapter=None, subtitle=None):
    """
    Given a title number (e.g., 7) and optionally a chapter (e.g., 'I') or subtitle (e.g., 'C'),
    this function queries the sections table. Instead of an exact match on title,
    it uses a wildcard so that the title starts with "Title {title_number}".
    It returns the count of matching sections.
    """
    # Use a wildcard on the title so that it matches any string starting with "Title {title_number}"
    title_pattern = f"Title {title_number}%"
    
    if chapter:
        query = """
            SELECT COUNT(*)
            FROM sections
            WHERE title LIKE ? AND chapter_short = ?
        """
        print(f"Querying for title pattern: {title_pattern} and chapter: {chapter}")
        cursor.execute(query, (title_pattern, chapter))
    elif subtitle:
        query = """
            SELECT COUNT(*)
            FROM sections
            WHERE title LIKE ? AND subtitle_short = ?
        """
        print(f"Querying for title pattern: {title_pattern} and subtitle: {subtitle}")
        cursor.execute(query, (title_pattern, subtitle))
    else:
        query = """
            SELECT COUNT(*)
            FROM sections
            WHERE title LIKE ?
        """
        print(f"Querying for title pattern: {title_pattern}")
        cursor.execute(query, (title_pattern,))

    count = cursor.fetchone()[0]
    print(f"Count returned: {count}")
    return count

def process_agency(agency):
    """
    Processes a single agency record:
      - Iterates over its cfr_references.
      - For each reference, queries the sections table
        and sums the counts.
      - Inserts the agency information along with the total regulation_count.
      - Processes any child agencies recursively.
    """
    regulation_count = 0

    # Iterate over each CFR reference for the agency.
    for ref in agency.get("cfr_references", []):
        title_number = ref.get("title")
        chapter = ref.get("chapter")
        subtitle = ref.get("subtitle")
        
        # Validation checks
        if chapter and subtitle:
            print(f"Warning: CFR reference has both chapter and subtitle set for agency {agency.get('name')}: {ref}")
            continue
            
        if not (chapter or subtitle):
            print(f"Warning: CFR reference has neither chapter nor subtitle for agency {agency.get('name')}: {ref}")
            continue
        
        # Get count based on available reference information
        if chapter:
            count = get_regulation_count(title_number, chapter=chapter)
        else:  # must be subtitle based on validation above
            count = get_regulation_count(title_number, subtitle=subtitle)
            
        regulation_count += count

    # Insert the agency record with its regulation count into the new table.
    cursor.execute('''
        INSERT INTO agency_regulations (name, short_name, display_name, sortable_name, slug, regulation_count)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        agency.get("name", ""),
        agency.get("short_name", ""),
        agency.get("display_name", ""),
        agency.get("sortable_name", ""),
        agency.get("slug", ""),
        regulation_count
    ))
    conn.commit()

    # Process any child agencies recursively.
    for child in agency.get("children", []):
        process_agency(child)

def main():
    # Clear the existing table before processing
    cursor.execute('DELETE FROM agency_regulations')
    conn.commit()
    
    # Open and load the agency.json file.
    json_file = "agency.json"
    if not os.path.exists(json_file):
        print(f"File {json_file} not found.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Process each top-level agency.
    for agency in data.get("agencies", []):
        process_agency(agency)

    conn.close()
    print("Agency regulation counts have been processed and stored.")

if __name__ == "__main__":
    main()
