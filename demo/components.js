// Vanilla DOM renderers for each fixture component.
// Each renderer mirrors the real component's structure so the demo shows
// what a developer actually sees after storybook-codex generates stories.

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === 'onClick') node.addEventListener('click', value);
    else node.setAttribute(key, value === true ? '' : String(value));
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    node.appendChild(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

function withDefaults(args, defaults) {
  const merged = { ...defaults, ...args };
  for (const [key, value] of Object.entries(merged)) {
    if (value && typeof value === 'object' && value.__event__) {
      merged[key] = () => {
        const toast = document.createElement('div');
        toast.className = 'action-toast';
        toast.textContent = `${key}() fired`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 900);
      };
    }
  }
  return merged;
}

export const renderers = {
  Button(rawArgs) {
    const a = withDefaults(rawArgs, {
      children: 'Save changes',
      size: 'md',
      tone: 'neutral',
      disabled: false,
      loading: false,
    });
    const btn = el(
      'button',
      {
        'data-size': a.size,
        'data-tone': a.tone,
        type: 'button',
        class: 'sb-button',
        onClick: a.onClick,
      },
      a.loading ? 'Working...' : a.children,
    );
    if (a.disabled || a.loading) btn.setAttribute('disabled', '');
    return btn;
  },

  Alert(rawArgs) {
    const a = withDefaults(rawArgs, {
      title: 'Heads up',
      message: 'Something worth noting.',
      tone: 'info',
      dismissible: false,
    });
    const children = [
      el('strong', { class: 'sb-alert__title' }, a.title),
      el('p', { class: 'sb-alert__message' }, a.message),
    ];
    if (a.dismissible) {
      children.push(
        el(
          'button',
          { type: 'button', class: 'sb-alert__dismiss', onClick: a.onDismiss },
          'Dismiss',
        ),
      );
    }
    return el(
      'section',
      { 'data-tone': a.tone, class: 'sb-alert' },
      children,
    );
  },

  ThemeBadge(rawArgs) {
    const a = withDefaults(rawArgs, {
      label: 'Ready',
      theme: 'system',
      selected: false,
      compact: false,
    });
    return el(
      'span',
      {
        'data-theme': a.theme,
        'data-compact': String(Boolean(a.compact)),
        'aria-pressed': String(Boolean(a.selected)),
        class: 'sb-theme-badge',
      },
      a.label,
    );
  },

  Badge(rawArgs) {
    const a = withDefaults(rawArgs, {
      label: 'Ready',
      variant: 'soft',
      rounded: true,
    });
    return el(
      'span',
      {
        'data-variant': a.variant,
        'data-rounded': String(Boolean(a.rounded)),
        class: 'sb-badge',
      },
      a.label,
    );
  },

  InfoPanel(rawArgs) {
    const a = withDefaults(rawArgs, {
      title: 'System status',
      tone: 'info',
      compact: false,
      slot: 'Helpful supporting detail.',
    });
    // Matches fixtures/vue-info-panel/InfoPanel.vue: <strong>{{title}}</strong>
    // followed directly by <slot>...</slot>, no wrapping element.
    return el(
      'section',
      {
        'data-tone': a.tone,
        'data-compact': String(Boolean(a.compact)),
        class: 'sb-info-panel',
      },
      [el('strong', { class: 'sb-info-panel__title' }, a.title), document.createTextNode(a.slot)],
    );
  },

  StatusPill(rawArgs) {
    const a = withDefaults(rawArgs, {
      label: 'Ready',
      tone: 'neutral',
      selected: false,
      compact: false,
    });
    return el(
      'span',
      {
        'data-tone': a.tone,
        'data-selected': String(Boolean(a.selected)),
        'data-compact': String(Boolean(a.compact)),
        class: 'sb-status-pill',
      },
      a.label,
    );
  },
};

export function renderPreview(componentName, args) {
  const fn = renderers[componentName];
  if (!fn) {
    const fallback = document.createElement('div');
    fallback.className = 'preview-missing';
    fallback.textContent = `No renderer registered for ${componentName}`;
    return fallback;
  }
  return fn(args || {});
}
