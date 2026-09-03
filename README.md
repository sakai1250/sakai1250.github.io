# Taigo Sakai — Portfolio

Personal portfolio for Taigo Sakai, a Ph.D. student, Special Assistant, computer vision researcher, and engineer at Meijo University.

## Quick links

- **Portfolio:** https://sakai1250.github.io
- **Research:** https://sakai1250.github.io/#research-content
- **Research achievements:** https://sakai1250.github.io/#research-research-achievements
- **Awards:** https://sakai1250.github.io/#research-awards
- **Engineering:** https://sakai1250.github.io/#engineer-content
- **Apps & services:** https://sakai1250.github.io/#engineer-my-apps-and-services
- **CV:** https://sakai1250.github.io/assets/cv.pdf
- **Machine-readable CV:** https://sakai1250.github.io/assets/cv.txt
- **Machine-readable sources:** https://sakai1250.github.io/llms.txt
- **Google Scholar:** https://scholar.google.com/citations?user=eS-5wrQAAAAJ
- **GitHub:** https://github.com/sakai1250
- **Qiita:** https://qiita.com/sakai1250
- **LinkedIn:** https://www.linkedin.com/in/sakai1250
- **Contact:** mailto:263441505@ccmailg.meijo-u.ac.jp

## Focus

- Research: continual learning, long-tailed learning, multi-view detection and tracking
- Engineering: deep learning systems, iOS/Web applications, research tooling

The site keeps research outputs, awards, applications, and the downloadable CV in one place so that research collaborators, recruiters, and engineers can reach the relevant material directly.

## Local preview

This site is static HTML, CSS, and JavaScript. No build step is required.

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Local validation

Before opening a pull request, install the maintenance dependency and run the same transforms checked by CI:

```bash
python3 -m pip install -r requirements-maintenance.txt
python3 -m py_compile scripts/*.py
python3 scripts/run_deterministic_maintenance.py
python3 scripts/check_deterministic_idempotency.py
python3 scripts/maintain_profile_metadata.py
python3 scripts/maintain_static_fallbacks.py
python3 scripts/check_app_repo_links.py
python3 scripts/check_local_deep_links.py
python3 scripts/check_site_integrity.py
python3 scripts/check_control_accessible_names.py
python3 scripts/check_form_control_names.py
python3 scripts/check_new_tab_link_security.py
python3 scripts/check_progressive_enhancement.py
python3 scripts/check_security_contact.py
python3 scripts/check_structured_profile.py
python3 scripts/check_llms_profile.py
python3 scripts/check_year_filter_coverage.py
git diff --exit-code -- index.html 404.html main.js effects.js style.css sitemap.xml
```

If the final command reports changes, include the generated maintenance updates in the same branch before pushing.

External URLs are checked by a separate network-dependent workflow. When changing publication, CV, profile, organization, app, or repository URLs, run the same check locally when network access is available:

```bash
python3 scripts/check_external_links.py
```

This catches broken or redirected navigation before it reaches researchers, recruiters, or other visitors, while keeping transient network failures separate from deterministic local checks.

## Maintenance

- `index.html` contains the portfolio content and page structure.
- `style.css` controls the visual presentation and light/dark themes.
- `main.js` handles filtering, language switching, statistics, and interaction.
- `effects.js` contains restrained visual effects plus accessibility and presentation helpers layered on top of the core interactions.
- `scripts/*.py` contains repeatable maintenance transforms and checks used by GitHub Actions; keep transforms idempotent so repeated runs do not alter already-correct content.
- `assets/cv.pdf` is the CV linked from the site header.
- `assets/cv.txt` mirrors the core CV content for machine-readable access.
- `llms.txt` routes machine-readable visitors to the appropriate primary sources.
- `sitemap.xml` and `robots.txt` support search indexing.
- Keep the visible role and affiliation in `index.html` aligned with `assets/cv.txt` and `llms.txt`, including current titles such as `Special Assistant`.
- Keep the JSON-LD `Person` data in `index.html` aligned with the visible profile and CV, especially `jobTitle`, current affiliation, and `sameAs` links.
- Keep the primary portfolio content visible without JavaScript. Do not place a full-screen loader or other overlay in front of the page that requires JavaScript to disappear; optional effects may fail without blocking research, CV, contact, or GitHub navigation.
- When editing an app card, verify that its title, App Store URL, image, and GitHub repository all refer to the same product. In particular, `PresentMemo` is the MAIORAL repository and `otsuri_docter` is the おつりDoctor repository.

When portfolio content changes, keep `index.html`, `assets/cv.pdf`, `assets/cv.txt`, `llms.txt`, visible counts, and sitemap dates consistent.

## Deployment

`.github/workflows/optimize-portfolio.yml` prepares and, when possible, commits the finalized portfolio state. `.github/workflows/static.yml` runs after that workflow completes regardless of its conclusion, checks out the latest `main` branch, and deploys that valid state to GitHub Pages. This keeps a transient optimization or external-fetch failure from blocking an otherwise valid portfolio update.