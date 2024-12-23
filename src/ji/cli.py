import click

from .model import Status, Comment, Task, Repo
from .pretty import pprint

@click.group
@click.pass_context
@click.option('-p', default=None, type=int)
def cli(ctx: click.Context, p: int | None) -> None:
    repo = Repo()
    ctx.obj = (repo, repo.get_wp() if p is None else p)

@cli.command(name='n')
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
        if page is None:
            click.echo('could not find page')
            return

        pprint(page, verbose=v)

@cli.command(name='t')
@click.argument('content')
@click.pass_obj
def touch(ctx: tuple[Repo, int], content: str) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if page is None:
            click.echo('could not find page')
            return

        id = len(page.task_map)
        page.task_map[id] = Task(
            id=id,
            status=Status.TODO,
            content=content,
            comment_list=[],
            last_modified=repo.event_time,
            created_at=repo.event_time
        )

@cli.command(name='rm')
@click.argument('id', type=int)
@click.confirmation_option(prompt='are you sure?')
@click.pass_obj
def remove(ctx: tuple[Repo, int], id: int) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if page is None:
            click.echo('could not find page')
            return

        if id not in page.task_map:
            click.echo('task does not exist')
            return

        del page.task_map[id]
        click.echo('done')

@cli.command(name='a')
@click.argument('id', type=int)
@click.pass_obj
def add(ctx: tuple[Repo, int], id: int) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if page is None:
            click.echo('could not find page')
            return

        if (task := page.task_map.get(id)) is None:
            click.echo('task does not exist')
            return

        task.status = Status.STAGED
        click.echo(f'staged {task}')

@cli.command(name='rs')
@click.argument('id', type=int)
@click.pass_obj
def restore(ctx: tuple[Repo, int], id: int) -> None:
    with repo.get_working_page() as page:
        if (task := page.task_map.get(id)) is None:
            click.echo('task does not exist')
            return

        if task.status != Status.STAGED:
            click.echo('task not currently staged')
            return

        task.status = Status.TODO
        click.echo(f'restored {task}')

@cli.command(name='c')
@click.argument('content')
@click.pass_obj
def comment(ctx: tuple[Repo, int], content: str) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if page is None:
            click.echo('could not find page')
            return

        if len((staged := page.filter(Status.STAGED))) == 0:
            click.echo('no staged tasks')
            return

        for task in staged:
            task.comment_list.append(Comment(created_at=repo.event_time, content=content))

        click.echo(f'{len(staged)} task(s) updated with \'{content}\'')

@cli.command(name='p')
@click.pass_obj
def push(ctx: tuple[Repo, int]) -> None:
    repo, p = ctx
    with repo.get_working_page(p) as page:
        if page is None:
            click.echo('could not find page')
            return

        if len((staged := page.filter(Status.STAGED))) == 0:
            click.echo('no staged tasks')
            return

        click.echo('pushed...')
        for task in staged:
            task.status = Status.PUSHED
            click.echo(f'\t{task}')
