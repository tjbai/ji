# help
```
ji n:
    create new page

ji st [-n N] [-p P] [-v/-nv]:
    show working page

ji t CONTENT:
    create a task

ji a ID:
    stage a task

ji rs ID:
    unstage a task

ji p:
    mark all currently staged tasks as complete

ji c CONTENT:
    append comment to all staged tasks
```

# on-disk:
```
~/.ji/
    pages/
        page_{id}.json
    wal/
        YYYY_MM/
            events_{DD}.log
    wp
```
