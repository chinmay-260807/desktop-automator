"""
Desktop File Organizer
A Python script that automatically organizes files on Windows Desktop by categorizing
them based on file extensions and moving them into appropriate folders.
"""

import os
import sys
import shutil
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class OrganizationStats:
    """Statistics for the organization process"""
    total_files: int
    files_moved: int
    files_failed: int
    category_counts: Dict[str, int]
    duration: float


class FileCategorizer:
    """Maps file extensions to category names"""
    
    CATEGORIES = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx', '.odt'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
        'Music': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.ts', '.json'],
    }
    
    def categorize_file(self, file_path: Path) -> str:
        """
        Return category name for a file based on its extension.
        Returns 'Miscellaneous' for unrecognized or missing extensions.
        """
        # Get the file extension (lowercase for case-insensitive matching)
        extension = file_path.suffix.lower()
        
        # If no extension, return Miscellaneous
        if not extension:
            return 'Miscellaneous'
        
        # Search through categories for matching extension
        for category, extensions in self.CATEGORIES.items():
            if extension in extensions:
                return category
        
        # If no match found, return Miscellaneous
        return 'Miscellaneous'


class FileScanner:
    """Enumerate files in the Desktop directory"""
    
    def __init__(self, desktop_path: str):
        """Initialize scanner with Desktop path"""
        self.desktop_path = Path(desktop_path)
    
    def scan_files(self) -> List[Path]:
        """
        Scan Desktop directory and return list of file paths.
        Excludes subdirectories, returns only files.
        """
        files = []
        
        # Check if desktop path exists
        if not self.desktop_path.exists():
            raise FileNotFoundError(f"Desktop path does not exist: {self.desktop_path}")
        
        # Iterate through items in desktop directory
        for item in self.desktop_path.iterdir():
            # Only include files, skip directories
            if item.is_file():
                files.append(item)
        
        return files


class FolderManager:
    """Create category folders as needed"""
    
    def __init__(self, base_path: str):
        """Initialize with base Desktop path"""
        self.base_path = Path(base_path)
    
    def create_category_folder(self, category_name: str) -> Path:
        """
        Create category folder if it doesn't exist.
        Returns path to the category folder.
        Handles existing folders gracefully.
        """
        folder_path = self.base_path / category_name
        
        # Create folder if it doesn't exist (exist_ok=True handles existing folders)
        folder_path.mkdir(exist_ok=True)
        
        return folder_path


class FileMover:
    """Move files to category folders with conflict resolution"""
    
    def move_file(self, source: Path, destination_folder: Path) -> tuple[bool, Optional[str]]:
        """
        Move file from source to destination folder.
        Handles name conflicts by appending numbers (e.g., file_1.txt).
        Returns (success, error_message) tuple.
        Preserves file extension and content.
        """
        try:
            # Construct destination path
            destination = destination_folder / source.name
            
            # Resolve name conflicts if file already exists
            if destination.exists():
                destination = self._resolve_name_conflict(destination)
            
            # Move the file
            shutil.move(str(source), str(destination))
            return True, None
            
        except PermissionError as e:
            return False, f"Permission denied: {str(e)}"
        except OSError as e:
            # Catches file in use errors and other OS-level errors
            return False, f"OS error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def _resolve_name_conflict(self, destination: Path) -> Path:
        """
        Generate unique filename if destination already exists.
        Appends _1, _2, etc. before the extension.
        """
        # Get the stem (filename without extension) and suffix (extension)
        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent
        
        # Try appending numbers until we find a non-existing filename
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1


class OrganizationLogger:
    """Provide user feedback and progress tracking"""
    
    def log_start(self):
        """Log organization process start"""
        print("=" * 60)
        print("Desktop File Organizer - Starting organization process")
        print("=" * 60)
    
    def log_file_move(self, filename: str, category: str):
        """Log individual file movement"""
        print(f"  Moved: {filename} -> {category}")
    
    def log_error(self, filename: str, error: str):
        """Log error for a specific file"""
        print(f"  ERROR: {filename} - {error}")
    
    def log_summary(self, stats: OrganizationStats):
        """Log final summary with category counts and execution time"""
        print("\n" + "=" * 60)
        print("Organization Complete!")
        print("=" * 60)
        print(f"Total files processed: {stats.total_files}")
        print(f"Files moved: {stats.files_moved}")
        print(f"Files failed: {stats.files_failed}")
        print("\nFiles organized by category:")
        for category, count in sorted(stats.category_counts.items()):
            if count > 0:
                print(f"  {category}: {count}")
        print(f"\nExecution time: {stats.duration:.2f} seconds")
        print("=" * 60)


