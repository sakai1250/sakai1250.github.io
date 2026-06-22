# Ivory Editorial Portfolio Redesign

## Goal

既存の情報、リンク、表示ロジック、主要操作を維持したまま、現在のサイバー・ゲーミング調UIを、上品で信頼感のある研究者ポートフォリオへ変更する。

採用する視覚方向は「A. Ivory Editorial」とする。

## Scope

### In scope

- `style.css`を中心としたデザイントークン、配色、書体、余白、境界線、角丸、影、ホバー表現の再設計
- 必要最小限の`index.html`調整
- `effects.js`にある演出の高級感に合わせた弱化
- カードのドラッグ並べ替え機能と関連表示の削除
- ライト・ダーク両テーマの再設計
- PCとモバイルのレイアウト調整
- 日本語と英語が混在する画面の可読性調整

### Out of scope

- 新しいコンテンツ、リンク、タブ、フィルタ、データ項目の追加
- 既存データ構造の変更
- 数値カードの算出ロジック変更
- EN切替、テーマ切替、研究・開発切替、年度フィルタ、モーダル、コピー、連絡フォームの機能変更
- ページ構成の全面的な作り直し

## Theme behavior

- 初回表示は現在どおりOSの`prefers-color-scheme`に連動する。
- ユーザーがテーマを切り替えた場合は、現在どおり`localStorage`の保存値を優先する。
- ライトテーマはIvory Editorialを標準とする。
- ダークテーマは完全な黒を避け、deep navyとcharcoalを使う。
- `meta[name="theme-color"]`も各テーマの背景色に合わせる。

## Design tokens

### Light theme

- Background: `#F7F3EA`
- Background secondary: `#FAF8F3`
- Surface: `#FFFFFF`
- Surface subtle: `#FBFAF7`
- Primary: `#071A2F`
- Primary soft: `#102A43`
- Text: `#111827`
- Text secondary: `#374151`
- Muted text: `#6B7280`
- Accent: `#B88A44`
- Accent soft: `#C6A15B`
- Border: `rgba(17, 24, 39, 0.10)`
- Shadow: `0 10px 30px rgba(15, 23, 42, 0.08)`

### Dark theme

- Background: `#09131F`
- Background secondary: `#0D1B2A`
- Surface: `#102235`
- Surface subtle: `#14283D`
- Primary text: `#F4F0E7`
- Secondary text: `#D6D0C3`
- Muted text: `#9CA7B5`
- Accent: `#C6A15B`
- Border: `rgba(226, 213, 184, 0.14)`
- Shadow: `0 14px 34px rgba(0, 0, 0, 0.22)`

グラデーション、ネオンシアン、発光用トークンは廃止する。背景、ボタン、文字、カードに強い色ぼかしを使わない。

## Typography

- `Taigo Sakai`、英字の主要見出し、数値には上品なセリフ体を使用する。
- 日本語と本文UIには`Noto Sans JP`を中心としたゴシック体を使用する。
- Orbitron、Chakra Petchなど、サイバー感の強い書体は外す。
- 名前は大きく見せるが、グラデーション文字、発光、過剰な太字は使わない。
- 本文は行間を広めにし、長い研究業績も読みやすくする。

## Layout

### Desktop

- 現在の2カラム構成を維持する。
- 左カラムは約296〜310px、右カラムは残りの幅とする。
- カラム間隔とセクション間隔を広げる。
- ヘッダーの情報量は維持し、視覚的な密度だけを下げる。
- 左プロフィールカードのsticky動作は維持する。

### Mobile

- プロフィールカードとメインコンテンツを縦積みにする。
- ヘッダー、数値カード、操作ボタン、年度チップは折り返し可能にする。
- アバター、名前、ボタンが画面上部を過度に占有しないサイズに調整する。
- 横スクロールが必要なセクションタブは、表示を保ちながら高さを抑える。
- 現在どおりモバイルではsticky追従を無効にする。

## Components

### Header

- アイボリーまたはdeep navyの半透明面を使用する。
- blurは軽く残してもよいが、彩度強調と発光は使わない。
- アバターは白またはゴールド系の細い境界線と自然な影にする。
- 名前はセリフ体の単色表示にする。
- 所属とタイプ入力テキストは控えめなmuted colorにする。

### Stats

- 3つの数値は独立した小型カードとして見せる。
- 数値はセリフ体、ラベルは小さなサンセリフ体とする。
- 数値のグラデーション文字は使わない。
- 区切り線はインラインstyleではなく、CSS側で統一する。

### Header buttons

- inactiveは薄い境界線付きの落ち着いたボタンにする。
- primaryはdeep navy背景とし、必要に応じて細いゴールド境界線を使う。
- hoverは1〜2pxの浮上、境界色、背景色の軽い変化だけにする。
- グロー、強いbrightness、急なscaleは使わない。

### Research / Engineering tabs and year filters

- activeタブはdeep navy背景またはゴールドの下線で示す。
- inactiveは薄い境界線付きのニュートラルな表示にする。
- 年度は小さく控えめなチップにする。
- 現在の`data-tab`、`data-year`、active classによるロジックを変更しない。

