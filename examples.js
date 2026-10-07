// Shared example controls work for lessons, quiz prompts, and worked answers.
export function installExampleTools() {
  const dialog = document.createElement('dialog');
  dialog.className = 'example-dialog';
  dialog.setAttribute('aria-labelledby', 'example-dialog-title');
  dialog.innerHTML = `<header><h2 id="example-dialog-title">Example</h2><button type="button" class="dialog-close" aria-label="Close expanded example">Close ✕</button></header><div class="example-zoom"><button type="button" data-zoom="-1" aria-label="Zoom out">−</button><output aria-live="polite">100%</output><button type="button" data-zoom="1" aria-label="Zoom in">+</button><button type="button" data-zoom="0">Reset</button></div><div class="expanded-example prose"></div><p class="meta">Scroll to explore · Escape to close</p>`;
  document.body.append(dialog);
  let opener;
  let zoom = 1;
  const updateZoom = () => {
    dialog.querySelector('output').textContent = `${Math.round(zoom * 100)}%`;
    dialog.querySelector('.expanded-example > *').style.zoom = zoom;
    dialog.querySelector('[data-zoom="-1"]').disabled = zoom <= .75;
    dialog.querySelector('[data-zoom="1"]').disabled = zoom >= 2;
  };
  dialog.querySelector('.dialog-close').onclick = () => dialog.close();
  dialog.addEventListener('close', () => {
    document.body.classList.remove('example-open');
    if (opener?.isConnected) opener.focus({ preventScroll: true });
  });
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) {
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    }
    const button = event.target.closest('[data-zoom]');
    if (!button) return;
    zoom = button.dataset.zoom === '0' ? 1 : Math.max(.75, Math.min(2, zoom + Number(button.dataset.zoom) * .25));
    updateZoom();
  });
  addEventListener('hashchange', () => { if (dialog.open) dialog.close(); });
  document.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-example]');
    if (!button) return;
    const figure = button.closest('.example-block');
    if (button.dataset.example === 'copy') {
      try {
        await navigator.clipboard.writeText(figure.querySelector('template').content.textContent);
        button.textContent = 'Copied ✓';
      } catch { button.textContent = 'Use Expand to select'; }
      setTimeout(() => { if (button.isConnected) button.textContent = 'Copy'; }, 2500);
      return;
    }
    opener = button;
    zoom = 1;
    dialog.querySelector('h2').textContent = figure.querySelector('.example-label').textContent;
    const clone = figure.querySelector('.example-content').cloneNode(true);
    clone.removeAttribute('tabindex');
    dialog.querySelector('.expanded-example').replaceChildren(clone);
    updateZoom();
    document.body.classList.add('example-open');
    dialog.showModal();
  });
}
