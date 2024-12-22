import os
import json
import click
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

'''
ji new (jn):
    make new page

ji status (jst) [-n N]:
    show status of past N days

ji create (jic):
    create new task

ji add (ja):
    stage a task

ji restore, jr:
    unstage a task

ji comment, jc:
    append comment to all staged tasks

ji push, jp:
    mark all currently staged tasks as complete

ji edit, je, -n N=1:
    interactive editor

####

Status: TODO | STAGED | PUSHED

Task: {
    task_id: int,
    status: Status,
    content: string,
    created_at: datetime,
    last_modified: datetime,
}

Page: {
    created_at: datetime,
    last_modified: datetime,
    task_map: Dict[int, Task]
}

event: # some kind of case class
'''

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

    def get_page(self, id: int) -> dict:
        with open(self.pages_dir / f'page_{id}.json', 'r') as f:
            return json.load(f)

    def write_page(self, id: int, content: dict = None) -> None:
        with open(self.pages_dir / f'page_{id}.json', 'w') as f:
            if content is None:
                content = {'created_at': self.event_time, 'last_modified': self.event_time, 'task_map': {}}
            json.dump(content, f)

    @contextmanager
    def get_working_page(self) -> dict:
        page = self.get_page(self.wp)
        try:
            yield page
        finally:
            page['last_modified'] = self.event_time
            return self.write_page(self.wp, page)

@click.group
@click.pass_context
def cli(ctx: click.Context) -> None:
    ctx.obj = Repo()

@cli.command
@click.pass_obj
def new(repo: Repo) -> None:
    wp = repo.get_wp()
    repo.set_wp(wp + 1)
    repo.write_page(wp + 1)

@cli.command()
@click.option('--n', default=1)
@click.pass_obj
def status(repo: Repo, n: int) -> None:
    with repo.get_working_page() as page:
        print(f'{page['created_at']}, {page['last_modified']}')
        for id, task in page['task_map'].items():
            print(f'{task['status']} {id} {task['content']}')

@cli.command
@click.argument('content')
@click.option('--status', type=click.Choice(['TODO', 'STAGED', 'PUSHED']), default='TODO')
@click.pass_obj
def create(repo: Repo, content: str, status: str) -> None:
    with repo.get_working_page() as page:
        id = len(page['task_map'])
        page['task_map'][id] = {
            'status': status,
            'content': content,
            'comments': [],
            'last_modified': repo.event_time,
            'created_at': repo.event_time
        }

@cli.command
@click.argument('id')
@click.pass_obj
def add(repo: Repo, id: int) -> None:
    with repo.get_working_page() as page:
        if id not in page['task_map']:
            print('task does not exist')
            return

        page['task_map'][id]['status'] = 'STAGED'

@cli.command
@click.argument('id')
@click.pass_obj
def restore(repo: Repo, id: int) -> None:
    with repo.get_working_page() as page:
        if id not in page['task_map']:
            print('task does not exist')
            return

        if page['task_map'][id]['status'] != 'STAGED':
            print('task not currently staged')
            return

        page['task_map'][id]['status'] = 'TODO'
