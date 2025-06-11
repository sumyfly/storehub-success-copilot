"""
Base extractor class for CSV data extraction.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class BaseExtractor(ABC):
    """Abstract base class for data extractors."""

    def __init__(self, data_path: str):
        """
        Initialize extractor with data path.

        Args:
            data_path: Path to the data directory
        """
        self.data_path = Path(data_path)
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_csv(
        self, filename: str, required_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Extract data from CSV file with validation.

        Args:
            filename: Name of CSV file
            required_columns: List of required column names for validation

        Returns:
            DataFrame with extracted data

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        file_path = self.data_path / filename

        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Loaded {len(df)} records from {filename}")

            # Validate required columns
            if required_columns:
                missing_cols = set(required_columns) - set(df.columns)
                if missing_cols:
                    raise ValueError(
                        f"Missing required columns in {filename}: {missing_cols}"
                    )

            return df

        except Exception as e:
            self.logger.error(f"Error reading {filename}: {str(e)}")
            raise

    @abstractmethod
    def extract(self) -> Dict:
        """Extract and return data specific to this extractor."""
        pass

    def validate_data_quality(self, df: pd.DataFrame, entity_name: str) -> Dict:
        """
        Validate basic data quality metrics.

        Args:
            df: DataFrame to validate
            entity_name: Name of entity for logging

        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            "total_records": len(df),
            "null_counts": df.isnull().sum().to_dict(),
            "duplicate_count": df.duplicated().sum(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
        }

        self.logger.info(f"{entity_name} quality metrics: {metrics}")
        return metrics
