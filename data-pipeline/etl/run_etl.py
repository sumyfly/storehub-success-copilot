#!/usr/bin/env python3
"""
Run Complete ETL Pipeline
Generates all output files for Customer Success Platform
"""

import os
import sys

# Add the etl directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import CustomerSuccessETLPipeline


def run_complete_etl():
    """Run the complete ETL pipeline and generate all outputs"""
    print("🚀 Starting Complete CustomerSuccess ETL Pipeline...")
    print("=" * 60)

    try:
        # Initialize pipeline with correct paths
        data_path = "mock_data"
        output_path = "output"

        pipeline = CustomerSuccessETLPipeline(data_path, output_path)

        # Run complete pipeline
        print("📊 Executing ETL Pipeline...")
        result = pipeline.run(include_csv_export=True)

        # Check if result has success key (pipeline.run returns dict directly)
        print("\n✅ ETL Pipeline Completed Successfully!")
        print(
            f"⏱️  Total Execution Time: {result.get('execution_time_seconds', 0):.2f} seconds"
        )
        print(f"📁 Output Files Generated in: {pipeline.output_path}")

        # List all generated files
        output_files = []
        for root, dirs, files in os.walk(pipeline.output_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                relative_path = os.path.relpath(file_path, pipeline.output_path)
                output_files.append((relative_path, file_size))

        print(f"\n📄 Generated Files ({len(output_files)}):")
        for filename, size in sorted(output_files):
            size_kb = size / 1024
            print(f"   ├─ {filename} ({size_kb:.1f} KB)")

        # Print summary statistics from ETL report
        summary = result.get("extraction_summary", {})
        print("\n📈 ETL Statistics:")
        print(f"   ├─ Total Records Processed: {summary.get('total_records', 0)}")
        print(f"   ├─ Customers: {summary.get('customers', 0)}")
        print(f"   ├─ Sales Records: {summary.get('sales', 0)}")
        print(f"   ├─ Support Tickets: {summary.get('support', 0)}")
        print(f"   ├─ Activity Events: {summary.get('activity', 0)}")

        health_summary = result.get("health_summary", {})
        print(
            f"   ├─ Health Scores Calculated: {health_summary.get('total_customers', 0)}"
        )
        print(
            f"   └─ Average Health Score: {health_summary.get('avg_health_score', 0):.3f}"
        )

    except Exception as e:
        print(f"\n💥 ETL Pipeline Error: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n🎉 CustomerSuccess ETL Pipeline Complete!")
    print("Ready for Backend Integration Testing")
    return True


if __name__ == "__main__":
    success = run_complete_etl()
    sys.exit(0 if success else 1)
