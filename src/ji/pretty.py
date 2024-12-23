from datetime import datetime
from rich.tree import Tree
from rich.text import Text
from rich.console import Console
from .model import Page, Task, Status

def format_time(ts: str) -> str:
    dt = datetime.fromisoformat(ts)
    return dt.strftime('%m/%d/%Y %H:%M')

def create_section_tree(title: str, tasks: list[Task], style: str, verbose: bool) -> Tree:
    branch = Tree(Text(title, style=f"bold {style}"))
    if tasks:
        for task in tasks:
            task_text = Text()
            task_text.append(f"{task.id:2}", style="dim")
            task_text.append(" ")
            task_text.append(task.content)

            if verbose and task.comment_list:
                task_node = branch.add(task_text)
                for comment in task.comment_list:
                    task_node.add(Text(f"{comment.content}", style="dim"))
            else:
                branch.add(task_text)
    else:
        branch.add(Text("(empty)", style="dim"))
    return branch

def pprint(page: Page, verbose: bool) -> None:
    console = Console()

    main_tree = Tree(Text(f"\n记#{page.id}", style="bold"), guide_style="dim")

    todo_tasks = [task for task in page.task_map.values() if task.status == Status.TODO]
    staged_tasks = [task for task in page.task_map.values() if task.status == Status.STAGED]
    pushed_tasks = [task for task in page.task_map.values() if task.status == Status.PUSHED]

    main_tree.add(create_section_tree("todo", todo_tasks, "green", verbose))
    main_tree.add(create_section_tree("stage", staged_tasks, "yellow", verbose))
    main_tree.add(create_section_tree("done", pushed_tasks, "red", verbose))

    console.print(main_tree)
