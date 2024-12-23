from datetime import datetime
from rich.console import Console, Group
from rich.padding import Padding
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .model import Page, Task, Status

def format_time(ts: str) -> str:
    dt = datetime.fromisoformat(ts)
    return dt.strftime('%Y-%m-%d %H:%M')

def format_task(task: Task, verbose: bool) -> Text:
    text = Text()
    text.append(f"{task.id:2}")
    text.append(" ")
    text.append(task.content)

    if verbose:
        for comment in task.comment_list:
            text.append("\n\t")
            text.append("• ", style="dim")
            text.append(comment.content, style="dim")

    return text

def pprint(page: Page, verbose: bool) -> None:
    console = Console()

    todo_tasks = [format_task(task, verbose) for task in page.task_map.values() if task.status == Status.TODO]
    staged_tasks = [format_task(task, verbose) for task in page.task_map.values() if task.status == Status.STAGED]
    pushed_tasks = [format_task(task, verbose) for task in page.task_map.values() if task.status == Status.PUSHED]

    sections = []
    sections.append(Panel(Group(*todo_tasks), title='TODO', title_align='left', expand=False))
    sections.append(Panel(Group(*staged_tasks), title='STAGED', title_align='left', expand=False))
    sections.append(Panel(Group(*pushed_tasks), title='PUSHED', title_align='left', expand=False))

    main_panel = Panel(
        Group(*sections),
        title=f'Page #{page.id} | C: {format_time(page.created_at)} | M: {format_time(page.last_modified)}',
        title_align='left',
        expand=False,
        padding=(0, 1)
    )

    console.print(main_panel)
