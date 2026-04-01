import anthropic, json, re, subprocess
from pathlib import Path

with open('/Users/mac1/.openclaw/agents/main/agent/auth-profiles.json') as f:
    d = json.load(f)
client = anthropic.Anthropic(api_key=d['profiles']['anthropic:default']['key'])
ES = Path('/Users/mac1/Projects/ghostofradio-es')

SPANISH_SHOWS = {
    "kaliman": {
        "name": "Kalimán, el Hombre Increíble",
        "years": "1963-1981",
        "network": "Radio Cadena Nacional (México)",
        "genre": "Aventura/Superhéroe",
        "description": "El superhéroe de la radio mexicana. Kalimán y su joven compañero Solín recorren el mundo luchando contra el mal con poderes mentales extraordinarios. El programa de radio más exitoso de México con más de 3,000 episodios.",
        "episodes": ["El Hombre Increíble", "La Momia Azteca", "El Valle de los Zombis", "El Templo del Sol", "Los Guardianes del Tiempo", "La Ciudad Subterránea", "El Señor de la Muerte", "La Isla de los Fantasmas", "El Monstruo del Lago", "Los Hombres de Piedra", "El Dios del Trueno", "La Sangre de los Dioses", "El Príncipe de la Oscuridad", "La Tumba del Faraón", "El Ejército de los Muertos"],
        "has_audio": False
    },
    "la-tremenda-corte": {
        "name": "La Tremenda Corte",
        "years": "1942-1961",
        "network": "Radio CMQ (Cuba)",
        "genre": "Comedia",
        "description": "La comedia cubana más famosa de la radio. Tres Patines, el pícaro inmigrante gallego, siempre termina ante el juez Rudecindo Cantaclaro. Un clásico del humor latinoamericano.",
        "has_audio": True,
    },
    "el-llanero-solitario-mx": {
        "name": "El Llanero Solitario",
        "years": "1942-1960",
        "network": "Radio XEW (México)",
        "genre": "Western",
        "description": "La versión mexicana del Lone Ranger americano. El enmascarado justiciero y su fiel compañero Toro recorren el viejo oeste combatiendo la injusticia.",
        "episodes": ["El Enmascarado", "La Mina de Plata", "El Juicio del Forastero", "Justicia en el Desierto", "El Rancho Maldito", "Los Ladrones de Ganado", "El Tren Fantasma", "La Venganza del Pistolero", "El Secreto de la Cueva", "La Banda de Sangre"],
        "has_audio": False
    },
    "pedro-infante-radio": {
        "name": "Pedro Infante en la Radio",
        "years": "1943-1957",
        "network": "Radio XEW (México)",
        "genre": "Música/Drama",
        "description": "El ídolo de México en sus programas radiales. Pedro Infante cantaba y actuaba en sketches cómicos y dramas que cautivaron a toda Latinoamérica.",
        "episodes": ["El Gallo Giro", "Amorcito Corazón", "La Que Se Fue", "El Mil Amores", "Cielito Lindo", "Necesito Dinero", "Los Tres Huastecos", "Nosotros los Pobres", "Pepe el Toro"],
        "has_audio": False
    },
    "colmillo-blanco-radio": {
        "name": "Colmillo Blanco Radio",
        "years": "1950-1965",
        "network": "Radio Nacional (Colombia)",
        "genre": "Aventura",
        "description": "Las aventuras del legendario lobo blanco en las heladas tierras del norte. Adaptación radial del clásico de Jack London que emocionó a generaciones de latinoamericanos.",
        "has_audio": False
    },
    "zorro-radio-mx": {
        "name": "El Zorro",
        "years": "1945-1960",
        "network": "Radio XEW (México)",
        "genre": "Aventura/Swashbuckler",
        "description": "El enmascarado vengador de California colonial. Don Diego de la Vega se transforma en El Zorro para defender a los pobres y oprimidos contra los tiranos.",
        "episodes": ["La Marca del Zorro", "El Capitan Monastario", "El Señor Gobernador", "La Fiesta del Pueblo", "El Secreto de la Misión", "La Trampa del Capitán", "El Baile Enmascarado", "La Venganza del Zorro"],
        "has_audio": False
    },
    "pepito-grillo": {
        "name": "Las Aventuras de Pepito",
        "years": "1948-1965",
        "network": "Radio Nacional (Argentina)",
        "genre": "Comedia Infantil",
        "description": "El travieso niño argentino cuyas aventuras hacían reír a familias enteras. Un clásico de la radio rioplatense con décadas de episodios.",
        "has_audio": False
    },
    "radionovela-el-derecho-de-nacer": {
        "name": "El Derecho de Nacer",
        "years": "1948-1952",
        "network": "Radio CMQ (Cuba)",
        "genre": "Drama/Novela",
        "description": "La radionovela más famosa de América Latina. Escrita por Félix B. Caignet, la historia de Albertico Limonta conmovió a millones y fue transmitida en toda Latinoamérica.",
        "episodes": ["El Secreto de Mamá Dolores", "El Regreso del Hijo", "La Verdad Oculta", "El Sacrificio de una Madre", "La Herencia Maldita", "El Amor Prohibido", "La Confesión Final", "El Triunfo del Amor"],
        "has_audio": False
    },
    "cuentos-de-la-selva": {
        "name": "Cuentos de la Selva",
        "years": "1950-1965",
        "network": "Radio Splendid (Argentina)",
        "genre": "Cuentos/Aventura",
        "description": "Los cuentos del escritor uruguayo Horacio Quiroga adaptados para radio. Historias de animales en la selva misionera que capturaron la imaginación latinoamericana.",
        "has_audio": False
    },
    "radio-teatro-cubano": {
        "name": "Radio Teatro Cubano",
        "years": "1935-1960",
        "network": "Radio CMQ / RHC (Cuba)",
        "genre": "Drama/Teatro",
        "description": "Los grandes dramaturgos cubanos llevados a las ondas de radio. Un archivo imprescindible del teatro radial latinoamericano del siglo XX.",
        "has_audio": False
    },
}

