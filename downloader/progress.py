from typing import Optional, Union

import rich.progress as progress
from rich.console import OverflowMethod
from rich.progress import JustifyMethod
from rich.text import Text


class SizedTextColumn(progress.ProgressColumn):
    """A column containing text."""

    def __init__(
        self,
        text_format: str,
        style="none",
        justify="left",
        markup: bool = True,
        highlighter=None,
        overflow=None,
        width: int = 40,
    ) -> None:
        self.text_format = text_format
        self.justify: Union[JustifyMethod, str] = justify
        self.style = style
        self.markup = markup
        self.highlighter = highlighter
        self.overflow: Optional[OverflowMethod] = overflow
        self.width = width
        super().__init__()

    def render(self, task):
        _text = self.text_format.format(task=task)
        if self.markup:
            text = Text.from_markup(_text, style=self.style, justify=self.justify)
        else:
            text = Text(_text, style=self.style, justify=self.justify)
        if self.highlighter:
            self.highlighter.highlight(text)

        text.truncate(max_width=self.width, overflow=self.overflow, pad=True)
        return text


progressmanager = progress.Progress(
    SizedTextColumn(
        "[progress.description]{task.description}", width=40, overflow="ellipsis"
    ),
    progress.BarColumn(),
    progress.DownloadColumn(),
    progress.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    progress.TimeRemainingColumn(),
)


class UIProgress:
    def __init__(self, description, total):
        progressmanager.__enter__()
        self.job = progressmanager.add_task(description, total=total, desc=description)

    def advance(self, value):
        progressmanager.advance(self.job, value)

    def update(self, **kwargs):
        progressmanager.update(self.job, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if all([t.finished for t in progressmanager.tasks]):
            progressmanager.__exit__(*_)
