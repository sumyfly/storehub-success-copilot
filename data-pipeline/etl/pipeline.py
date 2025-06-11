"""
Main ETL Pipeline for Customer Success Health Score Calculation.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from calculators import HealthScoreCalculator

# Import ETL components
from extractors import CombinedExtractor
from loaders import (
    AlertDataLoader,
    CustomerDataLoader,
    DataExportLoader,
    ETLReportLoader,
    HealthScoreLoader,
)
from transformers import (
    ActivityDataTransformer,
    CustomerDataTransformer,
    DataIntegrationTransformer,
    SalesDataTransformer,
    SupportDataTransformer,
)


class CustomerSuccessETLPipeline:
    """
    Main ETL Pipeline for Customer Success Health Score Calculation.

    Orchestrates the complete process:
    1. Extract data from CSV sources
    2. Transform and clean data
    3. Calculate health scores using 8-dimension algorithm
    4. Load results to JSON outputs
    """

    def __init__(self, data_path: str, output_path: str):
        """
        Initialize ETL pipeline.

        Args:
            data_path: Path to CSV data files
            output_path: Path for output files
        """
        self.data_path = Path(data_path)
        self.output_path = Path(output_path)

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize components
        self.extractor = CombinedExtractor(str(self.data_path))
        self.health_calculator = HealthScoreCalculator()

        # Initialize transformers
        self.customer_transformer = CustomerDataTransformer()
        self.sales_transformer = SalesDataTransformer()
        self.support_transformer = SupportDataTransformer()
        self.activity_transformer = ActivityDataTransformer()
        self.integration_transformer = DataIntegrationTransformer()

        # Initialize loaders
        self.health_loader = HealthScoreLoader(str(self.output_path))
        self.report_loader = ETLReportLoader(str(self.output_path))
        self.customer_loader = CustomerDataLoader(str(self.output_path))
        self.alert_loader = AlertDataLoader(str(self.output_path))
        self.export_loader = DataExportLoader(str(self.output_path))

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    f"etl_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                ),
                logging.StreamHandler(),
            ],
        )
        return logging.getLogger("ETLPipeline")

    def run(self, include_csv_export: bool = True) -> Dict[str, Any]:
        """
        Execute the complete ETL pipeline.

        Args:
            include_csv_export: Whether to export CSV files

        Returns:
            Dictionary with execution results and metrics
        """
        start_time = time.time()
        self.logger.info("🚀 Starting Customer Success ETL Pipeline")

        try:
            # Phase 1: Data Extraction
            self.logger.info("📥 Phase 1: Data Extraction")
            extraction_results = self._extract_data()

            # Phase 2: Data Transformation
            self.logger.info("🔄 Phase 2: Data Transformation")
            transformation_results = self._transform_data(extraction_results)

            # Phase 3: Health Score Calculation
            self.logger.info("🧮 Phase 3: Health Score Calculation")
            calculation_results = self._calculate_health_scores(transformation_results)

            # Phase 4: Data Loading
            self.logger.info("💾 Phase 4: Data Loading")
            loading_results = self._load_data(calculation_results, include_csv_export)

            # Generate execution report
            end_time = time.time()
            execution_report = self._generate_execution_report(
                extraction_results,
                transformation_results,
                calculation_results,
                loading_results,
                start_time,
                end_time,
            )

            self.logger.info(
                f"✅ ETL Pipeline completed successfully in {end_time - start_time:.2f} seconds"
            )
            return execution_report

        except Exception as e:
            self.logger.error(f"❌ ETL Pipeline failed: {str(e)}")
            raise

    def _extract_data(self) -> Dict[str, Any]:
        """Extract data from all CSV sources."""
        self.logger.info("Extracting data from CSV files...")

        extraction_start = time.time()
        extracted_data = self.extractor.extract()
        extraction_time = time.time() - extraction_start

        # Log extraction summary
        summary = extracted_data.get("extraction_summary", {})
        self.logger.info(
            f"Extracted {summary.get('total_records', 0)} total records in {extraction_time:.2f}s"
        )

        return extracted_data

    def _transform_data(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """Transform and integrate all data sources."""
        self.logger.info("Transforming and integrating data...")

        transformation_start = time.time()

        # Transform each data source
        customer_transformed = self.customer_transformer.transform(
            extraction_results["customers"]
        )
        sales_transformed = self.sales_transformer.transform(
            extraction_results["sales"]
        )
        support_transformed = self.support_transformer.transform(
            extraction_results["support"]
        )
        activity_transformed = self.activity_transformer.transform(
            extraction_results["activity"]
        )

        # Integrate all transformed data
        integration_data = {
            "customers": customer_transformed,
            "sales": sales_transformed,
            "support": support_transformed,
            "activity": activity_transformed,
        }

        integrated_data = self.integration_transformer.transform(integration_data)

        transformation_time = time.time() - transformation_start
        self.logger.info(
            f"Transformed and integrated data in {transformation_time:.2f}s"
        )

        return {
            "customers": customer_transformed,
            "sales": sales_transformed,
            "support": support_transformed,
            "activity": activity_transformed,
            "integration": integrated_data,
        }

    def _calculate_health_scores(
        self, transformation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate health scores for all customers."""
        self.logger.info("Calculating health scores...")

        calculation_start = time.time()

        # Get integrated data
        integrated_data = transformation_results["integration"]["integrated_data"]

        # Calculate health scores
        health_scored_data = self.health_calculator.calculate_health_scores(
            integrated_data
        )

        # Get summary statistics
        health_summary = self.health_calculator.get_health_summary(health_scored_data)

        calculation_time = time.time() - calculation_start
        self.logger.info(
            f"Calculated health scores for {health_summary['total_customers']} customers "
            f"(avg: {health_summary['avg_health_score']:.3f}) in {calculation_time:.2f}s"
        )

        return {
            "integrated_data": health_scored_data,
            "health_summary": health_summary,
            "calculation_time": calculation_time,
        }

    def _load_data(
        self, calculation_results: Dict[str, Any], include_csv_export: bool = True
    ) -> Dict[str, Any]:
        """Load results to output files."""
        self.logger.info("Loading results to output files...")

        loading_start = time.time()
        loading_results = {}

        # Load health scores
        loading_results["health_scores"] = self.health_loader.load(
            calculation_results, "health_scores.json"
        )

        # Load customer data (API format)
        loading_results["customer_data"] = self.customer_loader.load(
            calculation_results, "customer_data.json"
        )

        # Generate and load alerts
        loading_results["alerts"] = self.alert_loader.load(
            calculation_results, "alerts.json"
        )

        # Export CSV files if requested
        if include_csv_export:
            loading_results["csv_export"] = self.export_loader.export_csv_files(
                calculation_results
            )

        loading_time = time.time() - loading_start
        self.logger.info(f"Loaded all outputs in {loading_time:.2f}s")

        return loading_results

    def _generate_execution_report(
        self,
        extraction_results: Dict,
        transformation_results: Dict,
        calculation_results: Dict,
        loading_results: Dict,
        start_time: float,
        end_time: float,
    ) -> Dict[str, Any]:
        """Generate comprehensive execution report."""

        total_time = end_time - start_time

        # Collect metrics
        extraction_summary = extraction_results.get("extraction_summary", {})
        health_summary = calculation_results.get("health_summary", {})
        integration_quality = transformation_results.get("integration", {}).get(
            "integration_quality", {}
        )

        report = {
            "execution_metadata": {
                "pipeline_version": "1.0",
                "executed_at": datetime.fromtimestamp(start_time).isoformat(),
                "completed_at": datetime.fromtimestamp(end_time).isoformat(),
                "total_execution_time_seconds": total_time,
                "status": "completed",
            },
            "data_processing_summary": {
                "total_records_processed": extraction_summary.get("total_records", 0),
                "customers_processed": health_summary.get("total_customers", 0),
                "avg_health_score": health_summary.get("avg_health_score", 0),
                "health_score_distribution": health_summary.get(
                    "health_distribution", {}
                ),
                "risk_level_distribution": health_summary.get("risk_distribution", {}),
            },
            "data_quality_metrics": {
                "integration_coverage": {
                    "sales_coverage_pct": integration_quality.get(
                        "sales_coverage_pct", 0
                    ),
                    "support_coverage_pct": integration_quality.get(
                        "support_coverage_pct", 0
                    ),
                    "activity_coverage_pct": integration_quality.get(
                        "activity_coverage_pct", 0
                    ),
                },
                "factor_performance": health_summary.get("factor_averages", {}),
            },
            "output_status": loading_results,
            "performance_metrics": {
                "extraction_time": extraction_summary.get("extraction_time_seconds", 0),
                "calculation_time": calculation_results.get("calculation_time", 0),
                "records_per_second": extraction_summary.get("total_records", 0)
                / total_time
                if total_time > 0
                else 0,
            },
        }

        # Save execution report
        self.report_loader.load(
            {
                "extraction": extraction_results,
                "transformation": transformation_results,
                "calculation": health_summary,
                "total_time": total_time,
                "total_records": extraction_summary.get("total_records", 0),
            },
            "etl_execution_report.json",
        )

        return report


def main():
    """Main entry point for ETL pipeline execution."""
    from pathlib import Path

    # Default paths
    current_dir = Path(__file__).parent
    data_path = current_dir / "mock_data"
    output_path = current_dir / "output"

    # Initialize and run pipeline
    pipeline = CustomerSuccessETLPipeline(str(data_path), str(output_path))

    try:
        results = pipeline.run(include_csv_export=True)

        print("\n🎉 ETL Pipeline Execution Summary:")
        print(
            f"├─ Total Time: {results['execution_metadata']['total_execution_time_seconds']:.2f}s"
        )
        print(
            f"├─ Customers Processed: {results['data_processing_summary']['customers_processed']}"
        )
        print(
            f"├─ Average Health Score: {results['data_processing_summary']['avg_health_score']:.3f}"
        )
        print(
            f"└─ Output Files Generated: {len([k for k, v in results['output_status'].items() if v])}"
        )

        return 0

    except Exception as e:
        print(f"❌ Pipeline execution failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