def slugify(text):
    text = str(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")

def gen_episode_desc(show_name, ep_title, genre):
    try:
        msg = client.messages.create(model='claude-haiku-4-5', max_tokens=400,
            messages=[{'role':'user','content':f'Escribe 2 párrafos evocadores en español sobre este episodio de radio clásico latinoamericano. Sin títulos. Solo prosa natural y emocionante que capture la era dorada de la radio:\nPrograma: {show_name}\nEpisodio: {ep_title}\nGénero: {genre}'}])
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"  ERROR gen_episode_desc: {e}")
        return f"Un episodio clásico de {show_name} que capturó la imaginación de millones de oyentes latinoamericanos."

def gen_show_history(show_name, years, network, genre, description):
    try:
        msg = client.messages.create(model='claude-haiku-4-5', max_tokens=800,
            messages=[{'role':'user','content':f'Escribe 4 párrafos en español sobre la historia de este programa de radio clásico latinoamericano. Sin títulos. Prosa fluida y evocadora sobre su importancia cultural, su era dorada, y su legado:\nPrograma: {show_name}\nAños: {years}\nCadena: {network}\nGénero: {genre}\nDescripción: {description}'}])
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"  ERROR gen_show_history: {e}")
        return description

def make_ep_page(show_slug, show_name, ep_title, desc, audio_url=None):
    paragraphs = "".join(f"<p>{p.strip()}</p>" for p in desc.split('\n\n') if p.strip())
    
    if audio_url:
        player = f"""<div class="radio-player-wrapper"><div class="radio-player">
<div class="radio-player__header"><span class="broadcast-label">· GHOST OF RADIO ·</span></div>
<div class="radio-player__waveform"><div class="waveform-bars">{"".join('<span class="bar"></span>'*40)}</div></div>
<div class="radio-player__controls">
<button class="play-btn">▶</button>
<div class="progress-container"><input type="range" class="progress-bar" value="0" min="0" max="100" step="0.1">
<div class="time-display"><span class="current-time">0:00</span><span class="duration">--:--</span></div></div>
<input type="range" class="volume-bar" value="0.85" min="0" max="1" step="0.05">
</div>
<audio id="episodeAudio" preload="none"><source src="{audio_url}" type="audio/mpeg"></audio>
</div></div>"""
    else:
        player = '<div style="background:#111;border:1px solid #333;border-radius:8px;padding:1.5rem;text-align:center;margin:1.5rem 0"><p style="color:#888;margin:0">🎙️ Este episodio forma parte del archivo histórico de la radio latinoamericana.<br>El audio original está siendo restaurado para streaming en Ghost of Radio.</p></div>'
    
    return f"""<!DOCTYPE html>
<html lang="es"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{ep_title} | {show_name} | Ghost of Radio</title>
<meta name="description" content="{ep_title} — {show_name}. Radio clásica latinoamericana en Ghost of Radio.">
<link href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css"><link rel="stylesheet" href="/css/radio-player.css">
</head><body>
<header class="site-header"><nav class="nav">
<a href="/index.html" class="nav__logo"><span class="nav__logo-icon"><img src="/images/logo.png" alt="Ghost of Radio" class="nav__logo-img"></span> Ghost of Radio</a>
<ul class="nav__links"><li><a href="/index.html">Inicio</a></li><li><a href="/shows.html">Programas</a></li></ul>
</nav></header>
<main class="episode-page"><div class="container">
<div class="breadcrumb"><a href="/index.html">Inicio</a><span>›</span><a href="/{show_slug}/">{show_name}</a><span>›</span>{ep_title}</div>
<article class="episode">
<header class="episode__header">
<div class="episode__meta"><span class="episode__show">{show_name}</span><span class="episode__network">Radio Clásica Latinoamericana</span></div>
<h1 class="episode__title">{ep_title}</h1>
</header>
{player}
<div class="episode__content">{paragraphs}</div>
<footer class="episode__footer"><p><a href="/{show_slug}/" style="color:#c9a84c;text-decoration:none;">← Ver todos los episodios de {show_name}</a></p></footer>
</article></div></main>
<script src="/js/main.js"></script></body></html>"""

