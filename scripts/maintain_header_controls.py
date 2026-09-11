from pathlib import Path
import re

import maintain_filter_accessibility
from maintain_asset_versions import main as maintain_asset_versions


path = Path('index.html')
text = path.read_text(encoding='utf-8')

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

# The theme control's accessible name is maintained by the dedicated theme
# accessibility transform. Header maintenance only owns the decorative icon.
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
    section_matches = list(
        re.finditer(r'<section\b[^>]*\bclass="[^"]*\bsection-card\b[^"]*"[^>]*>', text[research_start:heading_pos])
    )
    section_start = research_start + section_matches[-1].start() if section_matches else -1
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

# Keep the GitHub header action as a secondary destination. The CV is the
# canonical primary action for research visitors and recruiters, so header
# maintenance must not require or recreate the older GitHub-primary state.
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
github_profile_primary = (
    '<a href="https://github.com/sakai1250" target="_blank" '
    'class="header-btn primary" rel="noopener noreferrer">\n'
    '              <span lang="ja">GitHub</span>\n'
    '              <span lang="en">GitHub</span>\n'
    '            </a>'
)
github_profile = (
    '<a href="https://github.com/sakai1250" target="_blank" '
    'class="header-btn" rel="noopener noreferrer">\n'
    '              <span lang="ja">GitHub</span>\n'
    '              <span lang="en">GitHub</span>\n'
    '            </a>'
)
if github_follow in text:
    text = text.replace(github_follow, github_profile, 1)
elif github_profile_same_tab in text:
    text = text.replace(github_profile_same_tab, github_profile, 1)
elif github_profile_primary in text:
    text = text.replace(github_profile_primary, github_profile, 1)
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

# Keep the CV as the primary static action at every maintenance stage instead of
# temporarily flipping priority and relying on a later transform to restore it.
cv_action = (
    '<a href="assets/cv.pdf" target="_blank" class="header-btn" '
    'rel="noopener noreferrer">'
)
cv_action_primary = (
    '<a href="assets/cv.pdf" target="_blank" class="header-btn primary" '
    'rel="noopener noreferrer">'
)
if cv_action in text:
    text = text.replace(cv_action, cv_action_primary, 1)
elif cv_action_primary not in text:
    raise SystemExit('Could not find primary CV header action')

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

path.write_text(text, encoding='utf-8')

# Keep browser cache keys tied to the current file contents. The optimization
# workflow already runs this helper whenever maintained site assets change.
maintain_asset_versions()
