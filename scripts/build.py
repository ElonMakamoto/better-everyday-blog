#!/usr/bin/env python3
"""Build the Better Everyday static site from editorially reviewed JSON."""
import datetime as dt
import html
import json
import pathlib
import shutil
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
BASE = "https://better-everyday-blog.pages.dev"
BRAND = "Better Everyday"
NOW = dt.datetime.now(dt.timezone.utc)
CATS = {"Healthy Living": "healthy-living", "Money & Savings": "money", "Home & Everyday": "home", "Simple Technology": "technology"}
POSTS = json.loads((ROOT / "content/posts.json").read_text(encoding="utf-8"))
def esc(text):
    return html.escape(str(text), quote=True)
def date_of(post):
    return dt.datetime.fromisoformat(post["publish_at"].replace("Z", "+00:00"))
POSTS = sorted([p for p in POSTS if date_of(p) <= NOW], key=date_of, reverse=True)
BY_SLUG = {p["slug"]: p for p in POSTS}
assert len(POSTS) == len(BY_SLUG), "Duplicate slugs detected"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

def photo(img, eager=False, card=False):
    if not img:
        return ""
    css = "card-image" if card else "editorial-image"
    loading = "eager" if eager else "lazy"
    priority = ' fetchpriority="high"' if eager else ""
    # Photos are licensed from Pexels. The photographer and original photo are linked in the caption.
    tag = ('<img class="'+css+'" src="'+esc(img["src"])+'" alt="'+esc(img["alt"])+
           '" width="1200" height="800" loading="'+loading+'" decoding="async"'+priority+'>')
    if card:
        return tag
    link = '<a href="'+esc(img["photo_url"])+'" target="_blank" rel="noopener noreferrer">'+esc(img["credit"])+' / Pexels</a>'
    return '<figure>'+tag+'<figcaption>'+esc(img["caption"])+' · Photo: '+link+'</figcaption></figure>'

def schemas(data):
    return '<script type="application/ld+json">'+json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")+'</script>'

def page(title, description, body, url="/", hero_image=None, schema=None, published=None, modified=None):
    nav_items = [("Home","/")] + [(name, "/category/"+slug+"/") for name,slug in CATS.items()] + [("About","/about/")]
    nav = "".join('<a href="'+href+'">'+esc(label)+'</a>' for label,href in nav_items)
    link = BASE + url
    description = description[:165]
    og_image = ('<meta property="og:image" content="'+esc(hero_image["src"])+'"><meta name="twitter:card" content="summary_large_image">' if hero_image else '<meta name="twitter:card" content="summary">')
    dates = ('<meta property="article:published_time" content="'+esc(published)+'">' if published else "") + ('<meta property="article:modified_time" content="'+esc(modified)+'">' if modified else "")
    structured = schemas(schema) if schema else ""
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="theme-color" content="#faf9f4">'
        '<title>'+esc(title)+' | '+BRAND+'</title>'
        '<meta name="description" content="'+esc(description)+'">'
        '<link rel="canonical" href="'+esc(link)+'">'
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
        '<meta property="og:site_name" content="'+BRAND+'">'
        '<meta property="og:type" content="'+('article' if published else 'website')+'">'
        '<meta property="og:url" content="'+esc(link)+'">'
        '<meta property="og:title" content="'+esc(title)+'">'
        '<meta property="og:description" content="'+esc(description)+'">'
        +og_image+dates+structured+
        '<link rel="stylesheet" href="/style.css"></head><body>'
        '<a class="skip-link" href="#main">Skip to content</a>'
        '<header><div class="wrap head"><a class="logo" href="/" aria-label="Better Everyday home">better<span>everyday.</span></a>'
        '<nav aria-label="Main navigation">'+nav+'</nav></div></header>'
        '<main id="main" class="wrap">'+body+'</main>'
        '<footer><div class="wrap foot"><div><strong>Better Everyday</strong><p>Useful answers. Less everyday friction.</p></div>'
        '<div class="footer-links"><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy/">Privacy</a><a href="/editorial-policy/">Editorial policy</a></div></div>'
        '<small class="wrap">© '+str(NOW.year)+' Better Everyday. General information, not personal professional advice.</small>'
        '</footer></body></html>')

