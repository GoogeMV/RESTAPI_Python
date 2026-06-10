import sys
from pathlib import Path

if sys.platform == "win32" and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Group

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Horizontal, VerticalScroll


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def find_project_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "main.py").exists():
            return p
    return start


def check_module_present(root: Path, module: str) -> bool:
    return (root / module / "app" / "data.py").exists()


MODULES = [
    {
        "id": "reports",
        "description": "Aggregation & analytics -- no own data store",
        "endpoints": [
            ("GET", "/reports/enrollment-stats", []),
            ("GET", "/reports/grade-distribution", ["min_avg: float (optional) -- filter by avg"]),
        ],
        "dependencies": [("enrollments", "enrollments_db", ["course_name"])],
        "pulled_by": [],
        "test_files": ["reports/tests/test_router.py"],
    },
]

KNOWN_BUG = "[!] service.get_grade_distribution() ignores ?min_avg= query param."
METHOD_STYLE = {
    "GET": ("bold green", "GET   "),
    "POST": ("bold blue", "POST  "),
}


def method_text(method: str) -> Text:
    style, label = METHOD_STYLE.get(method, ("white", method.ljust(6)))
    return Text(label, style=style)


def generate_module_detail(mod: dict, root: Path) -> Group:
    renderables = []

    renderables.append(Text(f"\n{mod['id'].upper()} - {mod['description']}\n", style="bold cyan"))

    renderables.append(Text("Endpoints", style="bold white"))
    for method, path, params in mod.get("endpoints", []):
        mt = method_text(method)
        line = Text("  ")
        line.append_text(mt)
        line.append(f"  {path}", style="white")
        renderables.append(line)
        for p in params:
            style = "red" if "BUG" in p.upper() else "dim yellow"
            renderables.append(Text(f"        -> {p}", style=style))

    renderables.append(Text(""))

    deps = mod.get("dependencies", [])
    if deps:
        renderables.append(Text("Required arguments", style="bold white"))
        dep_table = Table(show_edge=False, header_style="dim", padding=(0, 2))
        dep_table.add_column("Module", style="yellow")
        dep_table.add_column("Store", style="cyan")
        dep_table.add_column("Fields", style="white")
        for dep_mod, store, fields in deps:
            present = check_module_present(root, dep_mod)
            status = " [green]OK[/green]" if present else " [red]MISSING[/red]"
            dep_table.add_row(f"{dep_mod}{status}", store, ", ".join(fields))
        renderables.append(dep_table)
        renderables.append(Text(""))

    if mod["id"] == "reports":
        renderables.append(
            Panel(Text(KNOWN_BUG, style="yellow"), title="[bold red]Implementation Bug[/bold red]", border_style="red")
        )

    return Group(*renderables)


class MonitorApp(App):
    CSS = """
    Screen { layout: vertical; }
    #main_container { layout: horizontal; height: 1fr; }
    #sidebar { width: 40%; border-right: solid ascii; }
    #details_pane { width: 60%; padding: 1 2; }
    """

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle Dark Mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main_container"):
            yield DataTable(id="sidebar", cursor_type="row")
            with VerticalScroll(id="details_pane"):
                yield Static("Select a module to view details.", id="details")
        yield Footer()

    def on_mount(self) -> None:
        self.root_path = find_project_root(Path(".").resolve())

        table = self.query_one(DataTable)
        table.add_columns("Module", "Present", "Endpoints", "Tests")

        for i, m in enumerate(MODULES):
            present = "OK" if check_module_present(self.root_path, m["id"]) else "--"
            ep_count = str(len(m.get("endpoints", [])))
            test_count = str(len(m.get("test_files", [])))

            table.add_row(m["id"], present, ep_count, test_count, key=m["id"])

        table.focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        module_id = event.row_key.value

        mod_data = next((m for m in MODULES if m["id"] == module_id), None)
        if mod_data:
            details_view = self.query_one("#details", Static)
            details_view.update(generate_module_detail(mod_data, self.root_path))


if __name__ == "__main__":
    app = MonitorApp()
    app.run()
