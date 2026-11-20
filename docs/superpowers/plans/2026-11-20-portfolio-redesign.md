# ポートフォリオ再設計 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 静的ポートフォリオを「Index(紙面)土台 + ヒーローの動く研究図」の見た目に作り替え、研究業績 18 件を構造化する。

**Architecture:** 3 段階(Stage 1 再設計 / Stage 2 ヒーロー / Stage 3 業績の構造化)。この repo は 31 本の保守スクリプトと多数のチェックが HTML/CSS/JS の文字列を前提にしているため、**各タスクの終わりに必ず「保守を 2 回流しても差分が出ない」ことを確認**し、衝突したスクリプトは意味(アクセシビリティ・ローカライズ・リンク)を保ったまま新構造に更新する。テストに当たるものは、先に書く `check_*.py`(赤→緑)と、`run_local_validation.py`、ブラウザ目視。

**Tech Stack:** HTML / CSS(`@layer`、OKLCH、コンテナクエリ、スクロール連動、View Transitions)/ Vanilla JS(Canvas 2D)/ Python 3.14 の保守スクリプト / Node(構文確認と幾何の単体確認)。

**Spec:** `docs/superpowers/specs/2026-11-20-portfolio-redesign-design.md`(視覚の基準は承認済みモック `docs/superpowers/specs/assets/direction-v1.html` の A と C。Task 0 で repo にコピーする)

## Global Constraints

- 静的 HTML/CSS/JS。ビルド・フレームワークなし。主要内容は JS なしで読める(README の必須要件)。
- 論文・受賞・文言は 1 文字も変えない。新しい可視テキストは `<span lang="ja">` と `<span lang="en">` の両方を用意する。
- `style.css` は単一ファイルのまま(5 本の保守と `maintain_asset_versions` がパスで直接読む)。`@layer reset, tokens, base, layout, components;`
- 書体は Geist / Geist Mono / Noto Sans JP。Cormorant Garamond・DM Sans・ゴールド系(`#C6A15B` `#8A611E` `#EEE2CA`、`--accent-2`、`--accent-soft`)を残さない。
- 色は OKLCH。ライト: `--bg oklch(0.991 0.001 106)`、`--text-main oklch(0.178 0 90)`、`--muted oklch(0.557 0.008 107)`、`--accent oklch(0.56 0.19 34)`(文字・リンク用、4.97:1)、`--accent-mark oklch(0.639 0.206 34)`(点・罫線・ヒーロー用、文字に使わない)。ダーク: `--bg oklch(0.141 0.004 286)`、`--text-main oklch(0.929 0.004 286)`、`--muted oklch(0.636 0.013 286)`、`--accent` と `--accent-mark` は `oklch(0.639 0.206 34)`。文字は AA 4.5:1 以上。
- **既存のカスタムプロパティ名を維持して値だけ変える**: `--bg --bg-2 --surface --surface-2 --text-main --text-sub --muted --accent --stroke`(inline style・`main.js`・`maintain_storage_resilience.py` が使用)。
- 影は柔らかいもの(blur あり)を使わない(`.modal*` のみ可)。ピル型(`border-radius` 999px 等)を使わない。
- CSS に残してはいけない文字列: `.reveal-item` `.reveal-active` `#loading-screen` `.spinner` `quietPulse` `.cursor {` `@keyframes blink`。HTML に残してはいけない: `effects.js` `class="cursor"` `header-bottom` `data-jump=` `header-hint`。キーフレーム名に `blink` を使わない。
- 保守スクリプトが CSS に要求する文字列(新 CSS が満たす。満たせないものは意味を保ってスクリプトを更新): `/* Header stat navigation */` のブロック、`.badge-row h3 {`、`.app-detail-trigger {`、`.toc-link:hover::after,\n.toc-link:focus-visible::after {` のブロック、`html[data-lang="en"] [lang="en"] { display: revert !important; }`(と隣の `[lang="en"] { display: none !important; }`、`html[data-lang="en"] [lang="ja"] { display: none !important; }`)、`@media (max-width: 768px)` 内の `body::before { display: none !important; }` / `-webkit-backdrop-filter: none !important;` / `backdrop-filter: none !important;` / `.header-bar { background: var(--bg-2) !important; }`(`/* Mobile rendering safety: … */` の見出し付きブロック)。`.header-actions .header-btn.primary { display: none; }` は書かない。`.tab-content` に `display: none` を書かない。
- 保守スクリプトが HTML に要求する anchor(移動は**そのまま切り貼り**し、打ち直さない): `<h1 class="header-name">Taigo Sakai</h1>`、`<span id="typing-text">`、`.header-avatar`、`.stat-item` / `#stat-papers` `#stat-awards` `#stat-apps`、`.header-btn`(`#lang-toggle` `#theme-toggle` `#theme-icon`、CV は `.header-btn.primary`)、`nav.tab-nav.header-tab-nav` と `.tab-item[data-tab]`、`.filter-row.year-filter` と `.chip[data-year]`、`#search-count`、`#section-tab-nav`、`.profile-links`、`#toc-fab`、`#back-to-top`、`li[data-year]` + `.badge-year` + `.repo-list`(受賞など他セクションは構造を変えない)。
- `main.js` の関数本文は保守スクリプトが文字列で照合する。**関数を編集する前に** `grep -ln "<関数名>" scripts/*.py` を実行し、ヒットしたスクリプトを同時に更新する。
- 年フィルタ・検索は `li` に inline の `style.display` を付ける。`li` の `display` に `!important` を付けない。
- 検証コマンド(これが完了条件): `git diff --exit-code` が作業ツリーとインデックスを比べるため、対象をステージしてから流す。
  ```bash
  git add index.html main.js style.css scripts README.md
  python3 scripts/run_local_validation.py
  ```
  `hero-tracking.js` は Task 7 で作ってから `git add` に加える(存在しないパスを渡すと `git add` 全体が失敗する)。
  実行環境: Python は `.python-version`(3.14)、依存は `requirements-maintenance.txt`。未導入なら `uv run --python 3.14 --with-requirements requirements-maintenance.txt python scripts/run_local_validation.py`。
