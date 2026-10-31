#!/usr/bin/env python3
"""Builds the static site for luxecornerboutique.com into ./dist."""
import json, os, shutil, html
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
SITE = "https://www.luxecornerboutique.com"
IG_HANDLE = "waitlistforlife"
IG_URL = f"https://www.instagram.com/{IG_HANDLE}/"
IG_DM = f"https://ig.me/m/{IG_HANDLE}"
BRANDS_DISCLAIMER = ("The Luxe Corner is an independent dealer and is not affiliated with, authorized by or endorsed by "
                     "Patek Philippe, Audemars Piguet, Rolex, Vacheron Constantin, Romain Gauthier, Kollokium or any other brand shown. "
                     "Brand names and reference numbers are used only to describe the pieces offered. All trademarks belong to their owners.")

PIECES = json.load(open(os.path.join(ROOT, "pieces.json")))
CSS = open(os.path.join(ROOT, "_base.css")).read()
MONO = open(os.path.join(ROOT, "_mono_inner.txt")).read()

E = html.escape

CSS += """
.related{padding-block:clamp(3rem,6vw,5rem);border-top:1px solid var(--seam)}
.prose{display:grid;gap:clamp(2rem,4vw,3rem);max-width:760px}
.prose section{display:grid;gap:.8rem;padding-top:1.2rem;border-top:1px solid var(--seam)}
.prose h2{font-size:1.7rem}
.prose p,.prose li{color:var(--smoke);font-size:1rem}
.prose ul{margin:0;padding-left:1.1rem;display:grid;gap:.45rem}
.ig{color:var(--champagne-hi);text-decoration:none;border-bottom:1px solid var(--seam)}
.ig:hover{border-color:var(--champagne)}
.inquiry .actions{padding-top:0}
.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:16px;z-index:50;background:var(--case);padding:.6em 1em}
[hidden]{display:none!important}
html,body{margin:0}
"""

def mono_svg(gid, cls=""):
    return f'<svg viewBox="36 16 156 154" aria-hidden="true"{(" class=%s" % cls) if cls else ""}>{MONO.replace("lcGold", gid)}</svg>'

def price_text(p):
    return f"${p['price']:,.0f}" if p.get("price") else "Price on request"

def ref_text(p):
    if p.get("ref"): return f"Ref. {p['ref']}"
    if p.get("special"): return "Special order"
    return ""

def piece_title(p):
    return f"{p['maker']} {p['model']}" + (f" {p['ref']}" if p.get("ref") else "")

def url(path):
    return SITE + (path if path != "/" else "/")

NAV = [("/collection", "Collection", "collection"), ("/sell-or-trade", "Sell or Trade", "sell"),
       ("/about", "About", "about"), ("/contact", "Contact", "contact")]

def page(path, title, description, body, current=None, image=None, jsonld=None, extra_js=""):
    image = image or "/og.jpg"
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if k == current else ""}>{t}</a>' for h, t, k in NAV)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(description)}">
<link rel="canonical" href="{url(path)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="The Luxe Corner">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(description)}">
<meta property="og:url" content="{url(path)}">
<meta property="og:image" content="{SITE}{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0E0D0C">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@300;400;500&display=swap">
<link rel="stylesheet" href="/styles.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap head-row">
    <a class="brand" href="/" aria-label="The Luxe Corner, home">{mono_svg("hdrGold")}<span class="brand-name">THE LUXE CORNER</span></a>
    <nav class="nav" aria-label="Main">{nav}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <div class="foot-row">
      <div class="mark">{mono_svg("ftGold")}<div><div class="brand-name" style="font-size:1.05rem">THE LUXE CORNER</div><div class="eyebrow" style="font-size:.62rem;color:var(--smoke)">Fine watches &amp; jewelry</div></div></div>
      <div><h4>Explore</h4><ul><li><a href="/collection">Collection</a></li><li><a href="/sell-or-trade">Sell or trade</a></li><li><a href="/about">About</a></li></ul></div>
      <div><h4>Help</h4><ul><li><a href="/contact">Contact</a></li><li><a href="/policies">Shipping, payment and inspection</a></li><li><a href="{IG_URL}" target="_blank" rel="noopener">Instagram @{IG_HANDLE}</a></li></ul></div>
    </div>
    <div class="fine"><p>{E(BRANDS_DISCLAIMER)}</p><span>&copy; {date.today().year} The Luxe Corner LLC</span></div>
  </div>
