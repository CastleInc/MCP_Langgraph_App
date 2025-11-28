from jinja2 import Environment, FileSystemLoader, Template
from typing import Dict, Any, Optional
import os


class TemplateRenderer:
    """Utility class for rendering Jinja2 templates."""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the template renderer.
        
        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = templates_dir
        self.env = None
        
        # Create templates directory if it doesn't exist
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        # Initialize Jinja2 environment
        self._initialize_environment()
    
    def _initialize_environment(self):
        """Initialize the Jinja2 environment."""
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render a template with the provided data.
        
        Args:
            template_name: Name of the template file
            data: Dictionary of data to pass to the template
            
        Returns:
            Rendered template as a string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**data)
        except Exception as e:
            return f"Error rendering template '{template_name}': {str(e)}"
    
    def render_string(self, template_string: str, data: Dict[str, Any]) -> str:
        """
        Render a template from a string.
        
        Args:
            template_string: Template content as a string
            data: Dictionary of data to pass to the template
            
        Returns:
            Rendered template as a string
        """
        try:
            template = Template(template_string)
            return template.render(**data)
        except Exception as e:
            return f"Error rendering template string: {str(e)}"
    
    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            True if template exists, False otherwise
        """
        template_path = os.path.join(self.templates_dir, template_name)
        return os.path.exists(template_path)
    
    def get_template_for_tool(self, tool_name: str) -> Optional[str]:
        """
        Get the template name for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Template filename if it exists, None otherwise
        """
        template_name = f"{tool_name.lower()}_template.html"
        if self.template_exists(template_name):
            return template_name
        return None
