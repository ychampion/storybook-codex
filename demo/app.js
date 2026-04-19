import { renderPreview } from './components.js';

const listEl = document.getElementById('component-list');
const nameEl = document.getElementById('component-name');
const frameworkEl = document.getElementById('component-framework');
const pathEl = document.getElementById('component-path');
const storyGridEl = document.getElementById('story-grid');
const storySourceEl = document.getElementById('story-source');
const componentSourceEl = document.getElementById('component-source');
const blueprintEl = document.getElementById('blueprint-output');
const generatedAtEl = document.getElementById('generated-at');

function formatArgs(args) {
  const keys = Object.keys(args || {});
  if (!keys.length) return 'default meta args';
  return keys
    .map((key) => {
      const value = args[key];
      if (value && typeof value === 'object' && value.__event__) return `${key}=fn()`;
      if (typeof value === 'string') return `${key}="${value}"`;
      return `${key}=${value}`;
    })
    .join(' \u00B7 ');
}

// Append an inline-formatted text run to `parent`. Handles backticks for
// code, **bold**, and _italic_. All DOM creation is node-based so the
// blueprint markdown never flows through innerHTML.
function appendInline(parent, text) {
  const tokenRe = /(`[^`]+`|\*\*[^*]+\*\*|(?<![A-Za-z0-9])_[^_]+_(?![A-Za-z0-9]))/g;
  let lastIndex = 0;
  for (const match of text.matchAll(tokenRe)) {
    if (match.index > lastIndex) {
      parent.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
    }
    const token = match[0];
    if (token.startsWith('`')) {
      const code = document.createElement('code');
      code.textContent = token.slice(1, -1);
      parent.appendChild(code);
    } else if (token.startsWith('**')) {
      const strong = document.createElement('strong');
      strong.textContent = token.slice(2, -2);
      parent.appendChild(strong);
    } else {
      const em = document.createElement('em');
      em.textContent = token.slice(1, -1);
      parent.appendChild(em);
    }
    lastIndex = match.index + token.length;
  }
  if (lastIndex < text.length) {
    parent.appendChild(document.createTextNode(text.slice(lastIndex)));
  }
}

function renderMarkdownInto(container, markdown) {
  container.textContent = '';
  const lines = markdown.replace(/\r\n/g, '\n').split('\n');
  let paragraph = [];
  let listItems = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    const p = document.createElement('p');
    appendInline(p, paragraph.join(' '));
    container.appendChild(p);
    paragraph = [];
  };
  const flushList = () => {
    if (!listItems.length) return;
    const ul = document.createElement('ul');
    for (const text of listItems) {
      const li = document.createElement('li');
      appendInline(li, text);
      ul.appendChild(li);
    }
    container.appendChild(ul);
    listItems = [];
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      const h = document.createElement(`h${level}`);
      appendInline(h, heading[2]);
      container.appendChild(h);
      continue;
    }
    const bullet = line.match(/^[-*]\s+(.*)$/);
    if (bullet) {
      flushParagraph();
      listItems.push(bullet[1]);
      continue;
    }
    flushList();
    paragraph.push(line);
  }
  flushParagraph();
  flushList();
}

function renderStoryCards(component) {
  storyGridEl.textContent = '';
  const stories = component.stories.length
    ? component.stories
    : [{ name: 'Default', args: {} }];

  for (const story of stories) {
    const combined = { ...(component.metaArgs || {}), ...(story.args || {}) };
    const card = document.createElement('article');
    card.className = 'story-card';
    card.dataset.testid = `story-card-${story.name}`;

    const header = document.createElement('header');
    header.className = 'story-card__header';
    const title = document.createElement('h4');
    title.textContent = story.name;
    const argsLine = document.createElement('p');
    argsLine.className = 'story-card__args';
    argsLine.textContent = formatArgs(story.args || {});
    header.appendChild(title);
    header.appendChild(argsLine);

    const canvas = document.createElement('div');
    canvas.className = 'story-card__canvas';
    canvas.dataset.testid = `canvas-${story.name}`;
    try {
      canvas.appendChild(renderPreview(component.name, combined));
    } catch (error) {
      canvas.textContent = `Render error: ${error.message}`;
      canvas.classList.add('story-card__canvas--error');
    }

    card.appendChild(header);
    card.appendChild(canvas);
    storyGridEl.appendChild(card);
  }
}

function renderComponent(component) {
  nameEl.textContent = component.name;
  frameworkEl.textContent = component.framework;
  frameworkEl.dataset.framework = component.framework;
  pathEl.textContent = component.componentPath;

  renderStoryCards(component);

  storySourceEl.textContent = component.storySource;
  componentSourceEl.textContent = component.componentSource;
  renderMarkdownInto(blueprintEl, component.blueprintMarkdown);

  for (const button of listEl.querySelectorAll('button')) {
    const active = button.dataset.component === component.name;
    button.classList.toggle('is-active', active);
    button.setAttribute('aria-selected', active ? 'true' : 'false');
  }
}

function buildSidebar(components, onSelect) {
  listEl.textContent = '';
  for (const component of components) {
    const item = document.createElement('li');
    item.setAttribute('role', 'presentation');
    const button = document.createElement('button');
    button.type = 'button';
    button.setAttribute('role', 'tab');
    button.dataset.component = component.name;
    button.dataset.testid = `nav-${component.name}`;

    const nameSpan = document.createElement('span');
    nameSpan.className = 'nav-item__name';
    nameSpan.textContent = component.name;
    const fwSpan = document.createElement('span');
    fwSpan.className = 'nav-item__framework';
    fwSpan.dataset.framework = component.framework;
    fwSpan.textContent = component.framework;

    button.appendChild(nameSpan);
    button.appendChild(fwSpan);
    button.addEventListener('click', () => onSelect(component));
    item.appendChild(button);
    listEl.appendChild(item);
  }
}

async function main() {
  const res = await fetch('data.json', { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to load data.json: ${res.status}`);
  const payload = await res.json();
  if (payload.generatedAt) {
    const ts = new Date(payload.generatedAt);
    generatedAtEl.textContent = `Built ${ts.toISOString().slice(0, 19).replace('T', ' ')} UTC`;
  }
  const components = payload.components;
  buildSidebar(components, renderComponent);
  renderComponent(components[0]);
  document.body.dataset.ready = 'true';
}

main().catch((error) => {
  document.body.dataset.ready = 'error';
  const mainPanel = document.getElementById('main-panel');
  mainPanel.textContent = '';
  const errDiv = document.createElement('div');
  errDiv.className = 'fatal';
  errDiv.textContent = `Failed to load demo data: ${error.message}`;
  mainPanel.appendChild(errDiv);
  console.error(error);
});
