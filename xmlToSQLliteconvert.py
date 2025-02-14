import sqlite3
import xml.etree.ElementTree as ET
import glob
import os

# ----- Setup SQLite database and table -----
conn = sqlite3.connect("section_2_14.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        div8_n TEXT,
        node TEXT,
        head TEXT,
        content TEXT,
        cita TEXT,
        title TEXT,
        subtitle TEXT,
        chapter TEXT,
        subchapter TEXT,
        part TEXT
    )
''')
conn.commit()


def insert_section(div8_elem, context):
    """
    Extract data from a DIV8 SECTION element and insert a row into the DB,
    using the current context (title, subtitle, chapter, subchapter, part).
    """
    # Get attributes from the DIV8 element
    div8_n = div8_elem.attrib.get('N', '')
    node = div8_elem.attrib.get('NODE', '')
    
    # Get the section heading from the HEAD element
    head_elem = div8_elem.find('HEAD')
    head_text = head_elem.text.strip() if head_elem is not None and head_elem.text else ''
    
    # Concatenate text from all <P> elements in the section into a single string.
    paragraphs = []
    for p in div8_elem.findall('P'):
        if p.text:
            paragraphs.append(p.text.strip())
    content_text = "\n".join(paragraphs)
    
    # Extract text from the CITA tag, if present.
    cita_elem = div8_elem.find('CITA')
    cita_text = cita_elem.text.strip() if cita_elem is not None and cita_elem.text else ''
    
    # Insert into the database using the current context variables, including subtitle
    cursor.execute('''
        INSERT INTO sections (div8_n, node, head, content, cita, title, subtitle, chapter, subchapter, part)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        div8_n,
        node,
        head_text,
        content_text,
        cita_text,
        context.get('title', ''),
        context.get('subtitle', ''),
        context.get('chapter', ''),
        context.get('subchapter', ''),
        context.get('part', '')
    ))
    conn.commit()


def traverse(element, context):
    """
    Recursively traverse the XML tree. Update context when encountering nodes:
      - DIV1 (TITLE): update title from HEAD element.
      - DIV2 (SUBTITLE): update subtitle.
      - DIV3 (CHAPTER): update chapter.
      - DIV4 (SUBCHAP): update subchapter.
      - DIV5 (PART): update part.
      - DIV8 (SECTION): extract the section content and insert a row into the DB.
    """
    # Make a local copy of the context for child elements.
    new_context = context.copy()
    tag = element.tag.upper()
    elem_type = element.attrib.get("TYPE", "").upper()

    # Update context for a TITLE node (for example, DIV1 with TYPE="TITLE")
    if tag.startswith("DIV1") and elem_type == "TITLE":
        head_elem = element.find("HEAD")
        if head_elem is not None and head_elem.text:
            new_context["title"] = head_elem.text.strip()
    elif tag.startswith("DIV2") and elem_type == "SUBTITLE":
        head_elem = element.find("HEAD")
        if head_elem is not None and head_elem.text:
            new_context["subtitle"] = head_elem.text.strip()
    elif tag.startswith("DIV3") and elem_type == "CHAPTER":
        head_elem = element.find("HEAD")
        if head_elem is not None and head_elem.text:
            new_context["chapter"] = head_elem.text.strip()
    elif tag.startswith("DIV4") and elem_type == "SUBCHAP":
        head_elem = element.find("HEAD")
        if head_elem is not None and head_elem.text:
            new_context["subchapter"] = head_elem.text.strip()
    elif tag.startswith("DIV5") and elem_type == "PART":
        head_elem = element.find("HEAD")
        if head_elem is not None and head_elem.text:
            new_context["part"] = head_elem.text.strip()
    elif tag.startswith("DIV8") and elem_type == "SECTION":
        # When a section is found, insert it into the DB
        insert_section(element, new_context)
    
    # Recursively process child elements.
    for child in element:
        traverse(child, new_context)


if __name__ == "__main__":
    # Specify the directory containing the XML files
    xml_directory = "ecfr_downloads"  # Change this to the path of your XML files directory
    xml_pattern = os.path.join(xml_directory, "*.xml")
    
    # Loop through all XML files in the specified directory
    for xml_file in glob.glob(xml_pattern):
        print(f"Processing {xml_file}")
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            traverse(root, {})
        except ET.ParseError as e:
            print(f"Error parsing {xml_file}: {e}")

    # Close the database connection when done.
    conn.close()
