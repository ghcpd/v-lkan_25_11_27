"""
Label Conflict Analyzer Package
Initialize package and expose main components
"""

__version__ = "1.0.0"
__author__ = "Label Conflict Analysis Team"
__description__ = "Multi-Annotator Label Conflict Detection & Resolution System"

from .conflict_analyzer import ConflictAnalyzer, SampleAnalysis
from .data_handler import DataHandler
from .pipeline import AnalysisPipeline
from .report_generator import ReportGenerator

__all__ = [
    "ConflictAnalyzer",
    "SampleAnalysis",
    "DataHandler",
    "AnalysisPipeline",
    "ReportGenerator",
]
