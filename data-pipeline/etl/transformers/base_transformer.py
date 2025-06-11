"""
Base transformer class for data transformation.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd


class BaseTransformer(ABC):
    """Abstract base class for data transformers."""

    def __init__(self):
        """Initialize transformer."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def transform(self, data: Dict) -> Dict:
        """Transform data and return processed result."""
        pass

    def clean_dataframe(self, df: pd.DataFrame, entity_name: str) -> pd.DataFrame:
        """
        Apply common data cleaning operations.

        Args:
            df: DataFrame to clean
            entity_name: Name of entity for logging

        Returns:
            Cleaned DataFrame
        """
        initial_count = len(df)

        # Remove duplicates
        df = df.drop_duplicates()

        # Log cleaning results
        duplicate_count = initial_count - len(df)
        if duplicate_count > 0:
            self.logger.info(
                f"Removed {duplicate_count} duplicate records from {entity_name}"
            )

        return df

    def validate_required_fields(
        self, df: pd.DataFrame, required_fields: List[str], entity_name: str
    ) -> bool:
        """
        Validate that required fields exist and have values.

        Args:
            df: DataFrame to validate
            required_fields: List of required field names
            entity_name: Name of entity for logging

        Returns:
            True if validation passes

        Raises:
            ValueError: If validation fails
        """
        missing_fields = set(required_fields) - set(df.columns)
        if missing_fields:
            raise ValueError(
                f"Missing required fields in {entity_name}: {missing_fields}"
            )

        # Check for null values in required fields
        null_counts = df[required_fields].isnull().sum()
        fields_with_nulls = null_counts[null_counts > 0]

        if len(fields_with_nulls) > 0:
            self.logger.warning(
                f"Null values found in {entity_name}: {fields_with_nulls.to_dict()}"
            )

        return True

    def calculate_time_windows(
        self, df: pd.DataFrame, date_column: str, windows: List[int] = [7, 30, 90]
    ) -> Dict:
        """
        Calculate metrics for different time windows.

        Args:
            df: DataFrame with date column
            date_column: Name of date column
            windows: List of days for time windows

        Returns:
            Dictionary with windowed metrics
        """
        now = datetime.now()
        windowed_data = {}

        for window_days in windows:
            cutoff_date = now - timedelta(days=window_days)
            window_df = df[df[date_column] >= cutoff_date]

            windowed_data[f"last_{window_days}_days"] = {
                "record_count": len(window_df),
                "data": window_df,
            }

        return windowed_data

    def aggregate_by_customer(
        self, df: pd.DataFrame, customer_id_col: str = "customer_id"
    ) -> pd.DataFrame:
        """
        Aggregate data by customer for analysis.

        Args:
            df: DataFrame to aggregate
            customer_id_col: Name of customer ID column

        Returns:
            Aggregated DataFrame by customer
        """
        if customer_id_col not in df.columns:
            raise ValueError(f"Customer ID column '{customer_id_col}' not found")

        return df.groupby(customer_id_col)

    def add_transformation_metadata(self, data: Dict, transformation_type: str) -> Dict:
        """
        Add metadata about the transformation.

        Args:
            data: Transformed data
            transformation_type: Type of transformation applied

        Returns:
            Data with added metadata
        """
        data["transformation_metadata"] = {
            "transformation_type": transformation_type,
            "transformed_at": datetime.now().isoformat(),
            "transformer_class": self.__class__.__name__,
        }

        return data
