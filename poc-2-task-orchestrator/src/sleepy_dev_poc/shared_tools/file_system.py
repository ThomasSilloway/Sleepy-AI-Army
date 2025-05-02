from typing import Dict, Any
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_directory(path: str, create_parents: bool = True) -> Dict[str, Any]:
    """
    Creates a directory at the specified path.

    Args:
        path: The absolute or relative path of the directory to create.
        create_parents: If True, creates any necessary parent directories.
                        If False, raises an error if the parent doesn't exist.

    Returns:
        A dictionary containing:
            'status': 'success' or 'error'.
            'path': The path of the directory attempted to be created.
            'message': A confirmation message or error details.
    """
    logging.info(f"Attempting to create directory: {path}")
    try:
        if create_parents:
            os.makedirs(path, exist_ok=True)
            logging.info(f"Successfully created directory (or it already existed): {path}")
            return {"status": "success", "path": path, "message": f"Directory created or already exists: {path}"}
        else:
            if os.path.exists(path):
                 logging.warning(f"Directory already exists: {path}")
                 return {"status": "success", "path": path, "message": f"Directory already exists: {path}"}
            elif not os.path.exists(os.path.dirname(path)):
                logging.error(f"Parent directory does not exist for path: {path}")
                raise FileNotFoundError(f"Parent directory does not exist: {os.path.dirname(path)}")
            else:
                os.mkdir(path)
                logging.info(f"Successfully created directory: {path}")
                return {"status": "success", "path": path, "message": f"Directory created: {path}"}
    except OSError as e:
        logging.error(f"Error creating directory {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "message": f"Error creating directory: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error creating directory {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "message": f"Unexpected error: {e}"}

def write_file(path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Writes content to a file at the specified path.

    Args:
        path: The absolute or relative path of the file to write.
        content: The string content to write to the file.
        overwrite: If True, overwrites the file if it exists.
                   If False, raises an error if the file exists.

    Returns:
        A dictionary containing:
            'status': 'success' or 'error'.
            'path': The path of the file attempted to be written.
            'message': A confirmation message or error details.
    """
    logging.info(f"Attempting to write file: {path} (overwrite={overwrite})")
    try:
        if not overwrite and os.path.exists(path):
            logging.error(f"File already exists and overwrite is False: {path}")
            raise FileExistsError(f"File already exists: {path}")

        # Ensure parent directory exists
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
             logging.info(f"Parent directory {parent_dir} does not exist. Creating it.")
             os.makedirs(parent_dir, exist_ok=True)

        mode = 'w' # Default to write mode (overwrite or create)
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
            # Ensure newline at the end of the file as per best practices
            if not content.endswith('\n'):
                f.write('\n')

        logging.info(f"Successfully wrote content to file: {path}")
        return {"status": "success", "path": path, "message": f"File written successfully: {path}"}
    except FileExistsError as e:
         # Already logged above
        return {"status": "error", "path": path, "message": str(e)}
    except IOError as e:
        logging.error(f"Error writing file {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "message": f"Error writing file: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error writing file {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "message": f"Unexpected error: {e}"}
