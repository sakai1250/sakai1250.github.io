import re
import runpy
from pathlib import Path

path = Path('main.js')
text = path.read_text(encoding='utf-8')

contact_replacement = r'''function initContactForm() {
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
}'''

contact_pattern = re.compile(
    r'function initContactForm\(\) \{[\s\S]*?\n\}\n\n(?=async function initQiitaArticles\(\) \{)'
)
text, contact_count = contact_pattern.subn(contact_replacement + '\n\n', text, count=1)
if contact_count != 1:
    raise SystemExit('Could not find contact form function')

qiita_replacement = r'''async function initQiitaArticles() {
    const c = document.getElementById('qiita-list');
    if (!c) return;

    const showError = () => {
        const lang = document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'ja';
        c.textContent = lang === 'en'
            ? 'Could not load Qiita articles.'
            : 'Qiita記事を読み込めませんでした。';
    };

    try {
        const r = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent('https://qiita.com/sakai1250/feed')}`);
        if (!r.ok) {
            showError();
            return;
        }

        const d = await r.json();
        if (d.status !== 'ok' || !Array.isArray(d.items)) {
            showError();
            return;
        }

        const articles = [];
        d.items.slice(0, 5).forEach(i => {
            let url;
            try {
                url = new URL(i.link);
            } catch {
                return;
            }
            if (url.protocol !== 'https:' || url.hostname !== 'qiita.com') return;
            articles.push({ url: url.href, title: String(i.title || 'Qiita article') });
        });

        if (!articles.length) {
            showError();
            return;
        }

        c.replaceChildren();
        articles.forEach(article => {
            const l = document.createElement('li');
            const a = document.createElement('a');
            a.href = article.url;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            a.textContent = article.title;
            l.appendChild(a);
            c.appendChild(l);
        });
    } catch {
        showError();
    }
}'''

qiita_pattern = re.compile(
    r'async function initQiitaArticles\(\) \{[\s\S]*?\n\}',
)
text, qiita_count = qiita_pattern.subn(qiita_replacement, text, count=1)
if qiita_count != 1:
    raise SystemExit('Could not find Qiita article function')

path.write_text(text, encoding='utf-8')

html_path = Path('index.html')
html = html_path.read_text(encoding='utf-8')
contact_fields = {
    'name': 'name',
    'email': 'email',
}
for field_id, autocomplete in contact_fields.items():
    pattern = re.compile(rf'(<(?:input|textarea)\b(?=[^>]*\bid="{re.escape(field_id)}")[^>]*?)(?:\s+autocomplete="[^"]*")?\s*>')
    html, count = pattern.subn(rf'\1 autocomplete="{autocomplete}">', html, count=1)
    if count != 1:
        raise SystemExit(f'Could not find contact field: {field_id}')
html_path.write_text(html, encoding='utf-8')

runpy.run_path('scripts/maintain_external_links.py', run_name='__main__')
