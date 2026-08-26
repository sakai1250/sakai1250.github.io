import re
from pathlib import Path

path = Path('main.js')
text = path.read_text(encoding='utf-8')

replacement = r'''function initContactForm() {
    const f = document.getElementById('contact-form');
    if (!f) return;

    const status = document.getElementById('form-status');
    if (status) {
        status.setAttribute('role', 'status');
        status.setAttribute('aria-live', 'polite');
    }

    f.addEventListener('submit', async (e) => {
        e.preventDefault();
        const button = f.querySelector('button[type="submit"]') || f.querySelector('button');
        if (!button) return;

        const lang = document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'ja';
        const labels = lang === 'en'
            ? { sending: 'Sending…', success: 'Message sent.', error: 'Could not send the message.' }
            : { sending: '送信中…', success: '送信しました。', error: '送信できませんでした。' };
        const originalButtonHTML = button.innerHTML;

        button.disabled = true;
        button.setAttribute('aria-busy', 'true');
        button.textContent = labels.sending;

        try {
            const response = await fetch(f.action, {
                method: f.method,
                body: new FormData(f),
                headers: { 'Accept': 'application/json' }
            });
            if (status) status.textContent = response.ok ? labels.success : labels.error;
            if (response.ok) f.reset();
        } catch {
            if (status) status.textContent = labels.error;
        } finally {
            button.disabled = false;
            button.removeAttribute('aria-busy');
            button.innerHTML = originalButtonHTML;
        }
    });
}

async function initQiitaArticles() {'''

pattern = re.compile(
    r'function initContactForm\(\) \{[\s\S]*?\n\}\n\nasync function initQiitaArticles\(\) \{'
)
updated, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit('Could not find contact form function')

path.write_text(updated, encoding='utf-8')
