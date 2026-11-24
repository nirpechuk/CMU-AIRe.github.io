#!/usr/bin/env python3
"""Builds the AIRe Lab website.

Everything you are likely to edit is in this folder:
  - this file: people, news, the blog switch, page text;
  - papers/<year>.json: the publication list, one file per year;
  - content/: blog post text (the blog is currently archived);
  - manifest.json: which figure each paper shows (images live in ../media/papers/).

Run from anywhere:  python3 site-src/build.py
It writes the pages (index.html, people.html, ...) to the repository root, which
GitHub Pages serves as https://cmu-aire.github.io/. Commit the result.
"""
import html
import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent  # site-src/: the sources
OUT = HERE.parent                         # the repository root: what the website serves
META = HERE / "papers"

# ---------------------------------------------------------------- people

# Lab members, in the order shown: (group, name, role, research interests, homepage, photo).
# A photo is a file in media/; until it exists the person gets a plain tile.
MEMBERS = [
    ("Faculty", "Aviral Kumar", "Assistant Professor, Computer Science and Machine Learning", "",
     "https://aviralkumar2907.github.io/", "aviral.jpg"),
    ("PhD students", "Bhavya Agrawalla", "PhD in Computer Science",
     "Reinforcement learning algorithms with stronger predictive capabilities and theoretical guarantees.",
     "https://agrawallabhavya.github.io/", "bhavya.jpg"),
    ("PhD students", "Apurva Gandhi", "PhD in Computer Science",
     "Reinforcement learning, agents and multi-agent systems, LLMs and inference-time scaling.",
     "https://apga.github.io/", "people/apurva-gandhi.jpg"),
    ("PhD students", "Zheyuan Hu", "PhD in Robotics", "Scaling robot foundation models.",
     "https://huzheyuan.io/", "zheyuan.jpg"),
    ("PhD students", "Nathan S. de Lara", "PhD in Machine Learning", "Off-policy learning.",
     "https://delara38.github.io/", "people/nathan-s-de-lara.jpg"),
    ("PhD students", "Max Sobol Mark", "PhD in Computer Science", "Reinforcement learning with and for pre-trained policies and large datasets.",
     "https://maxsobolmark.com/", "max.jpg"),
    ("PhD students", "Yuxiao Qu", "PhD in Machine Learning", "The intersection of reinforcement learning and foundation models.",
     "https://cohenqu.github.io/", "people/yuxiao-qu.jpg"),
    ("PhD students", "Ian Wu", "PhD in Machine Learning", "Making LLMs smarter and better at learning.",
     "https://ianyhwu.github.io/", "people/ian-wu.jpg"),
    ("PhD students", "Lehong Wu", "PhD in Machine Learning", "Robot foundation models and reinforcement learning.",
     "https://lehongwu.github.io/", "people/lehong-wu.jpg"),
    ("Master's and undergraduate students", "Shashwat Chandra", "MS in Machine Learning",
     "Reinforcement learning on open-ended tasks, post-training and interpretability.",
     "https://shashwatchandra.com/", "people/shashwat-chandra.jpg"),
    ("Master's and undergraduate students", "Saksham Singh", "MS in Machine Learning",
     "Autonomous RL in the real world for long-horizon manipulation tasks, and pre-training recipes for generalist robot policies.",
     "https://github.com/saksham002", "people/saksham-singh.jpg"),
    ("Master's and undergraduate students", "Khush Agrawal", "MS in Robotics", "Machine learning and robotics.",
     "https://khush3.github.io/", "khush.jpg"),
    ("Master's and undergraduate students", "Kshitiz", "MS in Robotics",
     "Reinforcement learning, robotic manipulation and autonomous self-improvement.",
     "https://kshitiz-1225.github.io/", "people/kshitiz.jpg"),
    ("Master's and undergraduate students", "Sreyas Venkataraman", "MS in Robotics",
     "Exploration, new architectures and training foundation models.",
     "https://vsreyas.github.io/", "people/sreyas-venkataraman.jpg"),
    ("Master's and undergraduate students", "Philip Han", "Undergraduate researcher", "Robot learning and machine learning.",
     "https://yangphiliphan.com/", "people/philip-han.jpg"),
    ("Master's and undergraduate students", "Jojo Li", "Undergraduate researcher", "Robot learning for long-horizon manipulation tasks.",
     "https://www.linkedin.com/in/jojoli0430/", "people/jojo-li.jpg"),
    ("Master's and undergraduate students", "Nir Pechuk", "BS in Computer Science",
     "Generalizing, data-efficient and exploratory reinforcement learning, especially in robotics.",
     "https://nirpechuk.github.io/", "people/nir-pechuk.jpg"),
    ("Master's and undergraduate students", "Robyn Wu", "Undergraduate researcher", "Robot learning.",
     "https://www.linkedin.com/in/robynwuprofile/", "people/robyn-wu.jpg"),
    ("Master's and undergraduate students", "Gene Yang", "Undergraduate researcher", "How models can do research.",
     "https://3n3g.github.io/", "people/gene-yang.jpg"),
    ("Master's and undergraduate students", "Jeff Yu", "BS in Computer Science", "Teaching robots to do cool tasks.",
     "https://github.com/A-Speedy-Giraffe", "people/jeff-yu.jpg"),
    ("Master's and undergraduate students", "Ivan Zhang", "BS in Computer Science",
     "Natural language and simulation-based methods for robot manipulation.",
     "https://enspikondplusplus.github.io/", "people/ivan-zhang.jpg"),
    ("Affiliated researchers", "Vansh Kapoor", "Research assistant",
     "Principled algorithms for RL and generative modeling, with applications to foundation model reasoning, post-training and robotics.",
     "https://vansh28kapoor.github.io/", "people/vansh-kapoor.jpg"),
    ("Affiliated researchers", "Taeyoun Kim", "PhD at NYU",
     "Using RL to understand model capability and complexity, and to optimize model training.",
     "https://danielkty.github.io/", "people/taeyoun-kim.jpg"),
    ("Affiliated researchers", "Qixin Xu", "Visiting researcher", "Continual learning and agentic RL.",
     "https://scholar.google.com/citations?user=AvbV0HcAAAAJ", "people/qixin-xu.jpg"),
    ("Alumni", "Hao Bai", "PhD at UIUC", "",
     "https://biechi.github.io/", "people/hao-bai.jpg"),
    ("Alumni", "Matthew Y.R. Yang", "PhD at MIT", "",
     "https://www.matthewyryang.com/", "matthew.jpg"),
]