def write(url, markup):
    path = OUT / "index.html" if url == "/" else OUT / url.strip("/") / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markup, encoding="utf-8")

def card(post):
    url="/articles/"+post["slug"]+"/"
    return ('<article class="card"><a class="card-photo-link" href="'+url+'" aria-label="'+esc(post["title"])+'">'+photo(post["hero"], card=True)+'</a>'
            '<div class="card-inner"><span class="tag">'+esc(post["category"])+'</span>'
            '<h3><a href="'+url+'">'+esc(post["title"])+'</a></h3>'
            '<p>'+esc(post["excerpt"])+'</p><a class="read" href="'+url+'">Read the guide <span aria-hidden="true">→</span></a></div></article>')

def list_items(items, tag="ul"):
    return "<"+tag+">"+"".join("<li>"+esc(item)+"</li>" for item in items)+"</"+tag+">"

def article(post):
    article_url="/articles/"+post["slug"]+"/"
    cat_slug=CATS[post["category"]]
    parts=['<article class="article"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/category/'+cat_slug+'/">'+esc(post["category"])+'</a></nav>',
           '<div class="article-label">'+esc(post["category"])+' <span>·</span> '+esc(post["read_time"])+'</div>',
           '<h1>'+esc(post["title"])+'</h1>',
           '<div class="byline">By '+BRAND+' · Published <time datetime="'+post["publish_at"][:10]+'">'+esc(post["publish_at"][:10])+'</time> · Updated '+esc(post["date_modified"])+'</div>',
           '<p class="lede">'+esc(post["introduction"])+'</p>', photo(post["hero"], eager=True),
           '<div class="toc"><strong>In this guide</strong><ol>'+''.join('<li><a href="#'+esc(s["id"])+'">'+esc(s["heading"])+'</a></li>' for s in post["sections"])+'</ol></div>']
    for sec in post["sections"]:
        parts.append('<section class="article-section" id="'+esc(sec["id"])+'"><h2>'+esc(sec["heading"])+'</h2>')
        if sec.get("lead"):
            parts.append('<p>'+esc(sec["lead"])+'</p>')
        if sec.get("steps"):
            parts.append(list_items(sec["steps"], "ol"))
        for para in sec.get("paragraphs", []):
            parts.append("<p>"+esc(para)+"</p>")
        if sec.get("bullets"):
            parts.append(list_items(sec["bullets"]))
        if sec.get("image"):
            parts.append(photo(sec["image"]))
        parts.append("</section>")
    if post.get("faq"):
        parts.append('<section class="faq" id="frequently-asked-questions"><h2>Frequently asked questions</h2>')
        for qa in post["faq"]:
            parts.append('<div class="faq-entry"><h3>'+esc(qa["q"])+'</h3><p>'+esc(qa["a"])+'</p></div>')
        parts.append("</section>")
    if post.get("sources"):
        parts.append('<section class="further" id="sources"><h2>Sources and further reading</h2><ul>')
        for source in post["sources"]:
            parts.append('<li><a href="'+esc(source["url"])+'" rel="noopener noreferrer" target="_blank">'+esc(source["name"])+'</a></li>')
        parts.append('</ul></section>')
    parts.append('<aside class="note">This guide is for general information. Settings vary by device, and savings depend on circumstances. For health, safety, legal or financial questions, consult qualified professionals and follow the manufacturer’s instructions.</aside>')
    related=[BY_SLUG[slug] for slug in post.get("related",[]) if slug in BY_SLUG and slug!=post["slug"]]
    if related:
        parts.append('<section class="related"><h2>Keep reading</h2><div class="cards">'+''.join(map(card,related))+'</div></section>')
    parts.append('</article>')
    structured=[
        {"@context":"https://schema.org","@type":"BlogPosting","headline":post["title"],
         "description":post["meta_description"],"image":[post["hero"]["src"]],
         "datePublished":post["publish_at"],"dateModified":post["date_modified"],
         "mainEntityOfPage":{"@type":"WebPage","@id":BASE+article_url},
         "author":{"@type":"Organization","name":BRAND,"url":BASE+"/about/"},
         "publisher":{"@type":"Organization","name":BRAND,"url":BASE}},
        {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},
            {"@type":"ListItem","position":2,"name":post["category"],"item":BASE+"/category/"+cat_slug+"/"},
            {"@type":"ListItem","position":3,"name":post["title"],"item":BASE+article_url}]}
    ]
    # On ordinary blogs Google generally does not show FAQ rich results.
    if post.get("faq"):
        structured.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":qa["q"],"acceptedAnswer":{"@type":"Answer","text":qa["a"]}}
            for qa in post["faq"]]})
    return page(post.get("seo_title",post["title"]),post["meta_description"],"".join(parts),
                article_url,hero_image=post["hero"],schema=structured,
                published=post["publish_at"],modified=post["date_modified"])

