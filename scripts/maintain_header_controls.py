from pathlib import Path

import maintain_filter_accessibility
from maintain_asset_versions import main as maintain_asset_versions


path = Path('index.html')
text = path.read_text(encoding='utf-8')

# Make search results and shared links identify both the current academic stage
# and the research field immediately. Keep older titles as migration inputs so
# repeated maintenance remains safe across previously generated states.
legacy_titles = (
    '<title>Taigo Sakai | Portfolio</title>',
    '<title>Taigo Sakai | Computer Vision Researcher</title>',
    '<title>Taigo Sakai | Ph.D. Student &amp; Computer Vision Researcher</title>',
)
current_title = '<title>Taigo Sakai | Ph.D. Student, Special Assistant &amp; Computer Vision Researcher</title>'
for legacy_title in legacy_titles:
    if legacy_title in text:
        text = text.replace(legacy_title, current_title, 1)
        break
else:
    if current_title not in text:
        raise SystemExit('Could not find expected document title')

legacy_og_titles = (
    '<meta property="og:title" content="Taigo Sakai | Portfolio">',
    '<meta property="og:title" content="Taigo Sakai | Computer Vision Researcher">',
    '<meta property="og:title" content="Taigo Sakai | Ph.D. Student &amp; Computer Vision Researcher">',
)
current_og_title = '<meta property="og:title" content="Taigo Sakai | Ph.D. Student, Special Assistant &amp; Computer Vision Researcher">'
for legacy_og_title in legacy_og_titles:
    if legacy_og_title in text:
        text = text.replace(legacy_og_title, current_og_title, 1)
        break
else:
    if current_og_title not in text:
        raise SystemExit('Could not find expected Open Graph title')

# Keep social-card metadata as complete as the Open Graph metadata. This makes
# shared portfolio links identify the person and research field without relying
# on platform-specific fallback behavior.
twitter_creator = '<meta name="twitter:creator" content="@ikaitaig">'
twitter_metadata = (
    '<meta name="twitter:creator" content="@ikaitaig">\n'
    '  <meta name="twitter:title" content="Taigo Sakai | Ph.D. Student, Special Assistant &amp; Computer Vision Researcher">\n'
    '  <meta name="twitter:description" content="Ph.D. Student and Special Assistant at Meijo University researching Computer Vision, Continual Learning, and Multi-View Tracking.">\n'
    '  <meta name="twitter:image" content="https://github.com/sakai1250.png">\n'
    '  <meta name="twitter:image:alt" content="Portrait of Taigo Sakai">'
)
legacy_twitter_titles = (
    '<meta name="twitter:title" content="Taigo Sakai | Computer Vision Researcher">',
    '<meta name="twitter:title" content="Taigo Sakai | Ph.D. Student &amp; Computer Vision Researcher">',
)
current_twitter_title = '<meta name="twitter:title" content="Taigo Sakai | Ph.D. Student, Special Assistant &amp; Computer Vision Researcher">'
if '<meta name="twitter:title"' not in text:
    if twitter_creator not in text:
        raise SystemExit('Could not find Twitter creator metadata')
    text = text.replace(twitter_creator, twitter_metadata, 1)
else:
    for legacy_twitter_title in legacy_twitter_titles:
        if legacy_twitter_title in text:
            text = text.replace(legacy_twitter_title, current_twitter_title, 1)
            break
    else:
        if current_twitter_title not in text:
            raise SystemExit('Could not find expected Twitter title')

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

# Google Fonts is optional visual polish, not a prerequisite for the portfolio.
# A normal external stylesheet in <head> can hold first paint while a mobile
# browser waits on fonts.googleapis.com. Load it with print media first so the
# page renders immediately using the existing system-font fallbacks, then apply
# the web fonts only after the stylesheet has arrived.
google_fonts_url = (
    'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&'
    'family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;600;700&display=swap'
)
blocking_google_fonts = (
    '  <link\n'
    f'    href="{google_fonts_url}"\n'
    '    rel="stylesheet">'
)
nonblocking_google_fonts = (
    '  <link\n'
    f'    href="{google_fonts_url}"\n'
    '    rel="stylesheet" media="print" onload="this.media=\'all\'">'
)
if blocking_google_fonts in text:
    text = text.replace(blocking_google_fonts, nonblocking_google_fonts, 1)
elif nonblocking_google_fonts not in text:
    raise SystemExit('Could not find expected Google Fonts stylesheet')
if f'href="{google_fonts_url}"' in text and 'media="print" onload="this.media=\'all\'"' not in text:
    raise SystemExit('Google Fonts must remain non-render-blocking')

# Primer CSS was only used for the footer share button. Reuse the site's own
# button style instead so initial rendering does not depend on an extra CDN CSS
# request, especially on slower mobile connections.
primer_css = '  <link rel="stylesheet" href="https://unpkg.com/@primer/css@22.0.2/dist/primer.css">\n'
if primer_css in text:
    text = text.replace(primer_css, '', 1)
elif 'unpkg.com/@primer/css' in text:
    raise SystemExit('Unexpected Primer CSS reference')

