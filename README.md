# Taigo Sakai — Portfolio

Personal portfolio for Taigo Sakai, a Ph.D. student, Special Assistant, computer vision researcher, and engineer at Meijo University.

## Quick links

- **Portfolio:** https://sakai1250.github.io
- **Research:** https://sakai1250.github.io/#research-content
- **Engineering:** https://sakai1250.github.io/#engineer-content
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
for script in \
  scripts/maintain_tabs.py \
  scripts/maintain_contact_form.py \
  scripts/maintain_header_controls.py \
  scripts/maintain_profile_metadata.py \
  scripts/maintain_filter_accessibility.py \
  scripts/maintain_storage_resilience.py \
  scripts/maintain_external_links.py \
  scripts/maintain_resource_link_accessibility.py \
  scripts/maintain_reduced_motion.py \
  scripts/maintain_asset_versions.py; do
  python3 "$script"
done
python3 scripts/check_app_repo_links.py
git diff --exit-code -- index.html 404.html main.js effects.js style.css
```

If the final command reports changes, include the generated maintenance updates in the same branch before pushing.

## Maintenance

- `index.html` contains the portfolio content and page structure.
- `style.css` controls the visual presentation and light/dark themes.
- `main.js` handles filtering, language switching, statistics, and interaction.
- `effects.js` contains restrained visual effects plus accessibility and presentation helpers layered on top of the core interactions.
- `scripts/*.py` contains repeatable maintenance transforms used by GitHub Actions; keep these transforms idempotent so repeated runs do not alter already-correct content.
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