"""Defines the WriteFileFromTemplateService class."""
import logging
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, exceptions, select_autoescape

logger = logging.getLogger(__name__)

class WriteFileFromTemplateService:
    """
    A service class responsible for rendering files using Jinja2 templates
    and writing them to disk.
    """

    def __init__(self):
        """Initializes the WriteFileFromTemplateService."""
        pass

    def render_and_write_file(
        self,
        template_abs_path_str: str,
        context: dict[str, Any],
        output_abs_path_str: str
    ) -> bool:
        """
        Renders a file from a Jinja2 template and writes it to the specified output path.

        Args:
            template_abs_path_str: The absolute path to the Jinja2 template file.
            context: A dictionary containing data for rendering the template.
            output_abs_path_str: The absolute path where the rendered file will be written.

        Returns:
            True if the file was successfully rendered and written, False otherwise.
        """
        logger.info(f"Attempting to render template '{Path(template_abs_path_str).name}' to '{Path(output_abs_path_str).name}'.")

        try:
            template_path = Path(template_abs_path_str)
            output_path = Path(output_abs_path_str)

            if not template_path.is_file():
                logger.error(f"Template file not found: {template_path}")
                return False

            template_dir = template_path.parent
            template_name = template_path.name

            # Using select_autoescape for basic security, though for non-HTML less critical.
            # trim_blocks and lstrip_blocks are good for general template hygiene.
            env = Environment(
                loader=FileSystemLoader(searchpath=str(template_dir)),
                autoescape=select_autoescape(['html', 'xml', 'htm']), # General recommendation
                trim_blocks=True,
                lstrip_blocks=True
            )
            logger.debug(f"Jinja2 environment initialized for template directory: {template_dir}")

            try:
                template = env.get_template(template_name)
                logger.debug(f"Template '{template_name}' loaded successfully.")
            except exceptions.TemplateNotFound:
                logger.error(f"Jinja2 template not found: {template_name} in {template_dir}")
                return False
            except exceptions.TemplateSyntaxError as e:
                logger.error(f"Jinja2 template syntax error in '{template_name}': {e}")
                return False
            except Exception as e: # Catch other Jinja related loading errors
                logger.error(f"Error loading Jinja2 template '{template_name}': {e}", exc_info=True)
                return False


            rendered_content = template.render(context)
            logger.debug(f"Template '{template_name}' rendered successfully.")

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured output directory exists: {output_path.parent}")

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered_content)

            logger.info(f"Successfully wrote rendered content to '{output_path}'.")
            return True

        except OSError as e:
            logger.error(f"File I/O error while writing to '{output_abs_path_str}': {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred in render_and_write_file: {e}", exc_info=True)
            return False