share_primer_class = 'target="_blank" class="btn btn-sm"'
share_local_class = 'target="_blank" class="header-btn"'
if share_primer_class in text:
    text = text.replace(share_primer_class, share_local_class, 1)
elif share_local_class not in text:
    raise SystemExit('Could not find footer share button style marker')

# Never place a full-screen loader in front of the portfolio. If JavaScript fails
# or a mobile browser stops execution early, a blocking overlay turns a valid
# static page into a blank screen. The page is useful immediately without it.
loading_markup = (
    '  <div id="loading-screen" aria-hidden="true">\n'
    '    <div class="spinner">Taigo Sakai</div>\n'
    '  </div>\n'
)
if loading_markup in text:
    text = text.replace(loading_markup, '', 1)

# The research record is the strongest evidence for both research visitors and
# recruiters. Keep it before education in the source HTML, not only after a
# JavaScript DOM reorder, so the information priority survives script failures.
def find_research_section(english_heading):
    research_start = text.find('<div id="research-content"')
    if research_start == -1:
        raise SystemExit('Could not find research content')
    heading = f'<span lang="en">{english_heading}</span>'
    heading_pos = text.find(heading, research_start)
    if heading_pos == -1:
        raise SystemExit(f'Could not find research section: {english_heading}')
    section_start = text.rfind('<section class="section-card">', research_start, heading_pos)
    section_end = text.find('</section>', heading_pos)
    if section_start == -1 or section_end == -1:
        raise SystemExit(f'Could not bound research section: {english_heading}')
    return section_start, section_end + len('</section>')

education_start, education_end = find_research_section('Education')
achievements_start, achievements_end = find_research_section('Research Achievements')
if education_start < achievements_start:
    achievements_block = text[achievements_start:achievements_end]
    text = text[:achievements_start] + text[achievements_end:]
    education_start, _ = find_research_section('Education')
    text = text[:education_start] + achievements_block + '\n\n' + text[education_start:]

# The header action opens the GitHub profile; it does not perform a follow action.
# Keep the label explicit so visitors know where the link goes before clicking.
github_follow = (
    '<a href="https://github.com/sakai1250" class="header-btn primary">\n'
    '              <span lang="ja">フォロー</span>\n'
    '              <span lang="en">Follow</span>\n'
    '            </a>'
)
github_profile_same_tab = (
    '<a href="https://github.com/sakai1250" class="header-btn primary">\n'
    '              <span lang="ja">GitHub</span>\n'
    '              <span lang="en">GitHub</span>\n'
    '            </a>'
)
github_profile = (
    '<a href="https://github.com/sakai1250" target="_blank" '
    'class="header-btn primary" rel="noopener noreferrer">\n'
    '              <span lang="ja">GitHub</span>\n'
    '              <span lang="en">GitHub</span>\n'
    '            </a>'
)
if github_follow in text:
    text = text.replace(github_follow, github_profile, 1)
elif github_profile_same_tab in text:
    text = text.replace(github_profile_same_tab, github_profile, 1)
elif github_profile not in text:
    raise SystemExit('Could not find GitHub profile header action')

# The linked document is an academic CV rather than a general-purpose resume.
# Keep the header wording consistent with the 404 recovery navigation and the
# English label so research visitors and recruiters know what the document is.
cv_resume_label = (
    '              <span lang="ja">履歴書</span>\n'
    '              <span lang="en">CV</span>'
)
cv_academic_label = (
    '              <span lang="ja">CV</span>\n'
    '              <span lang="en">CV</span>'
)
if cv_resume_label in text:
    text = text.replace(cv_resume_label, cv_academic_label, 1)
elif cv_academic_label not in text:
    raise SystemExit('Could not find academic CV header label')

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

# Name the top-level tab list by what it actually switches. "Primary sections"
# is vague when announced without visual context; this identifies the two views
# directly for screen-reader users.
primary_nav_generic = '<nav class="tab-nav header-tab-nav" aria-label="Primary sections">'
primary_nav_descriptive = (
    '<nav class="tab-nav header-tab-nav" '
    'aria-label="Research and engineering / 研究と開発">'
)
if primary_nav_generic in text:
    text = text.replace(primary_nav_generic, primary_nav_descriptive, 1)
elif primary_nav_descriptive not in text:
    raise SystemExit('Could not find primary tab navigation landmark')

# Name navigation landmarks by their purpose rather than their visual contents.
# "Cards" does not tell screen-reader users that this control moves between
# portfolio sections such as research, awards, and engineering work.
section_nav_generic = '<nav id="section-tab-nav" class="section-tab-nav" aria-label="Cards"></nav>'
section_nav_descriptive = (
    '<nav id="section-tab-nav" class="section-tab-nav" '
    'aria-label="Portfolio sections / ポートフォリオ内の項目"></nav>'
)
if section_nav_generic in text:
    text = text.replace(section_nav_generic, section_nav_descriptive, 1)
elif section_nav_descriptive not in text:
    raise SystemExit('Could not find section navigation landmark')

path.write_text(text, encoding='utf-8')

# Keep browser cache keys tied to the current file contents. The optimization
# workflow already runs this helper whenever maintained site assets change.
maintain_asset_versions()
