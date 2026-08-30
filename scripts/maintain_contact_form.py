import re
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
            ? { sending: 'Sending…', success: 'Message sent.', error: 'Could not send the message.', emailFallback: 'Email directly instead.' }
            : { sending: '送信中…', success: '送信しました。', error: '送信できませんでした。', emailFallback: 'メールで直接連絡する' };
        const originalButtonHTML = button.innerHTML;
        const showError = () => {
            if (!status) return;
            const link = document.createElement('a');
            link.href = 'mailto:263441505@ccmailg.meijo-u.ac.jp';
            link.textContent = labels.emailFallback;
            status.replaceChildren(document.createTextNode(`${labels.error} `), link);
        };

        button.disabled = true;
        button.setAttribute('aria-busy', 'true');
        button.textContent = labels.sending;

        const controller = new AbortController();
        const timeoutId = window.setTimeout(() => controller.abort(), 10000);

        if (status) status.textContent = '';

        try {
            const response = await fetch(f.action, {
                method: f.method,
                body: new FormData(f),
                headers: { 'Accept': 'application/json' },
                signal: controller.signal
            });
            if (response.ok) {
                if (status) status.textContent = labels.success;
                f.reset();
            } else {
                showError();
            }
        } catch {
            showError();
        } finally {
            window.clearTimeout(timeoutId);
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
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = 'https://qiita.com/sakai1250';
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = lang === 'en' ? 'Open Qiita profile' : 'Qiitaプロフィールを開く';
        const message = lang === 'en'
            ? 'Could not load recent Qiita articles. '
            : 'Qiitaの最新記事を読み込めませんでした。';
        item.append(document.createTextNode(message), link);
        c.replaceChildren(item);
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

# The result of the contact submission is important user feedback, not visual
# decoration. Keep its live-region semantics in the static HTML so assistive
# technology can understand the region without relying on initialization code.
status_plain = '<div id="form-status" class="form-status"></div>'
status_accessible = (
    '<div id="form-status" class="form-status" role="status" '
    'aria-live="polite" aria-atomic="true"></div>'
)
if status_plain in html:
    html = html.replace(status_plain, status_accessible, 1)
elif status_accessible not in html:
    raise SystemExit('Could not find contact form status region')

html_path.write_text(html, encoding='utf-8')