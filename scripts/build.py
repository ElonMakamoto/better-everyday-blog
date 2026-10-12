import json, pathlib, html, datetime, re
from urllib.parse import quote
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"dist"
OUT.mkdir(exist_ok=True)
BASE="https://better-everyday-blog.pages.dev"
today=datetime.datetime.now(datetime.timezone.utc)
posts=json.loads((ROOT/"content/posts.json").read_text(encoding="utf-8"))
posts=sorted((p for p in posts if datetime.datetime.fromisoformat(p["publish_at"].replace("Z","+00:00"))<=today),key=lambda x:x["publish_at"],reverse=True)
esc=html.escape
def template(title,description,body,url="/"):
    nav='<a href="/">Home</a><a href="/category/healthy-living/">Healthy Living</a><a href="/category/money/">Money</a><a href="/category/home/">Home</a><a href="/category/technology/">Technology</a><a href="/about/">About</a>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Better Everyday</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{BASE}{url}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><link rel="stylesheet" href="/style.css"></head><body><header><div class="wrap head"><a class="logo" href="/">better<span>everyday.</span></a><nav>{nav}</nav></div></header><main class="wrap">{body}</main><footer><div class="wrap foot"><div><strong>Better Everyday</strong><p>Practical answers for everyday life.</p></div><div><a href="/about/">About</a> · <a href="/contact/">Contact</a> · <a href="/privacy/">Privacy</a> · <a href="/editorial-policy/">Editorial policy</a></div></div><small class="wrap">© {today.year} Better Everyday. Educational information, not individualized advice.</small></footer></body></html>'''
def write(url,doc):
    path=OUT/url.strip("/")/"index.html" if url!="/" else OUT/"index.html"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(doc,encoding="utf-8")
def card(p):
    return f'<article class="card"><span class="tag">{esc(p["category"])}</span><h2><a href="/articles/{p["slug"]}/">{esc(p["title"])}</a></h2><p>{esc(p["excerpt"])}</p><a class="read" href="/articles/{p["slug"]}/">Read guide →</a></article>'
hero='''<section class="hero"><span class="eyebrow">SMARTER LIVING, MADE SIMPLE</span><h1>Small changes.<br><em>Better every day.</em></h1><p>Clear, practical guides to help you save time, spend wisely, and make daily life easier.</p><a class="cta" href="#latest">Explore our guides →</a></section>'''
cats={"Healthy Living":"healthy-living","Money & Savings":"money","Home & Everyday":"home","Simple Technology":"technology"}
features='<section class="categories">'+''.join(f'<a href="/category/{v}/">{esc(k)} <span>↗</span></a>' for k,v in cats.items())+'</section>'
write("/",template("Practical Living Guides","Helpful everyday answers, home tips, money saving and simple technology.",hero+features+'<section id="latest"><div class="section-head"><span class="eyebrow">THE LATEST</span><h2>Useful reads for real life</h2></div><div class="cards">'+''.join(map(card,posts))+'</div></section>'))
for name,slug in cats.items():
    subset=[p for p in posts if p["category"]==name]
    write(f"/category/{slug}/",template(name,f"Practical guides about {name.lower()}.",f'<section class="page"><span class="eyebrow">TOPIC</span><h1>{esc(name)}</h1><div class="cards">'+''.join(map(card,subset))+'</div></section>',f"/category/{slug}/"))
for p in posts:
    content=f'<article class="article"><a class="back" href="/">← All articles</a><p class="eyebrow">{esc(p["category"])} · {esc(p["publish_at"][:10])}</p><h1>{esc(p["title"])}</h1><p class="lede">{esc(p["introduction"])}</p>'
    for sec in p["sections"]:
        content+=f'<h2>{esc(sec["heading"])}</h2>'+''.join(f'<p>{esc(par)}</p>' for par in sec["paragraphs"])
    if p.get("sources"):
        content+='<h2>Further reading</h2><ul>'+''.join(f'<li><a href="{esc(s["url"],quote=True)}" rel="noopener noreferrer">{esc(s["name"])}</a></li>' for s in p["sources"])+'</ul>'
    content+='<aside class="note">This article is general educational information. For personal medical, financial, or legal decisions, consult a qualified professional.</aside></article>'
    write(f'/articles/{p["slug"]}/',template(p["title"],p["excerpt"],content,f'/articles/{p["slug"]}/'))
pages={
"about":("About Us","Better Everyday shares plain-English guides about everyday living, home care, saving money and accessible technology. We aim for useful, accurate explanations rather than hype. Every article should be checked and updated when necessary."),
"contact":("Contact","For corrections, questions or partnerships, please use the contact details provided by the publisher. We are preparing a dedicated contact address. Until it is published, this site is not accepting direct enquiries."),
"privacy":("Privacy Policy","This website publishes general information. Hosting and delivery providers may process technical request data needed to provide the service. We do not intentionally collect information through a contact form. This policy must be updated before activating analytics, advertising or additional tracking technologies, including AdSense. Readers should check back for changes."),
"editorial-policy":("Editorial Policy","Our aim is practical, verifiable information. We avoid exaggerated claims, review facts before publication, link to primary sources where applicable and correct errors. Articles may be drafted with software assistance, but should be checked for factual accuracy and usefulness before publication. Sponsored relationships will be disclosed where applicable.")
}
for slug,(title,txt) in pages.items():
    write(f"/{slug}/",template(title,txt,f'<section class="page prose"><span class="eyebrow">BETTER EVERYDAY</span><h1>{esc(title)}</h1><p>{esc(txt)}</p></section>',f"/{slug}/"))
urls=["/"]+[f"/category/{v}/" for v in cats.values()]+[f"/articles/{p['slug']}/" for p in posts]+[f"/{x}/" for x in pages]
(OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f"<url><loc>{BASE}{esc(u)}</loc></url>" for u in urls)+'</urlset>',encoding="utf-8")
(OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n",encoding="utf-8")
(OUT/"style.css").write_text((ROOT/"static/style.css").read_text(encoding="utf-8"),encoding="utf-8")
print(f"Generated {len(posts)} public articles and {len(urls)} indexed URLs")
