# src/template_renderer.py
import string
from utils import setup_logging

logger = setup_logging(__name__)


class ContextFormatter(string.Formatter):
    """
    string.Formatter that also understands dotted paths into nested dicts/lists, e.g.
    "{attachments_meta.0.filepath}" or "{daily_report_email.recipients.to.0}".
    """

    def get_field(self, field_name, args, kwargs):
        first, *rest = field_name.split('.')
        obj = self.get_value(first, args, kwargs)
        for part in rest:
            if isinstance(obj, dict):
                obj = obj[part]
            elif isinstance(obj, (list, tuple)) and part.lstrip('-').isdigit():
                try:
                    obj = obj[int(part)]
                except IndexError:
                    raise KeyError(field_name)
            else:
                obj = getattr(obj, part)
        return obj, first


class TemplateRenderer:
    """
    A simple template renderer for string templates using Python's f-string like
    syntax (e.g. "{report_date}", "{sales_figure:.2f}", "{attachments_meta.0.filename}").

    It takes a template string and a context dictionary and substitutes the
    placeholders using values from the context.
    """

    def __init__(self):
        self.formatter = ContextFormatter()
        logger.debug("TemplateRenderer initialized.")

    def render(self, template_string, context):
        """
        Renders a template string using a dictionary context.

        :param template_string: A string containing {placeholder} style fields,
            optionally with format specs (e.g. "{sales_figure:.2f}").
        :param context: A dict-like object providing values for the placeholders.
        :return: The rendered string.
        :raises ValueError: If a placeholder key is missing from the context.
        """
        if template_string is None:
            return ""
        try:
            return self.formatter.vformat(template_string, [], context)
        except KeyError as e:
            logger.error(
                f"Missing key in template context: {e}. "
                f"Template: '{template_string}' Context keys: {list(context.keys())}"
            )
            raise ValueError(f"Missing context key: {e}")
        except Exception as e:
            logger.error(f"Error rendering template: {e}. Template: '{template_string}'")
            raise
