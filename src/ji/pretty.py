import time
from datetime import datetime
from rich.tree import Tree
from rich.text import Text
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from .model import Page, Task, Status

def format_time(ts: str) -> str:
    dt = datetime.fromisoformat(ts)
    return dt.strftime('%m/%d/%Y %H:%M')

def format_relative(ts: str) -> str:
    dt = datetime.fromisoformat(ts)
    now = datetime.now()

    delta = now - dt
    seconds = delta.total_seconds()

    if seconds < 0:
        return 'in the future'

    minutes = seconds / 60
    hours = minutes / 60
    days = delta.days
    months = days / 30.44
    years = days / 365.25

    if seconds < 60:
        return 'just now'
    elif minutes < 60:
        m = int(minutes)
        return f'{m} minute{'s' if m != 1 else ''} ago'
    elif hours < 24:
        h = int(hours)
        return f'{h} hour{'s' if h != 1 else ''} ago'
    elif days < 30:
        return f'{days} day{'s' if days != 1 else ''} ago'
    elif days < 365:
        m = int(months)
        return f'{m} month{'s' if m != 1 else ''} ago'
    else:
        y = int(years)
        return f'{y} year{'s' if y != 1 else ''} ago'

def celebrate(difficulty: int, task_content: str) -> None:
    duration = 0.85 * difficulty
    console = Console()

    with Progress(
        TextColumn('[bold blue]{task.description}'),
        BarColumn(complete_style='green', finished_style='green'),
        TaskProgressColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(task_content, total=100)

        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(duration / 200)

        console.print(Text(text=f'done! {task_content}', style='bold green'))

def create_section_tree(title: str, tasks: list[Task], style: str, verbose: bool) -> Tree:
    branch = Tree(Text(title, style=f'bold {style}'))
    if tasks:
        for task in tasks:
            task_text = Text()
            task_text.append(f'{task.id}', style='dim')
            task_text.append(f' {task.content}')

            if verbose:
                task_text.append(f', {format_relative(task.last_modified)}', style='dim')

            if verbose and task.comment_list:
                task_node = branch.add(task_text)
                for i, comment in enumerate(task.comment_list):
                    task_node.add(Text(f'{i} {comment.content}, {format_relative(comment.created_at)}', style='dim'))
            else:
                branch.add(task_text)
    else:
        branch.add(Text('(empty)', style='dim'))
    return branch

def pprint_page(page: Page, verbose: bool) -> None:
    console = Console()
    main_tree = Tree(Text(f'\n记 #{page.id}', style='bold'), guide_style='dim')

    todo_tasks = [task for task in page.task_map.values() if task.status == Status.TODO]
    staged_tasks = [task for task in page.task_map.values() if task.status == Status.STAGED]
    pushed_tasks = [task for task in page.task_map.values() if task.status == Status.PUSHED]

    main_tree.add(create_section_tree('todo', todo_tasks, 'green', verbose))
    main_tree.add(create_section_tree('stage', staged_tasks, 'yellow', verbose))
    main_tree.add(create_section_tree('done', pushed_tasks, 'red', verbose))

    console.print(main_tree)

def pprint_bl(bl: list[Task]) -> None:
    console = Console()
    main_tree = Tree(Text('\n旧', style='bold'), guide_style='dim')

    if bl:
        for i, task in enumerate(bl):
            task_text = Text()
            task_text.append(f'{i} ', style='dim')
            task_text.append(task.content)
            task_text.append(f', {format_relative(task.created_at)}', style='dim')
            main_tree.add(task_text)
    else:
        main_tree.add(Text('(empty)', style='dim'))

    console.print(main_tree)
