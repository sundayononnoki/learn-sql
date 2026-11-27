(() => {
  const root = document.documentElement;
  const dialects = new Set(['postgresql', 'sqlserver', 'mysql']);
  const preferenceKey = 'sql-notes-dialect';
  const nativeDialect = root.dataset.nativeDialect;

  function storedMode() {
    try {
      return localStorage.getItem(preferenceKey);
    } catch {
      return null;
    }
  }

  function rememberMode(dialect) {
    try {
      localStorage.setItem(preferenceKey, dialect);
    } catch {
      // URL parameters carry the selection on browsers that restrict local storage.
    }
  }

  function currentMode() {
    if (dialects.has(nativeDialect)) return nativeDialect;
    const urlMode = new URLSearchParams(location.search).get('dialect');
    if (dialects.has(urlMode)) return urlMode;
    const savedMode = storedMode();
    return dialects.has(savedMode) ? savedMode : 'postgresql';
  }

  function addressWithMode(href, dialect) {
    const url = new URL(href, location.href);
    url.searchParams.set('dialect', dialect);
    return url;
  }

  function replaceAddress(url) {
    try {
      history.replaceState(null, '', url);
    } catch {
      // Some file viewers restrict history changes. The current page still switches.
    }
  }

  function appliesTo(section, dialect) {
    return section?.dataset.dialects?.split(' ').includes(dialect);
  }

  function redirectHiddenSection(dialect) {
    let id;
    try {
      id = decodeURIComponent(location.hash.slice(1));
    } catch {
      return;
    }
    const target = document.getElementById(id);
    const section = target?.closest('section[data-dialects]');
    if (!section || appliesTo(section, dialect)) return;
    const alternatives = (section.dataset.alternateAnchor || '').split(' ');
    const fallback = alternatives.map(anchor => document.getElementById(anchor))
      .find(alternative => appliesTo(alternative, dialect))
      || document.querySelector(`section.point[data-dialects~="${dialect}"]`);
    if (!fallback) return;
    const url = new URL(location.href);
    url.hash = fallback.id;
    replaceAddress(url);
    fallback.scrollIntoView();
  }

  function applyMode(dialect, save) {
    root.dataset.dialect = dialect;
    if (save) {
      rememberMode(dialect);
      replaceAddress(addressWithMode(location.href, dialect));
    }

    document.querySelectorAll('[data-dialect-button]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.dialectButton === dialect));
    });

    document.querySelectorAll('a[href]').forEach(link => {
      const href = link.getAttribute('href');
      if (href.startsWith('#') || !/\.html(?:[?#]|$)/.test(href)) return;
      const url = new URL(href, location.href);
      if (url.protocol !== location.protocol || url.origin !== location.origin) return;
      link.href = addressWithMode(href, dialect).href;
    });

    redirectHiddenSection(dialect);
  }

  function selectMode(dialect) {
    if (nativeDialect && nativeDialect !== dialect) {
      const id = dialect === 'mysql' ? 'core-chapters' : `${dialect}-chapters`;
      rememberMode(dialect);
      location.assign(addressWithMode(`../v1.html#${id}`, dialect));
      return;
    }
    applyMode(dialect, true);
  }

  root.dataset.dialect = currentMode();
  document.addEventListener('DOMContentLoaded', () => {
    applyMode(currentMode(), false);
    document.querySelectorAll('[data-dialect-button]').forEach(button => {
      button.addEventListener('click', () => selectMode(button.dataset.dialectButton));
    });
    window.addEventListener('hashchange', () => redirectHiddenSection(root.dataset.dialect));
    window.addEventListener('popstate', () => applyMode(currentMode(), false));
  });

  const lookup = document.createElement('script');
  lookup.src = new URL('operation-lookup.js', document.currentScript.src);
  document.head.append(lookup);
})();