# Other spellings of members' names used in paper author lists, so their papers link to them.
MEMBER_SPELLINGS = {
    "Matthew Y. R. Yang": "Matthew Y.R. Yang",
    "Jeffrey Yu": "Jeff Yu",
    "Jasmine Li": "Jojo Li",
}

COLLABORATORS = [  # (name, affiliation, homepage, other spellings used in author lists)
    ("Amrith Setlur", "PhD student at CMU", "https://scholar.google.com/citations?user=i7V1kJgAAAAJ&hl=en", []),
    ("Mitsuhiko Nakamoto", "PhD student at UC Berkeley", "https://nakamotoo.github.io/", []),
    ("Yifei Zhou", "PhD student at UC Berkeley", "https://yifeizhou02.github.io/", []),
    ("Fahim Tajwar", "PhD student at CMU", "https://tajwarfahim.github.io/", []),
    ("Anikait Singh", "PhD student at Stanford", "https://asap7772.github.io/", []),
    ("Seohong Park", "PhD student at UC Berkeley", "https://seohong.me/", []),
    ("Lunjun Zhang", "PhD student at University of Toronto", "https://lunjunzhang.github.io/", []),
    ("Katie Kang", "PhD student at UC Berkeley", "http://katiekang.com/", []),
    ("Oleh Rybkin", "Postdoctoral scholar at UC Berkeley", "https://people.eecs.berkeley.edu/~oleh/", []),
    ("Paul Zhou", "PhD student at UC Berkeley", "https://zhouzypaul.github.io/", ["Zhiyuan Zhou"]),
    ("Xinyang (Young) Geng", "Research Scientist at Google DeepMind", "https://young-geng.xyz/", ["Xinyang Geng"]),
    ("Rishabh Agarwal", "Research Scientist at Google DeepMind", "https://agarwl.github.io/", []),
    ("William Chen", "PhD student at UC Berkeley", "https://verityw.github.io/", []),
]

# The live Q-learning gridworld on the home page, shown under the news when enabled. Hidden for now; gridworld.js is kept.
SHOW_GRIDWORLD = False