- コミットはユーザーの許可があったときだけ。許可前は `git add` までで止める。メッセージは Conventional Commits、末尾に `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。Stage ごとに 1 コミットを提案する。

## Review Focus

仕様が示唆しているが、どのタスクのテストも直接は踏まない入力。持ち主のいるタスクに、それぞれ確認手順を入れてある。

1. 国内発表 11 件は `「題名」` 形式でリンクなし(国際 7 件は `“題名,”` + Paper リンク)。構造化は両方で、可視テキストが不変であること → Task 10, 11。
2. 年フィルタ・検索で構造化行が隠れ、戻ること。全件が隠れたセクションごと消えること → Task 12。
3. 390px 幅で長い英語題名(ATLASFusion)と長い著者列が横スクロールを起こさないこと → Task 12。
4. `prefers-reduced-motion` で図が止まり、View Transitions も使わないこと → Task 5, 7。
5. JS 無効でも、暗い帯の中の名前・役割・統計が読め、言語切替で免責文言が ja/en 切り替わること。`#engineer-content` への直リンクで開発タブが開くこと → Task 6, 9。

## File Structure

- 作る: `hero-tracking.js`(図の純粋な幾何+描画)、`scripts/check_color_contrast.py`、`scripts/check_design_system.py`、`scripts/check_hero_tracking.py`、`scripts/check_publication_structure.py`、`scripts/maintain_publication_structure.py`、`docs/superpowers/specs/assets/direction-v1.html`(モックの複製)
- 変える: `style.css`(全面)、`index.html`(ヘッダー/ヒーロー/レールの構造、書体リンク、図)、`main.js`(`initStats`、`initReadingProgress`、新 `initViewTransitions`)、`scripts/maintain_tabs.py` `maintain_static_portfolio_polish.py` `maintain_reduced_motion.py` `maintain_asset_versions.py`、`scripts/run_local_validation.py`(CHECKS 追加と `node --check hero-tracking.js`)、`scripts/run_deterministic_maintenance.py`(登録)、`scripts/check_site_integrity.py`(必須ファイルに `hero-tracking.js`)、`README.md`(保守の説明)
- 変えない: 受賞・学歴などのリスト構造、`assets/`、`404.html`、`llms.txt`、`sitemap.xml`

---

## Stage 0 — 基準

### Task 0: 基準の確定とモックの複製

**Files:** Create `docs/superpowers/specs/assets/direction-v1.html`

**Interfaces:** Produces: 変更前の緑の検証結果(以降の赤は自分の変更が原因と言い切れる)と、視覚の基準ファイル。

- [ ] **Step 1: 作業ツリーを確認** — `git status --short`。期待: `index.html` `main.js` `style.css` が変更されていない(`.claude/` `.opencode/` `docs/` `fix_*.py` などの未追跡のみ)。変更があれば止めてユーザーに報告。
- [ ] **Step 2: 変更前の検証を通す** — 上記の検証コマンドを実行。期待: 終了コード 0。**失敗したら既存の問題なので、手を付けずにユーザーへ報告して止まる。**
- [ ] **Step 3: モックを複製** — `cp /private/tmp/claude-501/-Users-sakaitaigoware-sakai1250-github-io/d737f2a1-0f37-44d1-8456-ce1ba4cecbac/scratchpad/brainstorm-project/.superpowers/brainstorm/42308-1795102100/content/direction-v1.html docs/superpowers/specs/assets/direction-v1.html`(`mkdir -p` してから)。コピー元が無ければ、承認済みの値は本計画の Global Constraints を正とし、ユーザーに伝える。
- [ ] **Step 4: 論文一覧の変更前テキストを退避** — Task 11 の「可視テキスト不変」の基準にする。
  ```bash
  python3 - <<'EOF'
  import re, html
  t = open('index.html', encoding='utf-8').read()
  s = re.search(r'<section class="section-card" id="research-research-achievements">(.*?)</section>', t, re.S).group(1)
  items = re.findall(r'<li data-year="\d{4}">(.*?)</li>', s, re.S)
  open('/private/tmp/claude-501/-Users-sakaitaigoware-sakai1250-github-io/d737f2a1-0f37-44d1-8456-ce1ba4cecbac/scratchpad/achievements-before.txt', 'w', encoding='utf-8').write(
      "\n".join(" ".join(html.unescape(re.sub(r'<[^>]+>', ' ', i)).split()) for i in items))
  print(len(items))
  EOF
  ```
  期待: `18`。

