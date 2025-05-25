import asyncio
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from src.config import AppConfig
from src.services.write_file_from_template_service import \
    WriteFileFromTemplateService
from src.utils.logging_setup import setup_logging

# Get a logger for this test script
logger = logging.getLogger(__name__)

# --- Constants for the test ---
TEMP_TEST_DIR_NAME = "temp_write_service_test_data"
TEMPLATE_SUBDIR = "templates"
OUTPUT_SUBDIR = "output"
SAMPLE_TEMPLATE_FILENAME = "test_template.txt.j2"
SAMPLE_OUTPUT_FILENAME = "test_output.txt"
# --- End Constants ---

async def run_write_file_service_test(
    app_config: AppConfig, 
    service: WriteFileFromTemplateService,
    temp_base_path: Path
):
    """
    Executes a golden path test for WriteFileFromTemplateService.render_and_write_file.
    """
    logger.overview("--- Starting WriteFileFromTemplateService Golden Path Test ---")

    context = {
        "name": "Test User",
        "timestamp": datetime.now().isoformat(),
        "app_config": app_config # Pass the whole app_config for demonstration
    }

    # 2. Define paths
    template_dir = temp_base_path / TEMPLATE_SUBDIR
    output_dir = temp_base_path / OUTPUT_SUBDIR
    
    template_file_abs_path = template_dir / SAMPLE_TEMPLATE_FILENAME
    output_file_abs_path = output_dir / SAMPLE_OUTPUT_FILENAME

    logger.debug(f"Sample template file path: {template_file_abs_path.resolve()}")
    logger.debug(f"Sample output file path: {output_file_abs_path.resolve()}")

    # 4. Call the service method
    logger.info(f"Attempting to call service.render_and_write_file...")
    logger.info(f"  Template: {template_file_abs_path}")
    logger.info(f"  Output:   {output_file_abs_path}")
    logger.info(f"  Context:  { {k: v if k != 'app_config' else 'AppConfig(...)' for k, v in context.items()} }") # Avoid logging full AppConfig

    try:
        success = service.render_and_write_file(
            template_abs_path_str=str(template_file_abs_path),
            context=context,
            output_abs_path_str=str(output_file_abs_path)
        )

        logger.info(f"service.render_and_write_file returned: {success}")

        if success:
            logger.info(f"Successfully rendered and wrote file to: {output_file_abs_path}")
            if output_file_abs_path.is_file():
                logger.info("Output file exists. Reading content...")
                with open(output_file_abs_path, "r", encoding="utf-8") as f:
                    output_content = f.read()
                logger.overview("--- Generated File Content ---")
                # Use a print here for direct console visibility during testing, in addition to log
                print("\n--- BEGIN Generated File Content ---")
                print(output_content)
                print("--- END Generated File Content ---\n")
                logger.info(f"Content of '{SAMPLE_OUTPUT_FILENAME}':\n{output_content}")
            else:
                logger.error("Service reported success, but output file was not found!")
        else:
            logger.error("Service reported failure. Check logs from WriteFileFromTemplateService for details.")

    except Exception as e:
        logger.error(f"An error occurred during service.render_and_write_file call: {e}", exc_info=True)

    logger.overview("--- WriteFileFromTemplateService Golden Path Test Finished ---")
    logger.overview(f"*** Please MANUALLY VERIFY the console output and log files for correctness. ***")
    logger.overview(f"*** Temporary files were located in: {temp_base_path.resolve()} (should be cleaned up). ***")


if __name__ == "__main__":
    # Load environment variables from .env file, if present
    if load_dotenv():
        print("Loaded .env file.")
    else:
        print("No .env file found or it is empty.")

    # Initialize a basic logger for messages prior to full logging setup
    main_logger = logging.getLogger(__name__)

    app_config = None
    try:
        # Load application configuration
        # Assuming config.yml is in the project root relative to where this script is run from
        # Adjust path if necessary, e.g., Path(__file__).resolve().parent.parent / "config.yml"
        app_config = AppConfig.load_from_yaml() 

        # Setup logging system based on AppConfig
        setup_logging(app_config=app_config)
        
        main_logger.overview("\n\n====== Starting WriteFileFromTemplateService Test Script ======")
        main_logger.info("AppConfig loaded and logging configured successfully.")
    except Exception as e:
        main_logger.error("Failed to load AppConfig or setup logging.", exc_info=True)
        main_logger.error("Cannot proceed with tests without AppConfig and logging.")
        main_logger.info("====== WriteFileFromTemplateService Test Script Aborted ======")
        sys.exit(1)

    write_file_service = None
    try:
        # Instantiate WriteFileFromTemplateService
        main_logger.info("Initializing WriteFileFromTemplateService...")
        write_file_service = WriteFileFromTemplateService()
        main_logger.overview("WriteFileFromTemplateService instantiated successfully.")
    except Exception as e:
        main_logger.error(f"An unexpected error occurred while instantiating WriteFileFromTemplateService: {e}", exc_info=True)
        main_logger.info("====== WriteFileFromTemplateService Test Script Aborted ======")
        sys.exit(1)

    # Define temporary directory path (e.g., in tests/ relative to project root)
    # Assuming this script is in 'tests/' and project root is its parent.
    project_root = Path(__file__).resolve().parent.parent 
    temp_test_root_path = project_root / "tests" / TEMP_TEST_DIR_NAME
    main_logger.info(f"Temporary test data base directory: {temp_test_root_path.resolve()}")

    try:
        # Create the base temporary directory before running the test
        # The test function itself will create subdirectories
        temp_test_root_path.mkdir(parents=True, exist_ok=True)
        main_logger.debug(f"Ensured base temporary directory exists: {temp_test_root_path}")

        # Execute the WriteFileFromTemplateService method tests
        asyncio.run(run_write_file_service_test(app_config, write_file_service, temp_test_root_path))
    
    except Exception as e:
        main_logger.error(f"An error occurred while running the test function: {e}", exc_info=True)
    
    # finally:
    #     # Teardown: Clean up temporary directory
    #     main_logger.info(f"Attempting to clean up temporary directory: {temp_test_root_path.resolve()}")
    #     if temp_test_root_path.exists():
    #         try:
    #             shutil.rmtree(temp_test_root_path)
    #             main_logger.info(f"Successfully removed temporary directory: {temp_test_root_path.resolve()}")
    #         except OSError as e:
    #             main_logger.error(f"Error removing temporary directory {temp_test_root_path.resolve()}: {e}", exc_info=True)
    #             main_logger.warning("Manual cleanup of temporary directory may be required.")
    #     else:
    #         main_logger.info("Temporary directory did not exist, no cleanup needed.")

    main_logger.overview("====== WriteFileFromTemplateService Test Script Finished ======")
