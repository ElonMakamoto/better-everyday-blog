# Better Everyday
An independent English-language practical living blog focused on useful, well-sourced guides for adults.

## Architecture
- GitHub contains the source articles and the static site builder.
- Cloudflare Pages deploys `dist/` using `python3 scripts/build.py`.
- New articles are added to `content/posts.json`. Include a future ISO UTC `publish_at` to queue an article.
- A scheduled GitHub Actions workflow runs every four hours and regenerates `dist/` only when new articles are due. It does **not** generate AI content automatically or bypass editorial review.
- For Google indexing: submit `https://better-everyday-blog.pages.dev/sitemap.xml` in Google Search Console once the deployment is live.
- Before monetization: review every claim and source, add editorial contact details and a real privacy policy covering the tools actually used, then apply to AdSense. No fixed number of posts or posting frequency guarantees approval.

## Writing and review
Edit `content/posts.json`. Each item needs a unique `slug`, `title`, `category`, `excerpt`, `publish_at`, `introduction`, `sections`, and optionally `sources`. Use original, human-reviewed content with accurate source links. Keep titles factual instead of misleading or sensational.

## Deploy
Cloudflare Pages Git integration: connect `ElonMakamoto/better-everyday-blog`, branch `main`, build command `python3 scripts/build.py`, output directory `dist`. Python standard library only; no npm dependencies.

## Safety
Never commit API keys, credentials, personal data, or AdSense secrets. Update the public contact address and privacy policy before applying for AdSense.
