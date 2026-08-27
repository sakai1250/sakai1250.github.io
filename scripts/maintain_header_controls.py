from pathlib import Path

import maintain_filter_accessibility
from maintain_asset_versions import main as maintain_asset_versions


path = Path('index.html')
text = path.read_text(encoding='utf-8')

# Make search results and shared links identify the research field immediately.
# "Portfolio" alone is generic and wastes the most visible metadata field.
old_title = '<title>Taigo Sakai | Portfolio</title>'
new_title = '<title>Taigo Sakai | Computer Vision Researcher</title>'
if old_title in text:
    text = text.replace(old_title, new_title, 1)
elif new_title not in text:
    raise SystemExit('Could not find expected document title')

old_og_title = '<meta property="og:title" content="Taigo Sakai | Portfolio">'
new_og_title = '<meta property="og:title" content="Taigo Sakai | Computer Vision Researcher">'
if old_og_title in text:
    text = text.replace(old_og_title, new_og_title, 1)
elif new_og_title not in text:
    raise SystemExit('Could not find expected Open Graph title')

# Keep social-card metadata as complete as the Open Graph metadata. This makes
# shared portfolio links identify the person and research field without relying
# on platform-specific fallback behavior.
twitter_creator = '<meta name="twitter:creator" content="@ikaitaig">'
twitter_metadata = (
    '<meta name="twitter:creator" content="@ikaitaig">\n'
    '  <meta name="twitter:title" content="Taigo Sakai | Computer Vision Researcher">\n'
    '  <meta name="twitter:description" content="Ph.D. Student and Special Assistant at Meijo University researching Computer Vision, Continual Learning, and Multi-View Tracking.">\n'
    '  <meta name="twitter:image" content="https://github.com/sakai1250.png">\n'
    '  <meta name="twitter:image:alt" content="Portrait of Taigo Sakai">'
)
if '<meta name="twitter:title"' not in text:
    if twitter_creator not in text:
        raise SystemExit('Could not find Twitter creator metadata')
    text = text.replace(twitter_creator, twitter_metadata, 1)

og_image = '<meta property="og:image" content="https://github.com/sakai1250.png">'
og_image_with_alt = (
    '<meta property="og:image" content="https://github.com/sakai1250.png">\n'
    '  <meta property="og:image:alt" content="Portrait of Taigo Sakai">'
)
if '<meta property="og:image:alt"' not in text:
    if og_image not in text:
        raise SystemExit('Could not find Open Graph image metadata')
    text = text.replace(og_image, og_image_with_alt, 1)

# Keep social previews on the same origin as the portfolio. Using the local
# avatar avoids making Open Graph/Twitter previews depend on GitHub's profile
# image endpoint, which can change independently of this site.
legacy_social_image = 'content="https://github.com/sakai1250.png"'
local_social_image = 'content="https://sakai1250.github.io/assets/avatar.jpg"'
if legacy_social_image in text:
    text = text.replace(legacy_social_image, local_social_image)
elif text.count(local_social_image) < 2:
    raise SystemExit('Could not find expected social preview image metadata')

# The default document language is Japanese, but the page can switch to English.
# Keep the keyboard skip link consistent with the visible language as well.
skip_link_ja_only = '<a class="skip-link" href="#main-content">本文へスキップ</a>'
skip_link_bilingual = (
    '<a class="skip-link" href="#main-content">'
    '<span lang="ja">本文へスキップ</span>'
    '<span lang="en">Skip to main content</span>'
    '</a>'
)
if skip_link_ja_only in text:
    text = text.replace(skip_link_ja_only, skip_link_bilingual, 1)
elif skip_link_bilingual not in text:
    raise SystemExit('Could not find skip link')

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

# The theme control already has an accessible name. Its moon/sun glyph is only
# visual state decoration, so do not make screen readers announce it as text.
theme_icon = '<span id="theme-icon">☾</span>'
theme_icon_decorative = '<span id="theme-icon" aria-hidden="true">☾</span>'
if theme_icon in text:
    text = text.replace(theme_icon, theme_icon_decorative, 1)
elif theme_icon_decorative not in text:
    raise SystemExit('Could not find theme icon')

# The loading overlay is visual feedback only and repeats the already available
# page identity. Keep it out of the accessibility tree from the first render.
loading_screen = '<div id="loading-screen">'
loading_screen_decorative = '<div id="loading-screen" aria-hidden="true">'
if loading_screen in text:
    text = text.replace(loading_screen, loading_screen_decorative, 1)
elif loading_screen_decorative not in text:
    raise SystemExit('Could not find loading screen')

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

# The portrait sits immediately beside the visible name and identity. Announcing
# the same name again for the image adds noise without conveying new content.
header_avatar = 'class="header-avatar" src="assets/avatar.jpg" alt="Taigo Sakai"'
header_avatar_decorative = 'class="header-avatar" src="assets/avatar.jpg" alt=""'
if header_avatar in text:
    text = text.replace(header_avatar, header_avatar_decorative, 1)
elif header_avatar_decorative not in text:
    raise SystemExit('Could not find header avatar accessibility marker')

# App names are already visible beside their thumbnails. Treat the thumbnails as
# decorative so screen readers do not announce the same generic "icon" label
# for every card.
app_thumbnail_alt = 'class="app-thumb" alt="icon"'
app_thumbnail_decorative = 'class="app-thumb" alt=""'
if app_thumbnail_alt in text:
    text = text.replace(app_thumbnail_alt, app_thumbnail_decorative)
elif app_thumbnail_decorative not in text:
    raise SystemExit('Could not find app thumbnail accessibility markers')

# Utility controls sit outside the main language-toggle labels. Give each one a
# bilingual accessible name so screen-reader users do not encounter a mixed
# Japanese/English control surface after switching the visible language.
utility_labels = {
    'aria-label="Back to top"': 'aria-label="Back to top / トップへ戻る"',
    'aria-label="目次"': 'aria-label="Table of contents / 目次"',
    'aria-label="Close"': 'aria-label="Close / 閉じる"',
}
for old_label, bilingual_label in utility_labels.items():
    if old_label in text:
        text = text.replace(old_label, bilingual_label, 1)
    elif bilingual_label not in text:
        raise SystemExit(f'Could not find utility control label: {old_label}')

path.write_text(text, encoding='utf-8')

# Keep browser cache keys tied to the current file contents. The optimization
# workflow already runs this helper whenever maintained site assets change.
maintain_asset_versions()
