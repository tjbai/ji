import click

from .model import Status, Comment, Task, Repo
from .pretty import pprint

@click.group
@click.pass_context
def cli(ctx: click.Context) -> None:
    ctx.obj = Repo()

@cli.command(name='n')
@click.pass_obj
def new(repo: Repo) -> None:
    wp = repo.get_wp()
    repo.set_wp(wp + 1)
    repo.write_page(wp + 1)

@cli.command(name='st')
@click.option('-n', default=1)
@click.option('-p', default=None, type=int)
@click.option('-v/-nv', default=False)
@click.pass_obj
def status(repo: Repo, n: int, p: int | None, v: bool) -> None:
    if p is None:
        with repo.get_working_page() as page:
            pprint(page, verbose=v)
            return

@cli.command(name='t')
@click.argument('content')
@click.pass_obj
def touch(repo: Repo, content: str) -> None:
    with repo.get_working_page() as page:
        id = len(page.task_map)
        page.task_map[id] = Task(
            id=id,
            status=Status(status),
            content=content,
            comment_list=[],
            last_modified=repo.event_time,
            created_at=repo.event_time
        )

@cli.command(name='a')
@click.argument('id', type=int)
@click.pass_obj
def add(repo: Repo, id: int) -> None:
    with repo.get_working_page() as page:
        if (task := page.task_map.get(id)) is None:
            print('task does not exist')
            return

        task.status = Status.STAGED
        print(f'staged {task}')

@cli.command(name='rs')
@click.argument('id', type=int)
@click.pass_obj
def restore(repo: Repo, id: int) -> None:
    with repo.get_working_page() as page:
        if (task := page.task_map.get(id)) is None:
            print('task does not exist')
            return

        if task.status != Status.STAGED:
            print('task not currently staged')
            return

        task.status = Status.TODO
        print(f'restored {task}')

@cli.command(name='c')
@click.argument('content')
@click.pass_obj
def comment(repo: Repo, content: str) -> None:
    with repo.get_working_page() as page:
        if len((staged := page.filter(Status.STAGED))) == 0:
            print('no staged tasks')
            return

        for task in staged:
            task.comment_list.append(Comment(created_at=repo.event_time, content=content))

        print(f'{len(staged)} task(s) updated with \'{content}\'')

@cli.command(name='p')
@click.pass_obj
def push(repo: Repo) -> None:
    with repo.get_working_page() as page:
        if len((staged := page.filter(Status.STAGED))) == 0:
            print('no staged tasks')
            return

        print('pushed...')
        for task in staged:
            task.status = Status.PUSHED
            print(f'\t{task}')
