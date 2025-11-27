"""
Data handling module for loading and saving datasets
"""

import json
import jsonlines
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataHandler:
    """Handles loading and saving JSON/JSONL data"""

    @staticmethod
    def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
        """Load JSONL file and return list of samples"""
        samples = []
        try:
            with jsonlines.open(file_path) as reader:
                for obj in reader:
                    samples.append(obj)
            logger.info(f"Loaded {len(samples)} samples from {file_path}")
            return samples
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSONL file: {e}")
            raise

    @staticmethod
    def load_json(file_path: str) -> Any:
        """Load JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON from {file_path}")
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSON file: {e}")
            raise

    @staticmethod
    def save_jsonl(data: List[Dict[str, Any]], file_path: str) -> None:
        """Save data as JSONL file"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with jsonlines.open(file_path, mode='w') as writer:
                for item in data:
                    writer.write(item)
            logger.info(f"Saved {len(data)} items to {file_path}")
        except Exception as e:
            logger.error(f"Error saving JSONL file: {e}")
            raise

    @staticmethod
    def save_json(data: Any, file_path: str, indent: int = 2) -> None:
        """Save data as JSON file"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            logger.info(f"Saved JSON to {file_path}")
        except Exception as e:
            logger.error(f"Error saving JSON file: {e}")
            raise

    @staticmethod
    def convert_analysis_to_dict(analysis_obj) -> Dict[str, Any]:
        """Convert analysis object to dictionary for JSON serialization"""
        if hasattr(analysis_obj, 'to_dict'):
            return analysis_obj.to_dict()
        return dict(analysis_obj)
