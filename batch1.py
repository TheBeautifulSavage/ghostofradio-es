import anthropic, json, re, subprocess
from pathlib import Path

with open('/Users/mac1/.openclaw/agents/main/agent/auth-profiles.json') as f:
    d = json.load(f)
client = anthropic.Anthropic(api_key=d['profiles']['anthropic:default']['key'])

EN = Path('/Users/mac1/Projects/ghostofradio')
ES = Path('/Users/mac1/Projects/ghostofradio-es')

# Spanish nav/footer replacements (simple string replace - no API needed)
REPLACEMENTS = [
    ('Home</a>', 'Inicio</a>'),
    ('>Shows<', '>Programas<'),
    ('>About<', '>Acerca<'),
    ('Browse All', 'Ver todos los'),
    ('Episodes', 'Episodios'),
    ('Listen Free', 'Escuchar Gratis'),
    ('Subscribe', 'Suscribirse'),
    ('All Shows', 'Todos los Programas'),
    ('Ghost of Radio', 'Ghost of Radio'),
    ('Old Time Radio', 'Radio Clásica'),
    ('Next Episode', 'Siguiente Episodio'),
    ('Previous Episode', 'Episodio Anterior'),
    ('More from Ghost of Radio', 'Más de Ghost of Radio'),
    ('lang="en"', 'lang="es"'),
]

def translate_description(content_html):
    """Only translate the episode__content div paragraphs."""
    m = re.search(r'(<div class="episode__content">)(.*?)(</div>)', content_html, re.DOTALL)
    if not m:
        return content_html
    orig = m.group(2)
    if len(orig.strip()) < 50:
        return content_html
    try:
        msg = client.messages.create(
            model='claude-haiku-4-5', max_tokens=800,
            messages=[{'role':'user','content':f'Translate to Spanish (Latin American). Keep all HTML tags exactly. Only translate visible text. Be concise:\n\n{orig}'}]
        )
        translated = msg.content[0].text
        return content_html.replace(orig, translated)
    except Exception as e:
        print(f'  translate error: {e}')
        return content_html

def copy_show(show_slug):
    src_dir = EN / show_slug
    dst_dir = ES / show_slug
    dst_dir.mkdir(exist_ok=True, parents=True)
    
    pages = [p for p in src_dir.glob('*.html') if p.name != 'index.html']
    print(f'{show_slug}: {len(pages)} pages', flush=True)
    
    copied = 0
    for i, page in enumerate(pages):
        dst = dst_dir / page.name
        if dst.exists():
            continue
        
        content = page.read_text(encoding='utf-8', errors='ignore')
        
        # Apply simple string replacements (no API)
        for old, new in REPLACEMENTS:
            content = content.replace(old, new)
        
        # Update canonical URL
        content = content.replace('https://ghostofradio.com/', 'https://es.ghostofradio.com/')
        
        # Translate description paragraphs (API call)
        content = translate_description(content)
        
        dst.write_text(content, encoding='utf-8')
        copied += 1
        
        if (i+1) % 100 == 0:
            print(f'  {i+1}/{len(pages)}...', flush=True)
            # Commit every 100 pages
            subprocess.run(['git','add','-A'], cwd=ES, capture_output=True)
            subprocess.run(['git','commit','-m',f'feat: {show_slug} Spanish — {i+1} pages'], cwd=ES, capture_output=True)
            subprocess.run(['git','push','origin','main'], cwd=ES, capture_output=True)
    
    # Final commit for this show
    subprocess.run(['git','add','-A'], cwd=ES, capture_output=True)
    r = subprocess.run(['git','commit','-m',f'feat: {show_slug} complete in Spanish ({len(pages)} pages)'], cwd=ES, capture_output=True, text=True)
    subprocess.run(['git','push','origin','main'], cwd=ES, capture_output=True)
    print(f'✅ {show_slug} done — {copied} new pages copied', flush=True)
    return copied

import sys

# Use command-line args if provided, otherwise run all shows with gaps
if len(sys.argv) > 1:
    shows_to_run = sys.argv[1:]
else:
    # Auto-detect shows with gaps between EN and ES
    shows_to_run = []
    for d in sorted(EN.iterdir()):
        if not d.is_dir() or d.name.startswith('.'): continue
        en_count = len(list(d.glob('*.html')))
        es_dir = ES / d.name
        es_count = len(list(es_dir.glob('*.html'))) if es_dir.exists() else 0
        if en_count > es_count:
            shows_to_run.append(d.name)

print(f'Running {len(shows_to_run)} shows: {shows_to_run[:5]}...', flush=True)
total = 0
for show in shows_to_run:
    total += copy_show(show)

print(f'Complete — {total} total pages copied')
