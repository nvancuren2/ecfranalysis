import sqlite3

def add_chapter_and_subtitle_short():
    # Connect to the database
    conn = sqlite3.connect('section_2_14.db')
    cursor = conn.cursor()
    
    # Check and add chapter_short column if it doesn't exist
    cursor.execute("SELECT name FROM pragma_table_info('sections') WHERE name='chapter_short'")
    if not cursor.fetchone():
        print("Adding chapter_short column...")
        cursor.execute('ALTER TABLE sections ADD COLUMN chapter_short TEXT;')
        
        # Get all chapters and update chapter_short
        cursor.execute('SELECT rowid, chapter FROM sections')
        chapters = cursor.fetchall()
        
        for rowid, chapter in chapters:
            # Handle NULL or empty chapters
            if chapter is None or chapter.strip() == '':
                chapter_short = None
            # Handle chapters that start with "CHAPTER "
            elif chapter.startswith("CHAPTER "):
                # Split on the em dash (—) and take just the first part
                chapter_parts = chapter.replace("CHAPTER ", "").split("—")[0].strip()
                chapter_short = chapter_parts
            else:
                chapter_short = None
            
            # Update the row
            cursor.execute('UPDATE sections SET chapter_short = ? WHERE rowid = ?', 
                          (chapter_short, rowid))
    else:
        print("chapter_short column already exists")

    # Check and add subtitle_short column if it doesn't exist
    cursor.execute("SELECT name FROM pragma_table_info('sections') WHERE name='subtitle_short'")
    if not cursor.fetchone():
        print("Adding subtitle_short column...")
        cursor.execute('ALTER TABLE sections ADD COLUMN subtitle_short TEXT;')
        
        # Get all subtitles and update subtitle_short
        cursor.execute('SELECT rowid, subtitle FROM sections')
        subtitles = cursor.fetchall()
        
        for rowid, subtitle in subtitles:
            # Handle NULL or empty subtitles
            if subtitle is None or subtitle.strip() == '':
                subtitle_short = None
            # Handle subtitles that contain "Subtitle "
            elif "Subtitle " in subtitle:
                # Split on the em dash (—) and take just the first part
                subtitle_parts = subtitle.split("—")[0].strip()
                # Extract the letter after "Subtitle "
                subtitle_short = subtitle_parts.replace("Subtitle ", "")
            else:
                subtitle_short = None
            
            # Update the row
            cursor.execute('UPDATE sections SET subtitle_short = ? WHERE rowid = ?', 
                          (subtitle_short, rowid))
    else:
        print("subtitle_short column already exists")

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Run the function
if __name__ == "__main__":
    add_chapter_and_subtitle_short()