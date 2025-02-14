import json
import sqlite3
import os

# Connect to the database (sections.db)
conn = sqlite3.connect("sections.db")
cursor = conn.cursor()

# Create the agencies table (if it doesn't already exist)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS agencies (
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


def process_agency(agency):
    """
    Processes a single agency record:
      - Counts the number of regulations from its cfr_references.
      - Inserts the agency data into the agencies table.
      - Recursively processes any child agencies.
    """
    # Calculate the regulation count based on the number of cfr_references.
    regulation_count = len(agency.get("cfr_references", []))
    
    # Insert the agency's information into the table.
    cursor.execute('''
        INSERT INTO agencies (name, short_name, display_name, sortable_name, slug, regulation_count)
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
    
    # Process any children agencies recursively.
    for child in agency.get("children", []):
        process_agency(child)


def export_agency_data():
    """
    Exports agency data as JSON to be used in JavaScript.
    """
    cursor.execute('''
        SELECT name, regulation_count 
        FROM agencies 
        ORDER BY regulation_count DESC
    ''')
    
    agencies_data = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    with open("agency_data.js", "w", encoding="utf-8") as f:
        f.write("export const agencyData = ")
        json.dump(agencies_data, f, indent=2)
        f.write(";")


def main():
    # Open and load the agency.json file.
    json_file = "agency.json"
    if not os.path.exists(json_file):
        print(f"File {json_file} does not exist.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Iterate over all top-level agencies and process them.
    for agency in data.get("agencies", []):
        process_agency(agency)

    # After processing all agencies, export the data
    export_agency_data()
    
    # Close the database connection
    conn.close()


if __name__ == "__main__":
    main()