</footer>
{extra_js}
</body>
</html>
"""

def card(p):
    r = ref_text(p) or "&nbsp;"
    return f"""<a class="card" href="/watches/{p['slug']}" data-cat="{p['cat']}" data-maker="{E(p['maker'])}">
  <div class="frame"><img src="/{p['images'][0]}" alt="{E(p['alt'])}" loading="lazy" decoding="async"></div>
  <div class="meta"><span class="brandline">{E(p['maker'])}</span><span class="model">{E(p['model'])}</span>
  <span class="row"><span class="ref">{E(r) if r != '&nbsp;' else r}</span><span>{price_text(p)}</span></span></div>
</a>"""

def write(path, content):
    out = os.path.join(DIST, path.strip("/"), "index.html") if not path.endswith((".html", ".xml", ".txt", ".json", ".svg")) else os.path.join(DIST, path.strip("/"))
    if path == "/": out = os.path.join(DIST, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(content)

ORG_LD = {"@context": "https://schema.org", "@type": "Store", "name": "The Luxe Corner", "legalName": "The Luxe Corner LLC",
          "url": SITE, "logo": SITE + "/logo.svg", "sameAs": [IG_URL],
          "description": "Fine watches and jewelry, privately offered."}

def build():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    open(os.path.join(DIST, "styles.css"), "w").write(CSS)
    shutil.copytree(os.path.join(ROOT, "img"), os.path.join(DIST, "img"))
    for f in ("favicon.svg", "apple-touch-icon.png", "og.jpg", "logo.svg"):
        shutil.copy(os.path.join(ROOT, "assets", f), os.path.join(DIST, f))

    hero = next(p for p in PIECES if p["slug"] == "patek-5990-1r")
    makers = list(dict.fromkeys(p["maker"] for p in PIECES))

    # HOME
    home = f"""
<div class="wrap hero">
  <div class="hero-copy">
    <span class="eyebrow">Fine watches &amp; jewelry, privately offered</span>
    <h1>Pieces chosen by a collector, <em>offered to collectors.</em></h1>
    <p class="lede">A small, considered selection from Patek Philippe, Audemars Piguet, Rolex, Vacheron Constantin and the independent watchmakers we admire. Each piece is photographed in hand and offered directly, with every question answered personally.</p>
    <div class="actions"><a class="btn" href="/collection">View the collection</a><a class="btn ghost" href="/sell-or-trade">Sell or trade a watch</a></div>
  </div>
  <figure class="hero-plate">
    <a href="/watches/{hero['slug']}"><img src="/img/patek-5990-1r-2.jpg" alt="{E(hero['alt'])}" width="1400" height="1018" fetchpriority="high"></a>
    <figcaption><span><b>Patek Philippe</b> &nbsp;Nautilus Travel Time Chronograph</span><span class="ref">Ref. 5990/1R-001</span></figcaption>
  </figure>
</div>
<div class="sec"><div class="wrap">
  <div class="sec-head"><div class="stack"><span class="eyebrow">Currently in the case</span><h2>The collection</h2></div><a class="textlink" href="/collection">See every piece</a></div>
  <div class="grid">{''.join(card(p) for p in PIECES)}</div>
</div></div>
<div class="sec"><div class="wrap promises">
  <div class="promise"><span class="eyebrow">In hand</span><h3>The photographs show the piece you receive</h3><p>Every image on a listing is of that exact watch, taken by us. Ask for more angles, a video or a wrist shot and we will send them.</p></div>
  <div class="promise"><span class="eyebrow">Delivery</span><h3>Fully insured, signature required</h3><p>Every shipment is insured for its full purchase price and released only against a signature. Armored delivery is available on request.</p></div>
  <div class="promise"><span class="eyebrow">Inspection</span><h3>Three days to inspect at home</h3><p>You have three days from delivery to examine your piece. <a class="ig" href="/policies">Read the full terms</a>.</p></div>
</div></div>
<div class="sec"><div class="wrap band">
  <img src="/img/patek-5738-51g-1.jpg" alt="Patek Philippe Golden Ellipse with a hand-engraved black enamel dial" width="1400" height="931" loading="lazy">
  <div class="copy"><span class="eyebrow">Sell or trade</span><h2>Have a piece you are ready to part with?</h2>
  <p class="lede">We buy and trade fine watches from fellow collectors, with a quiet process and a direct offer. Send us the reference, its condition and a few photographs to begin.</p>
  <div class="actions"><a class="btn ghost" href="/sell-or-trade">Start a conversation</a></div></div>
</div></div>"""
    write("/", page("/", "The Luxe Corner | Fine Watches & Jewelry",
        "Fine watches and jewelry, privately offered. Patek Philippe, Audemars Piguet, Rolex, Vacheron Constantin and independent watchmakers.",
        home, jsonld=ORG_LD))

    # COLLECTION
    chips_m = "".join(f'<button class="chip" type="button" id="f-maker-{i}" data-f-maker="{E(m)}" aria-pressed="{str(m == "all").lower()}">{"All" if m == "all" else E(m)}</button>' for i, m in enumerate(["all"] + makers))
    coll = f"""
