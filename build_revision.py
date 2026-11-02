#!/usr/bin/env python3
"""Static, progressive-enhancement Harbor City Archives index.

Source of truth: catalog.json. Public markup and JSON-LD are generated from it.
No email signup or analytics is activated without the owner's account details.
"""
import html, json, datetime, re
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).parent
books=json.loads((ROOT/'catalog.json').read_text())
by_id={b['id']:b for b in books}
TODAY=datetime.date.today()
SHELVES=[
('shocks','Tales From the Vault: Short Shocks','Short Shocks','Short, high-concept technology and glitch horror around Harbor City. Start with The AFK Kid.'),
('vault','Vault Chronicles','Vault Chronicles','Young investigators follow impossible clues beneath a familiar city.'),
('receipts','The Receipt Society / Harbor Six Mysteries','The Receipt Society','Six girls, impossible paperwork, and official explanations that never quite match the evidence.'),
('pier','Harbor Pier','Harbor Pier','Harbor City stories told through the machinery of ordinary civic life.'),
('hydrogen','The Hydrogen Tapestry','The Hydrogen Tapestry','The speculative machinery behind worlds, histories, conflict, and the cost of refusing it.'),
('balloon','The Boy in the Balloon','Boy in the Balloon','A literary journey that begins with exile, invention, and a hum beneath the coast.'),
('ire','CL Ire / 505 Chronicles','CL Ire / 505','Literary records, memory, history, and memoir noir. No invented sequence imposed on unnumbered titles.'),
('armor','CLH Armor','CLH Armor','Protective storytelling for younger readers, with approachable monsters and useful language.')]
AUDIENCE={'shocks':'Middle Grade','vault':'Teen','receipts':'YA','pier':'Adult','hydrogen':'Adult','balloon':'Adult','ire':'Adult','armor':'Picture Book'}
ENTRIES=[
('Creepy, quick, and clever','The wrong headset','the-afk-kid'),
('Mystery and investigation','Start with the ledger','soot-season'),
('Young adventurers','The door beneath the floor','the-hatch-in-the-hollow'),
('Harbor City itself','Start at the seawall','the-maintenance-window'),
('Big cosmic science fiction','Find the engine','the-spite-engine'),
('Strange literary history','Follow the first flight','the-first-lift'),
('A memoir-shaped record','Open the black box','the-unbreakable-fool'),
('Younger readers','Meet the monsters','the-clh-armor-series')]
# Short selections from the actual manuscripts uploaded for this project.
# Avoid attaching unverified marketing copy to books without blurbs.
EXCERPTS={
'shocks':('The AFK Kid','the-afk-kid',["Sam Hawthorne stood in front of the window like he was waiting for it to blink.","The rain had just stopped. Harbor City always looked cleaner right after rain, like the town had been rinsed and put back on a shelf. The Seawall loomed down the street, a gray curve of concrete pretending it was just a wall and not a warning."]),
'vault':('The Hatch in the Hollow','the-hatch-in-the-hollow',["Jace Moreno hated detention for the same reason he hated waiting rooms.","Nothing happened, and adults acted like that was good."]),
'receipts':('Soot Season','soot-season',["Harbor City has a lot of rules.","Some of them are printed on signs, like NO SWIMMING and DO NOT FEED THE GULLS and PARK CLOSES AT DUSK (which is a lie, because the park closes whenever it feels like it and no one argues with a park that has fog).","Some of the rules are unspoken, which is worse."]),
'pier':('The Maintenance Window','the-maintenance-window',["Dale Pitkin had eleven years on the wall and nothing to show for it but a bad knee and a lanyard collection.","Night shift. Seawall Monitoring Station 7. A concrete room with four screens, a coffee maker from the Clinton administration, and a chair that reclined just enough to ruin your back but not enough to let you sleep."]),
'hydrogen':('The Spite Engine','the-spite-engine',["He learned early that the planet did not hate him.","Hate took breath. Hate took heat. Hate took a sky that bothered to hold sound long enough for a scream to matter.","This world had none of that."]),
'balloon':('The First Lift','the-first-lift',["The boy did not remember the day he was cast out because there was no day.","There was only a quiet math that changed, little by little, until it ended with him standing in the wrong place with nobody correcting him."]),
'ire':('The Unbreakable Fool','the-unbreakable-fool',["I do not remember my first word.","I remember the hum.","It lived behind the walls like an animal you never saw but always heard breathing. It lived in the outlets, in the refrigerator’s steady throat, in the soft, endless whisper of wires doing their work."]),
'armor':('Meet JADE (CLH Armor story files)','the-clh-armor-series',["Inside Caroline’s armor lives a tiny helper.","Its name is JADE.","JADE is made of little notes and bright ideas."])}


