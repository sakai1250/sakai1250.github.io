# Taigo Sakai — Portfolio

Personal portfolio for Taigo Sakai, a computer vision researcher and engineer.

## Quick links

- **Portfolio:** https://sakai1250.github.io
- **CV:** https://sakai1250.github.io/assets/cv.pdf
- **Machine-readable CV:** https://sakai1250.github.io/assets/cv.txt
- **Machine-readable sources:** https://sakai1250.github.io/llms.txt
- **Research:** https://sakai1250.github.io/#research-content
- **Engineering:** https://sakai1250.github.io/#engineer-content
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

## Maintenance

- `index.html` contains the portfolio content and page structure.
- `style.css` controls the visual presentation and light/dark themes.
- `main.js` handles filtering, language switching, statistics, and interaction.
- `assets/cv.pdf` is the CV linked from the site header.
- `assets/cv.txt` mirrors the core CV content for machine-readable access.
- `llms.txt` routes machine-readable visitors to the appropriate primary sources.
- `sitemap.xml` and `robots.txt` support search indexing.
- When editing an app card, verify that its title, App Store URL, image, and GitHub repository all refer to the same product. In particular, `PresentMemo` is the MAIORAL repository and `otsuri_docter` is the おつりDoctor repository.

When portfolio content changes, keep `index.html`, `assets/cv.pdf`, `assets/cv.txt`, `llms.txt`, visible counts, and sitemap dates consistent.

## Deployment

GitHub Pages serves the `main` branch directly.
