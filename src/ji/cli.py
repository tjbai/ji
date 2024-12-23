import os
import json
import click
from datetime import datetime
from pathlib import Path
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from enum import Enum

'''
'''

class Status(str, Enum):
    TODO = 'TODO'
    STAGED = 'STAGED'
    PUSHED = 'PUSHED'

@dataclass
class Task:
    status: Status
    content: str
    comments: list[str]
    created_at: str
    last_modified: str

@dataclass
class Page:
    created_at: str
    last_modified: str
    task_map: dict[int, Task]

    @classmethod
    def from_dict(cls, data: dict) -> 'Page':
        task_map = {
            int(k): Task(
                status=Status(v['status']),
                content=v['content'],
                comments=v['comments'],
                created_at=v['created_at'],
                last_modified=v['last_modified']
            ) for k, v in data['task_map'].items()
        }

        return cls(
            created_at=data['created_at'],
            last_modified=data['last_modified'],
            task_map=task_map
        )

    def filter(self, status: Status) -> list[Task]:
        return [task for task in self.task_map.values() if task.status == status]

class Repo:
    '''
    ~/.ji/
        pages/
            page_{id}.json
        wal/
            YYYY_MM/
                events_{DD}.log
        wp
    '''

    base_dir = Path.home() / '.ji'
    pages_dir = base_dir / 'pages'
    wal_dir = base_dir / 'wal'
    wp_path = base_dir / 'wp'

    def __init__(self) -> None:
        self.event_time = datetime.now().isoformat()
        if not os.path.exists(self.base_dir):
            os.makedirs(self.pages_dir)
            os.makedirs(self.wal_dir)
            self.set_wp(0)
            self.write_page(0)
        else:
            with open(self.wp_path, 'r') as f:
                self.wp = int(f.readlines()[0])

    def get_wp(self) -> int:
        return self.wp

    def set_wp(self, id: int) -> None:
        with open(self.wp_path, 'w') as f:
            f.write(str(id))
            self.wp = id

    def get_page(self, id: int) -> Page:
        with open(self.pages_dir / f'page_{id}.json', 'r') as f:
            return Page.from_dict(json.load(f))

    def write_page(self, id: int, page: Page | None = None) -> None:
        with open(self.pages_dir / f'page_{id}.json', 'w') as f:
            if page is None:
                page = Page(created_at=self.event_time, last_modified=self.event_time, task_map={})
            json.dump(asdict(page), f)

    @contextmanager
    def get_working_page(self) -> Iterator[Page]:
        page = self.get_page(self.wp)
        try:
            yield page
        finally:
            page.last_modified = self.event_time
            self.write_page(self.wp, page)

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
@click.option('--n', default=1)
@click.pass_obj
def status(repo: Repo, n: int) -> None:
    with repo.get_working_page() as page:
        print(f'{page.created_at}, {page.last_modified}')
        for id, task in page.task_map.items():
            print(f'{task.status} {id} {task.content}')

@cli.command(name='t')
@click.argument('content')
@click.option('--status', type=click.Choice(['TODO', 'STAGED', 'PUSHED']), default='TODO')
@click.pass_obj
def touch(repo: Repo, content: str, status: str) -> None:
    with repo.get_working_page() as page:
        id = len(page.task_map)
        page.task_map[id] = Task(
            status=Status(status),
            content=content,
            comments=[],
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
@click.argument('message')
@click.pass_obj
def comment(repo: Repo, message: str) -> None:
    with repo.get_working_page() as page:
        staged = page.filter(Status.STAGED)

@cli.command(name='p')
@click.pass_obj
def push(repo: Repo) -> None:
    with repo.get_working_page() as page:
        staged = page.filter(Status.STAGED)

        if len(staged) == 0:
            print('no staged tasks')
            return

        print('pushed...')
        for task in staged:
            task.status = Status.PUSHED
            print(f'\t{task}')
