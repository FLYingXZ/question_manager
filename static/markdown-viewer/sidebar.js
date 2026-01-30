(function() {
    'use strict';

    var sidebarClass = function() {
        this.init();
        for (var key = 0; key < window.eocourse.sidebarConstant.list.length; key++) {
            var val = window.eocourse.sidebarConstant.list[key];
            val.level = 0;
            this.paint(val, document.getElementById('sidebar_js'));
        }
    };

    // 解析 URL 参数
    var href = '';
    try {
        href = decodeURI(window.location.search).split('?target=/')[1].split(/&origin=\//g);
    } catch (e) {
        href = '';
    }

    sidebarClass.prototype = {
        init: function() {
            var template = {
                target: null
            };
            try {
                template.target = decodeURI(window.location.search)
                    .split('?target=')[1].split(/&origin=/g)[0];
            } catch (e) {
                template.target = null;
            }

            // emoji 配置
            editormd.emoji = {
                path: "http://www.emoji-cheat-sheet.com/graphics/emojis/",
                ext: ".png"
            };
            editormd.twemoji = {
                path: "http://twemoji.maxcdn.com/72x72/",
                ext: ".png"
            };

            // 加载 markdown 内容
            if (template.target) {
                var http = new XMLHttpRequest();
                http.open("GET", window.location.origin + template.target + '.md', true);
                http.send(null);
                http.onload = function() {
                    switch (http.status) {
                        case 200:
                            editormd.markdownToHTML("article-container-js", {
                                markdown: http.responseText,
                                sequenceDiagram: true,
                                flowChart: true,
                                emoji: true,
                                tex: true,
                                taskList: true
                            });
                            break;
                        default:
                            document.getElementById('article-container-js').innerHTML =
                                http.responseText.replace(/<(.*)style(.*)>/g, '');
                            break;
                    }
                };
            } else {
                window.location.href = window.location.href +
                    '?target=/static/markdown-viewer/md/index';
            }

            // 初始化编辑器相关逻辑
            this.initEditor();
        },

        paint: function(arg, elem) {
            var uniqueId = arg.href || arg.title; // 每项唯一标识
            var template = {
                target: (href[0] || '').replace(/\//g, '.'),
                origin: (href[1] || '').replace(/\//g, '.'),
                array: '',
                icon: (arg.icon || '').replace(/\//g, ''),
                title: arg.title.replace(/\//g, ''),
                href: (arg.href || '').replace(/\//g, '.')
            };
            template.array = (template.origin || template.target).split('.');

            var urlParams = new URLSearchParams(window.location.search);
            var currentTarget = urlParams.get('target');
            var isCurrent = (arg.href && arg.href === currentTarget);

            if (arg.href && isCurrent) {
                if ((template.origin && !arg.originHref) ||
                    (!template.origin && arg.originHref) ||
                    !(eval('/' + (template.href) + '$/').test('.' + template.target))) {
                    isCurrent = false;
                }
            }
            if (isCurrent && arg.href) {
                window.document.title = arg.title + ' - 学习中心';
            }

            // 展开状态
            var isExpanded = localStorage.getItem('sidebar_' + uniqueId) === 'expanded';

            var currentSelectedClass = (isCurrent && arg.href) ? ' current-selected' : '';

            var baseClass = 'common-level-' + arg.level;
            var activeClass = '';
            if (isCurrent && arg.href) {
                activeClass = ' elem-active level' + arg.level;
            } else if (arg.childList && isExpanded) {
                activeClass = ' level' + arg.level;
            } else if (arg.childList && !isExpanded) {
                activeClass = ' hidden';
            }

            var templateHtml =
                '<li class="' + baseClass + activeClass + currentSelectedClass + '" ' +
                    'data-id="' + uniqueId + '">' +
                    '<p level="' + arg.level + '" ' +
                        'class="' + (isExpanded ? 'ico_up' : 'ico_down') + '" ' +
                        'onclick="eocourse.sidebarClass.click(this)">' +
                        '<a ' + (arg.href ? (
                            'onclick="eocourse.sidebarClass.router(\'' + arg.href + '\'' +
                            (arg.originHref ? (',\'' + arg.originHref + '\'') : '') +
                            ')"') : '') + '>' +
                            (arg.childList
                                ? '<span class="pull-left ico"></span>'
                                : '<span class="pull-left unchild-span"></span>') +
                            arg.title +
                        '</a>' +
                    '</p>' +
                '</li>';

            var templateObj = {
                html: templateHtml,
                elem: null
            };
            templateObj.elem = document.createElement('ul');
            templateObj.elem.innerHTML = templateObj.html;
            elem.appendChild(templateObj.elem);

            // 递归子节点
            if (arg.childList) {
                for (var key = 0; key < arg.childList.length; key++) {
                    var val = arg.childList[key];
                    val.level = arg.level + 1;
                    this.paint(val, templateObj.elem.firstChild);
                }
            }
        },

        click: function(arg) {
            var liElement = arg.parentElement;
            var currentClass = liElement.getAttribute('class') || '';
            var level = arg.getAttribute('level');
            var uniqueId = liElement.getAttribute('data-id');

            if (/hidden/.test(currentClass)) {
                arg.setAttribute('class', 'ico_up');
                liElement.setAttribute(
                    'class',
                    currentClass.replace(/hidden/g, 'level' + level)
                );
                if (uniqueId) {
                    localStorage.setItem('sidebar_' + uniqueId, 'expanded');
                }
            } else {
                arg.setAttribute('class', 'ico_down');
                liElement.setAttribute('class', currentClass + ' hidden');
                if (uniqueId) {
                    localStorage.setItem('sidebar_' + uniqueId, 'collapsed');
                }
            }
        },

        router: function(href, originHref) {
            if (originHref) {
                window.location.href =
                    window.location.origin + window.location.pathname +
                    '?target=' + href + '&origin=' + originHref;
            } else {
                window.location.href =
                    window.location.origin + window.location.pathname +
                    '?target=' + href;
            }
        },

        initEditor: function() {
            const editButton = document.getElementById('edit-button');
            const editorContainer = document.getElementById('editor-container');
            const articleContainer = document.getElementById('article-container-js');
            const editorButtons = document.getElementById('editor-buttons');
            const saveButton = document.getElementById('save-markdown');
            const cancelButton = document.getElementById('cancel-edit');

            let editor = null;
            let currentFile = null;

            // 非管理员没有按钮，直接返回
            if (!editButton) return;
            if (!saveButton || !cancelButton || !editorContainer) return;

            const saveMarkdownContent = () => {
                if (!currentFile || !editor) {
                    alert('没有编辑的文件');
                    return;
                }
                const updatedMarkdown = editor.getMarkdown();

                fetch('/save_markdown', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: currentFile,
                        content: updatedMarkdown
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // 静默保存，可在需要时解开 alert
                            // alert('保存成功');
                        } else {
                            alert('保存失败: ' + data.message);
                        }
                    })
                    .catch(() => {
                        alert('保存请求失败');
                    });
            };

            editButton.addEventListener('click', () => {
                const urlParams = new URLSearchParams(window.location.search);
                const target = urlParams.get('target');
                if (!target) {
                    alert('未选择要编辑的文件');
                    return;
                }
                currentFile = target;

                fetch(currentFile + '.md')
                    .then(response => {
                        if (!response.ok) throw new Error('无法加载Markdown文件');
                        return response.text();
                    })
                    .then(markdown => {
                        articleContainer.style.display = 'none';
                        editorContainer.style.display = 'block';
                        editorButtons.style.display = 'flex';

                        editor = editormd("editor-container", {
                            width: "100%",
                            height: 800,
                            path: "/static/markdown-viewer/libs/",
                            value: markdown,
                            toolbarIcons: function () {
                                return editormd.toolbarModes['full'];
                            },
                            saveHTMLToTextarea: true,
                            htmlDecode: true,
                            onload: function () {
                                // Ctrl + S / Cmd + S
                                document.addEventListener('keydown', function(event) {
                                    if ((event.ctrlKey || event.metaKey) &&
                                        event.key.toLowerCase() === 's') {
                                        event.preventDefault();
                                        saveMarkdownContent();
                                    }
                                });
                            }
                        });
                    })
                    .catch(error => {
                        alert(error.message);
                    });
            });

            // 保存按钮
            saveButton.addEventListener('click', () => {
                if (!currentFile || !editor) {
                    alert('没有编辑的文件');
                    return;
                }
                const updatedMarkdown = editor.getMarkdown();

                fetch('/save_markdown', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: currentFile,
                        content: updatedMarkdown
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('保存成功');
                            window.location.reload();
                        } else {
                            alert('保存失败: ' + data.message);
                        }
                    })
                    .catch(() => {
                        alert('保存请求失败');
                    });
            });

            // 取消按钮
            cancelButton.addEventListener('click', () => {
                editorContainer.style.display = 'none';
                editorButtons.style.display = 'none';
                articleContainer.style.display = 'block';
            });
        }
    };

    window.eocourse.sidebarClass = new sidebarClass();
})();