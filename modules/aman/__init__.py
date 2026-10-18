"""
modules/aman/__init__.py
========================
Aman's module for the Smart File Manager project.

Exposes the three core OS functions and the recommendation service
so that teammates can import them directly from `modules.aman`.
"""

from .file_classifier import classify_file
from .duplicate_detector import find_duplicates, calculate_sha256
from .allocation_recommender import recommend_storage
from .recommendation_service import generate_recommendation

__all__ = [
    "classify_file",
    "find_duplicates",
    "calculate_sha256",
    "recommend_storage",
    "generate_recommendation",
]