site_schema={"@context":"https://schema.org","@type":"WebSite","name":BRAND,"url":BASE+"/","description":"Plain-English practical guides to money, home and everyday technology."}
intro=('<section class="hero"><span class="eyebrow">SMARTER LIVING, MADE SIMPLE</span>'
       '<h1>Small changes.<br><em>Better every day.</em></h1>'
       '<p>Real-life guides to saving money, caring for your home, and making technology easier — written in plain English.</p>'
       '<a class="cta" href="#latest">Browse the guides <span aria-hidden="true">→</span></a></section>')
cats='<section class="categories" aria-label="Browse topics">'+''.join('<a href="/category/'+slug+'/">'+esc(name)+' <span>↗</span></a>' for name,slug in CATS.items())+'</section>'
latest='<section id="latest" class="listing"><div class="section-head"><span class="eyebrow">OUR GUIDES</span><h2>Practical reading, right when you need it</h2></div><div class="cards">'+''.join(map(card, POSTS))+'</div></section>'
write("/",page("Practical Guides for Everyday Living","Clear, useful guides to saving money, solving household problems, and using your smartphone with confidence.",intro+cats+latest,"/",schema=site_schema))
for name,slug in CATS.items():
    subset=[p for p in POSTS if p["category"]==name]
    body='<section class="page"><span class="eyebrow">EXPLORE</span><h1>'+esc(name)+'</h1><p class="lede">Useful, easy-to-follow guides about '+esc(name.lower())+'.</p>'
    body+='<div class="cards">'+''.join(map(card,subset))+'</div>'
    if not subset:body+='<p>New guides are being prepared. Browse other topics on our home page.</p>'
    body+='</section>'
    write("/category/"+slug+"/",page(name,"Helpful, plain-English guides about "+name.lower()+".",body,"/category/"+slug+"/"))
for post in POSTS:
    write("/articles/"+post["slug"]+"/",article(post))

