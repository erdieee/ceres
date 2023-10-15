import os

from rich.console import Console
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.status import Status

from ceres import __version__


class ConsolePanel(Console):
    def __init__(self, *args, **kwargs):
        console_file = open(os.devnull, "w")
        super().__init__(record=True, file=console_file, *args, **kwargs)

    def __rich_console__(self, console, options):
        texts = self.export_text(clear=False).split("\n")
        for line in texts[-options.height :]:
            yield line


class Dashboard:
    def __init__(self) -> None:
        self.console: list[ConsolePanel] = [ConsolePanel() for _ in range(3)]
        self.layout = self.get_renderable()

    @property
    def get_layout(self):
        return self.layout

    def get_renderable(self):
        layout = Layout(name="root")
        layout.split(
            Layout(self.console[0], name="title", ratio=1),
            Layout(name="main", ratio=12),
        )
        layout["title"].update(
            Markdown(
                "# Ceres",
            )
        )
        layout["main"].split_row(
            Layout(self.console[1], name="left"),
            Layout(self.console[2], name="right"),
        )
        layout["left"].split(Layout(name="profit"), Layout(name="orderbook"))
        layout["profit"].update(
            Panel(
                Status("Loading...", spinner="line"),
                title="Profit",
                border_style="Red",
            )
        )
        layout["orderbook"].update(
            Panel(
                Status("Loading...", spinner="line"),
                title="Orderbook",
                border_style="green",
            )
        )
        layout["right"].update(
            Panel(
                Status("Loading...", spinner="line"),
                title="Logs",
                border_style="green",
            )
        )
        return layout

    def update(self, name, message, title="Info", border_style="green"):
        self.layout[name].update(Panel(message, title=title, border_style=border_style))