def is_preprint(paper):
    """Not yet published at a venue: still only on arXiv or bioRxiv."""
    return paper["venue"].split(" ")[0].lower() in ("arxiv", "biorxiv")

# Teaser shown when a paper is opened on the home page: (kind, file, width, height, description[, poster]).
MEDIA = {
    "ideataste": ("image", "ideataste.jpg", 1000, 249, "How human and AI scientists cite prior work and propose new papers"),
    "librarian_agents": ("image", "librarian_agents.jpg", 1000, 335, "An agent building a workspace from a corpus, then searching it to answer a query"),
    "magicbeanstalk": ("image", "magicbeanstalk.jpg", 1000, 416, "Problem difficulty across training data, showing a band of useful difficulty"),
    "seeq": ("image", "seeq.jpg", 1000, 400, "Pretraining a generalist value function and using it to steer a robot policy"),
    "r3_robot_reasoning": ("image", "r3_robot_reasoning.jpg", 1000, 667, "Two-stage training of a robot policy that reasons in language"),
    "generalist_adaptation_minimal_data": ("image", "generalist_adaptation_minimal_data.jpg", 1000, 400, "Adapting a pretrained robot policy from one demonstration with residual RL"),
    "mirror": ("image", "mirror.jpg", 1000, 470, "The same problem given as an image, as text, or both, with a teacher chosen per problem"),
    "digirl": ("video", "digirl.mp4", 800, 440, "An agent operating an Android phone while its success rate rises", "digirl.jpg"),
    "steering_generalists": ("video", "vgps.mp4", 800, 396, "A robot arm choosing between proposed actions using a value function", "vgps.jpg"),
    "llmcognition@icml": ("image", "rise.jpg", 1000, 563, "A language model improving its answer over several turns"),
    "stop_regressing": ("image", "stop.png", 640, 534, "A scalar target spread over neighbouring bins as a Gaussian histogram"),
    "parl": ("image", "parl.jpg", 1000, 445, "Actions from a base policy filtered and refined using Q-values"),
    "efficient_rl_finetune": ("image", "wsrl.jpg", 941, 431, "Return over time when fine-tuning online without the offline data"),
    "rewarding_progress": ("image", "prm.jpg", 1000, 283, "Search over reasoning steps guided by a process verifier"),
    "value_learning_bottleneck": ("image", "offrl.jpg", 1000, 654, "Actions chosen by two policy extraction methods"),
}

SITE = "https://cmu-aire.github.io/"
CONTACT = "aviralku@andrew.cmu.edu"

# The blog is archived: its posts and code are kept, but no pages, feed, menu item or links
# are built while this is False. Set it to True to bring the blog back.
SHOW_BLOG = False

# Blog posts: (file name, title, author, ISO date, shown date, summary, content file)
POSTS = [
    ("blog-rl-perspectives-2024.html", "Some Perspectives on Reinforcement Learning Research", "Aviral Kumar",
     "2025-01-01", "January 2025",
     "The guiding principles behind our research, and a summary of our work in 2024 on deep RL algorithms "
     "and RL for foundation models.", "rl-perspectives-2024.html"),
]

NEWS = [
    ("2024-11", "Nov 2024", "Aviral was named one of five Samsung AI Researchers of the Year."),
    ("2024-11", "Nov 2024", "Aviral received the AI2050 Early Career Fellowship from Schmidt Sciences."),
]


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


esc = html.escape

PERSON_ID = {}  # every spelling of a name -> that person's id
for _, name, *_ in MEMBERS:
    PERSON_ID[name] = slug(name)


def member_photo(file):
    """The photo's path under media/, or None while it has not been added yet."""
    return file if file and (OUT / "media" / file).exists() else None
for spelling, name in MEMBER_SPELLINGS.items():
    PERSON_ID[spelling] = slug(name)
for name, _, _, other in COLLABORATORS:
    for spelling in [name, *other]:
        PERSON_ID[spelling] = slug(name)

# ---------------------------------------------------------------- papers


def short_venue(text):
    """'International Conference on Machine Learning (ICML), 2024' -> ('ICML 2024', '')"""
    head, _, note = text.partition(";")
    match = re.search(r"\((\w+)\),?\s*(\d{4})", head)
    return (f"{match.group(1)} {match.group(2)}" if match else head.strip()), note.strip()