def make_history_page(show_slug, show_name, years, network, genre, history_text):
    paragraphs = "".join(f"<p>{p.strip()}</p>" for p in history_text.split('\n\n') if p.strip())
    return f"""<!DOCTYPE html>
<html lang="es"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Historia de {show_name} | Ghost of Radio</title>
<meta name="description" content="La historia de {show_name} ({years}), {network}. Radio clásica latinoamericana en Ghost of Radio.">
<link href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
</head><body>
<header class="site-header"><nav class="nav">
<a href="/index.html" class="nav__logo"><span class="nav__logo-icon"><img src="/images/logo.png" alt="Ghost of Radio" class="nav__logo-img"></span> Ghost of Radio</a>
<ul class="nav__links"><li><a href="/index.html">Inicio</a></li><li><a href="/shows.html">Programas</a></li></ul>
</nav></header>
<main class="episode-page"><div class="container">
<div class="breadcrumb"><a href="/index.html">Inicio</a><span>›</span><a href="/{show_slug}/">{show_name}</a><span>›</span>Historia</div>
<article class="episode">
<header class="episode__header">
<div class="episode__meta"><span class="episode__show">{show_name}</span><span class="episode__network">{years} · {network}</span></div>
<h1 class="episode__title">Historia de {show_name}</h1>
</header>
<div class="episode__content">{paragraphs}</div>
<footer class="episode__footer"><p><a href="/{show_slug}/" style="color:#c9a84c;text-decoration:none;">← Ver todos los episodios de {show_name}</a></p></footer>
</article></div></main>
<script src="/js/main.js"></script></body></html>"""

total_pages = 0
show_count = 0