---

## Stage 1 — 見た目の置き換え

Stage 1 の途中(Task 3 と 4 の間)は見た目が中間状態になる。コミットは Task 6 の後に 1 回。

### Task 1: コントラスト検査(ガードレール)

**Files:** Create `scripts/check_color_contrast.py`; Modify `scripts/run_local_validation.py`(`CHECKS` に追加)

**Interfaces:** Produces:
- `parse_color(value: str) -> tuple[float, float, float]`(sRGB 0–1。`#rrggbb` と `oklch(L C H)` を受ける)
- `contrast_ratio(fg: str, bg: str) -> float`
- `theme_tokens(css: str) -> dict[str, dict[str, str]]`(キー `"light"` は最初の `:root {…}`、`"dark"` は `[data-theme="dark"] {…}`。値が `var(...)` のものは読み飛ばす)

- [ ] **Step 1: 自己テストを先に書く**(`check_sidebar_role_derivation.py` と同じ流儀で、合成入力を `main()` の先頭に置く)。アサーション: `round(contrast_ratio("#000000", "#ffffff"), 2) == 21.0`、`contrast_ratio("oklch(0.178 0 90)", "oklch(0.991 0.001 106)") >= 18.0`、`parse_color("oklch(0.639 0.206 34)")` が `parse_color("#EE4B24")` と各チャンネル 0.02 以内。
- [ ] **Step 2: 実行して失敗を確認** — `python3 scripts/check_color_contrast.py`。期待: `FAIL`(未実装)。
- [ ] **Step 3: 実装** — OKLab→線形 sRGB 変換(Björn Ottosson の係数)→ガンマ→相対輝度。実 CSS の検査: 各テーマで `(--text-main,--bg)` `(--text-sub,--bg)` `(--muted,--bg)` `(--accent,--bg)` は 4.5 以上、`(--accent-mark,--bg)` は 3.0 以上、`--hero-fg`/`--hero-bg` があれば 4.5 以上。さらに `--hero-accent-rgb`(後述)があれば `--accent-mark` を変換した値と各チャンネル 3 以内で一致すること。
- [ ] **Step 4: 実行して通ることを確認** — 現行 CSS(16 進)で `PASS`(ガードレールであり、ここは赤ではない)。
- [ ] **Step 5: 登録の整合** — `python3 scripts/check_validation_docs.py`。期待: `Validation entry point aligned: …` の行(CHECKS に漏れなし)。ステージのみ。

### Task 2: デザイン方針の検査(先に赤)

**Files:** Create `scripts/check_design_system.py`; Modify `scripts/run_local_validation.py`

**Interfaces:** Produces: `problems_in_index(html: str) -> list[str]`、`problems_in_css(css: str) -> list[str]`(空なら合格)。

- [ ] **Step 1: 失敗するテストを書く** — 合成入力で、悪い例が検出されること、良い例が通ることを `main()` 先頭で検証する。検出する項目: (a) `index.html` の Google Fonts リンクに `family=Geist:` `family=Geist+Mono:` `Noto+Sans+JP` が無い、または `Cormorant` / `DM+Sans` がある (b) CSS に `Cormorant` `DM Sans` ゴールド系の値(Global Constraints)がある (c) `@layer reset, tokens, base, layout, components;` が無い (d) `--accent-mark` が未定義 (e) `border-radius` が 999/9999/50/100px (`50%` は可) (f) blur を持つ `box-shadow` が `.modal` を含まないセレクタにある (g) 禁止文字列(Global Constraints)がある。
- [ ] **Step 2: 実行して失敗を確認** — 現行ファイルに対して `python3 scripts/check_design_system.py`。期待: (a)(b)(c)(d)(e)(f) で `FAIL`。これが Task 4 で緑にする赤。
- [ ] **Step 3: `CHECKS` に登録** し、`python3 scripts/check_validation_docs.py` が通ることを確認。

### Task 3: ヘッダー・ヒーロー・レールの構造変更

