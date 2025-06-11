"""
Base loader class for data output.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd


class BaseLoader(ABC):
    """Abstract base class for data loaders."""

    def __init__(self, output_path: str):
        """
        Initialize loader with output path.

        Args:
            output_path: Path to the output directory
        """
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def load(self, data: Dict, filename: str) -> bool:
        """Load data to output destination."""
        pass

    def save_json(self, data: Dict, filename: str, indent: int = 2) -> bool:
        """
        Save data as JSON file.

        Args:
            data: Data to save
            filename: Output filename
            indent: JSON indentation level

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.output_path / filename

            # Convert pandas objects to serializable format
            serializable_data = self._make_serializable(data)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(serializable_data, f, indent=indent, ensure_ascii=False)

            self.logger.info(
                f"Successfully saved {filename} ({self._get_file_size(file_path)})"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error saving {filename}: {str(e)}")
            return False

    def save_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """
        Save DataFrame as CSV file.

        Args:
            df: DataFrame to save
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.output_path / filename
            df.to_csv(file_path, index=False)

            self.logger.info(f"Successfully saved {filename} ({len(df)} records)")
            return True

        except Exception as e:
            self.logger.error(f"Error saving {filename}: {str(e)}")
            return False

    def _make_serializable(self, data: Any) -> Any:
        """
        Convert data to JSON-serializable format.

        Args:
            data: Data to convert

        Returns:
            JSON-serializable data
        """
        import numpy as np

        if isinstance(data, pd.DataFrame):
            return data.to_dict("records")
        elif isinstance(data, pd.Series):
            return data.to_dict()
        elif isinstance(data, (pd.Timestamp, datetime)):
            return data.isoformat()
        elif isinstance(data, np.integer):
            return int(data)
        elif isinstance(data, np.floating):
            return float(data)
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, dict):
            return {k: self._make_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_serializable(item) for item in data]
        elif pd.isna(data):
            return None
        else:
            return data

    def _get_file_size(self, file_path: Path) -> str:
        """Get human-readable file size."""
        size_bytes = file_path.stat().st_size

        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / 1024**2:.1f} MB"
        else:
            return f"{size_bytes / 1024**3:.1f} GB"

    def get_output_summary(self) -> Dict[str, Any]:
        """Get summary of output files."""
        output_files = list(self.output_path.glob("*"))

        return {
            "output_directory": str(self.output_path),
            "total_files": len(output_files),
            "files": [
                {
                    "name": f.name,
                    "size": self._get_file_size(f),
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                }
                for f in output_files
            ],
        }
