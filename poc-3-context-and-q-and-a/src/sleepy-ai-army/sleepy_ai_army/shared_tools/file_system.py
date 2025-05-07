from typing import Dict, Any, List, Optional
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

def read_file(path: str) -> Dict[str, Any]:
    """
    Reads the content of a file at the specified path.

    Args:
        path: The absolute or relative path of the file to read.

    Returns:
        A dictionary containing:
            'status': 'success' or 'error'.
            'path': The path of the file attempted to be read.
            'content': The content of the file (if successful), otherwise None.
            'message': A confirmation message or error details.
    """
    logging.info(f"Attempting to read file: {path}")
    try:
        if not os.path.exists(path):
            logging.error(f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")
        if not os.path.isfile(path):
            logging.error(f"Path is not a file: {path}")
            raise IsADirectoryError(f"Path is not a file: {path}") # Or appropriate error

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        logging.info(f"Successfully read content from file: {path}")
        return {"status": "success", "path": path, "content": content, "message": f"File read successfully: {path}"}
    except FileNotFoundError as e:
        return {"status": "error", "path": path, "content": None, "message": str(e)}
    except IsADirectoryError as e:
         return {"status": "error", "path": path, "content": None, "message": str(e)}
    except IOError as e:
        logging.error(f"Error reading file {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "content": None, "message": f"Error reading file: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error reading file {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "content": None, "message": f"Unexpected error: {e}"}

def append_file(path: str, content: str) -> Dict[str, Any]:
    """
    Appends content to a file at the specified path. Creates the file if it doesn't exist.

    Args:
        path: The absolute or relative path of the file to append to.
        content: The string content to append to the file.

    Returns:
        A dictionary containing:
            'status': 'success' or 'error'.
            'path': The path of the file attempted to be appended to.
            'message': A confirmation message or error details.
    """
    logging.info(f"Attempting to append to file: {path}")
    try:
        # Ensure parent directory exists
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
             logging.info(f"Parent directory {parent_dir} does not exist. Creating it.")
             os.makedirs(parent_dir, exist_ok=True)

        with open(path, 'a', encoding='utf-8') as f:
            # Ensure content starts with a newline if file is not empty and doesn't end with one
            if f.tell() > 0:
                f.seek(0, os.SEEK_END) # Go to end to check last char
                f.seek(f.tell() - 1, os.SEEK_SET) # Go to second to last char
                if f.read(1) != '\n':
                    f.write('\n') # Add newline if missing before appending

            f.write(content)
            # Ensure newline at the end of the appended content
            if not content.endswith('\n'):
                f.write('\n')

        logging.info(f"Successfully appended content to file: {path}")
        return {"status": "success", "path": path, "message": f"Content appended successfully: {path}"}
    except IOError as e:
        logging.error(f"Error appending to file {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "message": f"Error appending to file: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error appending to file {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "message": f"Unexpected error: {e}"}

def list_directory(path: str, max_items: int = 100) -> Dict[str, Any]:
    """
    Lists the contents (files and directories) of a specified directory.

    Args:
        path: The absolute or relative path of the directory to list.
        max_items: The maximum number of items to return. Defaults to 100.

    Returns:
        A dictionary containing:
            'status': 'success' or 'error'.
            'path': The path of the directory attempted to be listed.
            'items': A list of item names (if successful), otherwise None.
            'message': A confirmation message or error details.
    """
    logging.info(f"Attempting to list directory: {path}")
    try:
        if not os.path.exists(path):
            logging.error(f"Directory not found: {path}")
            raise FileNotFoundError(f"Directory not found: {path}")
        if not os.path.isdir(path):
            logging.error(f"Path is not a directory: {path}")
            raise NotADirectoryError(f"Path is not a directory: {path}")

        items = os.listdir(path)
        limited_items = items[:max_items]
        message = f"Directory listed successfully: {path}"
        if len(items) > max_items:
            message += f" (truncated to first {max_items} items)"
            logging.warning(f"Directory listing for {path} truncated to {max_items} items.")

        logging.info(f"Successfully listed directory: {path}")
        return {"status": "success", "path": path, "items": limited_items, "message": message}
    except FileNotFoundError as e:
        return {"status": "error", "path": path, "items": None, "message": str(e)}
    except NotADirectoryError as e:
        return {"status": "error", "path": path, "items": None, "message": str(e)}
    except OSError as e:
        logging.error(f"Error listing directory {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "items": None, "message": f"Error listing directory: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error listing directory {path}: {e}", exc_info=True)
        return {"status": "error", "path": path, "items": None, "message": f"Unexpected error: {e}"}

