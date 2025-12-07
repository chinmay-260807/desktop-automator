"""
Tests for Desktop File Organizer
Includes both unit tests and property-based tests using Hypothesis
"""

import pytest
from hypothesis import given, strategies as st
from pathlib import Path
import tempfile
import os

from desktop_organizer import (
    FileCategorizer,
    FileScanner,
    FolderManager,
    FileMover,
    OrganizationLogger,
    DesktopOrganizer,
    OrganizationStats
)


# Unit tests will be added here as we implement features

# Property-based tests will be added here as we implement features