**Files:** Modify `index.html`、`main.js`(`initStats`)、`scripts/maintain_reduced_motion.py`

**Interfaces:** Produces(Task 4・8 が使う DOM):
```
header.header-bar            スティッキーな細いバー
  .header-inner > .header-top > a.header-brand[href="#top"] "T. Sakai" + .header-actions(そのまま)
  .header-tab-row(そのまま: nav.header-tab-nav + .filter-row.year-filter)
section.hero#top             header の直後に新設
  .header-profile(そのまま移動: img.header-avatar, h1.header-name, .header-subtitle, #typing-text)
  ul.hero-areas > li ×N       assets/cv.txt の RESEARCH AREAS の箇条書きと同じ文字
  .header-stats(そのまま移動)
```
旧 `aside.profile-sidebar` は構造を変えず、CSS(Task 4)で左レールにする。

- [ ] **Step 1: ブロックを切り貼りで移動** — `.header-profile` と `.header-stats` を `header.header-bar` から出して `section.hero#top` に入れる。打ち直さない。`.header-top` には `a.header-brand` と `.header-actions` を残す。`ul.hero-areas` は `scripts/cv_profile.py` の `read_cv_section_bullets(cv_text, "RESEARCH AREAS")` と同じ文字にする。
- [ ] **Step 2: 保守を流して衝突を洗い出す** — `python3 scripts/run_deterministic_maintenance.py`。期待: 終了コード 0 で `git diff --stat -- index.html` が意図した移動だけ。`SystemExit` が出たら、そのスクリプト名を読み、正規表現を新構造に合わせる。**アサーション(アクセシビリティ名・ローカライズ・リンク・CV 由来の値)は 1 つも消さない。** 直したら `python3 scripts/check_*.py` の関連チェックも流す。
- [ ] **Step 3: `initStats` を静的に** — `grep -ln "initStats" scripts/*.py` で `maintain_reduced_motion.py` を確認。`initStats()` はカウントアップをやめ、`publicationCount` `awardCount` `appCount` を `textContent` に直接代入する。`maintain_reduced_motion.py` の `reduced_motion_stats` を新本文に置き換え、旧 2 形(`legacy_stats` と現行)をどちらも新本文へ移行できるようにする。
- [ ] **Step 4: 検証** — `node --check main.js`。ステージして `python3 scripts/run_deterministic_maintenance.py && git diff --exit-code -- index.html main.js style.css`(保守が冪等)。期待: 終了コード 0。`run_local_validation.py` 全体は Task 2 で登録した `check_design_system.py` が Task 4 まで赤のため、`CHECKS` のうちそれ以外を `for c in $(grep -o 'scripts/check_[a-z_]*\.py' scripts/run_local_validation.py | grep -v design_system); do python3 $c || break; done` で流し、全て終了コード 0。

### Task 4: `style.css` の全面置き換え

**Files:** Modify `style.css`、`index.html`(書体リンク)、`scripts/maintain_tabs.py`、`scripts/maintain_static_portfolio_polish.py`

**Interfaces:** Consumes: Task 3 の DOM。Produces: `@layer` 構成と、後続タスクが使うトークン `--hero-bg --hero-fg --hero-accent-rgb --hair --hair-strong`、グリッド骨格 `.hero` `.container-lg`。

- [ ] **Step 1: 書体リンクを置換** — `index.html` の Google Fonts `href` を `family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Noto+Sans+JP:wght@400;500;700&display=swap` にする(`media="print" onload` の方式は維持)。
- [ ] **Step 2: `style.css` を書き直す** — 数値(名前の `clamp(56px,10.5vw,124px)`、字間 `-.058em`、罫線の間隔、行の余白)は承認済みモックの `.mock-a` 規則を写す。構成: `tokens`(ライト/`[data-theme="dark"]`、`--hero-*` は両テーマで暗い帯)/ `base`(書体と文字サイズ)/ `layout`(細いスティッキーバー、ヒーロー 12 カラム、左レール + 本文の 2 カラム、モバイル 1 カラム)/ `components`(タブはテキスト+下線、`.chip` は選択中を下線+太字、`.section-card` は罫線のみ、リスト、アプリカード、モーダル、TOC・トップへ戻る、連絡フォーム、`.badge-row h3 {`、`.app-detail-trigger {`、`/* Header stat navigation */`、言語切替 3 行、モバイル安全ブロック)。`.profile-card` は枠・影なしのレール。サイドバーの `.profile-name` は視覚的に隠す(ヒーローと二重になるため。DOM は残す)。
- [ ] **Step 3: 衝突するスクリプトを更新** — `maintain_tabs.py` の `new_css` を新しい `.tab-item {` ブロックの冒頭に合わせ、`old_css`(旧ピル)は移行元として残す。`maintain_static_portfolio_polish.py` は `DESKTOP_STATS_RULE` とその追記分岐を削除(新ヘッダーは `.header-stats` を平行移動しない)。カーソル除去は残す。
- [ ] **Step 4: 赤を緑に** — `python3 scripts/check_design_system.py`(Task 2 の赤)→ `PASS`。`python3 scripts/check_color_contrast.py` → `PASS`。
- [ ] **Step 5: 保守が冪等** — ステージして `python3 scripts/run_local_validation.py`。期待: 終了コード 0。差分が出るスクリプトがあれば、その CSS 期待を Global Constraints の文字列で満たす(満たせないものだけスクリプトを更新)。