class DesktopOrganizer:
    """Coordinate the entire organization process"""
    
    def __init__(self, desktop_path: Optional[str] = None):
        """
        Initialize organizer with Desktop path.
        If None, automatically detect Windows Desktop path.
        """
        if desktop_path is None:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        self.desktop_path = desktop_path
        self.scanner = FileScanner(desktop_path)
        self.categorizer = FileCategorizer()
        self.folder_manager = FolderManager(desktop_path)
        self.file_mover = FileMover()
        self.logger = OrganizationLogger()
    
    def organize(self) -> OrganizationStats:
        """
        Execute the full organization process:
        1. Scan files
        2. Categorize each file
        3. Create necessary folders
        4. Move files to categories
        5. Return statistics
        """
        start_time = time.time()
        
        # Log start
        self.logger.log_start()
        
        # Scan files
        files = self.scanner.scan_files()
        
        # Track statistics
        total_files = len(files)
        files_moved = 0
        files_failed = 0
        category_counts = {}
        
        # Process each file
        for file_path in files:
            try:
                # Categorize the file
                category = self.categorizer.categorize_file(file_path)
                
                # Create category folder if needed
                category_folder = self.folder_manager.create_category_folder(category)
                
                # Move the file
                success, error_msg = self.file_mover.move_file(file_path, category_folder)
                
                if success:
                    files_moved += 1
                    category_counts[category] = category_counts.get(category, 0) + 1
                    self.logger.log_file_move(file_path.name, category)
                else:
                    files_failed += 1
                    self.logger.log_error(file_path.name, error_msg or "Failed to move file")
                    
            except PermissionError as e:
                files_failed += 1
                self.logger.log_error(file_path.name, f"Permission denied: {str(e)}")
            except OSError as e:
                files_failed += 1
                self.logger.log_error(file_path.name, f"OS error (file may be in use): {str(e)}")
            except Exception as e:
                files_failed += 1
                self.logger.log_error(file_path.name, f"Unexpected error: {str(e)}")
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Create statistics object
        stats = OrganizationStats(
            total_files=total_files,
            files_moved=files_moved,
            files_failed=files_failed,
            category_counts=category_counts,
            duration=duration
        )
        
        # Log summary
        self.logger.log_summary(stats)
        
        return stats


def main():
    """Main entry point for the script"""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Desktop File Organizer - Automatically organize files on your Desktop by category',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Categories:
  Images      - .jpg, .jpeg, .png, .gif, .bmp, .svg, .ico
  Documents   - .pdf, .doc, .docx, .txt, .xlsx, .pptx, .odt
  Videos      - .mp4, .avi, .mkv, .mov, .wmv, .flv
  Music       - .mp3, .wav, .flac, .aac, .ogg, .wma
  Archives    - .zip, .rar, .7z, .tar, .gz
  Code        - .py, .js, .html, .css, .java, .cpp, .c, .ts, .json
  Miscellaneous - All other file types

Example:
  python desktop_organizer.py
  python desktop_organizer.py --path "C:\\Users\\YourName\\Desktop"
        '''
    )
    
    parser.add_argument(
        '--path',
        type=str,
        default=None,
        help='Path to the directory to organize (default: Windows Desktop)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Desktop File Organizer 1.0'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Create organizer with specified or default path
        organizer = DesktopOrganizer(args.path)
        
        # Run organization
        stats = organizer.organize()
        
        # Return success
        return 0
        
    except FileNotFoundError as e:
        print("=" * 60)
        print("ERROR: Cannot access Desktop directory")
        print("=" * 60)
        print(f"Details: {str(e)}")
        print("\nPlease ensure the Desktop directory exists and is accessible.")
        print("=" * 60)
        return 1
        
    except PermissionError as e:
        print("=" * 60)
        print("ERROR: Permission denied accessing Desktop")
        print("=" * 60)
        print(f"Details: {str(e)}")
        print("\nPlease run the script with appropriate permissions.")
        print("=" * 60)
        return 1
        
    except Exception as e:
        print("=" * 60)
        print("ERROR: Unexpected error occurred")
        print("=" * 60)
        print(f"Details: {str(e)}")
        print("\nPlease report this error if it persists.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
