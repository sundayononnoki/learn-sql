(() => {
  const assetUrl = new URL('.', document.currentScript.src);
  const projectUrl = new URL('../', assetUrl);
  const engines = { postgresql: 'PostgreSQL', sqlserver: 'SQL Server', mysql: 'MySQL' };

  function homepageLinks() {
    return Array.from(document.querySelectorAll('.roadmap-directory .roadmap-topic-list a[href]'), link => ({
      title: link.textContent.trim(),
      chapter: link.closest('.roadmap-stage').querySelector('h2').textContent.trim().replace(/^(\d{2})\s*/u, '$1 '),
      url: link.href,
    }));
  }

  let directoryRequest;
  function loadDirectory() {
    if (!directoryRequest) {
      directoryRequest = new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = new URL('search-index.js', assetUrl);
        script.onload = () => {
          if (Array.isArray(window.sqlRoadmapDirectoryLinks)) resolve(window.sqlRoadmapDirectoryLinks);
          else reject(new Error('Homepage directory links were not loaded'));
        };
        script.onerror = reject;
        document.head.append(script);
      }).catch(error => {
        directoryRequest = undefined;
        throw error;
      });
    }
    return directoryRequest;
  }

  function normalize(text) {
    return text.normalize('NFKC').trim().toLowerCase().replace(/\s+/gu, ' ');
  }

  function matchingLinks(links, query) {
    const terms = query.split(' ');
    return links
      .map(item => {
        const title = normalize(item.title);
        const score = title === query ? 3
          : title.startsWith(query) ? 2
          : terms.every(term => title.includes(term)) ? 1
          : 0;
        return { item, score };
      })
      .filter(({ score }) => score > 0)
      .sort((a, b) => b.score - a.score)
      .map(({ item }) => item);
  }

  function init() {
    const dialog = document.createElement('dialog');
    dialog.id = 'operation-dialog';
    dialog.setAttribute('aria-label', '搜索 SQL 笔记');
    dialog.innerHTML = `
      <div class="operation-search">
        <span class="operation-icon" aria-hidden="true"></span>
        <input type="search" aria-label="搜索首页关键词或用途"
          placeholder="搜索首页关键词或用途" autocomplete="off" aria-controls="operation-list" autofocus>
        <button type="button" id="operation-close" aria-label="关闭搜索">×</button>
      </div>
      <div class="operation-results">
        <p class="operation-status" role="status"></p>
        <ul class="operation-list" id="operation-list"></ul>
      </div>
      <div class="operation-footer">
        <span class="operation-engine"></span>
        <span class="operation-keys"><kbd>↑↓</kbd> 选择 <kbd>↵</kbd> 打开 <kbd>Esc</kbd> 关闭</span>
      </div>`;
    document.body.append(dialog);

    let launcher = document.querySelector('#operation-launcher');
    if (!launcher) {
      launcher = document.createElement('button');
      launcher.type = 'button';
      launcher.id = 'operation-launcher';
      launcher.className = 'operation-launcher-compact';
      launcher.setAttribute('aria-haspopup', 'dialog');
      launcher.setAttribute('aria-controls', dialog.id);
      launcher.setAttribute('aria-keyshortcuts', 'F');
      launcher.setAttribute('aria-label', '搜索 SQL 笔记');
      launcher.title = '搜索 SQL 笔记 (F)';
      launcher.innerHTML = '<span class="operation-icon" aria-hidden="true"></span>';
      document.querySelector('.site-header nav')?.append(launcher);
    }
    const search = dialog.querySelector('input');
    const status = dialog.querySelector('[role="status"]');
    const results = dialog.querySelector('.operation-results');
    const list = dialog.querySelector('ul');
    const engine = dialog.querySelector('.operation-engine');
    const activeMode = () => document.documentElement.dataset.dialect;
    let directory = homepageLinks();
    let returnFocus;

    function showResults(items, mode) {
      const entries = items.map(item => {
        const li = document.createElement('li');
        const link = document.createElement('a');
        const url = new URL(item.url, projectUrl);
        url.searchParams.set('dialect', mode);
        link.href = url;
        const title = document.createElement('span');
        title.textContent = item.title;
        link.append(title);
        link.className = 'operation-hit';
        const context = document.createElement('small');
        context.textContent = item.chapter;
        link.append(context);
        li.append(link);
        return li;
      });
      list.replaceChildren(...entries);
      results.scrollTop = 0;
    }

    async function filterOperations() {
      const query = normalize(search.value);
      const mode = activeMode();
      engine.textContent = engines[mode];
      if (!query) {
        status.textContent = '';
        showResults([], mode);
        return;
      }
      const isCurrent = () => dialog.open && query === normalize(search.value) && mode === activeMode();
      try {
        if (!directory.length) {
          status.textContent = '正在载入首页目录…';
          showResults([], mode);
          directory = await loadDirectory();
          if (!isCurrent()) return;
        }
        const matches = matchingLinks(directory, query);
        status.textContent = matches.length
          ? '找到 ' + matches.length + ' 项'
          : '首页目录里没有匹配的链接。';
        showResults(matches, mode);
      } catch {
        if (isCurrent()) status.textContent = '首页目录加载失败。';
      }
    }

    function openLookup() {
      if (dialog.open) return;
      returnFocus = document.activeElement;
      search.value = '';
      filterOperations();
      dialog.showModal();
      search.focus();
      if (!directory.length) loadDirectory().then(links => { directory = links; }).catch(() => {});
    }

    search.addEventListener('input', filterOperations);
    launcher.addEventListener('click', openLookup);
    launcher.hidden = false;

    const header = document.querySelector('.site-header');
    if (header) {
      const alignAnchor = () => {
        const { height, bottom } = header.getBoundingClientRect();
        document.documentElement.style.setProperty('--measured-header-offset', `calc(${Math.ceil(height)}px + .5rem)`);
        const target = document.querySelector(':target');
        const top = target?.getBoundingClientRect().top;
        if (top >= 0 && top < bottom) target.scrollIntoView();
      };
      alignAnchor();
      new ResizeObserver(alignAnchor).observe(header);
    }

    dialog.querySelector('#operation-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('close', () => {
      if (returnFocus && returnFocus !== document.body) returnFocus.focus({ preventScroll: true });
    });

    let pointerStartedOutside = false;
    dialog.addEventListener('pointerdown', event => {
      pointerStartedOutside = event.target === dialog;
    });
    dialog.addEventListener('click', event => {
      if (pointerStartedOutside && event.target === dialog) dialog.close();
      if (event.target.closest('a') && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) {
        dialog.close();
      }
      pointerStartedOutside = false;
    });

    document.addEventListener('keydown', event => {
      if (dialog.open || event.defaultPrevented || event.repeat || event.isComposing ||
          event.metaKey || event.ctrlKey || event.altKey || event.key.toLowerCase() !== 'f') return;
      if (event.target instanceof HTMLElement &&
          (event.target.isContentEditable || event.target.closest('input, textarea, select'))) return;
      event.preventDefault();
      openLookup();
    });

    dialog.addEventListener('keydown', event => {
      if (event.isComposing || event.keyCode === 229) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        dialog.close();
        return;
      }
      const focused = document.activeElement;
      if (event.key === 'Enter' && focused === search) {
        event.preventDefault();
        list.querySelector('a')?.click();
      }
      if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
      const focusOrder = [search, ...list.querySelectorAll('a')];
      const index = focusOrder.indexOf(focused);
      if (index < 0) return;
      event.preventDefault();
      focusOrder[index + (event.key === 'ArrowDown' ? 1 : -1)]?.focus();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
