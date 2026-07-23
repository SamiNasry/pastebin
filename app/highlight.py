from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound


FORMATTER = HtmlFormatter(
    linenos="table",
    cssclass="highlight",
    wrapcode=True,
)


def render(content: str, language: str) -> tuple[str,str]:
    try:
        lexer = get_lexer_by_name(language, stripall=False)
    except ClassNotFound:
        try:
            lexer = guess_lexer(content)
        except ClassNotFound:
            lexer = get_lexer_by_name("text")
    return pygments_highlight(content, lexer, FORMATTER), lexer.aliases[0]