# Editorial and legal pages: accurately describe present capabilities. Avoid made-up contact data.
about=[
"Better Everyday is an independent English-language publication that explains everyday tasks in clear, practical steps. Our current topics include simple technology, household care and money-saving habits.",
"We aim to answer one useful question at a time. We favor specific instructions and official or reliable source material over misleading headlines or unsupported promises. We update articles when instructions or facts change.",
"The site is published by Better Everyday. It is not affiliated with Apple, Google, the U.S. Department of Energy, Pexels or any other brand mentioned in our articles.",
"Some photographs are licensed from Pexels and credited to their creators. Photographs illustrate a topic; they are not screenshots of settings unless explicitly described as such."]
contact=[
"Corrections, feedback and content-related questions are welcome. At present we handle public editorial messages through the GitHub Issues page for this project. A GitHub account is required and the message will be public.",
"Do not submit passwords, phone numbers, payment details, health information or other sensitive personal information to a public issue. A dedicated private contact channel will be added when available.",
'<a href="https://github.com/ElonMakamoto/better-everyday-blog/issues/new" target="_blank" rel="noopener noreferrer">Open the editorial feedback page ↗</a>']
privacy=[
"Last updated: October 12, 2026. This notice explains how Better Everyday currently operates. It is a general information notice and will be updated as site features change.",
"Information you provide: We do not currently offer accounts, payments, comments, newsletter signup or a contact form on this website. If you choose to open a public GitHub issue, GitHub handles that interaction under its own privacy practices.",
"Hosting: Cloudflare Pages serves this site. Cloudflare may process IP addresses, request information, technical identifiers and security-related data as needed to deliver and protect the site. See Cloudflare's privacy policy for details.",
"Third-party images and fonts: Pages may load photographs from the Pexels image CDN and fonts from Google Fonts. Loading those files may cause a request to the relevant service, which can receive technical connection information such as an IP address.",
"Advertising and analytics: We have not yet enabled Google AdSense or a dedicated site analytics tracker in the site code. If these services are enabled, we will update this policy and provide any required notices or consent controls beforehand. Google and its advertising partners may then use cookies or similar identifiers to serve and measure advertising, including interest-based advertising where permitted.",
"Choices: You may manage browser cookies through browser settings. When Google advertising becomes active, Google's ad preferences are available at https://myadcenter.google.com/ and third-party advertising opt-outs may be available through https://www.aboutads.info/. These links do not mean ads are currently running.",
"Updates: We may update this notice when site functionality or applicable requirements change. For questions or correction requests, see our Contact page."]
editorial=[
"Our mission: Publish useful guides that answer specific questions in language everyday readers can act on.",
"Research: For changing product settings or public guidance, we prioritize official support pages and other primary sources. Articles link to sources where useful. We distinguish confirmed instructions from general suggestions.",
"Review and corrections: Drafts may be assisted by AI or software, but the goal is to check instructions and claims before publication. If you notice an error, please report it on our Contact page. Material corrections may lead to a revised article and update date.",
"Images: We use appropriately licensed photographs. Image captions describe what is pictured; stock imagery is illustrative, not proof of a claim.",
"Independence: We do not accept payments to make misleading claims. If affiliate links or sponsorships are added, they will be clearly disclosed. This site is not a substitute for medical, legal or financial advice.",
"Publishing schedule: Our system supports scheduled posts. Publishing frequency is not a substitute for quality; additional articles will appear only when editorial content is ready."]
policy_pages={
 "about":("About Better Everyday","Learn what Better Everyday covers and how our practical guides are prepared.",about),
 "contact":("Contact Better Everyday","Send editorial feedback or report an error through our public GitHub feedback page.",contact),
 "privacy":("Privacy Policy","Learn about hosting, third-party images, fonts, data processing and our planned advertising disclosures.",privacy),
 "editorial-policy":("Editorial Policy","Our principles for sourcing, reviewing, crediting photographs and correcting practical guides.",editorial)
}
for slug,(heading,desc,paragraphs) in policy_pages.items():
    # A single trusted internal link in the Contact page is intentional HTML; all other passages escaped.
    prose="".join('<p>'+ (p if p.startswith('<a href=') else esc(p)) +'</p>' for p in paragraphs)
    write("/"+slug+"/",page(heading,desc,'<section class="page prose"><span class="eyebrow">ABOUT THE SITE</span><h1>'+esc(heading)+'</h1>'+prose+'</section>',"/"+slug+"/"))

all_urls=["/"]+["/category/"+slug+"/" for slug in CATS.values()]+["/articles/"+p["slug"]+"/" for p in POSTS]+["/"+slug+"/" for slug in policy_pages]
ns="http://www.sitemaps.org/schemas/sitemap/0.9"
ET.register_namespace("",ns)
urlset=ET.Element("{"+ns+"}urlset")
for url in all_urls:
    entry=ET.SubElement(urlset,"{"+ns+"}url")
    ET.SubElement(entry,"{"+ns+"}loc").text=BASE+url
    if url.startswith("/articles/"):
        p=BY_SLUG[url.split("/")[2]]
        ET.SubElement(entry,"{"+ns+"}lastmod").text=p["date_modified"]
ET.ElementTree(urlset).write(OUT/"sitemap.xml",encoding="utf-8",xml_declaration=True)
(OUT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: "+BASE+"/sitemap.xml\n",encoding="utf-8")
for name in ["style.css","favicon.svg"]:
    shutil.copyfile(ROOT/"static"/name,OUT/name)
print("Published",len(POSTS),"articles,",len(all_urls),"URLs,",sum(1+sum(bool(s.get("image")) for s in p["sections"]) for p in POSTS),"photographs")