def load_papers():
    papers = []
    for path in sorted(META.glob("*.json")):
        for key, p in json.loads(path.read_text()).items():
            venue, note = short_venue(p.get("conference", ""))
            links = [(label, p.get(field)) for label, field in
                     [("Paper", "arxiv"), ("Code", "code"), ("Project page", "website"), ("Video", "video")]]
            papers.append({
                "key": key,
                "id": slug(key),
                "title": p["title"],
                "authors": p["authors"],
                "people": [PERSON_ID[a] for a in p["authors"] if a in PERSON_ID],
                "venue": venue,
                "note": note,
                "when": datetime.strptime(p["date"], "%B %Y"),
                "links": [(label, url) for label, url in links if url],
            })
    return sorted(papers, key=lambda p: p["when"], reverse=True)


PAPERS = load_papers()

# ---------------------------------------------------------------- shared page parts

MARK = '<img src="media/logo.png" alt="" width="24" height="24">'  # the lab logo (images/logo.png, scaled down)

NAV = [("Publications", "publications.html"), ("People", "people.html")] + \
    ([("Blog", "blog.html")] if SHOW_BLOG else []) + [("Join", "join.html")]


def page(filename, title, description, body, scripts, site_header=True, current=None, kind="website", data=None):
    """A full page. `current` is the menu item to mark (defaults to this file); `data` is structured data for search engines."""
    current = current or filename
    url = SITE + ("" if filename == "index.html" else filename)
    nav = "\n      ".join(
        (f'<li><a href="{href}" aria-current="page">{label}<span class="nav-mark" aria-hidden="true"></span></a></li>'
         if href == current else f'<li><a href="{href}">{label}</a></li>')
        for label, href in NAV)
    ld = f'\n<script type="application/ld+json">\n{json.dumps(data, indent=1, ensure_ascii=False)}\n</script>' if data else ""
    tags = "\n".join(f'<script src="{src}"></script>' for src in scripts)
    header = f"""<header class="wrap top">
  <a class="brand" href="index.html" aria-label="AIRe Lab home">
    {MARK}
    AIRe Lab
  </a>
  <nav aria-label="Main">
    <ul>
      {nav}
    </ul>
  </nav>
</header>

"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="favicon.png" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
{'<link rel="alternate" type="application/rss+xml" title="AIRe Lab blog" href="feed.xml">' + chr(10) if SHOW_BLOG else ""}<meta property="og:type" content="{kind}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="AIRe Lab">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{SITE}media/group.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">{ld}
</head>
<body{' class="home-page"' if not site_header else ''}>

{header if site_header else ""}{body}

<footer class="wrap">
  <span>AIRe Lab, School of Computer Science, Carnegie Mellon University</span>
  <ul>
    <li><a href="mailto:{CONTACT}">Contact</a></li>
    <li><a href="https://github.com/CMU-AIRe">GitHub</a></li>
{'    <li><a href="feed.xml">Blog feed</a></li>' + chr(10) if SHOW_BLOG else ""}  </ul>
</footer>

{tags}
</body>
</html>
"""


# ---------------------------------------------------------------- home

MANIFEST_PATH = HERE / "manifest.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {"papers": {}, "people": {}}


def media_for(paper):
    """(kind, file, width, height, alt[, poster]) for a paper's figure, or None."""
    media = MEDIA.get(paper["key"])
    found = MANIFEST["papers"].get(paper["key"])
    if not media and found:
        media = ("image", found["file"], found["width"], found["height"], found.get("alt", ""))
    return media


def preview(paper):
    media = media_for(paper)
    if not media:
        return ""
    kind, file, width, height, alt = media[:5]
    if kind == "video":
        tag = (f'<video src="media/{file}" poster="media/{media[5]}" width="{width}" height="{height}" '
               f'muted loop playsinline preload="none" aria-label="{esc(alt)}"></video>')
    else:
        tag = f'<img src="media/{file}" width="{width}" height="{height}" alt="{esc(alt)}" loading="lazy">'
    return f'<div class="preview">{tag}</div>'


def venue_html(venue):
    """Venue with any distinction (Oral, Spotlight, an award) set apart so it can be highlighted."""
    m = re.match(r"(.*?)\s*\(((?:Oral|Spotlight|Outstanding|Best)[^)]*)\)\s*$", venue)
    if not m:
        return esc(venue)
    return f'{esc(m.group(1))} <span class="award">{esc(m.group(2))}</span>'


