import os
import json
from .model import Repo, Page, Status
from .pretty import format_time

def generate(repo: Repo) -> str:
    pages = []
    for page_path in os.listdir(repo.pages_dir):
        with open(repo.pages_dir / page_path, 'r') as f:
            pages.append(Page.from_dict(json.load(f)))

    pages = sorted(pages, key=lambda x: x.id, reverse=True)

    html_content = '''
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Azeret+Mono:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
    <title>记</title>
    <style>
        :root {
            --width: 900px;
            --font-main: "Azeret Mono", monospace;
            --bg-color: #272727;
            --text-color: #e4d7b1;
            --dim-color: #f2ebd8;
            --todo-color: #e75740;
            --stage-color: #f0bf4f;
            --done-color: #abaf3f;
            --font-scale: 1em;
        }

        body {
            font-family: var(--font-main);
            font-size: var(--font-scale);
            margin: 2rem auto;
            padding: 20px;
            max-width: var(--width);
            text-align: left;
            background-color: var(--bg-color);
            word-wrap: break-word;
            line-height: 1.6;
            color: var(--text-color);
        }

        body.light {
            --bg-color: #e8e8e8;
            --text-color: #444;
            --dim-color: #444;
            //--todo-color: #FF6B6B;
            //--done-color: #98FB98;
            //--stage-color: #FFD93D;
            --todo-color: #D32F2F;
            --done-color: #2E7D32;
            --stage-color: #F57C00;
            //--todo-color: #E06C75;
            //--done-color: #3D9970;
            //--stage-color: #F4B942;
        }

        .page { margin-bottom: 3em; }

        .page-header {
            display: flex;
            align-items: center;
            margin-bottom: 1em;
            cursor: pointer;
            user-select: none;
        }

        .section {
            margin: 0.5em 0 0.5em 1.5em;
            padding-left: 1em;
            border-left: 1px solid var(--dim-color);
        }

        .section-header {
            color: var(--dim-color);
            margin: 1em 0;
            cursor: pointer;
            user-select: none;
        }

        .task {
            display: flex;
            align-items: flex-start;
            margin: 0.5em 0;
            padding-left: 1.5em;
        }

        .task-id {
            color: var(--dim-color);
            margin-right: 1em;
            min-width: 2em;
            text-align: right;
        }

        .todo { color: var(--todo-color); }
        .staged { color: var(--stage-color); }
        .pushed { color: var(--done-color); }

        .comments {
            margin: 0.3em 0 0.3em 3em;
            color: var(--dim-color);
            font-size: 0.8em;
        }

        .dim {
            color: var(--dim-color);
        }

        .timestamp {
            color: var(--dim-color);
            font-size: 0.9em;
            margin-left: auto;
            padding-left: 2em;
        }

        .collapsed { display: none; }

        .arrow {
            display: inline-block;
            transition: transform 0.2s;
            margin-right: 0.5em;
            color: var(--dim-color);
        }

        .arrow.collapsed { transform: rotate(-90deg); }

        .section-title {
            display: inline-block;
            min-width: 5em;
        }

        .section-title.todo { color: var(--todo-color) }
        .section-title.stage { color: var(--stage-color) }
        .section-title.done { color: var(--done-color) }

        .task-content {
            flex: 1;
        }

        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 4px 8px;
            font-family: var(--font-main);
            font-size: 0.8em;
            background: transparent;
            color: var(--dim-color);
            border: none;
            cursor: pointer;
            opacity: 0.8;
            transition: opacity 0.2s;
        }

        .theme-toggle:hover {
            opacity: 1.0;
        }
    </style>
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()">Toggle Theme</button>
'''

    for page in pages:
        html_content += f'''
        <div class="page">
            <div class="page-header" onclick="toggleSection(this.parentElement)">
                <span class="arrow">▼</span>记 #{page.id}
                <span class="timestamp">{format_time(page.created_at)}</span>
            </div>
        <div class="page-content">'''

        sections = [
            ('todo', {k:v for k,v in page.task_map.items() if v.status == Status.TODO}, 'todo'),
            ('stage', {k:v for k,v in page.task_map.items() if v.status == Status.STAGED}, 'staged'),
            ('done', {k:v for k,v in page.task_map.items() if v.status == Status.PUSHED}, 'pushed')
        ]

        for section_name, section_tasks, status_class in sections:
            html_content += f'''
            <div class="section">
                <div class="section-header" onclick="toggleSection(this.parentElement)">
                    <span class="arrow">▼</span>
                    <span class="task-count">({len(section_tasks)})</span>
                    <span class="section-title {section_name}">{section_name}</span>
                </div>
            <div class="section-content">'''

            if not section_tasks:
                html_content += '''
                <div class="task">
                    <span class="task-id"></span>
                    <span class="dim">(empty)</span>
                </div>'''
            else:
                for task_id, task in sorted(section_tasks.items()):
                    html_content += f'''
                    <div class="task">
                        <span class="task-id">{task_id}</span>
                        <span class="task-content {status_class}">{task.content}</span>
                        <span class="timestamp">{format_time(task.last_modified)}</span>
                    </div>'''

                    if task.comment_list:
                        html_content += '<div class="comments">'
                        for i, comment in enumerate(task.comment_list):
                            html_content += f'''
                            <div class="task">
                                <span class="task-id">{i}</span>
                                <span class="task-content dim">{comment.content}</span>
                                <span class="timestamp">{format_time(comment.created_at)}</span>
                            </div>
                            '''

                        html_content += '</div>'
            html_content += '''</div></div>'''
        html_content += '''</div></div>'''

    html_content += '''
    <script>
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

        function toggleTheme() {
            document.body.classList.toggle('light');
            localStorage.setItem('theme', document.body.classList.value);
        }

        function loadSavedTheme() {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                document.body.classList.value = savedTheme;
            }
        }

        document.addEventListener('DOMContentLoaded', loadSavedTheme);
    </script>
    </body>
</html>'''

    output_path = repo.base_dir / 'tasks.html'
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f'Generated html at {output_path}')
    return output_path