### Task 5: 標準機能(スクロール連動の進捗・View Transitions)

**Files:** Modify `main.js`、`style.css`

**Interfaces:** Produces: `initViewTransitions(): void`(`DOMContentLoaded` の `safeInit` 列に追加)。

- [ ] **Step 1: 先に赤のテストを書く** — `check_design_system.py` に追加: `main.js` の `function initViewTransitions` の本文に `prefers-reduced-motion` と `startViewTransition` の両方がある。`style.css` に `animation-timeline: scroll(` が `@supports` の内側にある。`python3 scripts/check_design_system.py` が追加分で `FAIL`(Review Focus 4 のうち View Transitions 側の担保)。
- [ ] **Step 2: 進捗リングをスクロール連動に** — `grep -ln "initReadingProgress" scripts/*.py` を実行(ヒットしたらそのスクリプトも更新)。CSS で `.progress-ring__circle` に `animation: ring-progress linear both; animation-timeline: scroll(root);` とキーフレーム `ring-progress`(`stroke-dashoffset` を円周 `163.36` から 0)を `@supports (animation-timeline: scroll())` 内に置く。`initReadingProgress()` は `CSS.supports('animation-timeline: scroll()')` が真なら scroll リスナーを付けず、偽なら現行どおり。
- [ ] **Step 3: View Transitions を既存ハンドラに触れず追加** — `initViewTransitions()` は `document` の capture 段階の `click` で `#lang-toggle` `#theme-toggle` `.tab-item[data-tab]` を拾い、`document.startViewTransition` があり、`prefers-reduced-motion` でなく、再入でないときだけ `preventDefault()` と `stopImmediatePropagation()` をして `document.startViewTransition(() => { passthrough = true; target.click(); passthrough = false; })` で再送する。非対応・低減モーションでは何もしない(= 現行動作)。`maintain_tabs.py` `maintain_theme_*` `maintain_language_*` が書き換える既存関数本文は触らない。
- [ ] **Step 4: 緑を確認** — `python3 scripts/check_design_system.py` が `PASS`。`node --check main.js`。ステージして `python3 scripts/run_local_validation.py`(終了コード 0)。ブラウザ(`preview_start portfolio`)で、言語・テーマ・タブ切替が動き、コンソールにエラーが無いこと(`read_console_messages onlyErrors`)。

### Task 6: Stage 1 の確認ゲート

**Files:** (修正があれば `style.css` `index.html`)

- [ ] **Step 1: 表示マトリクスを確認** — `resize_window` で 1440×900 と 390×844、`colorScheme` をライト/ダーク、`localStorage.setItem('lang','en')` と `'ja'`、研究/開発タブ。最低でも 4 通り(PC・ライト・ja・研究 / PC・ダーク・en・開発 / モバイル・ライト・ja・研究 / モバイル・ダーク・en・開発)を見る。期待: 旧デザインの要素(角丸カード、影、ゴールド、ピル、縦棒)が残っていない。名前がヒーローの 1 か所。レールに連絡先リンクが出る。
- [ ] **Step 2: 横スクロールなし** — `javascript_tool` で `document.documentElement.scrollWidth <= window.innerWidth` が全表示で `true`。
- [ ] **Step 3: キーボードとフォーカス** — Tab キーで、スキップリンク → ブランド → タブ → 操作ボタン → フィルタの順にフォーカスが進み、各所で輪郭が見える。
- [ ] **Step 4: JS なしの内容** — `curl -s http://localhost:8000/ | grep -c 'class="header-name"'` が `1`、`id="typing-text"` と `id="stat-papers"` の本文が静的 HTML にある。`python3 scripts/check_progressive_enhancement.py` が `PASS` 相当(終了コード 0)。`#engineer-content` を直接開いて開発タブが出る。
- [ ] **Step 5: ステージ** — 検証コマンドが終了コード 0。コミットはユーザーの許可後(`feat: replace portfolio visual system with ruled index layout`)。

---

## Stage 2 — ヒーローの動く図

