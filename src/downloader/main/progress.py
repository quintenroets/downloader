from __future__ import annotations

import typing
from dataclasses import dataclass
from typing import Any

from rich import progress
from rich.text import Text

if typing.TYPE_CHECKING:
    from types import TracebackType

    from rich.console import OverflowMethod
    from rich.progress import JustifyMethod, Task
    from typing_extensions import Self


@dataclass
class SizedTextColumn(progress.ProgressColumn):
    text_format: str
    style: str = "none"
    justify: JustifyMethod = "left"
    markup: bool = True
    highlighter: None = None
    overflow: OverflowMethod | None = None
    width: int = 40

    def __post_init__(self) -> None:
        super().__init__()

    def render(self, task: Task) -> Text:
        _text = self.text_format.format(task=task)
        if self.markup:
            text = Text.from_markup(_text, style=self.style, justify=self.justify)
        else:
            text = Text(_text, style=self.style, justify=self.justify)
        if self.highlighter:
            self.highlighter.highlight(text)

        text.truncate(max_width=self.width, overflow=self.overflow, pad=True)
        return text


progress_manager = progress.Progress(
    SizedTextColumn(
        "[progress.description]{task.description}",
        width=40,
        overflow="ellipsis",
    ),
    progress.BarColumn(),
    progress.DownloadColumn(),
    progress.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    progress.TimeRemainingColumn(),
)


class UIProgress:
    def __init__(self, description: str, total: float) -> None:
        progress_manager.__enter__()
        self.job = progress_manager.add_task(description, total=total, desc=description)

    def advance(self, value: float) -> None:
        progress_manager.advance(self.job, value)

    def update(self, **kwargs: Any) -> None:
        progress_manager.update(self.job, **kwargs)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if all(t.finished for t in progress_manager.tasks):
            progress_manager.__exit__(exception_type, exception_value, traceback)