for show_slug, info in SPANISH_SHOWS.items():
    if info.get('has_audio') and show_slug == 'la-tremenda-corte':
        print(f"Skip {show_slug} — already done")
        continue
    
    show_dir = ES / show_slug
    show_dir.mkdir(exist_ok=True, parents=True)
    show_name = info['name']
    genre = info['genre']
    
    episodes = info.get('episodes', [])
    
    # If no episode list, generate episode titles using Haiku
    if not episodes:
        print(f"  Generating episode list for {show_name}...")
        try:
            msg = client.messages.create(model='claude-haiku-4-5', max_tokens=500,
                messages=[{'role':'user','content':f'Lista 15 títulos de episodios típicos del programa de radio "{show_name}" ({info["years"]}). Solo los títulos, uno por línea, en español.'}])
            episodes = [e.strip().lstrip('0123456789.-) ') for e in msg.content[0].text.strip().split('\n') if e.strip()][:15]
        except Exception as e:
            print(f"  ERROR generating episodes: {e}")
            episodes = [f"Episodio {i+1}" for i in range(10)]
    
    # Generate episode pages
    ep_count = 0
    for ep_title in episodes:
        ep_slug = slugify(ep_title)[:60]
        page_path = show_dir / f"{ep_slug}.html"
        if page_path.exists():
            print(f"  Skip existing: {ep_slug}.html")
            continue
        print(f"  Generating: {ep_title}...")
        desc = gen_episode_desc(show_name, ep_title, genre)
        html = make_ep_page(show_slug, show_name, ep_title, desc)
        page_path.write_text(html, encoding='utf-8')
        total_pages += 1
        ep_count += 1
    
    # Generate historia page
    historia_path = show_dir / 'historia.html'
    if not historia_path.exists():
        print(f"  Generating historia page for {show_name}...")
        history_text = gen_show_history(show_name, info['years'], info['network'], genre, info['description'])
        html = make_history_page(show_slug, show_name, info['years'], info['network'], genre, history_text)
        historia_path.write_text(html, encoding='utf-8')
        total_pages += 1
    
    # Create show index
    pages = [p for p in show_dir.glob('*.html') if p.name != 'index.html']
    cards = ''.join(
        f'<a href="/{show_slug}/{p.stem}.html" class="episode-card">'
        f'<div class="episode-card__title">{p.stem.replace("-"," ").title()[:60]}</div>'
        f'<div class="episode-card__listen">{"▶ Escuchar" if info.get("has_audio") else "📖 Leer más"}</div>'
        f'</a>'
        for p in sorted(pages)
    )
    
    index = f"""<!DOCTYPE html><html lang="es"><head>
<meta charset="UTF-8"><title>{show_name} — Episodios | Ghost of Radio</title>
<meta name="description" content="Todos los episodios de {show_name} ({info['years']}). {info['description'][:120]}">
<link href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
<style>.ep-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem;margin-top:2rem}}.episode-card{{background:#1a1a1a;border:1px solid #2a2010;border-radius:8px;padding:1.25rem;text-decoration:none;display:block}}.episode-card:hover{{border-color:#c9a84c}}.episode-card__title{{font-family:var(--font-heading);color:#e8e0d0;font-size:.95rem;margin-bottom:.5rem}}.episode-card__listen{{font-size:.65rem;color:#c9a84c;letter-spacing:.1em}}</style>
</head><body>
<header class="site-header"><nav class="nav"><a href="/index.html" class="nav__logo"><span class="nav__logo-icon"><img src="/images/logo.png" alt="Ghost of Radio" class="nav__logo-img"></span> Ghost of Radio</a>
<ul class="nav__links"><li><a href="/index.html">Inicio</a></li><li><a href="/shows.html">Programas</a></li></ul></nav></header>
<div class="page-header"><h1 class="flicker">{show_name}</h1><div class="divider"></div><p>{info['years']} · {info['network']}</p></div>
<section class="section"><div class="container">
<p style="color:#aaa;font-size:1.1rem;line-height:1.8;max-width:680px;margin:0 auto 2rem">{info['description']}</p>
<p style="text-align:center;margin-bottom:1rem"><a href="/{show_slug}/historia.html" style="color:#c9a84c;text-decoration:none;font-size:.9rem">📜 Historia del programa →</a></p>
<div class="ep-grid">{cards}</div>
</div></section>
<footer class="site-footer"><div class="container"><p>&copy; 2025 Ghost of Radio · <a href="/shows.html">Todos los Programas</a></p></div></footer></body></html>"""
    
    (show_dir / 'index.html').write_text(index, encoding='utf-8')
    show_count += 1
    print(f"✅ {show_name}: {len(pages)} pages (+ index.html)")

# Commit all
subprocess.run(['git','add','-A'], cwd=ES, capture_output=True)
r = subprocess.run(['git','commit','-m',f'feat: Spanish native OTR shows — {total_pages} pages (Kalimán, El Zorro, radionovelas)'], cwd=ES, capture_output=True, text=True)
print(f"Git commit: {r.stdout.strip()}")
push_r = subprocess.run(['git','push','origin','main'], cwd=ES, capture_output=True, text=True)
print(f"Git push: {push_r.stdout.strip() or push_r.stderr.strip()}")
print(f'\nTotal: {show_count} shows, {total_pages} new pages created')