<div class="wrap page">
  <div class="page-head"><span class="eyebrow">The collection</span><h1>Currently in the case</h1>
  <p class="lede">Every piece is offered with box and papers. For pieces marked price on request, send us a message and we will reply personally.</p></div>
  <div>
    <div class="filters">
      <div class="chipset" role="group" aria-label="Category"><span class="label">Category</span>
        <button class="chip" type="button" id="f-cat-all" data-f-cat="all" aria-pressed="true">All</button>
        <button class="chip" type="button" id="f-cat-watch" data-f-cat="watch" aria-pressed="false">Watches</button>
        <button class="chip" type="button" id="f-cat-jewelry" data-f-cat="jewelry" aria-pressed="false">Jewelry</button></div>
      <div class="chipset" role="group" aria-label="Maker"><span class="label">Maker</span>{chips_m}</div>
    </div>
    <div class="grid" id="grid">{''.join(card(p) for p in PIECES)}</div>
    <div class="empty" id="empty" hidden><span class="eyebrow">Nothing here yet</span><h3>Our first jewelry pieces are being photographed now</h3>
      <p>If you are looking for something specific, send us a message. We often know of pieces before they are listed.</p>
      <a class="btn ghost" href="{IG_DM}" target="_blank" rel="noopener">Message us on Instagram</a></div>
  </div>
</div>"""
    coll_js = """<script>
