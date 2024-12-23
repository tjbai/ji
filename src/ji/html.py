import os
import json
from .model import Repo, Page, Status
from .pretty import format_time

def generate(repo: Repo):
    pages = []
    for page_path in os.listdir(repo.pages_dir):
        with open(repo.pages_dir / page_path, 'r') as f:
            pages.append(Page.from_dict(json.load(f)))

    pages = sorted(pages, key=lambda x: x.id, reverse=True)

    html_content = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Azeret+Mono:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
<title>TJ's Tasks</title><style>
:root {
    --width: 720px;
    --font-main: "Azeret Mono", monospace;
    --background-color: #e8e8e8;
    --heading-color: #222;
    --text-color: #444;
    --link-color: #3273dc;
    --visited-color: #8b6fcb;
    --font-scale: 1em;
}
body {
    font-family: var(--font-main);
    font-size: var(--font-scale);
    margin: auto;
    padding: 20px;
    max-width: var(--width);
    text-align: left;
    background-color: var(--background-color);
    word-wrap: break-word;
    line-height: 1.5;
    color: var(--text-color);
}
h2 { color: var(--heading-color); font-weight: normal; margin-bottom: 2em; }
.page { margin-bottom: 2.5em; }
.page-header {
    display: flex;
    flex-direction: horizontal;
    align-items: center;
    cursor: pointer;
    user-select: none;
}
.section { margin: 1em 0 1em 2em; }
.section-header {
    margin: 0.8em 0;
    cursor: pointer;
    user-select: none;
}
.task {
    display: flex;
    flex-direction: horizontal;
    align-items: flex-start;
    margin: 0.5em 0 0.5em 1.5em;
}
.task-id {
    color: var(--text-color);
    margin-right: 1em;
    min-width: 2em;
}
.todo { color: var(--link-color); }
.staged { color: var(--link-color); }
.pushed { color: var(--text-color); }
.comments {
    margin: 0.3em 0 0.3em 3em;
    color: var(--text-color);
    font-size: 0.9em;
}
.collapsed { display: none; }
.arrow {
    display: inline-block;
    transition: transform 0.2s;
    margin-right: 0.5em;
}
.arrow.collapsed { transform: rotate(-90deg); }
.metadata {
    margin-left: 1em;
}
</style></head>
<body><h2><b>TJ's Tasks</b></h2>'''

    for page in pages:
        html_content += f'''<div class="page"><div class="page-header" onclick="toggleSection(this.parentElement)">
<span class="arrow collapsed">▼</span> <time class="metadata">{format_time(page.created_at)}</time></div><div class="page-content collapsed">'''

        sections = [
            ('Todo', {k:v for k,v in page.task_map.items() if v.status == Status.TODO}, 'todo'),
            ('Stage', {k:v for k,v in page.task_map.items() if v.status == Status.STAGED}, 'staged'),
            ('Done', {k:v for k,v in page.task_map.items() if v.status == Status.PUSHED}, 'pushed')
        ]

        for section_name, section_tasks, status_class in sections:
            html_content += f'''<div class="section"><div class="section-header" onclick="toggleSection(this.parentElement)">
<span class="arrow collapsed">▼</span>{section_name} ({len(section_tasks)})</div><div class="section-content collapsed">'''

            for task_id, task in sorted(section_tasks.items()):
                html_content += f'''<div class="task"><span class="task-id">{task_id}</span>
<span class="{status_class}">{task.content}</span></div>'''

                if task.comment_list:
                    html_content += '<div class="comments">'
                    for comment in task.comment_list:
                        html_content += f'{comment.content}<br>'
                    html_content += '</div>'

            html_content += '</div></div>'
        html_content += '</div></div>'

    html_content += '''<script>
function toggleSection(element) {
    const content = element.querySelector(':scope > div:not(.page-header):not(.section-header)');
    const arrow = element.querySelector(':scope > div > .arrow, :scope > .arrow');
    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        arrow.classList.remove('collapsed');
    } else {
        content.classList.add('collapsed');
        arrow.classList.add('collapsed');
    }
}
</script></body></html>'''

    output_path = repo.base_dir / 'tasks.html'
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f'Generated html at {output_path}')