def title_html(title):
    """The short name before a colon is set heavier; a title without one is set heavier throughout."""
    head, colon, rest = title.partition(":")
    if colon and len(head) <= 40:
        return f"<strong>{esc(head)}</strong>:{esc(rest)}"
    return f'<strong class="whole">{esc(title)}</strong>'



def home_paper(p):
    """A row in the home page list. Selecting it opens a larger preview with the links."""
    links = "".join(f'<a href="{esc(url)}">{label}</a>' for label, url in p["links"])
    return f"""        <li data-paper="{p["id"]}" data-kind="{"preprints" if is_preprint(p) else "published"}" data-authors="{" ".join(p["people"])}">
          <a class="row" href="publications.html#{p["id"]}" aria-expanded="false" aria-controls="about-{p["id"]}"><span class="title">{title_html(p["title"])}</span><span class="venue">{venue_html(p["venue"])}</span></a>
          <div class="detail" id="about-{p["id"]}" inert><div>
            {preview(p)}
            <p class="authors">{esc(", ".join(p["authors"]))}</p>
            <div class="meta">{links}</div>
          </div></div>
        </li>"""


def person_photo(pid, photo=None):
    found = photo or (MANIFEST["people"].get(pid) or {}).get("file")
    if found:
        return f'<img src="media/{found}" alt="" width="40" height="40" loading="lazy">'
    return '<span class="blank" aria-hidden="true"></span>'


def home():
    papers = "\n".join(home_paper(p) for p in PAPERS)
    world = """
    <figure class="world" data-gridworld>
      <svg role="img" aria-label="An agent learning the shortest route through a small maze by Q-learning"></svg>
    </figure>""" if SHOW_GRIDWORLD else ""

    roster, group = [], None
    for g, name, _, _, _, photo in MEMBERS:
        if g != group:
            if group is not None:
                roster.append("        </div>")
            roster.append(f'        <div class="group"><h3>{esc(g)}</h3>')
            group = g
        roster.append(
            f'        <a class="person" href="people.html#{slug(name)}" data-person="{slug(name)}">'
            f'{person_photo(slug(name), member_photo(photo))}<span>{esc(name)}</span></a>')
    roster.append('        </div>\n        <div class="group"><h3>Collaborators</h3>')
    for name, *_ in COLLABORATORS:
        pid = slug(name)
        roster.append(f'        <a class="person" href="people.html#{pid}" data-person="{pid}">{person_photo(pid)}<span>{esc(name)}</span></a>')
    roster.append("        </div>")

    news = "\n".join(f'        <li><time datetime="{iso}">{label}</time><span>{text}</span></li>'
                     for iso, label, text in NEWS)

    body = f"""<main class="wrap home" data-home>
  <div class="fold">
  <div class="top-band">
    <section class="intro" aria-labelledby="lab-name">
      <h1 id="lab-name">AIRe Lab @ CMU</h1>
      <p class="full-name">CMU Artificial Intelligence and Reinforcement Learning Lab</p>
      <p class="lede">We develop machines that act intelligently and autonomously in open-world scenarios, building reinforcement learning and sequential decision-making algorithms for AI systems in the intersection of language, robotics, software agents, science and engineering, and more.</p>
      <h2 class="col-head">News</h2>
      <ul class="news">
{news}
      </ul>{world}
    </section>
    <div class="photo-frame"><img class="group-photo" src="media/group.jpg" width="1200" height="900" alt="Members of the AIRe Lab around a long table at a group dinner"></div>
  </div>

  <section class="swarm" data-band data-band-plain aria-label="A swarm of dots learning its way through a maze"></section>
  <div class="fold-actions">
    <a class="jump" href="#work">Check out our work<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3v9M3.5 7.5 8 12l4.5-4.5"/></svg></a>
    <button class="round-toggle" type="button" data-band-pause></button>
  </div>
  </div>
  <div class="lists" id="work">
    <section class="col people" aria-labelledby="people-head">
      <h2 class="col-head" id="people-head"><a href="people.html">People</a></h2>
      <div class="scroll">
        <div class="roster">
{chr(10).join(roster)}
        </div>
      </div>
    </section>

    <section class="col" aria-label="Papers">
      <div class="col-head">
        <div class="tabs" role="group" aria-label="Show">
          <button type="button" data-show="published" aria-pressed="true">Publications</button>
          <button type="button" data-show="preprints" aria-pressed="false">Preprints</button>
        </div>
        <a class="all" href="publications.html">All papers</a>
      </div>
      <div class="scroll">
        <ol class="papers">
{papers}
        </ol>
      </div>
    </section>
  </div>
</main>"""
    return page("index.html", "AIRe Lab",
                "The AIRe Lab at Carnegie Mellon University, led by Aviral Kumar, builds reinforcement learning "
                "and decision-making methods for language models, robots and software agents.",
                body, (["gridworld.js"] if SHOW_GRIDWORLD else []) + ["swarm.js", "home.js"], data=lab_data())