### Profile card

- テーマに関係なくdeep navyを基調とする。
- 上端または左端に細いシャンパンゴールド線を置く。
- 名前、所属、リンクの情報量は変更しない。
- リンク間隔と内側余白を広げる。
- アイコン色はivoryまたはmuted goldに統一する。
- コピー操作の見た目を同じデザイン言語へ合わせる。

### Section navigation

- sticky動作と動的生成を維持する。
- シンプルな横並びナビゲーションにする。
- 選択中はゴールドの下線または淡い面で示す。
- 発光する枠とシャドウは使わない。

### Section cards

- 白またはsurface色、薄い境界線、自然な影を使用する。
- セクションごとのネオン色分けを廃止する。
- 見出しには細いゴールド線を使う。
- hover時の回転を廃止し、最大2px程度の浮上にする。
- セクション間の余白を広げる。

### Education and achievement lists

- 既存の`ul.repo-list > li`構造を維持する。
- 視覚表現は控えめなタイムライン風にする。
- 左側の細い線と小さなゴールドドットで時系列を示す。
- 年度バッジは単色の落ち着いたチップにする。
- 年度ごとの派手な色分けと発光を廃止する。
- 既存の右側矢印リンクは維持し、deep navyまたはgoldの小型ボタンへ変更する。

### Application cards

- 現在の画像、説明、リンク、モーダル起動を維持する。
- 背景はsurface、境界はsubtle borderとする。
- hoverは浅い浮上と影の変化だけにする。
- 3Dチルトはごく浅くし、回転角と移動量を大幅に減らす。

### Modal and floating navigation

- モーダルはdeep navyまたはsurface背景にし、黒い強いオーバーレイを弱める。
- FABとTOCは円形を維持してよいが、ネオン色と強い影を廃止する。
- focus-visibleを明確にし、キーボード操作を保つ。

## Motion and effects

### Remove

- カードのドラッグ並べ替え
- ドラッグハンドル
- ドラッグ用placeholder、drop target、tooltip
- カードを掴めることを示すgrab cursor

### Retain with refinement

- 背景パーティクル:
  - 粒子数と接続線を減らす。
  - opacityを下げる。
  - muted goldまたはsoft navyを使用する。
- 3D effect:
  - application cardだけに限定する。
  - 回転角を小さくし、上方向の移動を2px程度に抑える。
- タイプ入力:
  - 現在の文言とロジックを維持する。
  - uppercase、強いletter-spacing、発光を外す。
  - カーソルは細いゴールド線にする。
- 物体検出風ホバー:
  - 機能的な遊びとして残す。
  - magenta / greenの強い矩形を、細いゴールドまたはmuted blueの線と小さなラベルへ変更する。
  - 常時目立たず、hover時だけ静かに表示する。
- reveal:
  - 透明度と小さなY移動だけにする。
  - `prefers-reduced-motion`では停止する。

## Functional preservation

以下はDOM属性、ID、イベント対象を維持する。

- `#lang-toggle`
- `#theme-toggle`
- `.tab-item[data-tab]`
- `.tab-content`
- `.chip[data-year]`
- `.chip[data-filter]`
- `#section-tab-nav`
- `.section-card`
- `.repo-list li[data-year]`
- `.app-card[data-tags]`
- `.copy-btn`
- `#app-modal`
- 連絡フォーム関連ID

スタイル変更のためにこれらの名称や階層を不要に変更しない。

## Accessibility

- 本文と背景はWCAG AA相当のコントラストを目標にする。
- muted textも読み取れる濃度を確保する。
- hoverだけに状態を依存させず、active、focus-visibleを明確にする。
- motionは`prefers-reduced-motion`に対応する。
- ボタンとリンクのクリック領域をモバイルで最低約40px確保する。
- 日本語本文のfont-sizeを小さくしすぎない。

## Verification

実装後に以下を確認する。

1. ライトテーマがIvory Editorialとして表示される。
2. ダークテーマがdeep navy / charcoalとして表示される。
3. 保存テーマがない場合、OS設定に連動する。
4. EN / JA切替が機能する。
5. 研究 / 開発タブが切り替わる。
6. 年度フィルタと開発カテゴリフィルタが既存データに一致する。
7. セクションナビゲーションが生成され、クリックとscroll active更新が機能する。
8. コピー、外部リンク、アプリモーダル、連絡フォームの既存操作が壊れていない。
9. カードがドラッグできず、ドラッグハンドルが表示されない。
10. desktop、tablet、mobileで横方向のoverflowがない。
11. 日本語と英語の長い項目がカードからはみ出さない。
12. コンソールに初期化エラーが出ない。

## Expected file changes

- `style.css`: デザイントークンと全コンポーネントの視覚再設計
- `index.html`: フォント読込、インラインstyle整理、cache version、必要なアクセシビリティ属性
- `effects.js`: ドラッグ並べ替え削除、残す演出の弱化
- `main.js`: theme color更新など、見た目に必要な最小変更のみ

内容データ、リンク先、`assets/data.json`、画像、アイコンは原則変更しない。
