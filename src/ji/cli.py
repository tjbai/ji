import subprocess
import click

from .model import Status, Comment, Task, Repo
from .pretty import pprint_page, pprint_bl, celebrate
from .html import generate

@click.group
@click.pass_context
@click.option('-p', default=None, type=int)
def cli(ctx: click.Context, p: int | None) -> None:
    repo = Repo()
    ctx.obj = (repo, repo.get_wp() if p is None else p)
    with repo.get_working_page(p) as page:
        if page is None:
            click.echo('Could not find page')
            ctx.exit()

@cli.command(name='e')
@click.pass_obj
def edit(ctx: tuple[Repo, int]) -> None:
    repo, _ = ctx
    subprocess.run(['vi', repo.base_dir])

#### page ops

@cli.command(name='n')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
def new(ctx: tuple[Repo, int]) -> None:
    repo, _ = ctx
    wp = repo.get_wp()
    repo.set_wp(wp + 1)
    repo.write_page(wp + 1)

@cli.command(name='st')
@click.option('-n', default=1)
@click.option('-p', default=None, type=int)
@click.option('-v/-nv', default=False)
@click.pass_obj
def status(ctx: tuple[Repo, int], n: int, p: int | None, v: bool) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        pprint_page(page, verbose=v)

@cli.command(name='t')
@click.argument('content')
@click.option('-d', default=1)
@click.pass_obj
def touch(ctx: tuple[Repo, int], content: str, d: int) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        id = len(page.task_map)
        page.task_map[id] = Task(
            id=id,
            status=Status.TODO,
            content=content,
            comment_list=[],
            last_modified=repo.event_time,
            created_at=repo.event_time,
            difficulty=d
        )

@cli.command(name='rm')
@click.argument('id', type=int)
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
def remove(ctx: tuple[Repo, int], id: int) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if id not in page.task_map:
            click.echo('Task does not exist')
            return

        del page.task_map[id]
        click.echo('Done')

@cli.command(name='a')
@click.argument('id', type=int)
@click.pass_obj
def add(ctx: tuple[Repo, int], id: int) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if (task := page.task_map.get(id)) is None:
            click.echo('task does not exist')
            return

        task.status = Status.STAGED
        click.echo('done')

@cli.command(name='rs')
@click.argument('id', type=int)
@click.pass_obj
def restore(ctx: tuple[Repo, int], id: int) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if (task := page.task_map.get(id)) is None:
            click.echo('Task does not exist')
            return

        if task.status != Status.STAGED:
            click.echo('Task not currently staged')
            return

        task.status = Status.TODO
        click.echo('done')

@cli.command(name='c')
@click.argument('content')
@click.pass_obj
def comment(ctx: tuple[Repo, int], content: str) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if len((staged := page.filter(Status.STAGED))) == 0:
            click.echo('No staged tasks')
            return

        for task in staged:
            task.comment_list.append(Comment(created_at=repo.event_time, content=content))

        click.echo(f'{len(staged)} task(s) updated with \'{content}\'')

@cli.command(name='p')
@click.pass_obj
def push(ctx: tuple[Repo, int]) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if len((staged := page.filter(Status.STAGED))) == 0:
            click.echo('No staged tasks')
            return

        for task in staged:
            celebrate(task.difficulty, task.content)

        for task in staged:
            task.status = Status.PUSHED

@cli.command(name='b')
@click.option('-o/-no', default=False)
@click.pass_obj
def build(ctx: tuple[Repo, int], o: bool) -> None:
    repo, _ = ctx
    output_path = generate(repo)
    if o: subprocess.run(['open', output_path])

#### backlog ops

@cli.group(name='u')
@click.pass_context
def bl(ctx: click.Context) -> None:
    pass

@bl.command(name='st')
@click.pass_obj
def status_bl(obj: tuple[Repo, int]) -> None:
    repo, _ = obj
    with repo.get_backlog() as bl:
        pprint_bl(bl)

@bl.command(name='t')
@click.argument('content')
@click.pass_obj
def touch_bl(obj: tuple[Repo, int], content: str) -> None:
    repo, _ = obj
    with repo.get_backlog() as bl:
        bl.append(Task(
            id=len(bl),
            status=Status.TODO,
            content=content,
            comment_list=[],
            last_modified=repo.event_time,
            created_at=repo.event_time
        ))

@bl.command(name='p')
@click.argument('id', type=int)
@click.pass_obj
def pop_bl(obj: tuple[Repo, int], id: int) -> None:
    repo, p = obj
    with repo.get_working_page(p) as page, repo.get_backlog() as bl:
        if id >= len(bl):
            click.echo('Task index out of bounds')
            return

        task = bl.pop(id)
        task.id = len(page.task_map)
        task.status = Status.TODO
        page.task_map[task.id] = task
        click.echo('Done')