# ---------------------------------------------------------------- publications

def thumbnail(paper):
    """The paper's figure in a fixed frame; a quiet tile with its short name if there is no figure."""
    media = media_for(paper)
    if media:
        kind, file, width, height, alt = media[:5]
        file = media[5] if kind == "video" else file  # use the video's still frame here
        return f'<div class="thumb"><img src="media/{file}" alt="{esc(alt)}" loading="lazy"></div>'
    name = paper["title"].split(":")[0] if ":" in paper["title"][:40] else ""
    return f'<div class="thumb empty" aria-hidden="true"><span>{esc(name)}</span></div>'


def publications():
    blocks, year = [], None
    for p in PAPERS:
        if p["when"].year != year:
            if year is not None:
                blocks.append("  </ol>")
            year = p["when"].year
            blocks.append(f"  <h2>{year}</h2>\n  <ol class=\"pubs\">")
        target = next((url for label, url in p["links"] if label == "Project page"), None) or \
            next((url for _, url in p["links"]), None)
        title = f'<a href="{esc(target)}">{esc(p["title"])}</a>' if target else esc(p["title"])
        meta = [f"<span>{venue_html(p['venue'])}</span>"] + ([f"<span>{esc(p['note'])}</span>"] if p["note"] else []) + \
               [f'<a href="{esc(url)}">{label}</a>' for label, url in p["links"]]
        blocks.append(
            f'    <li id="{p["id"]}">\n'
            f'      {thumbnail(p)}\n'
            f'      <div>\n'
            f'        <h3>{title}</h3>\n'
            f'        <p class="authors">{esc(", ".join(p["authors"]))}</p>\n'
            f'        <div class="meta">{"".join(meta)}</div>\n'
            f'      </div>\n'
            f'    </li>')
    blocks.append("  </ol>")
    body = f"""<main class="wrap page">
  <h1>Publications</h1>
{chr(10).join(blocks)}
</main>"""
    return page("publications.html", "AIRe Publications",
                "Papers from the AIRe Lab at Carnegie Mellon University on reinforcement learning, "
                "language model agents and robot learning.", body, [], data={
                    "@context": "https://schema.org", "@type": "CollectionPage", "name": "AIRe Lab publications",
                    "url": SITE + "publications.html", "hasPart": [scholarly(p) for p in PAPERS]})


# ---------------------------------------------------------------- people

def papers_of(pid):
    return [p for p in PAPERS if pid in p["people"]]


def people():
    blocks, group = [], None
    for g, name, role, note, url, photo in MEMBERS:
        if g != group:
            if group is not None:
                blocks.append("  </ul>")
            blocks.append(f"  <h2>{esc(g)}</h2>\n  <ul class=\"members\">")
            group = g
        pid = slug(name)
        blocks.append(
            f'    <li id="{pid}">\n'
            + (f'      <img src="media/{member_photo(photo)}" alt="" width="84" height="84" loading="lazy">\n'
               if member_photo(photo) else '      <span class="blank" aria-hidden="true"></span>\n') +
            f'      <div>\n'
            f'        <h3><a href="{esc(url)}">{esc(name)}</a></h3>\n'
            + (f'        <p class="role">{esc(role)}</p>\n' if role else "")
            + (f'        <p>{esc(note)}</p>\n' if note else "") +
            f'      </div>\n'
            f'    </li>')
    blocks.append("  </ul>")

    rows = []
    for name, where, url, _ in COLLABORATORS:
        pid = slug(name)
        rows.append(f'    <li id="{pid}"><a href="{esc(url)}">{esc(name)}</a> <span class="soft">{esc(where)}</span></li>')

    body = f"""<main class="wrap page">
  <h1>People</h1>
{chr(10).join(blocks)}
  <h2>Close collaborators</h2>
  <ul class="collab">
{chr(10).join(rows)}
  </ul>
</main>"""
    return page("people.html", "AIRe People",
                "Faculty, students and collaborators of the AIRe Lab at Carnegie Mellon University.", body, [], data=lab_data())