> **改訂(2026-11-20、実行中のユーザー指示):** 複数カメラ追跡の図は採用しない。ヒーローの図は「普通のニューラルネットワーク」(全結合 4-6-6-3、細い辺と円、ゆっくりした順伝播の波)に置き換え、「説明用シミュレーション」の注記と「2台以上のカメラで捕捉」のカウンターは置かない。ファイル名・ID は `hero-network.js` / `#hero-network` / `scripts/check_hero_network.py`。以下の Task 7–9 のうち tracking・カメラ・ID 札・`.hero-note`・`#hero-fused` に関する記述は、この改訂で読み替える(実装の記録は台帳を参照)。

### Task 7: 図の純粋な幾何(先にテスト)

**Files:** Create `hero-tracking.js`、`scripts/check_hero_tracking.py`; Modify `scripts/run_local_validation.py`(`CHECKS` と `node --check hero-tracking.js`)

**Interfaces:** Produces(`hero-tracking.js` の末尾で `if (typeof module !== 'undefined') module.exports = {...}`):
- `angleDiff(a: number, b: number): number`(最小の符号付き差、`(-π, π]`)
- `camerasSeeing(point: {x:number,y:number}, cameras: {x:number,y:number,a:number}[], fov: number, range: number): number[]`(視野の扇形に入るカメラの添字)
- `trackPosition(track: {cx,cy,rx,ry,s,ph:number}, t: number): {x:number,y:number}`(0–1 に正規化、決定的)
- `createScene(): {cameras, tracks}`(カメラ 4、トラック 9)
- `shouldAnimate(state: {reduceMotion: boolean, hidden: boolean, intersecting: boolean}): boolean`(三つが `false / false / true` のときだけ `true`)

- [ ] **Step 1: 失敗するテストを書く** — `check_hero_tracking.py` が `node -e` で `require('./hero-tracking.js')` を呼び、次をアサート: `Math.abs(angleDiff(0.1, 2*Math.PI - 0.1)) ≈ 0.2`、`camerasSeeing({x:1,y:0}, [{x:0,y:0,a:0}], 1.2, 2)` が `[0]`、`{x:0,y:1}` `{x:-1,y:0}` `{x:3,y:0}`(範囲外)は `[]`、`createScene()` のカメラ 4 本・トラック 9 本、`t` が 0 から 600 まで 0.5 刻みで全トラックの `trackPosition` が 0–1 に収まる、`shouldAnimate` の 8 通りの真理値表。
- [ ] **Step 2: 実行して失敗** — `python3 scripts/check_hero_tracking.py`。期待: `FAIL`(ファイル無し)。
- [ ] **Step 3: 実装** — 係数はモック C の値(`cams`、`peds` の生成式)を基にし、`rx ≤ 0.36` `ry ≤ 0.30` で範囲内に収める。
- [ ] **Step 4: 通ることを確認と登録** — `PASS`。`node --check hero-tracking.js` も通す。`scripts/run_local_validation.py` の `CHECKS` に `scripts/check_hero_tracking.py` を、`main()` の `node --check main.js` の次に `node --check hero-tracking.js` を追加。以後の検証コマンドの `git add` に `hero-tracking.js` を加える。

### Task 8: ヒーローへの組み込み

**Files:** Modify `index.html`、`style.css`、`hero-tracking.js`、`scripts/check_hero_tracking.py`、`scripts/maintain_asset_versions.py`(`ASSETS` に追加)、`scripts/check_site_integrity.py`(必須ファイル)

**Interfaces:** Consumes: Task 7 の関数、Task 3 の `section.hero#top`。Produces: `<canvas id="hero-tracking" class="hero-canvas" aria-hidden="true">`、`#hero-fused`、`.hero-note`。

- [ ] **Step 1: 静的な契約を先にテストへ** — `check_hero_tracking.py` に追加: `index.html` に上記 canvas(`aria-hidden="true"`、`.hero` の内側)がある。`.hero-note` に `lang="ja"` と `lang="en"` の両方があり、英語側に `Illustrative simulation`、日本語側に `説明用シミュレーション` を含む。`<script src="hero-tracking.js?v=…" defer>` がある。`hero-tracking.js` に `prefers-reduced-motion` `IntersectionObserver` `visibilitychange` `devicePixelRatio` `requestAnimationFrame` がある。`fetch(` `XMLHttpRequest` `WebSocket` `import ` が無い。6144 バイト以下。`style.css` に `.hero-canvas` が `position: fixed` でない、`backdrop-filter` を使わない、`--hero-accent-rgb` の定義がある。期待: `FAIL`。
- [ ] **Step 2: 描画を実装** — 起動は `window.addEventListener('load', …)` の後。`shouldAnimate` が偽のとき rAF を止める。低減モーションでは `t = 4` の静止フレームを 1 回描く。DPR は `Math.min(devicePixelRatio, 2)`、`ResizeObserver` で追従。色は CSS の `--hero-accent-rgb`(例 `238, 75, 36`)を `getComputedStyle` で読んで `rgba()` に組む。2 台以上に映るトラックだけ朱色の枠と `ID 01` 形式の札、他は灰色。`#hero-fused` に枠付きの数を書く。
- [ ] **Step 3: マークアップと CSS** — `.hero` は両テーマで暗い帯(`--hero-bg` `--hero-fg`)、下端にグラデで文字の可読性を確保、モバイル(768px 以下)は高さ 280px。注記は `.hero-note`(可視、日英)。点滅は `@keyframes hero-pulse`(`blink` は使えない)。`maintain_asset_versions.py` の `ASSETS` に `hero-tracking.js` を足す。`<script>` の初期値は `?v=000000000000` とし、`python3 scripts/maintain_asset_versions.py` を流して実ハッシュに書き換わることを確認する。
- [ ] **Step 4: 緑を確認** — `python3 scripts/check_hero_tracking.py` → `PASS`。ステージして `python3 scripts/run_local_validation.py` → 終了コード 0。

