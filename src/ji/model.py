import os
import json
from datetime import datetime
from pathlib import Path
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from enum import Enum

class Status(str, Enum):
    TODO = 'TODO'
    STAGED = 'STAGED'
    PUSHED = 'PUSHED'

@dataclass
class Comment:
    created_at: str
    content: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Comment':
        return cls(created_at=data['created_at'], content=data['content'])

@dataclass
class Task:
    id: int
    status: Status
    content: str
    comment_list: list[Comment]
    created_at: str
    last_modified: str
    difficulty: int = 1

@dataclass
class Page:
    id: int
    created_at: str
    last_modified: str
    task_map: dict[int, Task]

    @classmethod
    def from_dict(cls, data: dict) -> 'Page':
        task_map = {
            int(k): Task(
                id=int(k),
                status=Status(v['status']),
                content=v['content'],
                comment_list=[Comment.from_dict(c_dict) for c_dict in v['comment_list']],
                created_at=v['created_at'],
                last_modified=v['last_modified'],
                difficulty=v.get('difficulty', 1)
            ) for k, v in data['task_map'].items()
        }

        return cls(
            id=data['id'],
            created_at=data['created_at'],
            last_modified=data['last_modified'],
            task_map=task_map
        )

    def filter(self, status: Status) -> list[Task]:
        return [task for task in self.task_map.values() if task.status == status]

@dataclass
class WalEvent:
    id: int
    page: Page
    timestamp: str

    def __str__(self) -> str:
        return json.dumps({
            'id': self.id,
            'page': asdict(self.page),
            'timestamp': self.timestamp
        })

class Repo:
    base_dir = Path.home() / '.ji'
    pages_dir = base_dir / 'pages'
    build_dir = base_dir / 'build'
    wp_path = base_dir / 'wp'

    # not using this rn
    wal_dir = base_dir / 'wal'

    def __init__(self) -> None:
        self.event_time = datetime.now().isoformat()
        if not self.base_dir.exists():
            os.makedirs(self.pages_dir)
            os.makedirs(self.wal_dir)
            self.set_wp(0)
            self.write_page(0)
        else:
            with open(self.wp_path, 'r') as f:
                self.wp = int(f.readlines()[0])

    # not using this rn
    def _write_wal(self, page: Page) -> None:
        dt = datetime.fromisoformat(self.event_time)
        dir = self.wal_dir / f'{dt.year}' / f'{dt.month:02d}'
        if not dir.exists(): os.makedirs(dir)
        event = WalEvent(id=page.id, page=page, timestamp=self.event_time)
        with open(dir / 'events.log', 'a') as f:
            f.write(str(event))
            f.write('\n')

    def get_wp(self) -> int:
        return self.wp

    def set_wp(self, id: int) -> None:
        with open(self.wp_path, 'w') as f:
            f.write(str(id))
            self.wp = id

    def get_page(self, id: int) -> Page | None:
        if not os.path.exists(self.pages_dir / f'page_{id}.json'):
            return None

        with open(self.pages_dir / f'page_{id}.json', 'r') as f:
            return Page.from_dict(json.load(f))

    def write_page(self, id: int, page: Page | None = None) -> None:
        with open(self.pages_dir / f'page_{id}.json', 'w') as f:
            if page is None:
                page = Page(
                    id=id,
                    created_at=self.event_time,
                    last_modified=self.event_time,
                    task_map={}
                )

            json.dump(asdict(page), f)

    @contextmanager
    def get_working_page(self, p: int | None = None, disable_wal: bool = False) -> Iterator[Page | None]:
        cp = self.wp if p is None else p
        page = self.get_page(cp)
        try:
            yield page
        finally:
            if page is not None:
                page.last_modified = self.event_time
                if not disable_wal: self._write_wal(page)
                self.write_page(cp, page)