# ---------------------------------------------------------------- structured data for search engines

def lab_data():
    return {
        "@context": "https://schema.org",
        "@type": "ResearchOrganization",
        "name": "AIRe Lab",
        "alternateName": "CMU Artificial Intelligence and Reinforcement Learning Lab",
        "url": SITE,
        "logo": SITE + "apple-touch-icon.png",
        "image": SITE + "media/group.jpg",
        "email": CONTACT,
        "sameAs": ["https://github.com/CMU-AIRe"],
        "parentOrganization": {"@type": "CollegeOrUniversity", "name": "Carnegie Mellon University", "url": "https://www.cmu.edu/"},
        "founder": {"@type": "Person", "name": "Aviral Kumar", "url": "https://aviralkumar2907.github.io/",
                    "jobTitle": "Assistant Professor", "affiliation": "Carnegie Mellon University"},
        "member": [{"@type": "Person", "name": name, "url": url} for g, name, _, _, url, _ in MEMBERS if g != "Alumni"],
    }


def scholarly(p):
    url = next((u for label, u in p["links"] if label == "Paper"), None) or \
        next((u for _, u in p["links"]), SITE + "publications.html#" + p["id"])
    return {"@type": "ScholarlyArticle", "headline": p["title"], "url": url,
            "datePublished": p["when"].strftime("%Y-%m"),
            "author": [{"@type": "Person", "name": a} for a in p["authors"]],
            "publisher": p["venue"]}


# ---------------------------------------------------------------- blog

def blog():
    items = "\n".join(f"""    <li>
      <a href="{file}"><h2>{esc(title)}</h2></a>
      <p class="meta"><time datetime="{iso}">{shown}</time> <span>{esc(author)}</span></p>
      <p>{esc(summary)}</p>
    </li>""" for file, title, author, iso, shown, summary, _ in POSTS)
    body = f"""<main class="wrap page">
  <h1>Blog</h1>
  <p class="lede">Longer write-ups of what we are working on and how we think about it.</p>
  <ol class="posts">
{items}
  </ol>
</main>"""
    return page("blog.html", "AIRe Blog",
                "Posts from the AIRe Lab at Carnegie Mellon University about reinforcement learning research.", body, [])


def post(entry):
    file, title, author, iso, shown, summary, content = entry
    text = (HERE / "content" / content).read_text()

    # Give each section heading an anchor, and list them as the post's contents.
    toc = []
    def anchor(m):
        level, inner = m.group(1), m.group(2)
        hid = slug(re.sub(r"<[^>]+>", "", html.unescape(inner)))
        toc.append((level, hid, inner))
        return f'<h{level} id="{hid}">{inner}</h{level}>'
    text = re.sub(r"<h([23])>(.*?)</h\1>", anchor, text)
    # The opening paragraph reads as an introduction.
    text = text.replace("<p>", '<p class="opening">', 1)
    # Everything before the first section heading is the introduction.
    toc.insert(0, ("2", "top", "Introduction"))
    words = len(re.sub(r"<[^>]+>", " ", text).split())
    contents = "\n".join(f'        <li class="l{level}"><a href="#{hid}">{inner}</a></li>' for level, hid, inner in toc)

    body = f"""<main class="wrap page post-page">
  <header class="post-head" id="top">
    <p class="crumb"><a href="blog.html">Blog</a></p>
    <h1>{esc(title)}</h1>
    <p class="meta"><span>{esc(author)}</span> <time datetime="{iso}">{shown}</time> <span>{round(words / 230)} minute read</span></p>
  </header>
  <div class="post-body">
    <nav class="toc" aria-label="Contents">
      <p>Contents</p>
      <ol>
{contents}
      </ol>
    </nav>
    <article class="prose">
{text}    </article>
  </div>
</main>"""
    return page(file, "AIRe Blog", summary, body, ["post.js"], current="blog.html", kind="article", data={
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": title,
        "author": {"@type": "Person", "name": author}, "datePublished": iso,
        "publisher": {"@type": "ResearchOrganization", "name": "AIRe Lab", "url": SITE},
        "mainEntityOfPage": SITE + file, "description": summary, "wordCount": words})


