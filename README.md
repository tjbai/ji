```
ji n:
    create new page

ji st [-n N] [-v/-nv]:
    show working page

ji t CONTENT [-d D]:
    create a task

ji rm ID:
    remove a task

ji a ID:
    stage a task

ji rs ID:
    unstage a task

ji p:
    mark all currently staged tasks as complete

ji c CONTENT:
    append comment to all staged tasks

ji e:
    edit pages directory

ji b [-o/-no]:
    generate html

ji u:
    backlog operations

ji u st:
    show backlog

ji u t:
    add task to backlog

ji u p ID:
    add task from backlog to page
```

```
~/.ji/
    pages/
        page_{id}.json
    wal/
        YYYY_MM/
            events_{DD}.log
    wp
    bl.jsonl
```
