import re
import os

def normalise_lyrics_for_distrokid(master_lyrics):
    """
    Takes a string of master lyrics and formats it for Distrokid.
    - Removes bracketed OR parenthesised headers (e.g., [Verse], (Chorus)).
    - Removes ALL trailing punctuation from the end of each line.
    - Ensures the first letter of each line is capitalised.
    """
    normalised_lines = []
    
    # --- FIX #1: Characters to strip from the end of a line ---
    punctuation_to_strip = '.,!?;:' 
    
    for line in master_lyrics.strip().split('\n'):
        # 1. Trim whitespace from the line
        clean_line = line.strip()
        
        # --- FIX #2: Updated regex to detect [headers] OR (headers) ---
        if not clean_line or re.match(r'^\s*[\(\[].*[\)\]]\s*$', clean_line):
            continue
            
        # --- FIX #3: More robustly remove ALL trailing punctuation ---
        clean_line = clean_line.rstrip(punctuation_to_strip)
            
        # 4. Capitalise the first letter of the line
        if clean_line:
            clean_line = clean_line[0].upper() + clean_line[1:]
        
        normalised_lines.append(clean_line)
        
    return "\n".join(normalised_lines)

def process_obsidian_file(file_path):
    """
    Reads an Obsidian note, extracts the master lyrics, normalises them,
    and replaces the content in the Distrokid section.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the Master and Distrokid sections
        master_start_marker = "## Lyrics (Master Version)"
        distrokid_start_marker = "## Lyrics (Distrokid Normalised)"
        next_section_marker = "---"

        # Extract master lyrics block
        master_start_index = content.find(master_start_marker)
        if master_start_index == -1:
            print(f"Error: Could not find '{master_start_marker}' in {file_path}")
            return

        master_lyrics_block_start = master_start_index + len(master_start_marker)
        next_marker_after_master = content.find(next_section_marker, master_lyrics_block_start)
        master_lyrics_block = content[master_lyrics_block_start:next_marker_after_master].strip()
        
        # --- FIX #4: Smarter extraction to ignore the description line ---
        master_lyrics_lines = master_lyrics_block.split('\n')
        # Find the first non-empty line that isn't the italicised description
        first_lyric_line_index = 0
        for i, line in enumerate(master_lyrics_lines):
            if line.strip() and not line.strip().startswith('*'):
                first_lyric_line_index = i
                break
        master_lyrics = "\n".join(master_lyrics_lines[first_lyric_line_index:])

        # Normalise the lyrics
        distrokid_lyrics = normalise_lyrics_for_distrokid(master_lyrics)
        
        # Find the Distrokid section to replace
        distrokid_start_index = content.find(distrokid_start_marker)
        if distrokid_start_index == -1:
            print(f"Error: Could not find '{distrokid_start_marker}' in {file_path}")
            return
            
        distrokid_lyrics_block_start = distrokid_start_index + len(distrokid_start_marker)
        next_marker_after_distrokid = content.find(next_section_marker, distrokid_lyrics_block_start)

        # Clear out the old description text from the Distrokid section first
        pre_distrokid_section = content[:distrokid_lyrics_block_start]
        post_distrokid_section = content[next_marker_after_distrokid:]

        # Reconstruct the file content
        new_content = (
            pre_distrokid_section +
            f"\n\n{distrokid_lyrics}\n\n" +
            post_distrokid_section
        )

        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Successfully processed and updated: {os.path.basename(file_path)}")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    file_path_input = input("Drag and drop the Obsidian song file here and press Enter: ").strip()
    
    file_path_input = file_path_input.strip('\'"') 
        
    if os.path.exists(file_path_input):
        process_obsidian_file(file_path_input)
    else:
        print("The file path you provided does not exist.")