def feed():
    items = "".join(f"""  <item>
    <title>{esc(title)}</title>
    <link>{SITE}{file}</link>
    <guid>{SITE}{file}</guid>
    <pubDate>{datetime.strptime(iso, "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 GMT")}</pubDate>
    <description>{esc(summary)}</description>
  </item>
""" for file, title, _, iso, _, summary, _ in POSTS)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>AIRe Lab blog</title>
  <link>{SITE}blog.html</link>
  <description>Posts from the AIRe Lab at Carnegie Mellon University.</description>
  <language>en</language>
{items}</channel>
</rss>
"""


# ---------------------------------------------------------------- join

def join():
    body = f"""<main class="wrap page">
  <article class="post">
    <h1>Join us</h1>
    <div class="prose">
      <h2>PhD researchers</h2>
      <p>We generally recruit self-motivated and talented students working in AI, decision-making and reinforcement learning every year. If you are a prospective PhD student, thank you for your interest! Please apply through the CMU School of Computer Science PhD programs (Machine Learning, Computer Science, Robotics). The lab can recruit students from all of these programs, with a slight preference towards CS and ML.</p>
      <p><strong>Please do not email Aviral or current students before admissions, since decisions are made at the department level by a committee.</strong></p>
      <p><em>If you are <strong>already</strong> admitted to a CMU PhD program and want to explore working in the lab, please <a href="mailto:{CONTACT}">email Aviral</a> with your resume and a short description of your interests.</em></p>
      <h2>MS and undergraduate researchers</h2>
      <p>If you are a current MS or undergraduate student in SCS at CMU and are interested in getting involved in our research, please apply to the lab using <a href="https://forms.gle/MHTkMnqS6vPvGVuT7">this form</a> (it requires a CMU login). We periodically update the form and check responses. We recruit undergraduate researchers at all class levels, though a background in AI and machine learning, as well as excellent grades, are preferred. We typically interview new undergraduate and MS researchers at the beginning of the semester, but we might also interview students at other times.</p>
      <h2>Visitors and postdocs</h2>
      <p>If you are not a current CMU student, chances are that at least in academic year 2024–2025, we will likely not be able to support you for in-person visits. However, we might be able to support some remote collaborations. If you are interested in this option, please <a href="mailto:{CONTACT}">email Prof. Kumar</a> with what you are interested in and a rough background. We are not hiring postdoctoral fellows at this time.</p>
    </div>
  </article>
</main>"""
    return page("join.html", "AIRe Join Us",
                "How to join the AIRe Lab at Carnegie Mellon University as a PhD student, MS or undergraduate researcher, or visitor.",
                body, [])


# ---------------------------------------------------------------- files for search engines and browsers

def sitemap():
    pages = ["", "publications.html", "people.html", "join.html"]
    if SHOW_BLOG:
        pages += ["blog.html"] + [p[0] for p in POSTS]
    urls = "".join(f"  <url><loc>{SITE}{p}</loc></url>\n" for p in pages)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n"


# ---------------------------------------------------------------- old addresses

# Pages of the previous site, and where each one now lives.
MOVED = {"pages/people.html": "people.html", "pages/publications.html": "publications.html",
         "pages/join_us.html": "join.html", "pages/research.html": ""}


def redirect(target):
    url = SITE + target
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AIRe Lab</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url=../{target}">
</head>
<body><p>This page has moved to <a href="../{target}">{url}</a>.</p></body>
</html>
"""


if __name__ == "__main__":
    outputs = [("index.html", home), ("publications.html", publications), ("people.html", people),
               ("join.html", join), ("sitemap.xml", sitemap),
               ("robots.txt", robots)]
    if SHOW_BLOG:
        outputs += [("blog.html", blog), ("feed.xml", feed)]
        outputs += [(entry[0], lambda entry=entry: post(entry)) for entry in POSTS]
    outputs += [(old, lambda new=new: redirect(new)) for old, new in MOVED.items()]
    (OUT / "pages").mkdir(exist_ok=True)
    for name, build in outputs:
        (OUT / name).write_text(build())
        print("wrote", name)
    print(len(PAPERS), "papers;", sum(1 for _, n, *_ in MEMBERS if papers_of(slug(n))), "of", len(MEMBERS), "members have papers listed")