### Task 9: Stage 2 の確認ゲート

- [ ] **Step 1: 動作と負荷** — ブラウザで PC・モバイルとも図が動き、`#hero-fused` の数が変化する。`javascript_tool` で `await new Promise(r=>{let n=0,t0=performance.now();(function f(){n++;performance.now()-t0<2000?requestAnimationFrame(f):r(n/2)})()})` が PC で 55 以上、モバイル幅で 40 以上。`read_console_messages onlyErrors` が空。
- [ ] **Step 2: 画面外で止まる** — 図が見えている間に `#hero-fused` の値が時間とともに変わることを確認し、下へスクロールして図を画面外に出し、`#hero-fused` の `textContent` を 2 秒おきに 3 回読んで値が変わらない(止まっている)こと。戻すと再び変わる。
- [ ] **Step 3: 可読性と言語** — ライト/ダークとも、名前・役割・統計が図の上で読める(`--hero-fg`/`--hero-bg` は検査済み)。言語を切り替えると `.hero-note` が日英で切り替わる。
- [ ] **Step 4: ステージ** — 検証コマンドが終了コード 0。コミットは許可後(`feat: add live multi-view tracking hero`)。

---

## Stage 3 — 研究業績の構造化

### Task 10: 構造の検査と変換器の固定(先に赤)

**Files:** Create `scripts/check_publication_structure.py`; Modify `scripts/run_local_validation.py`

**Interfaces:** Produces: 目標マークアップ。`#research-research-achievements` の各 `li[data-year]` は次の形。
```html
<li data-year="2026">
  <span class="badge-year">2026</span>
  <span class="pub-authors"><b>T. Sakai</b>, K. Hotta</span>, <span class="pub-title"><span class="pub-q" aria-hidden="true">“</span>題名<span class="pub-q" aria-hidden="true">,”</span></span>
  <div class="muted pub-venue">会場, Oral, <span class="pub-tag">Outstanding Paper Award</span>, Malmö, Sweden.</div>
  <a …>Paper</a>   <!-- 国際のみ。変更しない -->
</li>
```
国内発表の引用符は `「` `」`(`.pub-q`)。区切りの `, ` や空白は span の外にそのまま残す。

- [ ] **Step 1: 失敗するテストを書く** — `check_publication_structure.py` の `main()` 先頭に合成テスト(`structure_entry` 用、Task 11 の関数を import)。fixture: ①国際(NeuroGuard。`<b>` あり、Paper リンクあり、`Outstanding Paper Award`)②国内(`「…」`、リンクなし、会場のみ)③会場の `div.muted` が無い項目 → `SystemExit` ④既に構造化済みの入力 → 出力が入力と等しい(冪等)。各 fixture で、タグを除去して空白を正規化した可視テキストが変換前後で一致。
- [ ] **Step 2: 実ファイルの検査を書く** — 各 `li` に `.pub-authors` `.pub-title` `.pub-venue` が 1 つずつ、出現順が authors → title → venue、`.pub-q` が題名の前後に対で 2 つ、`.badge-year` の本文が `data-year` と同じ、`<a` の数が変換前と同じ(リンク保持)。
- [ ] **Step 3: 実行して失敗** — `python3 scripts/check_publication_structure.py`。期待: `FAIL`(`maintain_publication_structure` が未作成)。`CHECKS` に登録。

### Task 11: 変換器

**Files:** Create `scripts/maintain_publication_structure.py`; Modify `scripts/run_deterministic_maintenance.py`(`MAINTENANCE_SCRIPTS` の `maintain_research_awards.py` の次に登録)

**Interfaces:** Produces:
- `PUB_TAGS: tuple[str, ...] = ("Outstanding Paper Award",)`
- `structure_entry(li_html: str) -> str`(未知の形は `SystemExit("unrecognized publication entry: …")`)
- `structure_achievements(html: str) -> str`(対象セクションだけ。構造化済みは触らない)
- `main() -> None`(`index.html` を読み書き)

