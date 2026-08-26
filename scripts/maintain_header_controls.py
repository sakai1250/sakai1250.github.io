from pathlib import Path


path = Path('index.html')
text = path.read_text(encoding='utf-8')

language_button = '<button class="header-btn" id="lang-toggle" type="button">'
language_button_accessible = (
    '<button class="header-btn" id="lang-toggle" type="button" '
    'aria-label="Switch language / 言語切り替え">'
)
if language_button in text:
    text = text.replace(language_button, language_button_accessible, 1)
elif language_button_accessible not in text:
    raise SystemExit('Could not find language toggle button')

theme_button = (
    '<button class="header-btn" id="theme-toggle" type="button" '
    'aria-label="テーマ切り替え">'
)
theme_button_accessible = (
    '<button class="header-btn" id="theme-toggle" type="button" '
    'aria-label="Switch theme / テーマ切り替え">'
)
if theme_button in text:
    text = text.replace(theme_button, theme_button_accessible, 1)
elif theme_button_accessible not in text:
    raise SystemExit('Could not find theme toggle button')

# The header action opens the GitHub profile; it does not perform a follow action.
# Keep the label explicit so visitors know where the link goes before clicking.
github_follow = (
    '<a href="https://github.com/sakai1250" class="header-btn primary">\n'
    '              <span lang="ja">フォロー</span>\n'
    '              <span lang="en">Follow</span>\n'
    '            </a>'
)
github_profile = (
    '<a href="https://github.com/sakai1250" class="header-btn primary">\n'
    '              <span lang="ja">GitHub</span>\n'
    '              <span lang="en">GitHub</span>\n'
    '            </a>'
)
if github_follow in text:
    text = text.replace(github_follow, github_profile, 1)
elif github_profile not in text:
    raise SystemExit('Could not find GitHub profile header action')

# App names are already visible beside their thumbnails. Treat the thumbnails as
# decorative so screen readers do not announce the same generic "icon" label
# for every card.
app_thumbnail_alt = 'class="app-thumb" alt="icon"'
app_thumbnail_decorative = 'class="app-thumb" alt=""'
if app_thumbnail_alt in text:
    text = text.replace(app_thumbnail_alt, app_thumbnail_decorative)
elif app_thumbnail_decorative not in text:
    raise SystemExit('Could not find app thumbnail accessibility markers')

path.write_text(text, encoding='utf-8')
