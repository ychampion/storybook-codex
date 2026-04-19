const statusEl = document.querySelector('#status');
const summaryEl = document.querySelector('#summary');
const cardsEl = document.querySelector('#cards');
const reloadBtn = document.querySelector('#reload');
const fileInput = document.querySelector('#file-input');
const cardTemplate = document.querySelector('#card-template');

const DEFAULT_CASES_URL = '../../fixtures/cases.json';

function setStatus(message, tone = 'neutral') {
  statusEl.textContent = message;
  statusEl.dataset.tone = tone;
}

function stat(label, value) {
  const wrapper = document.createElement('div');
  wrapper.className = 'stat';
  wrapper.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
  return wrapper;
}

function renderSummary(contract) {
  const sections = Object.entries(contract).filter(([, value]) => Array.isArray(value));
  summaryEl.replaceChildren(
    ...sections.map(([name, value]) => stat(name, value.length)),
  );
}

function createList(items) {
  const list = document.createElement('ul');
  for (const item of items) {
    const entry = document.createElement('li');
    entry.textContent = item;
    list.append(entry);
  }
  return list;
}

function renderCard(sectionName, items) {
  const fragment = cardTemplate.content.cloneNode(true);
  fragment.querySelector('h2').textContent = sectionName;
  fragment.querySelector('.count').textContent = `${items.length} cases`;

  const body = fragment.querySelector('.card-body');
  for (const item of items) {
    const block = document.createElement('section');
    block.className = 'case';
    const title = document.createElement('h3');
    title.textContent = item.name || item.story || item.component || 'Unnamed case';
    block.append(title);

    const meta = document.createElement('p');
    meta.className = 'meta';
    meta.textContent = Object.entries(item)
      .filter(([key, value]) => typeof value === 'string' && key !== 'name')
      .map(([key, value]) => `${key}: ${value}`)
      .join(' • ');
    if (meta.textContent) {
      block.append(meta);
    }

    for (const [key, value] of Object.entries(item)) {
      if (!Array.isArray(value) || value.length === 0) {
        continue;
      }
      const label = document.createElement('h4');
      label.textContent = key;
      block.append(label);
      block.append(createList(value.map((entry) => (
        typeof entry === 'string' ? entry : JSON.stringify(entry)
      ))));
    }

    body.append(block);
  }

  return fragment;
}

function renderContract(contract) {
  renderSummary(contract);
  cardsEl.replaceChildren();

  for (const [sectionName, items] of Object.entries(contract)) {
    if (!Array.isArray(items)) {
      continue;
    }
    cardsEl.append(renderCard(sectionName, items));
  }
}

async function loadDefaultContract() {
  setStatus(`Loading ${DEFAULT_CASES_URL}…`);
  const response = await fetch(DEFAULT_CASES_URL, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const contract = await response.json();
  renderContract(contract);
  setStatus(`Loaded ${DEFAULT_CASES_URL}`, 'success');
}

reloadBtn.addEventListener('click', () => {
  loadDefaultContract().catch((error) => {
    setStatus(`Could not load contract automatically: ${error.message}`, 'error');
  });
});

fileInput.addEventListener('change', async (event) => {
  const [file] = event.target.files || [];
  if (!file) {
    return;
  }

  const contract = JSON.parse(await file.text());
  renderContract(contract);
  setStatus(`Loaded ${file.name}`, 'success');
});

loadDefaultContract().catch((error) => {
  setStatus(
    `Could not load ${DEFAULT_CASES_URL}. Use "Load local JSON" if you opened the viewer without a static server. (${error.message})`,
    'error',
  );
});
