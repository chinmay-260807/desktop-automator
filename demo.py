"""
Demo script to showcase the Desktop File Organizer
Creates a demo directory with sample files and organizes them
"""

import tempfile
import subprocess
import sys
from pathlib import Path
import time

print("=" * 70)
print("DESKTOP FILE ORGANIZER - DEMO")
print("=" * 70)
print()

# Create a temporary demo directory
with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)
    
    print("Step 1: Creating a messy directory with various file types...")
    print("-" * 70)
    
    # Create sample files
    demo_files = {
        "vacation_photo.jpg": b"fake image",
        "family_pic.png": b"fake image",
        "work_report.pdf": b"fake pdf",
        "meeting_notes.txt": b"some notes",
        "budget.xlsx": b"fake excel",
        "presentation.pptx": b"fake ppt",
        "tutorial_video.mp4": b"fake video",
        "favorite_song.mp3": b"fake music",
        "podcast.wav": b"fake audio",
        "project_backup.zip": b"fake archive",
        "website.html": b"<html></html>",
        "styles.css": b"body {}",
        "app.js": b"console.log('hi')",
        "script.py": b"print('hello')",
        "random_file.xyz": b"unknown",
    }
    
    for filename, content in demo_files.items():
        (temp_path / filename).write_bytes(content)
        print(f"  Created: {filename}")
    
    print(f"\nTotal: {len(demo_files)} files created")
    print()
    
    input("Press Enter to organize these files...")
    print()
    
    print("Step 2: Running Desktop File Organizer...")
    print("-" * 70)
    print()
    
    # Run the organizer
    result = subprocess.run(
        [sys.executable, "desktop_organizer.py", "--path", str(temp_path)],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    print()
    print("Step 3: Viewing organized structure...")
    print("-" * 70)
    
    # Show the organized structure
    for category_folder in sorted(temp_path.iterdir()):
        if category_folder.is_dir():
            files_in_category = list(category_folder.iterdir())
            print(f"\n📁 {category_folder.name}/ ({len(files_in_category)} files)")
            for file in sorted(files_in_category):
                print(f"   └─ {file.name}")
    
    print()
    print("=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print()
    print("Your Desktop can be this organized too!")
    print("Just run: python desktop_organizer.py")
    print()