def esc(x):return html.escape(str(x),quote=True)
def link_for(book,fmt):
    entry=book.get(fmt) or {}
    if entry.get('asin') and entry.get('status') in ('live','preorder'):
        return 'https://www.amazon.com/dp/'+entry['asin']
    return None

def primary(book):
    return next((url for x in ('kindle','paperback','hardcover') if (url:=link_for(book,x))),None)

def formats(b):
    pieces=[]
    for key,label in [('kindle','Kindle'),('paperback','Paperback'),('hardcover','Hardcover')]:
        url=link_for(b,key)
        if url:
            text=f'{label} preorder' if b[key]['status']=='preorder' else label
            pieces.append(f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer" aria-label="{esc(b["title"])}: {esc(text)}, opens Amazon in a new tab">{esc(text)} <span aria-hidden="true">↗</span></a>')
    return '<div class="buy-links">'+''.join(pieces)+'</div>' if pieces else '<span class="format-note">No public editions indexed</span>'

def sorted_titles(family):
    return sorted((b for b in books if b['family']==family),key=lambda b:(b['seriesNumber'] is None,b['seriesNumber'] or 999,b['title']))

def filed(b):
    dates=[]
    for fmt in ('kindle','paperback','hardcover'):
        s=b[fmt].get('submitted')
        if s:
            try: dates.append(datetime.datetime.strptime(s,'%B %d, %Y').date())
            except ValueError: pass
    return dates

def first_filed(b):
    v=filed(b)
    return min(v) if v else None

def last_filed(b):
    v=filed(b)
    return max(v) if v else None

def newest(b):
    first=first_filed(b)
    return first and 0<=(TODAY-first).days<=30 and any(b[k]['status']=='live' for k in ('kindle','paperback','hardcover'))

def book_card(b):
    title=esc(b['title']);author=esc(b['author']);genre=b['audience']
    cover=(f'<img src="{esc(b["cover"])}" alt="Cover of {title} by {author}" width="480" height="768" loading="lazy" decoding="async">'
           if b.get('cover') else '<div class="cover-pending">COVER PENDING INTAKE</div>')
    hook=f'<p class="book-hook">{esc(b["hook"])}</p>' if b.get('hook') else '<p class="book-hook pending">Summary awaiting intake.</p>'
    n=f'Book {b["seriesNumber"]}' if b.get('seriesNumber') else 'Archive title'
    stamp=f'<span class="new-stamp" data-filed-date="{first_filed(b).isoformat()}" hidden>NEWLY RECOVERED</span>' if newest(b) else ''
    data=' '.join(filter(None,[b['title'],b.get('subtitle') or '',b['author'],b['series'],b.get('hook') or ''])).lower()
    return f'''<article class="book-card" id="record-{esc(b['id'])}" data-search="{esc(data)}" data-author="{author}" data-audience="{esc(genre)}">
    <div class="cover" data-family="{esc(b['family'])}">{cover}</div>
    <div class="book-body"><div class="record-id">HC / {esc(b['family'].upper())} / {str(b['seriesNumber'] or 'FILE').zfill(2) if b.get('seriesNumber') else 'FILE'}</div>
    <div class="badge-row"><span class="audience-badge">{esc(genre)}</span>{stamp}</div>
    <h3>{title}</h3><div class="book-sub">{author} · {esc(n)}</div>{hook}{formats(b)}</div>
    </article>'''

def shelf(fid,name,short,intro):
    these=sorted_titles(fid)
    listing=''.join(f'<li><a href="#record-{esc(b["id"])}">{esc(b["title"])}</a>{f" <small>#{b[chr(115)+chr(101)+chr(114)+chr(105)+chr(101)+chr(115)+chr(78)+chr(117)+chr(109)+chr(98)+chr(101)+chr(114)]}</small>" if b.get("seriesNumber") else ""}</li>' for b in these)
    # Excerpts cite an actual source title, not an invented connection.
    source_title,source_id,paras=EXCERPTS[fid]
    doc=''.join('<p>'+esc(p)+'</p>' for p in paras)
    quote=f'''<details class="evidence-excerpt"><summary>Evidence excerpt: {esc(source_title)}</summary><div class="excerpt-document"><div class="eyebrow">RECOVERED TEXT / {esc(source_title)}</div><blockquote>{doc}</blockquote><a href="{esc(primary(by_id[source_id]))}" target="_blank" rel="noopener noreferrer">Open this record on Amazon ↗</a></div></details>'''
    return f'''<details class="family" id="shelf-{fid}" data-family="{fid}" {"open" if fid in ("shocks","receipts") else ""}>
      <summary><span class="family-title">{esc(name)}</span><span class="family-summary">{len(these):02d} RECORDS <span class="plus">+</span></span></summary>
      <div class="family-body"><p class="family-desc">{esc(intro)}</p>
      <details class="filing-order"><summary>Filing order / {len(these)} records</summary><ol>{listing}</ol></details>
      {quote}<div class="book-grid">{''.join(book_card(b) for b in these)}</div></div>
    </details>'''

def entry_cards():
    out=[]
    for tagline,heading,ident in ENTRIES:
        b=by_id[ident]; url=primary(b)
        cover=f'<img class="entry-cover" src="{esc(b["cover"])}" alt="" width="47" height="75" loading="lazy" decoding="async">' if b.get('cover') else ''
        out.append(f'''<article class="entry"><div class="entry-meta"><div class="eyebrow">{esc(tagline)}</div>{cover}</div><h3>{esc(heading)}</h3><p>{esc(b.get('hook') or b['series'])}</p><div class="entry-title"><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(b['title'])} ↗</a></div><div class="book-number">{esc(b['audience'])}</div></article>''')
    return ''.join(out)

def latest():
    chosen=sorted([b for b in books if last_filed(b)],key=lambda b:last_filed(b),reverse=True)[:3]
    rows=[]
    for b in chosen:
        cover=f'<img class="latest-cover" src="{esc(b["cover"])}" alt="Cover of {esc(b["title"])} by {esc(b["author"])}" width="68" height="109" loading="lazy" decoding="async">' if b.get('cover') else '<span class="latest-mark">HC</span>'
        rows.append(f'''<article class="latest-card">{cover}<div><div class="micro">{esc(b['author'])} / {last_filed(b).strftime('%b %-d, %Y')}</div><h3 class="latest-title">{esc(b['title'])}</h3><div class="status-note">RECENT FILING ENTERED</div>{formats(b)}</div></article>''')
    return ''.join(rows)

soup=BeautifulSoup((ROOT/'base_index.html').read_text(),'html.parser')
for node in soup.find_all('script'):node.decompose()
head=soup.head
# social preview: absolute URL required by most social scrapers
for prop,content in [('og:image','https://harborcityusa.com/assets/harbor-city-archive-share.jpg'),('og:image:width','1200'),('og:image:height','630'),('og:type','website'),('og:url','https://harborcityusa.com/')]:
    tag=soup.new_tag('meta');tag['property']=prop;tag['content']=content;head.append(tag)
for name,content in [('twitter:card','summary_large_image'),('twitter:image','https://harborcityusa.com/assets/harbor-city-archive-share.jpg')]:
    tag=soup.new_tag('meta');tag['name']=name;tag['content']=content;head.append(tag)
icon=soup.new_tag('link');icon['rel']='icon';icon['type']='image/svg+xml';icon['href']='assets/favicon.svg';head.append(icon)

def replace(el_id,markup):
    el=soup.find(id=el_id)
    if el is None:raise ValueError('missing '+el_id)
    el.clear()
    fragment=BeautifulSoup(markup,'html.parser')
    for node in list(fragment.contents):el.append(node)

replace('entry-grid',entry_cards())
replace('latest-grid',latest())
replace('catalog-shelves',''.join(shelf(*row) for row in SHELVES))
replace('series-list',''.join(f'<a class="series-link" href="#shelf-{fid}">{esc(short)} <span>{len(sorted_titles(fid)):02d}</span></a>' for fid,_,short,_ in SHELVES))
# The filter controls are a progressive enhancement; without JS there is nothing to disable browsing.
controls=soup.select_one('.catalog-controls')
controls['id']='catalog-controls'
controls['hidden']=''
for select_id,opts in [('series-filter',[(f,n) for f,n,_,_ in SHELVES]),('author-filter',[(a,a) for a in sorted({b['author'] for b in books})]),('audience-filter',[(a,a) for a in ['Picture Book','Middle Grade','Teen','YA','Adult']])]:
    select=soup.find(id=select_id)
    if select is None and select_id=='audience-filter':
        fragment=BeautifulSoup('<div class="field"><label for="audience-filter">Audience</label><select id="audience-filter"><option value="">All readers</option></select></div>','html.parser')
        controls.append(fragment.div)
        select=soup.find(id=select_id)
    for value,label in opts:
        op=soup.new_tag('option');op['value']=value;op.string=label;select.append(op)
no=soup.find(id='no-results');no['hidden']='';no.clear()
result=soup.find(id='result-count');result.string=f'Showing all {len(books)} cataloged records'
# Remove unverified metadata and replace in-world phrases.
latest_p=soup.select_one('#latest .section-head p');latest_p.string='The newest paperwork to reach the public desk. Filing dates are not necessarily first publication dates.'
soup.find(id='latest-title').string='Recently filed.'
notice=soup.select_one('#catalog .notice');notice.string='FORMAT NOTE: Books with purchase links are available now.'
footer=soup.select_one('.footer .wrap > div:nth-of-type(2) > div:first-child');footer.string='Archive index current as of November 2026.'
start_p=soup.select_one('#start .section-head p');start_p.string='Not sure where to begin? Choose the kind of story you want. No prior clearance or mythology lecture required.'
# Navigation takes the first CTA to the actual random selector, not the same destination as Browse.
soup.select_one('.nav-cta')['href']='#random-desk'
soup.select_one('.random-section')['id']='random-desk'
button=soup.find(id='random-button');button['disabled']='';button['title']='Enable JavaScript to draw a random record'

# Kit-hosted mailing-list form: this public embed requires no server or secret API token.
# Subscriber addresses are collected by Kit, not by our static website.
signup_markup='''<section class="filing-notices" id="filing-notices" aria-labelledby="notices-title"><div class="wrap">
<div><div class="eyebrow">PUBLIC DESK / CORRESPONDENCE</div><h2 id="notices-title">Request filing notices.</h2><p>Be told when new records are recovered. Select the signatures you wish to follow. Correspondence may be discontinued at any time.</p></div>
<div class="notices-status kit-panel" aria-label="Filing Notices subscription form"><div class="micro">SUBSCRIBER REGISTRY / FILING NOTICES</div>
<script async data-uid="3011d17545" src="https://harbor-city-archives.kit.com/3011d17545/index.js"></script>
<noscript><p>To request filing notices, enable JavaScript to load the Kit signup form.</p></noscript>
<p class="notices-privacy">The subscriber registry is administered by Kit. Unsubscribe through any filing notice.</p></div>
</div></section>'''
section=BeautifulSoup(signup_markup,'html.parser').section
soup.find(id='catalog').insert_after(section)
footer_main=soup.select_one('.footer .wrap > div:first-child')
footer_note=BeautifulSoup('<p class="footer-notices">Filing notices: <a href="#filing-notices">correspondence desk</a></p>','html.parser').p
footer_main.append(footer_note)

# Next filing cadence known, but a scheduled title is not. Do not invent one.
next_html='''<section class="next-filing" aria-label="Next filing"><div class="wrap"><div class="eyebrow">NEXT FILING / SHORT SHOCKS</div><div><strong>Weekly archive intake</strong><p>Next title and date awaiting confirmation. The desk will update when the record is filed.</p></div><a href="#shelf-shocks">Review Short Shocks ↗</a></div></section>'''
soup.find(id='latest').insert_after(BeautifulSoup(next_html,'html.parser').section)

# Keep the opening without-script message out of view; original placeholder is only for JS response.
soup.find(id='random-result')['aria-live']='polite'

css='''
/* Archive revisions / November 2026 */
.catalog-controls{grid-template-columns: minmax(0,2fr) repeat(3,minmax(0,1fr))}
.badge-row{display:flex;gap:.35rem;flex-wrap:wrap;margin-top:.38rem}
.audience-badge,.new-stamp{border:1px solid #879f99;padding:.19rem .4rem;font:800 .68rem/1.3 system-ui,sans-serif;letter-spacing:.01em;color:#254b4d;background:#e2f0e9;border-radius:2px}
.new-stamp{color:#654023;background:#f1dfba;border-color:#b78c55}
.cover-pending{display:flex;align-items:center;justify-content:center;height:100%;text-align:center;font:700 .78rem/1.5 ui-monospace,monospace;letter-spacing:.04em;color:#fff2d4;padding:.55rem}
.book-card .cover img{background:#122e39}
.book-card .buy-links{margin-top:auto}
.filing-order,.evidence-excerpt{border:1px solid #c4cec8;background:#e9ede7;margin:0 0 .7rem;max-width:100%}
.filing-order summary,.evidence-excerpt summary{padding:.7rem .9rem;cursor:pointer;font:700 .76rem/1.35 ui-monospace,monospace;text-transform:uppercase;letter-spacing:.03em;color:#1d4e51}
.filing-order ol{columns:2;column-gap:2rem;margin:.2rem 1rem 1rem;padding-left:1.5rem;font-size:.84rem}
.filing-order li{break-inside:avoid;padding:.12rem 0}
.filing-order li a,.evidence-excerpt a{color:#1d5559;text-underline-offset:3px}
.filing-order small{color:#54696a}
.excerpt-document{padding:1.05rem 1.2rem 1.25rem;background:#f9f7ee;border-top:1px solid #c9d3ca}
.excerpt-document .eyebrow{color:#446d6f;font-size:.69rem}
.excerpt-document blockquote{border-left:3px solid #91a6a0;padding-left:1rem;margin:1rem 0;font:1.02rem/1.55 Georgia,serif;color:#27393b;max-width:76ch}
.excerpt-document blockquote p{margin:.48rem 0}
.excerpt-document a{font-size:.83rem;font-weight:700}
.book-card[hidden],.family[hidden],.catalog-controls[hidden]{display:none!important}
.empty:not([hidden]){display:block}
.next-filing{background:#dfebe5;border-block:1px solid #c2d5ca;padding:1.25rem 0}
.next-filing .wrap{display:flex;align-items:center;gap:1.5rem;justify-content:space-between;flex-wrap:wrap}
.next-filing .eyebrow{color:#315e59}
.next-filing strong{font-family:Georgia,serif;font-size:1.3rem}
.next-filing p{margin:.2rem 0;font-size:.82rem;color:#3f5756}
.next-filing a{color:#1c5358;font-weight:800;font-size:.83rem;text-underline-offset:4px}
.filing-notices{padding:3.2rem 0;background:#193844;color:#ecf1e9}
.filing-notices .wrap{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:2rem;align-items:center}
.filing-notices h2{font:normal clamp(1.8rem,4vw,2.7rem) Georgia,serif;line-height:1.1;margin:.3rem 0 .7rem}
.filing-notices p{max-width:60ch;margin:.3rem 0 0;color:#cfddda}
.filing-notices .eyebrow,.filing-notices .micro{color:#a3d2c9}
.notices-status{padding:1.2rem 1.4rem;border:1px solid #66827d;background:#254650}
.notices-status strong{display:block;margin:.6rem 0;font-size:.98rem;color:#fff}
.notices-status p{font-size:.8rem}
.kit-panel{min-width:0;max-width:100%;background:#f5f2e8;color:#173039;border-color:#bdcbbf;overflow-wrap:anywhere}
.kit-panel .micro{color:#375e5c;font-weight:800;margin-bottom:1rem}
.kit-panel iframe,.kit-panel form{max-width:100%}
.kit-panel .notices-privacy{color:#36545a;font-size:.75rem;line-height:1.5;margin-top:1rem}
.kit-panel noscript p{color:#36545a}
.footer-notices a{color:#eceddf}
/* Remove mono microtext below legible sizes; contrast preserved on dark panels. */
.eyebrow,.micro,.record-id,.format-note,.cover .micro,.cover .cover-bottom,.latest-card .micro,.entry .book-number{font-size:clamp(.7rem,.8vw,.82rem)}
.cover .micro,.cover .cover-bottom{color:#f3f0e9}
.record-id{color:#6d4d33}
.series-strip .eyebrow{color:#37564f}
.series-link span{color:#435b53}
.catalog-meta{color:#485e5b}
.latest-card .micro{color:#68513e}
@media(max-width:880px){.catalog-controls{grid-template-columns:1fr 1fr}.catalog-controls .search-field{grid-column:1/-1}}
@media(max-width:980px){.filing-notices .wrap{grid-template-columns:1fr}.filing-notices .kit-panel{width:100%}}
@media(max-width:650px){.filing-notices .wrap{grid-template-columns:1fr}.filing-order ol{columns:1}.book-card{overflow-wrap:anywhere}.next-filing .wrap{align-items:flex-start;flex-direction:column;gap:.5rem}}
@media(max-width:540px){.catalog-controls{grid-template-columns:1fr}.catalog-controls .search-field{grid-column:auto}.audience-badge,.new-stamp{font-size:.64rem}}
'''
style=soup.find('style');style.append(css)
# Set JSON-LD per actual title in the generated page. One canonical catalog remains maintained externally.
for b in books:
    source={'@context':'https://schema.org','@type':'Book','name':b['title'],'author':{'@type':'Person','name':b['author']},'isPartOf':{'@type':'CreativeWorkSeries','name':b['series']}}
    if b.get('seriesNumber') is not None:source['position']=b['seriesNumber']
    if primary(b):source['url']=primary(b)
    tag=soup.new_tag('script',type='application/ld+json');tag.string=json.dumps(source,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c');head.append(tag)

# Progressive enhancement ONLY. No book titles, links or information is emitted by JS.
js=r'''(()=>{
  'use strict';
  const $=id=>document.getElementById(id);
  const cards=[...document.querySelectorAll('#catalog-shelves .book-card')];
  const groups=[...document.querySelectorAll('#catalog-shelves .family')];
  const controls=$('catalog-controls'); if(controls) controls.hidden=false;
  const draw=$('random-button'); if(draw){ draw.disabled=false;draw.removeAttribute('title'); }
  function applyFilters(shouldOpen=false){
    const query=$('book-search').value.trim().toLocaleLowerCase();
    const fam=$('series-filter').value, author=$('author-filter').value, audience=$('audience-filter').value;
    let count=0;
    for(const group of groups){let matched=0;
      for(const card of group.querySelectorAll('.book-card')){
        const show=(!query||card.dataset.search.includes(query))&&(!fam||group.dataset.family===fam)&&(!author||card.dataset.author===author)&&(!audience||card.dataset.audience===audience);
        card.hidden=!show;if(show) matched++;
      }
      group.hidden=!matched;count+=matched;
      if(matched&&(query||fam||author||audience||shouldOpen)) group.open=true;
    }
    $('result-count').textContent=`Showing ${count} of ${cards.length} records`;
    $('no-results').hidden=(count!==0);
    $('no-results').textContent=count?'':'No records match those filters. Try a different title or clear the filters.';
  }
  for(const id of ['book-search','series-filter','author-filter','audience-filter']){
    const el=$(id);if(el)el.addEventListener(id==='book-search'?'input':'change',()=>applyFilters());
  }
  $('reset-filters').addEventListener('click',()=>{
    for(const id of ['book-search','series-filter','author-filter','audience-filter'])$(id).value='';
    applyFilters();
  });
  for(const a of document.querySelectorAll('.series-link')){
    a.addEventListener('click',()=>{const target=document.querySelector(a.getAttribute('href'));if(target){target.hidden=false;target.open=true;} });
  }
  if(draw)draw.addEventListener('click',()=>{
    const candidates=cards.filter(c=>c.querySelector('.buy-links a'));
    if(!candidates.length) return;
    const target=candidates[Math.floor(Math.random()*candidates.length)];
    const main=target.querySelector('.buy-links a');
    const p=$('random-result');p.replaceChildren();
    p.append('RECOVERED FILE: ');
    const a=document.createElement('a');a.textContent=target.querySelector('h3').textContent+' ↗';a.href=main.href;a.rel='noopener noreferrer';a.target='_blank';
    p.append(a);p.classList.add('visible');
  });
  // A stamp is dated by the earliest title filing, not by a later paperback update.
  // New issues are marked at build time; hide expired stamps without needing redeployment.
  for(const stamp of document.querySelectorAll('.new-stamp[data-filed-date]')){
    const filed=new Date(stamp.dataset.filedDate+'T00:00:00Z');
    const now=new Date();
    const days=(now-filed)/86400000;
    stamp.hidden=Number.isNaN(filed.getTime())||days<0||days>30;
  }
  // No future release date has been confirmed beyond the filed preorders.
  applyFilters();
})();'''
script=soup.new_tag('script');script.string=js;soup.body.append(script)
# Save single canonical data file externally; no duplicate JSON needs to live inside page JS.
path=ROOT/'index.html';path.write_text(str(soup),encoding='utf8')

# Generated brand social image from real covers, no fabricated book art.
assets=ROOT/'assets';assets.mkdir(exist_ok=True)
W,H=1200,630
im=Image.new('RGB',(W,H),(8,29,39));d=ImageDraw.Draw(im)
for y in range(H):
    c=(int(8+y/H*7),int(29+y/H*14),int(39+y/H*14))
    d.line((0,y,W,y),fill=c)
for x in range(0,800,44):d.line((x,0,x,H),fill=(21,54,61),width=1)
for y in range(24,H,44):d.line((0,y,810,y),fill=(21,54,61),width=1)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
fontb=ImageFont.truetype(serif,64)
fonts=ImageFont.truetype(font,25)
fontm=ImageFont.truetype(font,18)
d.rectangle((58,73,740,80),fill=(131,195,186))
d.text((62,122),'HARBOR CITY',font=fontb,fill=(242,241,231))
d.text((65,220),'ARCHIVES',font=fontb,fill=(242,241,231))
d.text((67,318),'SHIVA LITERARY UNIVERSE',font=fonts,fill=(145,203,192))
d.text((67,378),'THE RECORD BREATHES.',font=ImageFont.truetype(serif,34),fill=(236,201,151))
d.text((68,531),'FIVE SIGNATURES / ONE ARCHIVE',font=fontm,fill=(195,210,203))
ids=['the-afk-kid','soot-season','the-spite-engine','the-hatch-in-the-hollow']
for i,ident in enumerate(ids):
    b=by_id[ident];f=ROOT/b['cover']
    if f.exists():
        cover=Image.open(f).convert('RGB')
        cover.thumbnail((147,248))
        x=810+(i%2)*164; y=64+(i//2)*282
        d.rectangle((x-5,y-5,x+153,y+253),fill=(31,59,65),outline=(122,171,161),width=2)
        im.paste(cover,(x+(147-cover.width)//2,y+(248-cover.height)//2))
im.save(assets/'harbor-city-archive-share.jpg',quality=88,optimize=True)

(assets/'favicon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#071a22"/><circle cx="32" cy="32" r="24" fill="none" stroke="#89c3bd" stroke-width="2"/><path d="M19 32h26M32 19v26" stroke="#e5b675" stroke-width="2"/><text x="32" y="38" fill="#f1f0e7" font-family="Georgia,serif" font-weight="bold" font-size="19" text-anchor="middle">H</text></svg>''',encoding='utf8')

print('Generated',path,'with',len(books),'static records',sum(bool(b.get('cover')) for b in books),'cover images; social image', (assets/'harbor-city-archive-share.jpg').stat().st_size)