(()=>{const st={cat:"all",maker:"all"};const cards=[...document.querySelectorAll("#grid .card")];
function run(){let n=0;cards.forEach(c=>{const ok=(st.cat==="all"||c.dataset.cat===st.cat)&&(st.maker==="all"||c.dataset.maker===st.maker);c.hidden=!ok;if(ok)n++;});
document.getElementById("grid").hidden=n===0;document.getElementById("empty").hidden=n!==0;
document.querySelectorAll("[data-f-cat]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.fCat===st.cat));
document.querySelectorAll("[data-f-maker]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.fMaker===st.maker));}
document.addEventListener("click",e=>{const c=e.target.closest("[data-f-cat]");if(c){st.cat=c.dataset.fCat;run();}
const m=e.target.closest("[data-f-maker]");if(m){st.maker=m.dataset.fMaker;run();}});})();
</script>"""
    write("/collection", page("/collection", "The Collection | The Luxe Corner",
        "Fine watches currently offered by The Luxe Corner, each with box and papers.", coll, "collection", extra_js=coll_js))

    # PIECES
    for p in PIECES:
        imgs = p["images"]
        thumbs = "" if len(imgs) < 2 else '<div class="thumbs">' + "".join(
            f'<button type="button" aria-pressed="{str(i == 0).lower()}" aria-label="Show photo {i + 1}" data-src="/{s}"><img src="/{s}" alt="" loading="lazy"></button>' for i, s in enumerate(imgs)) + "</div>"
        spec = "".join(f"<dt>{E(k)}</dt><dd>{E(v)}</dd>" for k, v in p["spec"] if v)
        inq = f"Inquiry: {p['maker']} {p.get('ref') or p['model']}"
        others = [o for o in PIECES if o["slug"] != p["slug"]]
        same = [o for o in others if o["maker"] == p["maker"]]
        related = (same + [o for o in others if o not in same])[:3]
        rt = ref_text(p)
        body = f"""
<div class="wrap">
  <nav class="crumb" aria-label="Breadcrumb"><a href="/collection">Collection</a><span aria-hidden="true">/</span><span>{E(p['maker'])} {E(p.get('ref') or p['model'])}</span></nav>
  <div class="piece">
    <div class="gallery"><figure class="main"><img id="main-img" src="/{imgs[0]}" alt="{E(p['alt'])}" fetchpriority="high"></figure>{thumbs}</div>
    <div class="detail">
      <div style="display:grid;gap:.6rem"><span class="eyebrow">{E(p['maker'])}</span>
        <h1 style="font-size:clamp(2.2rem,4vw,3.2rem)">{E(p['model'])}</h1>
        {f'<span class="refline ref">{E(rt)}</span>' if rt else ''}</div>
      <div class="price">{price_text(p)}</div>
      <div class="inquiry">
        <span class="eyebrow">Inquire</span>
        <p class="note">Send us a direct message on Instagram and include the line below so we know which piece you mean.</p>
        <div class="line"><code id="inq">{E(inq)}</code><button class="copybtn" type="button" id="copy-inq">Copy</button></div>
        <div class="actions"><a class="btn" href="{IG_DM}" target="_blank" rel="noopener">Message @{IG_HANDLE}</a></div>
      </div>
      <dl class="spec">{spec}</dl>
      <p class="note">Photographs show the actual piece offered. Additional photos and video are available on request. See our <a class="ig" href="/policies">shipping, payment and inspection terms</a>.</p>
    </div>
  </div>
</div>
<div class="related"><div class="wrap">
  <div class="sec-head"><div class="stack"><span class="eyebrow">Also in the case</span><h2>More from the collection</h2></div><a class="textlink" href="/collection">See every piece</a></div>
  <div class="grid">{''.join(card(o) for o in related)}</div>
</div></div>"""
        js = """<script>
(()=>{const m=document.getElementById("main-img");document.querySelectorAll(".thumbs button").forEach(b=>b.addEventListener("click",()=>{m.src=b.dataset.src;document.querySelectorAll(".thumbs button").forEach(x=>x.setAttribute("aria-pressed",x===b));}));
const cb=document.getElementById("copy-inq"),t=document.getElementById("inq");cb.addEventListener("click",async()=>{try{await navigator.clipboard.writeText(t.textContent);cb.textContent="Copied";}catch(e){const r=document.createRange();r.selectNodeContents(t);const s=getSelection();s.removeAllRanges();s.addRange(r);cb.textContent="Selected";}setTimeout(()=>cb.textContent="Copy",1800);});})();
</script>"""
        ld = {"@context": "https://schema.org", "@type": "Product", "name": piece_title(p),
              "brand": {"@type": "Brand", "name": p["maker"]}, "model": p["model"],
              "image": [SITE + "/" + s for s in imgs], "description": f"{piece_title(p)}. " + "; ".join(f"{k}: {v}" for k, v in p["spec"] if v),
              "itemCondition": "https://schema.org/UsedCondition"}
        if p.get("ref"): ld["mpn"] = p["ref"]
        desc = f"{piece_title(p)}, {next((v for k, v in p['spec'] if k == 'Year'), '')}, like new with box and papers. {price_text(p)}. Offered by The Luxe Corner."
        write(f"/watches/{p['slug']}", page(f"/watches/{p['slug']}", f"{piece_title(p)} | The Luxe Corner", desc, body, "collection",
              image="/" + imgs[0], jsonld=ld, extra_js=js))

    # SELL OR TRADE
    sell = f"""
<div class="wrap page">
  <div class="page-head"><span class="eyebrow">Sell or trade</span><h1>Part with a piece, quietly</h1>
  <p class="lede">We buy outright and accept trades toward any piece in the collection. Patek Philippe, Audemars Piguet and Rolex are our focus, and we are always glad to hear about independents.</p></div>
  <div class="cols">
    <div class="block"><span class="eyebrow">What to send</span><ul>
      <li>Maker, model and reference number</li><li>Year of purchase or the date on the papers</li>
      <li>Box, papers and any service records you have</li><li>Honest notes on condition, including any polishing</li>
      <li>Clear photos of the dial, case, caseback and clasp</li><li>Your asking price, or whether you would like a trade</li></ul></div>
    <div class="block"><span class="eyebrow">What happens next</span><p>We reply personally, usually with questions first. If the piece suits the collection, we make a direct offer. When we agree, we arrange fully insured shipping for inspection before payment is released.</p></div>
    <div class="block"><span class="eyebrow">Get in touch</span><p>Send a direct message on Instagram to <a class="ig" href="{IG_URL}" target="_blank" rel="noopener">@{IG_HANDLE}</a> with your photos and details.</p>
      <div class="actions"><a class="btn ghost" href="{IG_DM}" target="_blank" rel="noopener">Message us</a></div></div>
  </div>
</div>"""
    write("/sell-or-trade", page("/sell-or-trade", "Sell or Trade Your Watch | The Luxe Corner",
        "Sell or trade your Patek Philippe, Audemars Piguet, Rolex or independent watch with The Luxe Corner.", sell, "sell"))

    # ABOUT
    about = """
<div class="wrap page"><div class="band">
  <img src="/img/patek-5004j-2.jpg" alt="Patek Philippe 5004J split-seconds perpetual calendar chronograph in yellow gold on a green alligator strap" width="931" height="1400" style="aspect-ratio:4/5" loading="lazy">
  <div class="copy"><span class="eyebrow">About</span><h1>A collector's corner</h1>
    <p class="lede">The Luxe Corner began with a personal collection and a habit of looking closely: at dials, at movements, at the details that separate a good watch from an exceptional one.</p>
    <p class="lede">We keep the selection small on purpose. Every piece here is one we would gladly wear ourselves, and every conversation is handled personally, from first question to delivery.</p>
    <p class="lede">Alongside the great houses we carry the work of independent watchmakers, whose craft and vision we admire just as much.</p></div>
</div></div>"""
    write("/about", page("/about", "About | The Luxe Corner", "The Luxe Corner is a small, collector-run selection of fine watches and jewelry.", about, "about"))

    # CONTACT
    contact = f"""
<div class="wrap page">
  <div class="page-head"><span class="eyebrow">Contact</span><h1>Send us a message</h1>
  <p class="lede">We take all inquiries by direct message on Instagram and reply to every one personally.</p>
  <div class="actions"><a class="btn" href="{IG_DM}" target="_blank" rel="noopener">Message @{IG_HANDLE}</a></div></div>
  <div class="cols">
    <div class="block"><span class="eyebrow">Instagram</span><p><a class="ig" href="{IG_URL}" target="_blank" rel="noopener">@{IG_HANDLE}</a></p></div>
    <div class="block"><span class="eyebrow">Location</span><p>Online only. Viewings are not offered at this time.</p></div>
    <div class="block"><span class="eyebrow">Policies</span><p>Shipping, payment and our three-day inspection window are explained on the <a class="ig" href="/policies">policies page</a>.</p></div>
  </div>
</div>"""
    write("/contact", page("/contact", "Contact | The Luxe Corner", "Contact The Luxe Corner by direct message on Instagram.", contact, "contact"))

    # POLICIES
    pol = f"""
<div class="wrap page">
  <div class="page-head"><span class="eyebrow">Policies</span><h1>Shipping, payment and inspection</h1>
  <p class="lede">These terms apply to every purchase from The Luxe Corner LLC.</p></div>
  <div class="prose">
    <section id="shipping"><h2>Shipping</h2>
      <p>Every order ships fully insured for its full purchase price, and delivery requires a signature.</p>
      <p>Armored delivery is available on request. We quote its cost in advance, and the buyer pays it.</p></section>
    <section id="payment"><h2>Payment</h2>
      <p>We accept wire transfer and credit card.</p>
      <p>Credit card payment is accepted for purchases up to $150,000. Purchases above $150,000 must be paid by wire transfer.</p></section>
    <section id="inspection"><h2>Three-day inspection window</h2>
      <p>You may inspect your piece for 3 days from the date of delivery. To return it, send us a message on Instagram within those 3 days.</p>
      <ul><li>The piece must be returned unworn.</li>
        <li>The buyer pays for return shipping and insurance.</li>
        <li>Refunds are issued within 7 to 10 business days, once we have received and inspected the returned piece.</li></ul></section>
    <section id="condition"><h2>Condition and photographs</h2>
      <p>Condition descriptions are our good-faith assessment of each piece. The photographs on every listing show the actual piece offered.</p></section>
    <section id="pricing"><h2>Pricing and availability</h2>
      <p>Prices and availability may change without notice, and every piece is subject to prior sale.</p></section>
    <section id="independence"><h2>Independence</h2>
      <p>{E(BRANDS_DISCLAIMER)}</p></section>
  </div>
</div>"""
    write("/policies", page("/policies", "Shipping, Payment and Inspection | The Luxe Corner",
        "Insured shipping with signature, wire or card payment, and a three-day inspection window.", pol))

    # 404
    nf = """<div class="wrap page"><div class="page-head"><span class="eyebrow">Not found</span><h1>That page is not in the case</h1>
<p class="lede">The piece may have sold, or the link may be mistyped.</p><div class="actions"><a class="btn" href="/collection">View the collection</a></div></div></div>"""
    open(os.path.join(DIST, "404.html"), "w").write(page("/404", "Page Not Found | The Luxe Corner", "Page not found.", nf))

    # SEO files
    paths = ["/", "/collection", "/sell-or-trade", "/about", "/contact", "/policies"] + [f"/watches/{p['slug']}" for p in PIECES]
    today = date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"  <url><loc>{url(x)}</loc><lastmod>{today}</lastmod></url>\n" for x in paths) + "</urlset>\n"
    open(os.path.join(DIST, "sitemap.xml"), "w").write(sm)
    open(os.path.join(DIST, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    json.dump({"cleanUrls": True, "trailingSlash": False,
               "headers": [{"source": "/img/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=86400"}]}]},
              open(os.path.join(DIST, "vercel.json"), "w"), indent=1)
    print("built", len(paths), "pages")

if __name__ == "__main__":
    build()