- [ ] **Step 1: 実装** — 対象は `<section class="section-card" id="research-research-achievements">` の `li[data-year]` のみ。`.badge-year` の後ろから、最初の引用符(`“` または `「`)の手前までが著者、引用符から対応する閉じ引用符(`”` または `」`。国際は `,”` と閉じる)までが題名、`<div class="muted">…</div>` が会場、残り(`<a>`)はそのまま。`PUB_TAGS` の語は会場の中で `.pub-tag` に包むだけで、文言を増減しない。
- [ ] **Step 2: テストが通る** — `python3 scripts/check_publication_structure.py` の合成テスト(fixture ①〜④)が通る。
- [ ] **Step 3: 実ファイルに適用** — `python3 scripts/maintain_publication_structure.py`。続けて `python3 scripts/check_publication_structure.py` が `PASS`。
- [ ] **Step 4: 可視テキストの不変を実証** — Task 0 Step 4 のスクリプトを、出力先だけ `achievements-after.txt` に変えて再実行し、`diff achievements-before.txt achievements-after.txt` が**出力なし**。引用符の `.pub-q` もテキストに含まれるため一致する。
- [ ] **Step 5: 冪等と他保守との共存** — ステージして `python3 scripts/run_local_validation.py` が終了コード 0。`maintain_research_awards.py` が受賞リストを壊していない(`git diff -- index.html` が業績 18 件の構造化だけ)。

### Task 12: 論文行の CSS と Stage 3 の確認ゲート

**Files:** Modify `style.css`

- [ ] **Step 1: 行のレイアウト** — `#research-research-achievements` の `.section-card` を `container-type: inline-size` にする。コンテナ幅 720px 以上は `li` を `display: grid`(年 60px / 本文 1fr / 会場 210px)、未満は 2 列(年 / 本文、会場は本文の下)。視覚の順序は題名 → 著者 → 会場(グリッド配置で並べ替えるだけで DOM は変えない。フォーカス対象の Paper リンクは最後のまま)。`.pub-q` は `display: none`。`.pub-tag` は `--accent-mark` の点 + 中太字(文字色は `--text-main`)。題名は `text-wrap: balance`、長い語は `overflow-wrap: anywhere`。`li` の `display` に `!important` を付けない。
- [ ] **Step 2: 年フィルタ(Review Focus 2)** — ブラウザで年チップ `2025` をクリック。期待: `#search-count` の件数と、表示中の `li` の数(`[...document.querySelectorAll('#research-research-achievements li')].filter(l=>l.style.display!=='none').length`)が一致。存在しない年に絞って、セクションごと消え、`すべて` で全件戻る。
- [ ] **Step 3: 狭い幅(Review Focus 3)** — 390×844 で `document.documentElement.scrollWidth <= window.innerWidth` が `true`。ATLASFusion の行が折り返す。
- [ ] **Step 4: 国内発表(Review Focus 1)** — 日本語の 11 件で、著者・題名・会場が 3 段に出る。「」は表示されない。Paper リンクが無い行が崩れない。
- [ ] **Step 5: ステージ** — 検証コマンドが終了コード 0。コミットは許可後(`feat: structure research achievements into typeset rows`)。

---

## 仕上げ

### Task 13: ドキュメントと最終確認

**Files:** Modify `README.md`

- [ ] **Step 1: README を更新** — `## Maintenance` に、デザイントークンは `style.css` の `@layer tokens`、図は `hero-tracking.js`(装飾。`aria-hidden`、説明用シミュレーション)、業績の構造化は `scripts/maintain_publication_structure.py` が担うこと、新しい `check_*.py` 3 本の役割を 1 行ずつ。`## Local validation` の bash ブロックは変えない(`check_validation_docs.py` が見る)。
- [ ] **Step 2: 最終検証** — 検証コマンドが終了コード 0。Task 6 の表示マトリクスを再確認(特に Stage 3 後の研究タブ)。`git status --short` に、自分が作った以外の変更(ユーザーの `fix_*.py` など)が混ざっていないこと。
- [ ] **Step 3: 後片付け** — モック用サーバーを止める: `bash /Users/sakaitaigoware/.claude/plugins/cache/claude-plugins-official/superpowers/7.0.2/skills/brainstorming/scripts/stop-server.sh /private/tmp/claude-501/-Users-sakaitaigoware-sakai1250-github-io/d737f2a1-0f37-44d1-8456-ce1ba4cecbac/scratchpad/brainstorm-project/.superpowers/brainstorm/42308-1795102100`。`.claude/launch.json`(プレビュー用、未追跡)は残し、ユーザーに伝える。ユーザーの未追跡ファイル(`fix_*.py` など)には触れない。
- [ ] **Step 4: 報告とコミット提案** — 3 コミット(Stage 1 / 2 / 3)を提案し、許可を待つ。PR は依頼があったときだけ。
