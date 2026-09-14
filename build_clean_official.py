"""Générateur de l'outil PAE fidèle à 100% à l'UI/UX officielle FACSA (ABICIV0099).

Partie 1 : Tous les cours de la faculté pour cocher les cours déjà acquis.
            Boutons "Bloc 1 réussi" et "Blocs 1 & 2 réussis" sélectionnant uniquement les cours obligatoires.
Partie 2 : Tous les cours MOINS ceux déjà acquis, avec badges discrets ronds (P et C) pour prérequis et corequis,
            grille d'horaire officielle, détection des conflits, et liens compatibles officiel (#b=...).
Partie 3 : Débouchés & Masters accessibles avec détail précis des cours suivis et cours clés manquants.
"""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
HOR = os.path.join(BASE, "horaires")

def read(p):
    return open(os.path.join(HOR, p), encoding="utf-8").read()

def js_inline(txt):
    return txt.replace("</script", "<\\/script")

def build():
    src = read("ABICIV0099.html")
    data_raw = read("data/ABICIV0099.json")
    coreq_raw = read("corequis_officiels.json")
    icons_raw = read("assets/icons.svg")
    alpine_raw = read("js/alpine.esm.js")
    encoder_raw = read("js/encoder.min.js")
    decoder_raw = read("js/decoder.min.js")

    data = json.loads(data_raw)
    coreq = json.loads(coreq_raw)

    # Exclure ELEN0450-1 de l'Informatique (ne compte pas comme option d'info)
    for item in data.get("layout", {}).get("content", []):
        if item.get("h2") == "Domaine de l'Informatique":
            for sub in item.get("content", []):
                if sub.get("h3") == "Bloc 3":
                    sub["list"] = [c for c in sub["list"] if c != "ELEN0450-1"]

    # Extraction des domaines et ECTS
    domaines = {}
    ects_map = {}
    def walk_dom(node, path):
        for k in ("h2", "h3", "h4", "h5", "h6"):
            if k in node:
                path = path + [node[k]]
        for c in node.get("list", []):
            short = c[:10]
            domaines.setdefault(short, [])
            if len(path) >= 2 and path[0] != "Cours obligatoires" and path[:2] not in domaines[short]:
                domaines[short].append(path[:2])
        for item in node.get("content", []):
            if isinstance(item, dict):
                walk_dom(item, path)

    walk_dom(data["layout"], [])
    for short, part_dict in data["courses"].items():
        tot = sum(c.get("ects", 0) for long_code, c in part_dict.items() if len(long_code) <= 10)
        ects_map[short] = tot

    # Listes des cours obligatoires UNIQUEMENT pour les raccourcis Bloc 1 et Bloc 2
    bloc1_courses = []
    bloc2_courses = []
    obligatoires_content = data["layout"]["content"][0]["content"]
    for sub in obligatoires_content:
        if sub.get("h3") == "Bloc 1":
            bloc1_courses = sorted(list(set(c[:10] for c in sub.get("list", []))))
        elif sub.get("h3") == "Bloc 2":
            bloc2_courses = sorted(list(set(c[:10] for c in sub.get("list", []))))

    # Liste officielle des 12 Masters d'ingénieur civil FACSA avec leurs cours de domaine
    masters_data = [
        {
            "id": "aero",
            "name": "Master en Ingénieur Civil en Aérospatiale",
            "domain": "Domaine de la Mécanique (Orientation Aérospatiale)",
            "desc": "Aérodynamique, propulsion spatiale, structures d'aéronefs, dynamique de vol et astronautique.",
            "finalites": [{"title": "Présentation générale", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SAER01.html", "raw_title": "Présentation des études et des débouchés"}],
            "prereq": ["MECA0025-3", "MECA0155-2", "MECA0036-2"],
            "recommended": ["MECA0445-2", "MECA0012-6", "MECA0002-1", "PHYS0904-4", "MECA0444-1", "SYST0022-1"],
            "complementary": ["INFO0062-1", "ELEN0008-1"],
            "courses": ["MECA0025-3", "MECA0155-2", "MECA0036-2", "MECA0445-2", "MECA0012-6", "MECA0002-1", "PHYS0904-4", "MECA0444-1", "SYST0022-1"]
        },
        {
            "id": "biomed",
            "name": "Master en Ingénieur Civil Biomédical",
            "domain": "Domaine du Génie biomédical",
            "desc": "Dispositifs médicaux, capteurs biologiques, imagerie par résonance, biomécanique et bioinformatique.",
            "finalites": [{"title": "Présentation générale", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SBIM01.html", "raw_title": "Présentation des études et des débouchés"}],
            "prereq": ["GBIO0001-1", "GBIO0025-1", "GBIO0026-1"],
            "recommended": ["GBIO0002-1", "GBIO0011-1", "GBIO0021-1", "GBIO0005-1", "GBIO0013-1"],
            "complementary": ["PHYS0904-4", "MECA0012-6", "MECA0036-2", "CHIM0604-2", "SYST0020-1", "ELEC0053-2", "ELEN0040-1", "ELEC0052-2", "SYST0022-1", "INFO0902-1", "INFO0062-1", "INFO0009-2"],
            "courses": ["GBIO0001-1", "GBIO0025-1", "GBIO0026-1", "GBIO0002-1", "GBIO0011-1", "GBIO0021-1", "GBIO0005-1", "GBIO0013-1"]
        },
        {
            "id": "chimie",
            "name": "Master en Ingénieur Civil en Chimie et Science des Matériaux",
            "domain": "Domaine de la Chimie et des Sciences des Matériaux",
            "desc": "Génie des procédés chimiques, polymères, synthèse catalytique, nanomatériaux et chimie verte.",
            "finalites": [{"title": "Finalité chemical engineering", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SCHE01.html", "raw_title": "Présentation des études et des débouchés finalité chemical engineering"}, {"title": "Finalité AMIR", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SADV02.html", "raw_title": "Présentation des études et des débouchés finalité AMIR"}],
            "prereq": ["CHIM0022-4", "CHIM0009-3", "CHIM0604-2", "CHIM9320-1"],
            "recommended": ["CHIM9322-1", "CHIM9318-1", "CHIM9315-1", "CHIM9297-1"],
            "complementary": ["PHYS0904-4", "MECA0025-3", "MECA0036-2", "ELEN0076-1", "PHYS0211-3", "ELEC0053-2", "GEOL0020-7", "GEOL0314-1", "GBIO0025-1", "GBIO0001-1"],
            "courses": ["CHIM0022-4", "CHIM0009-3", "CHIM0604-2", "CHIM9320-1", "CHIM9322-1", "CHIM9318-1", "CHIM9315-1", "CHIM9297-1"]
        },
        {
            "id": "constructions",
            "name": "Master en Ingénieur Civil des Constructions",
            "domain": "Domaine des Constructions",
            "desc": "Génie civil, calcul des structures béton et métal, géotechnique, hydraulique et ouvrages d'art.",
            "finalites": [{"title": "Finalité civil engineering", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SCIV01.html", "raw_title": "Présentation des études et des débouchés finalité civil engineering"}, {"title": "Finalité urban and environmental engineering", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SURB01.html", "raw_title": "Présentation des études et des débouchés finalité urban and environmental engineering"}],
            "prereq": ["GCIV2172-1", "GCIV2173-1", "GCIV0603-2", "GCIV0604-3"],
            "recommended": ["GCIV0184-5", "MECA0012-6", "GCIV0608-1", "GEOL0001-1"],
            "complementary": ["GEOL0021-7", "GEOL0020-7", "ARCH3260-2", "ARCH3275-1"],
            "courses": ["GCIV2172-1", "GCIV2173-1", "GCIV0603-2", "GCIV0604-3", "GCIV0184-5", "MECA0012-6", "GCIV0608-1", "GEOL0001-1"]
        },
        {
            "id": "elec",
            "name": "Master en Ingénieur Civil Électricien",
            "domain": "Domaine de l'Électricité et de l'Électronique",
            "desc": "Circuits électroniques intégrés, télécommunications, microélectronique et traitement numérique.",
            "finalites": [{"title": "Finalité electronic systems devices", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SDEV01.html", "raw_title": "Présentation des études et des débouchés finalité electronic systems devices"}, {"title": "Finalité neuromorphic engineering", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SNEU01.html", "raw_title": "Présentation des études et des débouchés finalité neuromorphic engineering"}],
            "prereq": ["SYST0022-1", "ELEC0052-2", "ELEC0053-2"],
            "recommended": ["ELEN0040-1", "ELEN0076-1", "ELEC0431-2", "ELEN0075-3", "ELEN0008-1"],
            "complementary": ["SYST0020-1", "INFO0902-1", "INFO0062-1", "INFO0012-2", "INFO0004-2", "INFO0009-2", "INFO0010-4", "MECA0445-2"],
            "courses": ["SYST0022-1", "ELEC0052-2", "ELEC0053-2", "ELEN0040-1", "ELEN0076-1", "ELEC0431-2", "ELEN0075-3", "ELEN0008-1"]
        },
        {
            "id": "energie",
            "name": "Master en Ingénieur Civil en Énergie",
            "domain": "Domaine de l'Énergie",
            "desc": "Réseaux électriques intelligents, conversion d'énergie, énergies renouvelables et transition énergétique.",
            "finalites": [{"title": "Présentation générale", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SGES01.html", "raw_title": "Présentation des études et des débouchés"}],
            "prereq": ["ELEC0053-2", "MECA0002-1", "SYST0022-1"],
            "recommended": ["MECA0445-2", "MECA0002-1", "CHIM9315-1", "ELEC0431-2", "ELEC0052-2", "CHIM0009-3", "MECA0012-6", "CHIM9322-1", "MECA0025-3", "MECA0155-2", "PHYS0904-4", "MECA0036-2"],
            "complementary": ["ELEN0040-1", "INFO0062-1", "ELEN0075-3", "ELEN0076-1", "INFO8006-1"],
            "courses": ["ELEC0053-2", "MECA0002-1", "SYST0022-1", "MECA0445-2", "CHIM9315-1", "ELEC0431-2", "ELEC0052-2", "CHIM0009-3", "MECA0012-6", "CHIM9322-1", "MECA0025-3", "MECA0155-2", "PHYS0904-4", "MECA0036-2"]
        },
        {
            "id": "geol",
            "name": "Master en Ingénieur Civil des Mines et Géologue",
            "domain": "Domaine des Géoressources et de la Géologie de l'Environnement",
            "desc": "Prospection minière, hydrogéologie, géotechnique de l'environnement et valorisation des géoressources.",
            "finalites": [{"title": "Finalité géologie de l'ingénieur et de l'environnement", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SMGE01.html", "raw_title": "Présentation des études et des débouchés finalité géologie de l'ingénieur et de l'environnement"}, {"title": "Finalité ressources minérales et recyclage", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SRES01.html", "raw_title": "Présentation des études et des débouchés finalité ressources minérales et recyclage"}],
            "prereq": ["GEOL0001-1", "GEOL0021-7", "GCIV0603-2", "GEOL1026-1", "GEOL0020-7", "GEOL0314-1", "GEOL0013-5"],
            "recommended": ["GEOL1032-1"],
            "complementary": ["MECA0445-2", "PHYS0904-4", "MECA0012-6", "MECA0036-2", "ELEN0076-1", "CHIM0009-3", "SYST0022-1", "INFO0009-2", "GCIV0184-5", "GCIV0604-3", "GCIV2173-1"],
            "courses": ["GEOL0001-1", "GEOL0021-7", "GCIV0603-2", "GEOL1026-1", "GEOL0020-7", "GEOL0314-1", "GEOL0013-5", "GEOL1032-1"]
        },
        {
            "id": "info",
            "name": "Master en Ingénieur Civil en Informatique",
            "domain": "Domaine de l'Informatique",
            "desc": "Systèmes logiciels complexes, algorithmique, réseaux, cybersécurité et intelligence artificielle.",
            "finalites": [{"title": "Finalité computer systems security", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SSEC01.html", "raw_title": "Présentation des études et des débouchés finalité computer systems security"}, {"title": "Finalité intelligent systems", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SISY01.html", "raw_title": "Présentation des études et des débouchés finalité intelligent systems"}, {"title": "Finalité management", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SIMA01.html", "raw_title": "Présentation des études et des débouchés finalité management"}],
            "prereq": ["INFO0902-1", "INFO0062-1", "INFO0010-4", "INFO0012-2", "INFO9012-1"],
            "recommended": ["INFO0009-2", "INFO0054-1", "INFO8006-1"],
            "complementary": ["ELEN0076-1", "SYST0020-1", "ELEC0053-2", "ELEN0040-1", "ELEC0431-2", "SYST0022-1", "ELEN0008-1", "GEOL1032-1", "GBIO0002-1", "GBIO0011-1"],
            "courses": ["INFO0902-1", "INFO0062-1", "INFO0010-4", "INFO0012-2", "INFO9012-1", "INFO0009-2", "INFO0054-1", "INFO8006-1"]
        },
        {
            "id": "meca",
            "name": "Master en Ingénieur Civil Mécanicien",
            "domain": "Domaine de la Mécanique",
            "desc": "Conception mécanique, dynamique des machines, transferts thermiques, mécanique des fluides et fabrication.",
            "finalites": [{"title": "Finalité matériaux et fabrication", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SMAF01.html", "raw_title": "Présentation des études et des débouchés finalité matériaux et fabrication"}, {"title": "Finalité mécatronique", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SMCT01.html", "raw_title": "Présentation des études et des débouchés finalité mécatronique"}, {"title": "Finalité technologies durables de l'automobile", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SMEA01.html", "raw_title": "Présentation des études et des débouchés finalité technologies durables de l'automobile"}],
            "prereq": ["MECA0155-2", "MECA0036-2", "MECA0444-1"],
            "recommended": ["MECA0445-2", "MECA0012-6", "MECA0002-1", "PHYS0904-4", "MECA0025-3"],
            "complementary": ["ELEN0076-1", "ELEC0053-2", "ELEN0040-1", "ELEC0052-2", "ELEC0431-2", "SYST0022-1", "ELEN0075-3", "ELEN0008-1"],
            "courses": ["MECA0155-2", "MECA0036-2", "MECA0444-1", "MECA0445-2", "MECA0012-6", "MECA0002-1", "PHYS0904-4", "MECA0025-3"]
        },
        {
            "id": "phys",
            "name": "Master en Ingénieur Civil Physicien",
            "domain": "Domaine de la Physique",
            "desc": "Physique quantique appliquée, optoélectronique, nanomatériaux, nanodispositifs et matière condensée.",
            "finalites": [{"title": "Présentation générale", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2APHY01.html", "raw_title": "Présentation des études et des débouchés"}],
            "prereq": ["MECA0036-2", "ELEN0076-1", "MECA0025-3", "PHYS0211-3"],
            "recommended": ["PHYS2026-2", "MECA0445-2", "PHYS0055-1", "SYST0020-1"],
            "complementary": ["PHYS0904-4", "MECA0012-6", "CHIM0022-4", "MECA0155-2", "ELEC0053-2", "ELEN0040-1", "ELEC0052-2", "ELEN0075-3", "INFO0062-1", "GBIO0011-1", "GBIO0001-1", "GBIO0013-1"],
            "courses": ["MECA0036-2", "ELEN0076-1", "MECA0025-3", "PHYS0211-3", "PHYS2026-2", "MECA0445-2", "PHYS0055-1", "SYST0020-1"]
        },
        {
            "id": "dats",
            "name": "Master en Ingénieur Civil en Science des Données",
            "domain": "Domaine de la Science des Données",
            "desc": "Machine Learning, Big Data, calcul haute performance, fouille de données et modélisation.",
            "finalites": [{"title": "Présentation générale", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2SIDA01.html", "raw_title": "Présentation des études et des débouchés"}],
            "prereq": ["INFO0902-1", "INFO0009-2", "INFO8006-1", "MATH0461-2"],
            "recommended": ["INFO0062-1", "INFO0939-1", "MATH1222-3", "DATS0002-1"],
            "complementary": ["INFO9012-1", "GEOL1032-1", "SYST0022-1", "GBIO0011-1"],
            "courses": ["INFO0902-1", "INFO0009-2", "INFO8006-1", "MATH0461-2", "INFO0062-1", "INFO0939-1", "MATH1222-3", "DATS0002-1"]
        },
        {
            "id": "archi",
            "name": "Master en Ingénieur Civil Architecte",
            "domain": "Domaine de l'Architecture",
            "desc": "Architecture durable, conception architecturale et structurale, physique du bâtiment et patrimoine.",
            "finalites": [{"title": "Présentation des études et des débouchés", "url": "https://www.programmes.uliege.be/cocoon/20262027/formations/bref/A2UARC01.html", "raw_title": "Présentation des études et des débouchés"}],
            "prereq": ["ARCH2224-1", "ARCH3260-2", "ARCH3275-1", "ARCH3260-2b"],
            "recommended": ["GCIV0184-5", "GCIV2172-1", "GCIV2173-1"],
            "complementary": ["GEOL0001-1", "GCIV0603-2"],
            "courses": ["ARCH2224-1", "ARCH3260-2", "ARCH3275-1", "ARCH3260-2b", "GCIV0184-5", "GCIV2172-1", "GCIV2173-1"]
        }
    ]

    # 1. Injection des données
    boot_script = f"""<script>
    const code = "ABICIV0099";
    window.__DATA__ = {js_inline(json.dumps(data, ensure_ascii=False))};
    window.__COREQUIS__ = {js_inline(json.dumps(coreq, ensure_ascii=False))};
    window.__DOMAINES__ = {js_inline(json.dumps(domaines, ensure_ascii=False))};
    window.__ECTS__ = {js_inline(json.dumps(ects_map))};
    window.__BLOC1__ = {js_inline(json.dumps(bloc1_courses))};
    window.__BLOC2__ = {js_inline(json.dumps(bloc2_courses))};
    window.__MASTERS__ = {js_inline(json.dumps(masters_data, ensure_ascii=False))};
    window.dataPromise = Promise.resolve(window.__DATA__);
  </script>"""

    m = re.search(r"<script>\s*const code = .*?</script>", src, re.S)
    src = src[: m.start()] + boot_script + src[m.end():]

    # 2. Inlining encodeur/décodeur
    enc = encoder_raw.replace("export function encode", "function encode")
    dec = decoder_raw.replace("export function decode", "function decode")
    helper = ("<script>\n(function(){\n" + js_inline(enc) + "\nwindow.__ENCODER__ = { encode: encode };\n})();\n</script>\n"
              "<script>\n(function(){\n" + js_inline(dec) + "\nwindow.__DECODER__ = { decode: decode };\n})();\n</script>\n")

    src = src.replace("decoder = await import('../js/decoder.min.js');", "decoder = window.__DECODER__;")
    src = src.replace("const encoder = await import('../js/encoder.min.js');", "const encoder = window.__ENCODER__;")

    # 3. Inlining Alpine
    alpine_body = alpine_raw.strip()
    alpine_body = re.sub(r"^/\*\*.*?\*/\s*", "", alpine_body, flags=re.S)
    alpine_body = re.sub(r"export\s*\{[^}]*\}\s*;?", "", alpine_body)
    alpine_body = re.sub(r"//# sourceMappingURL=.*$", "", alpine_body, flags=re.M)
    m = re.search(r"import\s*\{\s*default as Alpine\s*\}\s*from\s*'[^']+';", src)
    src = src[: m.start()] + alpine_body + "\n    const Alpine = js;\n" + src[m.end():]

    # 4. Inlining SVG sprite
    sprite = re.sub(r"<\?xml[^>]*\?>", "", icons_raw.strip())
    sprite = sprite.replace("<svg ", '<svg style="display:none" aria-hidden="true" id="svg-icons" ', 1)
    src = src.replace("../assets/icons.svg#", "#")
    src = re.sub(r"<body>", "<body>\n" + sprite, src, count=1)

    # 5. Polices locales & titre officiel
    src = re.sub(r'<link href="https://fonts\.googleapis\.com[^>]*>', "", src)
    src = src.replace('"Arimo", "Arial"', '"Arimo", "Liberation Sans", "Arial"')
    src = src.replace("<title>Horaire - ABICIV0099</title>", "<title>Horaire &amp; PAE interactif — ABICIV0099 (FACSA ULiège)</title>")

    # 6. Partage vers l'outil officiel
    src = src.replace(
        "this.share.url = this.share.prot + '//' + window.location.hostname + window.location.pathname + '#b=' + data;",
        "this.share.url = 'https://www.mmm.uliege.be/facsa/horaires/ABICIV0099#b=' + data;")

    # Inlining du helper
    anchor = "window.dataPromise = Promise.resolve(window.__DATA__);\n  </script>"
    src = src.replace(anchor, anchor + "\n" + helper, 1)

    # 7. Styles discrets parfaitement intégrés dans le design officiel
    extra_css = """
  <style>
    [x-cloak] { display: none !important; }

    /* Sélecteur d'étape fidèle au design officiel (3 étapes) */
    .phase-bar {
      display: flex;
      gap: 0.5em;
      margin: 1.2em auto 0;
      width: 50%;
      border-bottom: 1px solid #bbb;
      padding-bottom: 0.5em;
    }
    @media screen and (max-width: 1200px) and (min-width: 800px) {
      .phase-bar { width: 80%; }
    }
    @media screen and (max-width: 800px) {
      .phase-bar { width: auto; margin: 0.8em 0.6em 0; flex-wrap: wrap; }
    }
    .phase-tab {
      flex: 1;
      padding: 0.5em 0.8em;
      border-radius: 3px;
      font-size: 13px;
      font-weight: bold;
      color: #555;
      background: #f0f0f0;
      border: 1px solid #ccc;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.4em;
      transition: background 0.1s ease, color 0.1s ease;
    }
    .phase-tab:hover {
      background: #e4e4e4;
      color: #222;
    }
    .phase-tab.active {
      background: var(--c-faculty);
      border-color: var(--c-faculty);
      color: #fff;
    }
    .phase-badge {
      display: inline-block;
      font-size: 10.5px;
      padding: 1px 6px;
      border-radius: 999px;
      background: rgba(0,0,0,0.10);
      white-space: nowrap;
    }
    .phase-tab.active .phase-badge {
      background: rgba(255,255,255,0.22);
      color: #fff;
    }

    /* Rangée des boutons d'actions en haut à droite */
    #check .actions {
      float: right;
      display: inline-flex;
      gap: .5em;
      margin-top: 1.2em;
      margin-bottom: 0.5em;
    }
    /* Le titre de section se place systématiquement en dessous des boutons comme en Section 1 */
    #check .super {
      clear: both !important;
      margin-top: 0.4em !important;
      padding-top: 0.1em;
    }

    /* Description discrète sous le titre – style officiel */
    .phase-desc {
      clear: both;
      font-size: 13px;
      color: #444;
      margin: 0.8em 0 1.2em;
      line-height: 1.5;
    }

    /* Boutons d'action alignés sur le style officiel des boutons Partager/Tout effacer */
    #check .actions button {
      border-radius: 3px;
      font-size: 13px;
      padding: 0.3em 0.7em;
      gap: 0.3em;
    }

    /* Badges ronds discrets et élégants pour les prérequis et corequis */
    .req-dot {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      font-size: 9.5px;
      font-weight: bold;
      line-height: 1;
      margin-left: 4px;
      vertical-align: middle;
      cursor: help;
      transition: transform 0.12s ease, box-shadow 0.12s ease;
      user-select: none;
    }
    .req-dot:hover {
      transform: scale(1.3);
      box-shadow: 0 1px 5px rgba(0,0,0,0.28);
    }
    .req-dot.pre-ok {
      background: #e6f4ea;
      color: #137333;
      border: 1px solid #34a853;
    }
    .req-dot.pre-bad {
      background: #fce8e6;
      color: #c5221f;
      border: 1px solid #ea4335;
    }
    .req-dot.pre-warn {
      background: #fef7e0;
      color: #b06000;
      border: 1px solid #f9ab00;
    }
    .req-dot.coreq-ok {
      background: #e6f4ea;
      color: #137333;
      border: 1px solid #34a853;
    }
    .req-dot.coreq-warn {
      background: #fef7e0;
      color: #b06000;
      border: 1px solid #f9ab00;
    }

    /* Panneaux d'analyse officielle en bas de page */
    #panels {
      width: 50%;
      margin: 1.2em auto;
      padding-bottom: 1em;
    }
    @media screen and (max-width: 1200px) and (min-width: 800px) {
      #panels { width: 80%; }
    }
    @media screen and (max-width: 800px) {
      #panels { width: auto; margin: 1em 0.6em; }
    }
    #panels .box {
      border: 1px solid #e2b45f;
      border-left: 5px solid var(--c-faculty-light);
      background: #fffaf0;
      border-radius: 3px;
      padding: 0.7em 1em;
      margin-bottom: 0.7em;
      font-size: 13px;
    }
    #panels .box.info {
      border-color: #9fc3d8;
      border-left-color: var(--c-faculty-accent);
      background: #f2f9fb;
    }
    #panels .box.stop {
      border-color: #fca5a5;
      border-left-color: #b3261e;
      background: #fdf3f3;
    }
    #panels h6 {
      margin: 0 0 0.3em;
      font-size: 13.5px;
      font-weight: bold;
      color: #111;
    }
    #panels ul {
      margin: 0.25em 0 0.15em;
      padding-left: 1.2em;
    }
    #panels li {
      margin-bottom: 0.3em;
    }
    #panels code {
      background: rgba(0,0,0,0.06);
      padding: 0 0.3em;
      border-radius: 2px;
      font-family: monospace;
      font-size: smaller;
    }
    #panels .pill {
      display: inline-block;
      border-radius: 999px;
      padding: 0 0.5em;
      font-size: 11.5px;
      margin-left: 0.3em;
    }
    #panels .pill.good { background: #dff3e4; color: #0a6b34; }
    #panels .pill.bad { background: #fbe1e1; color: #97231c; }

    /* ===== Section 3 : Débouchés & Masters ===== */
    /* La section hérite du style #check officiel pour garder la même typographie */
    .masters-section {
      color: #141414;
      padding-bottom: 4em;
    }
    .masters-filter-bar {
      clear: both;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.6em;
      margin: 1.2em 0 1.4em;
      padding: 0.6em 0.9em;
      background: #f7f7f7;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    .masters-filter-bar .filter-label {
      font-size: 13px;
      font-weight: bold;
      color: #333;
    }
    .masters-filter-bar .filter-buttons {
      display: inline-flex;
      flex-wrap: wrap;
      gap: 0.5em;
    }
    .filter-pill {
      padding: 0.35em 0.85em;
      border-radius: 3px;
      font-size: 12.5px;
      font-weight: bold;
      cursor: pointer;
      border: 1px solid #ccc;
      background: #fff;
      color: #444;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.3em;
    }
    .filter-pill:hover {
      background: #eee;
      color: #111;
      border-color: #bbb;
    }
    .filter-pill.active {
      background: var(--c-faculty) !important;
      color: #fff !important;
      border-color: var(--c-faculty) !important;
      box-shadow: 0 1px 2px rgba(0,0,0,0.15);
    }
    .pill.good {
      background: #dff3e4;
      color: #0a6b34;
      border: 1px solid #b7e4c3;
    }
    .pill.mineure-pill {
      background: #fff3d4;
      color: #855500;
      border: 1px solid #fed287;
    }
    .pill.neutral-pill {
      background: #f0f0f0;
      color: #666;
      border: 1px solid #dcdcdc;
    }

    /* Style élégant pour les cases à cocher */
    #check .checkbox input[type="checkbox"] {
      cursor: pointer;
      width: 15px;
      height: 15px;
      accent-color: var(--c-faculty-accent);
      vertical-align: middle;
    }
    #check .checkbox input[type="checkbox"]:disabled {
      cursor: not-allowed;
      accent-color: #137333;
      opacity: 0.85;
    }

    /* Indicateurs latéraux discrets et élégants sur les lignes de tableau */
    #check table tr {
      border-left: 3px solid transparent;
    }
    #check table tr.course-acquis {
      background: #f3faf5 !important;
      border-left: 3px solid #137333 !important;
    }
    #check table tr.course-selected {
      background: #eef8f9 !important;
      border-left: 3px solid var(--c-faculty-accent) !important;
    }
    #check table tr.course-acquis:hover {
      background: #e7f5eb !important;
    }
    #check table tr.course-selected:hover {
      background: #e2f2f4 !important;
    }

    /* Pastilles de statut de cours (Acquis & Au PAE) */
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      font-weight: 600;
      line-height: 1;
      padding: 3px 8px;
      border-radius: 999px;
      white-space: nowrap;
      user-select: none;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .status-badge.acquis {
      background: #e6f4ea;
      color: #137333;
      border: 1px solid #a8dab5;
    }
    .status-badge.au-pae {
      background: #e0f4f7;
      color: #005f6b;
      border: 1px solid #9bdae3;
    }
    .status-badge.non-suivi {
      background: #f1f3f5;
      color: #6c757d;
      border: 1px solid #ced4da;
      box-shadow: none;
    }
    .status-badge svg {
      width: 11px;
      height: 11px;
      flex-shrink: 0;
    }

    /* Bandeaux noir et blanc officiels (zébrage haute lisibilité identique à la section 2) */
    #check table tr:nth-of-type(odd) {
      background: #d0d0d0 !important;
    }
    #check table tr:nth-of-type(even) {
      background: #ffffff !important;
    }
    #check table tr:hover {
      background: #c8c8c8 !important;
    }
    .master-option {
      border-bottom: 1px solid #d0d0d0;
      padding-bottom: 2em;
      margin-bottom: 2.2em;
    }
    .master-option:last-of-type {
      border-bottom: none;
    }
    .master-bloc-item {
      margin-bottom: 1.2em;
    }
    .master-bloc-item h5 {
      font-size: 1em;
      font-variant: small-caps;
      margin-top: 1em;
      margin-bottom: 0.5em;
      font-weight: bold;
      color: #222;
    }
    .finalite-chip {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 9px;
      font-size: 11.5px;
      font-weight: 500;
      color: #0369a1;
      background: #f0f9ff;
      border: 1px solid #bae6fd;
      border-radius: 12px;
      text-decoration: none;
      transition: all 0.15s ease;
    }
    .finalite-chip:hover {
      background: #e0f2fe;
      border-color: #7dd3fc;
      color: #0284c7;
      text-decoration: none;
    }
    .phase-badge-success {
      background: #137333 !important;
      color: white !important;
    }
    .master-gauge-track {
      flex: 1;
      min-width: 140px;
      max-width: 280px;
      height: 9px;
      background: #e2e8f0;
      border-radius: 9999px;
      overflow: hidden;
      box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.08);
      position: relative;
    }
    .master-gauge-fill {
      display: block;
      height: 100% !important;
      min-height: 9px;
      border-radius: 9999px;
      transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.35s ease;
    }
    .master-gauge-text {
      font-size: 12.5px;
      font-weight: bold;
    }
    .text-success { color: #15803d; }
    .text-warning { color: #c2410c; }
    .text-neutral { color: #64748b; }
    .tier-chevron-icon {
      width: 12px;
      height: 12px;
      transition: transform 0.2s ease;
    }
    .tier-chevron-icon.is-open {
      transform: rotate(180deg);
    }
    .tier-stat-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      font-size: 11.5px;
      border-radius: 4px;
      font-weight: 500;
    }
    .tier-stat-badge.stat-good {
      background: #e6f4ea;
      color: #137333;
      border: 1px solid #ceead6;
    }
    .tier-stat-badge.stat-warn {
      background: #fef7e0;
      color: #b06000;
      border: 1px solid #feefc3;
    }
    .tier-stat-badge.stat-info {
      background: #e8f0fe;
      color: #1a73e8;
      border: 1px solid #d2e3fc;
    }
    .tier-stat-badge.stat-neutral {
      background: #f1f3f4;
      color: #5f6368;
      border: 1px solid #dadce0;
    }
    .master-tier-block {
      margin-top: 1.1em;
      margin-bottom: 1.3em;
    }
    .tier-icon-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 22px;
      height: 22px;
      border-radius: 4px;
      flex-shrink: 0;
    }
    .tier-icon-badge svg {
      width: 14px;
      height: 14px;
    }
    .tier-icon-prereq {
      background: #fce8e6;
      color: #c5221f;
    }
    .tier-icon-rec {
      background: #e8f0fe;
      color: #1a73e8;
    }
    .tier-icon-comp {
      background: #f1f3f4;
      color: #5f6368;
    }
    .tier-header {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.6em;
      padding: 0.4em 0.7em;
      background: #f8f9fa;
      border-left: 4px solid #9aa0a6;
      border-radius: 3px;
      margin-bottom: 0.5em;
    }
    .tier-header-prereq {
      border-left-color: #d93025;
      background: #fdf7f7;
    }
    .tier-header-rec {
      border-left-color: #1a73e8;
      background: #f8fbff;
    }
    .tier-header-comp {
      border-left-color: #5f6368;
      background: #f8f9fa;
    }
    .tier-title {
      font-weight: bold;
      font-size: 13px;
      color: #202124;
    }
    .tier-subtitle {
      font-size: 11.5px;
      color: #70757a;
      margin-left: auto;
    }
    .tier-toggle-btn {
      font-size: 11.5px;
      padding: 2px 8px;
      background: #fff;
      border: 1px solid #dadce0;
      border-radius: 4px;
      cursor: pointer;
      color: #1a73e8;
      font-weight: 500;
    }
    .tier-toggle-btn:hover {
      background: #f1f3f4;
    }
    .course-link {
      color: inherit;
      text-decoration: none;
    }
    .course-link:hover {
      text-decoration: underline;
      color: #1a73e8;
    }

    @media print {
      .phase-bar, #panels, .masters-section { display: none !important; }
    }
  </style>
"""
    src = src.replace("</head>", extra_css + "</head>", 1)

    # 8. Remplacement du sélecteur d'étape (3 étapes)
    phase_bar_html = """
    <!-- Sélecteur d'étape fidèle au design officiel (3 étapes) -->
    <div class="phase-bar" x-show="!showAgenda" x-cloak>
      <button class="phase-tab" :class="{ active: phase == 1 }" @click="phase = 1">
        <span>1. Cours déjà acquis</span>
        <span class="phase-badge" x-text="acquisCount + ' cours (' + acquisEcts + ' cr)'"></span>
      </button>
      <button class="phase-tab" :class="{ active: phase == 2 }" @click="phase = 2">
        <span>2. Mon PAE &amp; Horaire</span>
        <span class="phase-badge" x-text="numSelected + ' cours (' + (ects[1] + ects[2]) + ' cr)'"></span>
      </button>
      <button class="phase-tab" :class="{ active: phase == 3 }" @click="phase = 3">
        <span>3. Débouchés &amp; Masters</span>
        <span class="phase-badge" :class="directMastersCount > 0 ? 'phase-badge-success' : ''" x-text="directMastersCount + ' optimal' + (directMastersCount > 1 ? 's' : '')"></span>
      </button>
    </div>
"""
    src = src.replace('<div id="root" :class="{ ok: showAgenda }">',
                      phase_bar_html + '\n    <div id="root" :class="{ ok: showAgenda }">', 1)

    # 9. Titres et actions adaptés selon la phase dans #check
    old_check_head = """    <div id="check">
      <h3 class="super" x-html="addBlocks(layout.h1)"></h3>
      <span class="actions">
        <button class="alt" @click="resetSelection();window.location.hash=''" title="cliquez ici pour effacer la sélection">
          <svg fill="currentColor"><use href="#trash"/></svg><span>Tout effacer</span>
        </button>
        <button @click="share.show = true" title="cliquez ici pour générer un lien de partage">
          <svg fill="currentColor"><use href="#arrow-up-on-square"/></svg><span>Partager</span>
        </button>
      </span>"""

    new_check_head = """    <div id="check">
      <!-- Titre et actions Phase 1 -->
      <template x-if="phase == 1">
        <div>
          <span class="actions">
            <button class="alt" @click="setPreset('b1')" title="Cocher uniquement les cours obligatoires du Bloc 1 (60 crédits)">
              <span>Bloc 1 réussi</span>
            </button>
            <button class="alt" @click="setPreset('b1_b2')" title="Cocher uniquement les cours obligatoires des Blocs 1 et 2 (106 crédits)">
              <span>Blocs 1 &amp; 2 réussis</span>
            </button>
            <button class="alt" @click="resetAcquis()" title="Effacer les cours acquis">
              <svg fill="currentColor"><use href="#trash"/></svg><span>Effacer</span>
            </button>
            <button @click="phase = 2" title="Passer à la construction du PAE" style="background-color: var(--c-faculty); color: white;">
              <span>Continuer vers mon PAE &rarr;</span>
            </button>
          </span>
          <h3 class="super"><span>1. Cours déjà acquis</span> - <span>Faculté des Sciences Appliquées</span></h3>
          <div class="phase-desc">
            Cochez ci-dessous les cours que vous avez <b>déjà validés</b> (crédités) les années précédentes.<br/>
            Ils seront automatiquement retirés de votre PAE pour cette année et serviront à vérifier vos prérequis et corequis.
          </div>
        </div>
      </template>

      <!-- Titre et actions Phase 2 -->
      <template x-if="phase == 2">
        <div>
          <span class="actions">
            <button class="alt" @click="phase = 1" title="Modifier la liste des cours déjà acquis">
              <span>&larr; Modifier mes acquis</span>
            </button>
            <button class="alt" @click="resetSelection();window.location.hash=''" title="cliquez ici pour effacer la sélection du PAE">
              <svg fill="currentColor"><use href="#trash"/></svg><span>Tout effacer</span>
            </button>
            <button class="alt" @click="phase = 3" title="Voir la préparation vers les 12 masters avec ces choix" style="color: #ffffff; font-weight: 500;">
              <span>Masters &amp; Débouchés &rarr;</span>
            </button>
            <button @click="share.show = true" title="cliquez ici pour générer un lien de partage">
              <svg fill="currentColor"><use href="#arrow-up-on-square"/></svg><span>Partager</span>
            </button>
          </span>
          <h3 class="super" x-html="addBlocks(layout.h1)"></h3>
          <div class="phase-desc">
            Sélectionnez vos cours pour cette année. Les cours déjà acquis à l'étape 1 sont masqués.<br/>
            Les pastilles rondes <b>P</b> (prérequis) et <b>C</b> (corequis) indiquent leur statut (validé, dérogation requise, ou bloquant).
          </div>
        </div>
      </template>

      <!-- Titre et contenu Section 3 : Débouchés & Masters accessibles -->
      <template x-if="phase == 3">
        <div class="masters-section">
          <span class="actions">
            <button class="alt" @click="phase = 2" title="Retourner à la composition de mon PAE">
              <span>&larr; Revenir à mon PAE</span>
            </button>
            <button @click="share.show = true" title="Partager mon parcours">
              <svg fill="currentColor"><use href="#arrow-up-on-square"/></svg><span>Partager</span>
            </button>
          </span>
          <h3 class="super"><span>3. Débouchés &amp; Masters d'ingénieur civil</span> - <span>Faculté des Sciences Appliquées</span></h3>
          
          <div class="box info" style="margin: 0.8em 0 1.2em 0; border-left: 4px solid var(--c-faculty-accent); background: #fdfaf6; padding: 0.9em 1.2em; border-radius: 4px;">
            <h6 style="margin: 0 0 0.4em 0; color: var(--c-faculty-accent); font-size: 14px; font-weight: bold; display: flex; align-items: center; gap: 6px;">
              <svg style="width: 16px; height: 16px; flex-shrink: 0;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z"/><line x1="9" y1="21" x2="15" y2="21"/></svg>
              <span>Cadre réglementaire FWB &amp; Préparation aux Masters</span>
            </h6>
            <div style="font-size: 13px; line-height: 1.5; color: #333;">
              En Fédération Wallonie-Bruxelles (FWB), l'obtention du grade de <b>bachelier en ingénieur civil</b> confère un <b>accès direct de plein droit à tous les Masters d'ingénieur civil</b> (programme de 120 ECTS, <b>sans programme complémentaire «&nbsp;Bloc 0&nbsp;»</b>).<br/>
              Vos choix d'options en bachelier définissent votre niveau de préparation :
              <ul style="margin: 0.4em 0 0.2em 1.2em; padding: 0;">
                <li><b>Continuité directe optimale (&ge;&nbsp;30 ECTS du domaine)</b> : Vous avez vu tous les prérequis disciplinaires. Vos crédits de cours au choix en Master restent <b>100% libres</b> pour vous spécialiser.</li>
                <li><b>Transition allégée avec mineure (10 à 25 ECTS)</b> : Transition fluide. Seuls quelques cours clés non vus en bachelier seront réalloués sur les crédits d'options du Master (sans allonger les 120 ECTS).</li>
                <li><b>Autre filière (&lt;&nbsp;10 ECTS)</b> : L'accès légal reste garanti (120 ECTS), mais une part substantielle de vos options de Master servira à rattraper les cours fondamentaux du domaine (exigeant notamment en Physique, Matériaux ou Géologie).</li>
              </ul>
            </div>
          </div>

          <!-- Barre de filtres dédiée pour les Masters -->
          <div class="masters-filter-bar">
            <div class="filter-label">Filtrer par niveau de préparation :</div>
            <div class="filter-buttons">
              <button class="filter-pill" :class="{ active: masterFilter === 'all' }" @click="masterFilter = 'all'">
                <span>Tous les masters (12)</span>
              </button>
              <button class="filter-pill" :class="{ active: masterFilter === 'direct' }" @click="masterFilter = 'direct'">
                <span>Continuité optimale (<span x-text="directMastersCount"></span>)</span>
              </button>
              <button class="filter-pill" :class="{ active: masterFilter === 'mineure' }" @click="masterFilter = 'mineure'">
                <span>Avec mineure (<span x-text="mineureMastersCount"></span>)</span>
              </button>
              <button class="filter-pill" :class="{ active: masterFilter === 'passerelle' }" @click="masterFilter = 'passerelle'">
                <span>Autre filière (<span x-text="12 - directMastersCount - mineureMastersCount"></span>)</span>
              </button>
            </div>
          </div>

          <!-- Synthèse officielle calquée sur le panneau #panels de l'étape 2 -->
          <div class="box info" style="margin: 0 0 1.8em 0;">
            <h6>Synth&egrave;se de votre pr&eacute;paration aux 12 Masters d'ing&eacute;nieur civil</h6>
            <div style="margin-bottom: 0.4em;">Sur base de votre parcours (<b><span x-text="acquisEcts"></span> cr&eacute;dits acquis</b> et <b><span x-text="ects[1] + ects[2]"></span> cr&eacute;dits au PAE</b>) :</div>
            <ul>
              <li>
                <b><span x-text="directMastersCount"></span> Master<span x-show="directMastersCount > 1">s</span> en continuit&eacute; directe optimale</b> (&ge; 30 cr&eacute;dits dans le domaine &mdash; options de Master 100% libres)
                <template x-if="directMastersCount > 0">
                  <span class="pill good" x-text="directMastersCount + ' optimal' + (directMastersCount > 1 ? 's' : '')"></span>
                </template>
              </li>
              <li>
                <b><span x-text="mineureMastersCount"></span> Master<span x-show="mineureMastersCount > 1">s</span> en transition all&eacute;g&eacute;e avec mineure</b> (10 &agrave; 25 cr&eacute;dits &mdash; transition fluide)
                <template x-if="mineureMastersCount > 0">
                  <span class="pill mineure-pill" x-text="mineureMastersCount + ' mineure' + (mineureMastersCount > 1 ? 's' : '')"></span>
                </template>
              </li>
              <li>
                <b><span x-text="12 - directMastersCount - mineureMastersCount"></span> Master<span x-show="12 - directMastersCount - mineureMastersCount > 1">s</span> en autre fili&egrave;re</b> (&lt; 10 cr&eacute;dits &mdash; acc&egrave;s direct l&eacute;gal garanti sans Bloc 0, r&eacute;allocation d'options en Master)
              </li>
            </ul>
          </div>

          <!-- Liste des Masters avec hiérarchie officielle : Débouchés, 1. Prérequis, 2. Recommandés, 3. Complémentaires -->
          <div class="masters-container">
            <template x-for="m in filteredMasters" :key="m.id">
              <div class="option master-option">
                <!-- En-tête du Master avec badge officiel -->
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5em; margin-bottom: 0.3em;">
                  <h4 style="margin: 0; font-size: 1.2em; font-weight: bold; color: #111;">
                    <span x-text="m.name"></span>
                  </h4>
                  <span class="pill"
                        :class="{ 'good': m.statusCategory === 'direct', 'mineure-pill': m.statusCategory === 'mineure', 'neutral-pill': m.statusCategory === 'passerelle' }"
                        style="font-size: 12px; font-weight: bold; padding: 3px 10px;"
                        x-text="m.statusBadge"></span>
                </div>

                <!-- Débouchés & Finalités officielles (liens directs cocoon ULiège) -->
                <template x-if="m.finalites && m.finalites.length > 0">
                  <div style="display: flex; flex-wrap: wrap; gap: 0.4em; align-items: center; margin: 0.4em 0 0.8em 0;">
                    <span style="font-size: 11px; font-weight: bold; text-transform: uppercase; color: #666; letter-spacing: 0.4px;">Débouchés &amp; finalités :</span>
                    <template x-for="f in m.finalites" :key="f.url">
                      <a :href="f.url" target="_blank" rel="noopener"
                         class="finalite-chip"
                         title="Consulter le programme officiel et les débouchés sur le catalogue ULiège">
                        <span x-text="f.title"></span>
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-left: 3px; opacity: 0.8;"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                      </a>
                    </template>
                  </div>
                </template>

                <!-- Description & jauge des 30 crédits recommandés dans le domaine -->
                <div class="phase-desc" style="clear: both; margin: 0.2em 0 1.2em 0;">
                  <div style="font-size: 13px; color: #444;"><span style="font-weight: bold; color: #111;" x-text="m.domain"></span> &mdash; <span x-text="m.desc"></span></div>
                  
                  <div style="display: flex; align-items: center; gap: 0.8em; margin-top: 0.6em; flex-wrap: wrap;">
                    <div class="master-gauge-track">
                      <div class="master-gauge-fill"
                           :style="'width: ' + m.progressPct + '%; height: 100%; background-color: ' + (m.totalEcts >= 30 ? '#16a34a' : (m.totalEcts >= 10 ? '#ea580c' : '#94a3b8')) + ';'"></div>
                    </div>
                    <div class="master-gauge-text"
                         :class="m.totalEcts >= 30 ? 'text-success' : (m.totalEcts >= 10 ? 'text-warning' : 'text-neutral')">
                      <span x-text="m.totalEcts"></span> / 30 ECTS recommandés du domaine
                    </div>
                    <!-- Pastilles de synthèse des 3 tiers avec icônes vectorielles SVG -->
                    <div style="display: flex; gap: 0.4em; flex-wrap: wrap; margin-left: auto;">
                      <span class="tier-stat-badge" :class="m.prereqTakenCount === m.prereqTotalCount ? 'stat-good' : (m.prereqTakenCount > 0 ? 'stat-warn' : 'stat-neutral')"
                            title="Cours prérequis indispensables au master">
                        <svg style="width: 12px; height: 12px; flex-shrink: 0;" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M10 1a4.5 4.5 0 0 0-4.5 4.5V9H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2h-.5V5.5A4.5 4.5 0 0 0 10 1Zm3 8V5.5a3 3 0 1 0-6 0V9h6Z" clip-rule="evenodd"/></svg>
                        <span>Prérequis : </span><b x-text="m.prereqTakenCount + ' / ' + m.prereqTotalCount"></b>
                      </span>
                      <span class="tier-stat-badge stat-info"
                            title="Cours fortement recommandés">
                        <svg style="width: 12px; height: 12px; flex-shrink: 0;" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M10.868 2.884c-.321-.772-1.415-.772-1.736 0l-1.83 4.401-4.753.381c-.833.067-1.171 1.107-.536 1.651l3.62 3.102-1.106 4.637c-.194.813.691 1.456 1.405 1.02L10 15.591l4.069 2.485c.713.436 1.598-.207 1.404-1.02l-1.106-4.637 3.62-3.102c.635-.544.297-1.584-.536-1.65l-4.752-.382-1.831-4.401Z" clip-rule="evenodd"/></svg>
                        <span>Recommandés : </span><b x-text="m.recTakenCount + ' / ' + m.recTotalCount"></b>
                      </span>
                      <template x-if="m.compCourses && m.compCourses.length > 0">
                        <span class="tier-stat-badge stat-neutral"
                              title="Cours complémentaires d'autres options suivis">
                          <svg style="width: 12px; height: 12px; flex-shrink: 0;" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z"/></svg>
                          <span>Complémentaires : </span><b x-text="m.compTakenCount + ' / ' + m.compTotalCount"></b>
                        </span>
                      </template>
                    </div>
                  </div>
                </div>

                <!-- 1. Cours prérequis au master -->
                <div class="master-tier-block">
                  <div class="tier-header tier-header-prereq">
                    <span class="tier-icon-badge tier-icon-prereq" aria-hidden="true">
                      <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 1a4.5 4.5 0 0 0-4.5 4.5V9H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2h-.5V5.5A4.5 4.5 0 0 0 10 1Zm3 8V5.5a3 3 0 1 0-6 0V9h6Z" clip-rule="evenodd"/></svg>
                    </span>
                    <span class="tier-title">1. Cours prérequis au master</span>
                    <span class="pill" :class="m.prereqTakenCount === m.prereqTotalCount ? 'good' : (m.prereqTakenCount > 0 ? 'mineure-pill' : 'neutral-pill')" style="font-size: 11px; padding: 1px 7px;">
                      <span x-text="m.prereqTakenCount + ' / ' + m.prereqTotalCount + ' au PAE'"></span>
                    </span>
                    <span class="tier-subtitle">Indispensables pour aborder le master sans lacunes</span>
                  </div>
                  <table>
                    <template x-for="c in m.prereqCourses" :key="c.code">
                      <tr x-id="['mcheck']" :class="{ 'course-selected': c.isSelected, 'course-acquis': c.isAcquis }">
                        <td class="checkbox">
                          <input :id="$id('mcheck')"
                                 type="checkbox"
                                 :disabled="c.isAcquis"
                                 :checked="c.isAcquis || c.isSelected"
                                 @change="toggleMasterCourse(c.code, $event)"
                                 :title="c.isAcquis ? 'Cours déjà validé (étape 1)' : (c.isSelected ? 'Inscrit au PAE (cliquez pour retirer)' : 'Cliquez pour inscrire à votre PAE')"/>
                        </td>
                        <td class="code">
                          <label :for="$id('mcheck')">
                            <a :href="'https://www.programmes.uliege.be/cocoon/20262027/cours/' + c.code + '.html'" target="_blank" rel="noopener" class="course-link" title="Ouvrir la fiche officielle du cours sur le catalogue ULiège" x-text="c.code"></a>
                          </label>
                        </td>
                        <td class="title">
                          <label :for="$id('mcheck')" style="display: flex; align-items: center; justify-content: space-between; width: 100%; cursor: pointer;">
                            <span style="display: inline-flex; align-items: center; gap: 0.4em; flex-wrap: wrap;">
                              <span x-text="c.title"></span>
                              <template x-if="c.bloc">
                                <span class="pill" style="font-size: 10.5px; padding: 1px 5px; background: #eee; color: #444;" x-text="c.bloc"></span>
                              </template>
                              <span x-html="renderReqTags(c.code)"></span>
                            </span>
                            <span style="margin-left: 1.2em; flex-shrink: 0;">
                              <template x-if="c.isAcquis">
                                <span class="status-badge acquis" title="Cours déjà validé les années précédentes">
                                  <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                  <span>Acquis</span>
                                </span>
                              </template>
                              <template x-if="c.isSelected">
                                <span class="status-badge au-pae" title="Cours sélectionné dans votre PAE pour cette année">
                                  <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                  <span>Au PAE</span>
                                </span>
                              </template>
                              <template x-if="!c.isAcquis && !c.isSelected">
                                <span class="status-badge non-suivi" title="Non suivi : ce prérequis devra être rattrapé via vos crédits d'options de Master">
                                  <span>Non suivi</span>
                                </span>
                              </template>
                            </span>
                          </label>
                        </td>
                        <td class="quadri">
                          <label :for="$id('mcheck')" x-text="c.quadri ? 'Q' + c.quadri : ''"></label>
                        </td>
                        <td class="ects">
                          <label :for="$id('mcheck')" x-text="c.ects"></label>
                        </td>
                      </tr>
                    </template>
                  </table>
                </div>

                <!-- 2. Cours fortement recommandés -->
                <template x-if="m.recCourses && m.recCourses.length > 0">
                  <div class="master-tier-block">
                    <div class="tier-header tier-header-rec">
                      <span class="tier-icon-badge tier-icon-rec" aria-hidden="true">
                        <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.868 2.884c-.321-.772-1.415-.772-1.736 0l-1.83 4.401-4.753.381c-.833.067-1.171 1.107-.536 1.651l3.62 3.102-1.106 4.637c-.194.813.691 1.456 1.405 1.02L10 15.591l4.069 2.485c.713.436 1.598-.207 1.404-1.02l-1.106-4.637 3.62-3.102c.635-.544.297-1.584-.536-1.65l-4.752-.382-1.831-4.401Z" clip-rule="evenodd"/></svg>
                      </span>
                      <span class="tier-title">2. Cours fortement recommandés</span>
                      <span class="pill good" style="font-size: 11px; padding: 1px 7px;">
                        <span x-text="m.recTakenCount + ' / ' + m.recTotalCount + ' suivis'"></span>
                      </span>
                      <span class="tier-subtitle">Cours majeurs de l'orientation</span>
                    </div>
                    <table>
                      <template x-for="c in m.recCourses" :key="c.code">
                        <tr x-id="['mcheck']" :class="{ 'course-selected': c.isSelected, 'course-acquis': c.isAcquis }">
                          <td class="checkbox">
                            <input :id="$id('mcheck')"
                                   type="checkbox"
                                   :disabled="c.isAcquis"
                                   :checked="c.isAcquis || c.isSelected"
                                   @change="toggleMasterCourse(c.code, $event)"
                                   :title="c.isAcquis ? 'Cours déjà validé (étape 1)' : (c.isSelected ? 'Inscrit au PAE (cliquez pour retirer)' : 'Cliquez pour inscrire à votre PAE')"/>
                          </td>
                          <td class="code">
                            <label :for="$id('mcheck')">
                              <a :href="'https://www.programmes.uliege.be/cocoon/20262027/cours/' + c.code + '.html'" target="_blank" rel="noopener" class="course-link" title="Ouvrir la fiche officielle du cours sur le catalogue ULiège" x-text="c.code"></a>
                            </label>
                          </td>
                          <td class="title">
                            <label :for="$id('mcheck')" style="display: flex; align-items: center; justify-content: space-between; width: 100%; cursor: pointer;">
                              <span style="display: inline-flex; align-items: center; gap: 0.4em; flex-wrap: wrap;">
                                <span x-text="c.title"></span>
                                <template x-if="c.bloc">
                                  <span class="pill" style="font-size: 10.5px; padding: 1px 5px; background: #eee; color: #444;" x-text="c.bloc"></span>
                                </template>
                                <span x-html="renderReqTags(c.code)"></span>
                              </span>
                              <span style="margin-left: 1.2em; flex-shrink: 0;">
                                <template x-if="c.isAcquis">
                                  <span class="status-badge acquis" title="Cours déjà validé les années précédentes">
                                    <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                    <span>Acquis</span>
                                  </span>
                                </template>
                                <template x-if="c.isSelected">
                                  <span class="status-badge au-pae" title="Cours sélectionné dans votre PAE pour cette année">
                                    <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                    <span>Au PAE</span>
                                  </span>
                                </template>
                                <template x-if="!c.isAcquis && !c.isSelected">
                                  <span class="status-badge non-suivi" title="Non suivi">
                                    <span>Non suivi</span>
                                  </span>
                                </template>
                              </span>
                            </label>
                          </td>
                          <td class="quadri">
                            <label :for="$id('mcheck')" x-text="c.quadri ? 'Q' + c.quadri : ''"></label>
                          </td>
                          <td class="ects">
                            <label :for="$id('mcheck')" x-text="c.ects"></label>
                          </td>
                        </tr>
                      </template>
                    </table>
                  </div>
                </template>

                <!-- 3. Cours d'autres options qui sont complémentaires (accordéon repliable) -->
                <template x-if="m.compCourses && m.compCourses.length > 0">
                  <div class="master-tier-block">
                    <div class="tier-header tier-header-comp" @click="toggleComp(m.id)" style="cursor: pointer;" title="Cliquer pour afficher ou masquer les cours complémentaires">
                      <span class="tier-icon-badge tier-icon-comp" aria-hidden="true">
                        <svg viewBox="0 0 20 20" fill="currentColor"><path d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z"/></svg>
                      </span>
                      <span class="tier-title">3. Cours d'autres options qui sont complémentaires</span>
                      <span class="pill neutral-pill" style="font-size: 11px; padding: 1px 7px;">
                        <span x-text="m.compTakenCount + ' suivi' + (m.compTakenCount > 1 ? 's' : '') + ' / ' + m.compTotalCount"></span>
                      </span>
                      <button type="button" class="tier-toggle-btn" style="margin-left: auto; display: inline-flex; align-items: center; gap: 4px;">
                        <span x-text="showComp[m.id] ? 'Masquer' : 'Afficher (' + m.compCourses.length + ' cours)'"></span>
                        <svg class="tier-chevron-icon" :class="showComp[m.id] ? 'is-open' : ''" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                    <div x-show="showComp[m.id]" x-cloak>
                      <table>
                        <template x-for="c in m.compCourses" :key="c.code">
                          <tr x-id="['mcheck']" :class="{ 'course-selected': c.isSelected, 'course-acquis': c.isAcquis }">
                            <td class="checkbox">
                              <input :id="$id('mcheck')"
                                     type="checkbox"
                                     :disabled="c.isAcquis"
                                     :checked="c.isAcquis || c.isSelected"
                                     @change="toggleMasterCourse(c.code, $event)"
                                     :title="c.isAcquis ? 'Cours déjà validé (étape 1)' : (c.isSelected ? 'Inscrit au PAE (cliquez pour retirer)' : 'Cliquez pour inscrire à votre PAE')"/>
                            </td>
                            <td class="code">
                              <label :for="$id('mcheck')">
                                <a :href="'https://www.programmes.uliege.be/cocoon/20262027/cours/' + c.code + '.html'" target="_blank" rel="noopener" class="course-link" title="Ouvrir la fiche officielle du cours sur le catalogue ULiège" x-text="c.code"></a>
                              </label>
                            </td>
                            <td class="title">
                              <label :for="$id('mcheck')" style="display: flex; align-items: center; justify-content: space-between; width: 100%; cursor: pointer;">
                                <span style="display: inline-flex; align-items: center; gap: 0.4em; flex-wrap: wrap;">
                                  <span x-text="c.title"></span>
                                  <template x-if="c.bloc">
                                    <span class="pill" style="font-size: 10.5px; padding: 1px 5px; background: #eee; color: #444;" x-text="c.bloc"></span>
                                  </template>
                                  <span x-html="renderReqTags(c.code)"></span>
                                </span>
                                <span style="margin-left: 1.2em; flex-shrink: 0;">
                                  <template x-if="c.isAcquis">
                                    <span class="status-badge acquis" title="Cours déjà validé les années précédentes">
                                      <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                      <span>Acquis</span>
                                    </span>
                                  </template>
                                  <template x-if="c.isSelected">
                                    <span class="status-badge au-pae" title="Cours sélectionné dans votre PAE pour cette année">
                                      <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                      <span>Au PAE</span>
                                    </span>
                                  </template>
                                  <template x-if="!c.isAcquis && !c.isSelected">
                                    <span class="status-badge non-suivi" title="Non suivi">
                                      <span>Non suivi</span>
                                    </span>
                                  </template>
                                </span>
                              </label>
                            </td>
                            <td class="quadri">
                              <label :for="$id('mcheck')" x-text="c.quadri ? 'Q' + c.quadri : ''"></label>
                            </td>
                            <td class="ects">
                              <label :for="$id('mcheck')" x-text="c.ects"></label>
                            </td>
                          </tr>
                        </template>
                      </table>
                    </div>
                  </div>
                </template>
              </div>
            </template>
            <template x-if="filteredMasters.length === 0">
              <div style="padding: 2em; text-align: center; color: #777; font-style: italic; background: #fafafa; border: 1px dashed #ccc; border-radius: 4px; margin-top: 1em;">
                Aucun master dans cette cat&eacute;gorie pour l'instant. Cochez des cours dans une option pour d&eacute;bloquer des acc&egrave;s !
              </div>
            </template>
          </div>
        </div>
      </template>"""

    assert old_check_head in src, "Failed to find old_check_head"
    src = src.replace(old_check_head, new_check_head, 1)

    # 10. Lignes du tableau :
    # Utilisation de longcode.substring(0,10) directement pour x-show et :class pour éviter toute erreur de scope
    old_tr = """            <tr x-id="['check']" x-data="{ shortcode: longcode.substring(0,10), c: courses[longcode.substring(0,10)][longcode] }" :class="{ bad: selected[shortcode], unsafe: conflict[shortcode].some(it => selected[it]) }">
              <td class="checkbox"><input :id="$id('check')" @input="updateAgenda" :disabled="loading" x-model="selected[shortcode]" :value="shortcode" type="checkbox"/></td>
              <td class="code"><label :for="$id('check')" x-text="longcode"></label></td>
              <td class="title"><label :for="$id('check')" x-text="c.title"></label></td>
              <td class="quadri"><label :for="$id('check')" x-text="c.quadri ? 'Q'+c.quadri : ''"></label></td>
              <td class="ects"><label :for="$id('check')" x-text="c.ects"></label></td>
            </tr>"""

    new_tr = """            <tr x-id="['check']"
                x-data="{ c: courses[longcode.substring(0,10)][longcode] }"
                x-show="phase == 1 || !acquis[longcode.substring(0,10)]"
                :class="{ bad: phase == 2 && selected[longcode.substring(0,10)], unsafe: phase == 2 && conflict[longcode.substring(0,10)] && conflict[longcode.substring(0,10)].some(it => selected[it]) }">
              <td class="checkbox">
                <input :id="$id('check')"
                       type="checkbox"
                       :disabled="loading"
                       :value="longcode.substring(0,10)"
                       :checked="phase == 1 ? !!acquis[longcode.substring(0,10)] : !!selected[longcode.substring(0,10)]"
                       @change="handleCheck(longcode.substring(0,10), $event)"/>
              </td>
              <td class="code"><label :for="$id('check')" x-text="longcode"></label></td>
              <td class="title">
                <label :for="$id('check')">
                  <span x-text="c.title"></span>
                  <span x-show="phase == 2" x-html="renderReqTags(longcode.substring(0,10))"></span>
                </label>
              </td>
              <td class="quadri"><label :for="$id('check')" x-text="c.quadri ? 'Q'+c.quadri : ''"></label></td>
              <td class="ects"><label :for="$id('check')" x-text="c.ects"></label></td>
            </tr>"""

    assert old_tr in src, "Failed to find old_tr"
    src = src.replace(old_tr, new_tr, 1)

    # Masquer les options et blocs en Phase 3 ou si validés (uniquement dans la section 2)
    old_sec2_bloc = """        <template x-for="bloc in opt.content">
        <div class="bloc">"""
    new_sec2_bloc = """        <template x-for="bloc in opt.content">
        <div class="bloc" x-show="isBlocVisible(bloc)">"""
    assert old_sec2_bloc in src, "Failed to find old_sec2_bloc"
    src = src.replace(old_sec2_bloc, new_sec2_bloc, 1)

    old_sec2_opt = """      <template  x-for="opt in layout.content">
      <div class="option">"""
    new_sec2_opt = """      <template  x-for="opt in layout.content">
      <div class="option" x-show="phase != 3 && isOptionVisible(opt)">"""
    assert old_sec2_opt in src, "Failed to find old_sec2_opt"
    src = src.replace(old_sec2_opt, new_sec2_opt, 1)

    # 11. Panneaux de contrôle pour la phase 2 sous le tableau
    panels_html = """
    <!-- Panneaux officiels de contrôle des exigences (Phase 2) -->
    <div id="panels" x-show="phase == 2 && !showAgenda" x-cloak>
      <template x-if="paeExigences.flags.length">
        <div class="box">
          <h6>D&eacute;rogations de corequis &agrave; d&eacute;clarer au jury</h6>
          <div>Le corequis n'est pas encore acquis&nbsp;: sur le portail d'inscription, cochez la case
               <b>&laquo;&nbsp;d&eacute;rogation de corequis&nbsp;&raquo;</b> pour chacun de ces cours&nbsp;:</div>
          <ul>
            <template x-for="f in paeExigences.flags" :key="f.course">
              <li>
                <b><span x-text="f.course"></span> &mdash; <span x-text="f.title"></span></b>
                <span class="pill" :class="f.allPlanned ? 'good' : 'bad'"
                      x-text="f.allPlanned ? 'corequis dans l’horaire : simple formalité' : 'corequis absent de l’horaire'"></span>
                <br/>
                <span style="opacity:.85; font-size:12.5px;">corequis concern&eacute;&nbsp;:
                  <template x-for="c in f.missing" :key="c.code">
                    <span><code x-text="c.code"></code> <span x-text="c.titre"></span><template x-if="c.planned"><span> (pr&eacute;vu au PAE &check;)</span></template></span>
                  </template>
                </span>
              </li>
            </template>
          </ul>
        </div>
      </template>

      <!-- Dérogations de fin de cycle sur prérequis (RGEE Art. 50, § 5) -->
      <template x-if="paeExigences.derogationsPre.length">
        <div class="box" style="border-left: 4px solid #f9ab00; background: #fffdf6;">
          <h6 style="color: #b06000;">D&eacute;rogations de fin de cycle sur pr&eacute;requis (RGEE Art. 50, &sect;&nbsp;5)</h6>
          <div>Ces cours et leurs pr&eacute;requis sont <b>inscrits simultan&eacute;ment &agrave; votre PAE</b> cette ann&eacute;e. En principe, un pr&eacute;requis doit &ecirc;tre r&eacute;ussi lors d'une ann&eacute;e ant&eacute;rieure, mais <b>en fin de cycle</b>, le jury peut le transformer en <b>co-requis</b> sur d&eacute;cision individuelle&nbsp;:</div>
          <ul style="margin: 0.5em 0;">
            <template x-for="dp in paeExigences.derogationsPre" :key="dp.course + dp.code">
              <li>
                <b><span x-text="dp.course"></span> &mdash; <span x-text="dp.courseTitle"></span></b>
                <span class="pill" style="background: #fef7e0; color: #b06000; border: 1px solid #f9ab00;">D&eacute;rogation fin de cycle requise</span>
                <br/>
                <span style="opacity:.85; font-size:12.5px;">Pr&eacute;requis inscrit en parall&egrave;le au PAE&nbsp;: <code x-text="dp.code"></code> <span x-text="dp.titre"></span></span>
              </li>
            </template>
          </ul>
          <div style="font-size: 12px; color: #666; margin-top: 0.5em; padding-top: 0.4em; border-top: 1px solid rgba(0,0,0,0.08); line-height: 1.45; display: flex; align-items: flex-start; gap: 6px;">
            <svg style="width: 15px; height: 15px; flex-shrink: 0; color: #1a73e8; margin-top: 2px;" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M10.75 16.82A7.462 7.462 0 0 1 15 15.5c.71 0 1.396.098 2.046.282A.75.75 0 0 0 18 15.06v-11a.75.75 0 0 0-.546-.721A9.006 9.006 0 0 0 15 3a8.963 8.963 0 0 0-4.25 1.065V16.82ZM9.25 4.065A8.963 8.963 0 0 0 5 3c-.85 0-1.673.118-2.454.339A.75.75 0 0 0 2 4.06v11a.75.75 0 0 0 .954.722A7.46 7.46 0 0 1 5 15.5c1.579 0 3.042.487 4.25 1.32V4.065Z"/></svg>
            <div><b>Cadre r&eacute;glementaire &amp; d&eacute;marche</b> : Selon l'article 50, &sect;&nbsp;5 du <em>R&egrave;glement g&eacute;n&eacute;ral des &eacute;tudes et des &eacute;valuations (RGEE 2026-2027)</em>, cette demande s'introduit aupr&egrave;s de votre conseiller/&egrave;re acad&eacute;mique. Le jury l'&eacute;value g&eacute;n&eacute;ralement favorablement si votre PAE totalise 180 ECTS (fin de cycle de bachelier), si le pr&eacute;requis se donne au Q1 et le cours au Q2 (ou au m&ecirc;me quadrimestre), s'il a d&eacute;j&agrave; &eacute;t&eacute; suivi ant&eacute;rieurement, et sans conflit horaire.</div>
          </div>
        </div>
      </template>

      <!-- Prérequis manquants stricts (bloquants) -->
      <template x-if="paeExigences.blocking.length">
        <div class="box stop">
          <h6>Pr&eacute;requis manquants (bloquants)</h6>
          <div>Attention&nbsp;: ces cours exigent un pr&eacute;requis qui n'est <b>ni acquis, ni inscrit &agrave; votre PAE</b>&nbsp;:</div>
          <ul>
            <template x-for="b in paeExigences.blocking" :key="b.course + b.code">
              <li><b><span x-text="b.course"></span> &mdash; <span x-text="b.courseTitle"></span></b> exige
                  <code x-text="b.code"></code> <span x-text="b.titre"></span> (absent de vos acquis et de votre PAE).</li>
            </template>
          </ul>
          <div style="font-size: 12px; opacity: 0.9; margin-top: 0.4em; line-height: 1.4;">
            Pour pouvoir solliciter une d&eacute;rogation de fin de cycle aupr&egrave;s du jury (RGEE Art. 50 &sect;&nbsp;5), le cours pr&eacute;requis doit &ecirc;tre obligatoirement ajout&eacute; &agrave; votre PAE.
          </div>
        </div>
      </template>

      <template x-if="listOfSelected.length > 0">
        <div class="box info">
          <h6>Contr&ocirc;le du PAE et des options</h6>
          <div x-html="paeExigences.report"></div>
        </div>
      </template>
      <!-- Espaceur pour que le dernier panneau s'arrête proprement au-dessus du bandeau fixe (3.1em) -->
      <div style="height: 3.6em;" aria-hidden="true"></div>
    </div>
"""
    src = src.replace('<div id="footer">', panels_html + '\n    <div id="footer">', 1)

    # 12. Bandeau inférieur adapté à la phase
    band_start = src.find('<div id="band">')
    band_end = src.find('</div>\n    </div>\n    <div id="agenda">') + 6
    assert band_start != -1 and band_end != -1, "Failed to locate band"

    new_band = """<div id="band">
        <!-- Bandeau Phase 1 -->
        <template x-if="phase == 1">
          <div class="mid">
            <span id="n" x-text="acquisCount + ' cours validé' + (acquisCount > 1 ? 's' : '')">0 cours validé</span>
            <span id="cr">
              <span class="num" x-text="acquisEcts">0</span> crédits acquis
            </span>
            <div id="b" class="actions">
              <button id="voir" @click="phase = 2" style="background-color: var(--c-faculty); color: white;" title="Continuer vers la sélection du PAE">
                <span>Construire mon PAE &rarr;</span>
              </button>
            </div>
          </div>
        </template>

        <!-- Bandeau Phase 2 (Officiel) -->
        <template x-if="phase == 2">
          <div class="mid">
            <span id="n" x-text="numSelectedStr">Aucun cours sélectionné</span>
            <span id="cr">
              <span x-show="ects[1] || ects[2]" x-cloak><span class="num" x-text="ects[1]"></span><span class="q">(Q1)</span> + <span class="num" x-text="ects[2]"></span><span class="q">(Q2)</span> = </span>
              <span class="num" x-text="ects[1] + ects[2]">0</span> crédits
            </span>
            <div id="b" class="actions">
              <button class="alt" @click="phase = 3" title="Voir la préparation vers les 12 masters avec mon PAE" style="color: #ffffff; font-weight: 500;">
                <span>Masters &amp; Débouchés &rarr;</span>
              </button>
              <button id="voir" @click="toggleAgenda" :title="showAgenda ? 'Cliquez ici pour retourner à la liste des cours' : 'Cliquez ici pour afficher l’horaire'">
                <svg fill="currentColor" x-show="!showAgenda"><use href="#calendar-days"/></svg>
                <svg fill="currentColor" x-show="showAgenda" x-cloak><use href="#list-bullet"/></svg>
                <span x-text="showAgenda ? 'Choisir les cours' : 'Voir l’horaire'">Voir l’horaire</span>
              </button>
            </div>
          </div>
        </template>

        <!-- Bandeau Phase 3 -->
        <template x-if="phase == 3">
          <div class="mid">
            <span id="n" x-text="filteredMasters.length + ' Master' + (filteredMasters.length > 1 ? 's' : '') + ' d\'ingénieur civil'">12 Masters d'ingénieur civil</span>
            <div id="b" class="actions">
              <button id="voir" @click="phase = 2" title="Retourner à la composition de mon PAE">
                <span>&larr; Revenir à mon PAE</span>
              </button>
            </div>
            <span id="cr">
              <span class="num" x-text="directMastersCount">0</span> optimale<span x-show="directMastersCount > 1">s</span> &middot; <span class="num" x-text="mineureMastersCount">0</span> mineure<span x-show="mineureMastersCount > 1">s</span>
            </span>
          </div>
        </template>
      </div>"""

    src = src[:band_start] + new_band + src[band_end:]

    # 13. Boutons additionnels dans la popup de partage officielle (Export iCal et Ouvrir sur site officiel)
    share_buttons = """
          <div style="margin-top: 1.2em; display: flex; flex-wrap: wrap; gap: 0.6em; justify-content: center;">
            <button class="actions button" @click="window.open(share.url, '_blank')" style="background-color: var(--c-faculty); color: white; padding: 0.4em 0.8em; border-radius: 4px; font-size: 13px;">
              <svg fill="currentColor" style="width:1.2em; height:1.2em; vertical-align:middle; margin-right:4px;"><use href="#paper-clip"/></svg>
              <span>Ouvrir sur l'horaire officiel ULiège</span>
            </button>
            <button class="actions button alt" @click="exportICalendar()" style="background-color: var(--c-faculty-accent); color: white; padding: 0.4em 0.8em; border-radius: 4px; font-size: 13px;">
              <svg fill="currentColor" style="width:1.2em; height:1.2em; vertical-align:middle; margin-right:4px;"><use href="#calendar-days"/></svg>
              <span>Télécharger agenda (.ics)</span>
            </button>
          </div>
"""
    src = src.replace('<div class="share_icons"', share_buttons + '\n          <div class="share_icons"', 1)

    # 14. Logique JS enrichie dans Alpine.data('app', ...)
    alpine_start = "Alpine.data('app', () => ({"
    assert alpine_start in src, "Cannot find Alpine.data('app')"

    app_logic = """
      // Gestion des trois phases
      phase: (function() {
        try {
          const p = localStorage.getItem('facsa_phase');
          return p ? parseInt(p, 10) : 1;
        } catch(e) { return 1; }
      })(),
      acquis: (function() {
        try {
          const raw = localStorage.getItem('facsa_acquis');
          return raw ? JSON.parse(raw) : {};
        } catch(e) { return {}; }
      })(),

      // Accordéon des cours complémentaires en Section 3
      showComp: {},
      toggleComp(masterId) {
        this.showComp[masterId] = !this.showComp[masterId];
      },

      // Données de référence
      get COREQUIS() { return window.__COREQUIS__ || {}; },
      get DOMAINES() { return window.__DOMAINES__ || {}; },
      get ECTS_MAP() { return window.__ECTS__ || {}; },
      get BLOC1() { return window.__BLOC1__ || []; },
      get BLOC2() { return window.__BLOC2__ || []; },
      get MASTERS() { return window.__MASTERS__ || []; },

      // Getters acquis
      get acquisCount() {
        return Object.values(this.acquis).filter(Boolean).length;
      },
      get acquisEcts() {
        let tot = 0;
        for (const [code, val] of Object.entries(this.acquis)) {
          if (val) tot += (this.ECTS_MAP[code] || 0);
        }
        return Math.round(tot * 2) / 2;
      },

      // Visibilité des éléments
      isCourseVisibleInPhase(shortcode) {
        if (this.phase == 1) return true;
        return !this.acquis[shortcode];
      },
      isBlocVisible(bloc) {
        if (this.phase == 1) return true;
        if (!bloc || !bloc.list) return false;
        return bloc.list.some(c => !this.acquis[c.substring(0, 10)]);
      },
      isOptionVisible(opt) {
        if (this.phase == 1) return true;
        if (!opt || !opt.content) return false;
        return opt.content.some(b => b.list && b.list.some(c => !this.acquis[c.substring(0, 10)]));
      },

      // Gestion des clics sur les cases à cocher
      handleCheck(shortcode, event) {
        const checked = event.target.checked;
        if (this.phase === 1) {
          this.acquis[shortcode] = checked;
          this.saveStorage();
        } else {
          this.selected[shortcode] = checked;
          this.updateAgenda({ target: { value: shortcode, checked: checked } });
          this.updateEcts();
          this.saveStorage();
        }
      },
      toggleMasterCourse(shortcode, event) {
        const checked = event.target.checked;
        this.selected[shortcode] = checked;
        this.updateAgenda({ target: { value: shortcode, checked: checked } });
        this.updateEcts();
        this.saveStorage();
      },

      // Méthodes pour la phase 1 (sélectionne uniquement les cours obligatoires)
      setPreset(kind) {
        if (kind === 'b1') {
          this.acquis = {};
          for (const c of this.BLOC1) this.acquis[c] = true;
        } else if (kind === 'b1_b2') {
          this.acquis = {};
          for (const c of this.BLOC1) this.acquis[c] = true;
          for (const c of this.BLOC2) this.acquis[c] = true;
        }
        this.refreshMasterOrder();
        this.saveStorage();
      },
      resetAcquis() {
        this.acquis = {};
        this.refreshMasterOrder();
        this.saveStorage();
      },
      saveStorage() {
        try {
          localStorage.setItem('facsa_phase', String(this.phase));
          localStorage.setItem('facsa_acquis', JSON.stringify(this.acquis));
          localStorage.setItem('facsa_selected', JSON.stringify(this.listOfSelected));
        } catch(e) {}
      },

      // Rendu des tags de prérequis et corequis : pastilles rondes discrètes avec tooltip
      renderReqTags(shortcode) {
        const info = this.COREQUIS[shortcode];
        if (!info) return '';
        let tags = '';

        // Prérequis
        for (const p of (info.pre || [])) {
          const pc = p.code.substring(0, 10);
          const isAcq = !!this.acquis[pc];
          const isSel = !!this.selected[pc];
          if (isAcq) {
            tags += `<span class="req-dot pre-ok" title="Prérequis validé : ${p.code} ${p.title}">P</span>`;
          } else if (isSel) {
            tags += `<span class="req-dot pre-warn" title="[Dérogation RGEE Art. 50 § 5] Prérequis inscrit au PAE en parallèle : requiert une dérogation de fin de cycle pour transformation en co-requis : ${p.code} ${p.title}">P</span>`;
          } else {
            tags += `<span class="req-dot pre-bad" title="[Bloquant] Prérequis non acquis et absent du PAE : ${p.code} ${p.title}">P</span>`;
          }
        }

        // Corequis
        for (const c of (info.coreq || [])) {
          const cc = c.code.substring(0, 10);
          const isAcq = !!this.acquis[cc];
          const isSelected = !!this.selected[cc];
          if (isAcq) {
            tags += `<span class="req-dot coreq-ok" title="Corequis validé les années précédentes : ${c.code} ${c.title}">C</span>`;
          } else if (isSelected) {
            tags += `<span class="req-dot coreq-ok" title="Corequis inscrit au PAE pour cette année : ${c.code} ${c.title}">C</span>`;
          } else {
            tags += `<span class="req-dot coreq-warn" title="[Dérogation requise] Dérogation de corequis requise au portail : ${c.code} ${c.title}">C</span>`;
          }
        }

        return tags;
      },

      masterFilter: 'all',
      masterOrder: [],

      // Calcule et mémorise l'ordre de tri des Masters (rafraîchi uniquement au changement de section)
      refreshMasterOrder() {
        const orderMap = { direct: 1, mineure: 2, passerelle: 3 };
        const sorted = [...this.mastersAnalysisRaw].sort((a, b) => {
          if (orderMap[a.statusCategory] !== orderMap[b.statusCategory]) {
            return orderMap[a.statusCategory] - orderMap[b.statusCategory];
          }
          if (b.prereqTakenCount !== a.prereqTakenCount) {
            return b.prereqTakenCount - a.prereqTakenCount;
          }
          return b.totalEcts - a.totalEcts;
        });
        this.masterOrder = sorted.map(m => m.id);
      },

      // Données en direct pour chaque Master avec hiérarchie officielle (sans réordonner l'interface)
      get mastersAnalysisRaw() {
        const res = [];

        for (const m of this.MASTERS) {
          const mapCourse = (code) => {
            const short = code.substring(0, 10);
            const isAcq = !!this.acquis[short];
            const isSel = !isAcq && !!this.selected[short];
            const partimDict = this.courses[short] || {};
            const firstCourse = Object.values(partimDict)[0] || {};
            const ects = this.ECTS_MAP[short] || firstCourse.ects || 0;
            const title = firstCourse.title || (this.COREQUIS[short] ? this.COREQUIS[short].title : code);
            const quadri = firstCourse.quadri || (this.COREQUIS[short] ? this.COREQUIS[short].quadri : null);
            const bInfo = this.COREQUIS[short] ? this.COREQUIS[short].bloc : '';
            const bloc = bInfo === 'B2' ? 'Bloc 2' : (bInfo === 'B3' ? 'Bloc 3' : (bInfo === 'B1' ? 'Bloc 1' : ''));

            return {
              code: short,
              title: title,
              quadri: quadri,
              bloc: bloc,
              ects: ects,
              isAcquis: isAcq,
              isSelected: isSel,
              isTaken: isAcq || isSel
            };
          };

          const prereqCourses = (m.prereq || []).map(mapCourse);
          const recCourses = (m.recommended || []).map(mapCourse);
          const compCourses = (m.complementary || []).map(mapCourse);

          const prereqTakenCount = prereqCourses.filter(c => c.isTaken).length;
          const prereqTotalCount = prereqCourses.length;

          const recTakenCount = recCourses.filter(c => c.isTaken).length;
          const recTotalCount = recCourses.length;

          const compTakenCount = compCourses.filter(c => c.isTaken).length;
          const compTotalCount = compCourses.length;

          // Crédits du domaine : cumul des cours prérequis et fortement recommandés suivis
          let domainEcts = 0;
          for (const c of prereqCourses) {
            if (c.isTaken) domainEcts += c.ects;
          }
          for (const c of recCourses) {
            if (c.isTaken) domainEcts += c.ects;
          }
          domainEcts = Math.round(domainEcts * 2) / 2;

          let category = 'passerelle';
          let badge = 'Autre filière (< 10 cr)';
          if (domainEcts >= 30) {
            category = 'direct';
            badge = 'Continuité optimale (≥ 30 cr)';
          } else if (domainEcts >= 10 || prereqTakenCount >= 2) {
            category = 'mineure';
            badge = 'Transition allégée (10-25 cr)';
          }

          const progress = Math.min(100, Math.round((domainEcts / 30) * 100));

          res.push({
            id: m.id,
            name: m.name,
            domain: m.domain,
            desc: m.desc,
            finalites: m.finalites || [],
            totalEcts: domainEcts,
            progressPct: progress,
            statusCategory: category,
            statusBadge: badge,
            prereqCourses: prereqCourses,
            prereqTakenCount: prereqTakenCount,
            prereqTotalCount: prereqTotalCount,
            recCourses: recCourses,
            recTakenCount: recTakenCount,
            recTotalCount: recTotalCount,
            compCourses: compCourses,
            compTakenCount: compTakenCount,
            compTotalCount: compTotalCount,
            allCourses: [...prereqCourses, ...recCourses],
            takenCourses: [...prereqCourses, ...recCourses].filter(c => c.isTaken),
            missingCourses: [...prereqCourses, ...recCourses].filter(c => !c.isTaken)
          });
        }

        return res;
      },

      // Liste des Masters : respecte strictement masterOrder afin de ne pas faire sauter l'interface en section 3
      get mastersAnalysis() {
        const raw = this.mastersAnalysisRaw;
        if (!this.masterOrder || this.masterOrder.length !== raw.length) {
          const orderMap = { direct: 1, mineure: 2, passerelle: 3 };
          return [...raw].sort((a, b) => {
            if (orderMap[a.statusCategory] !== orderMap[b.statusCategory]) {
              return orderMap[a.statusCategory] - orderMap[b.statusCategory];
            }
            if (b.prereqTakenCount !== a.prereqTakenCount) {
              return b.prereqTakenCount - a.prereqTakenCount;
            }
            return b.totalEcts - a.totalEcts;
          });
        }
        const dict = {};
        for (const item of raw) dict[item.id] = item;
        return this.masterOrder.map(id => dict[id]).filter(Boolean);
      },

      get filteredMasters() {
        if (this.masterFilter === 'direct') {
          return this.mastersAnalysis.filter(m => m.statusCategory === 'direct');
        }
        if (this.masterFilter === 'mineure') {
          return this.mastersAnalysis.filter(m => m.statusCategory === 'mineure');
        }
        if (this.masterFilter === 'passerelle') {
          return this.mastersAnalysis.filter(m => m.statusCategory === 'passerelle');
        }
        return this.mastersAnalysis;
      },

      get directMastersCount() {
        return this.mastersAnalysis.filter(m => m.statusCategory === 'direct').length;
      },

      get mineureMastersCount() {
        return this.mastersAnalysis.filter(m => m.statusCategory === 'mineure').length;
      },

      get mastersSummaryText() {
        const d = this.directMastersCount;
        const m = this.mineureMastersCount;
        if (d > 0 && m > 0) return `${d} en continuité directe & ${m} avec mineure`;
        if (d > 0) return `${d} master${d > 1 ? 's' : ''} en continuité directe optimale`;
        if (m > 0) return `${m} master${m > 1 ? 's' : ''} accessible${m > 1 ? 's' : ''} avec mineure`;
        return "Accès direct garanti aux 12 masters (réallocation d'options en master)";
      },

      toggleMasterCourse(shortcode, event) {
        if (this.acquis[shortcode]) {
          if (event && event.target) event.target.checked = true;
          return;
        }
        const checked = event && event.target ? event.target.checked : !this.selected[shortcode];
        this.selected[shortcode] = checked;
        this.updateAgenda({ target: { value: shortcode, checked: checked } });
        this.updateEcts();
        this.saveStorage();
      },

      addCourseToPae(shortcode) {
        this.toggleMasterCourse(shortcode, { target: { checked: true } });
      },

      // Calcul disjoint et rigoureux des options majeure (>= 30 cr) et mineure (>= 10 cr)
      computeDisjointOptions() {
        const clean = (d) => d.replace(/^Domaine (?:de |des |du )?/, '').replace(/^du du /, 'du ');
        
        // Tous les cours d'options pris (actuellement au PAE + déjà acquis)
        const optCoursesMap = {};
        const addOptCourse = (code, isAcq, isSel) => {
          const ds = this.DOMAINES[code] || [];
          if (!ds.length) return;
          const e = this.ECTS_MAP[code] || 0;
          const cleanDomains = [...new Set(ds.map(d => clean(d[0])))];
          optCoursesMap[code] = {
            code,
            ects: e,
            domains: cleanDomains,
            isAcquis: isAcq,
            isSelected: isSel
          };
        };

        for (const code of this.listOfSelected) addOptCourse(code, false, true);
        for (const [code, val] of Object.entries(this.acquis)) {
          if (val && !optCoursesMap[code]) addOptCourse(code, true, false);
        }

        const optCourses = Object.values(optCoursesMap);
        if (!optCourses.length) {
          return {
            hasOptions: false,
            entries: [],
            major: null,
            minor: null,
            sharedCourses: []
          };
        }

        // Domaines représentés et totaux bruts
        const allDomains = new Set();
        const rawByDomain = {};
        for (const c of optCourses) {
          for (const d of c.domains) {
            allDomains.add(d);
            rawByDomain[d] = (rawByDomain[d] || 0) + c.ects;
          }
        }
        const domainList = Array.from(allDomains);
        const entries = Object.entries(rawByDomain).sort((a, b) => b[1] - a[1]);

        if (domainList.length === 1) {
          const d = domainList[0];
          const tot = rawByDomain[d];
          return {
            hasOptions: true,
            entries: entries,
            major: { domain: d, ects: tot, isSatisfied: tot >= 30, courses: optCourses },
            minor: null,
            sharedCourses: []
          };
        }

        // Trouver la meilleure paire disjointe (dMaj, dMin)
        let bestPair = null;
        let bestScore = -1;

        for (let i = 0; i < domainList.length; i++) {
          for (let j = 0; j < domainList.length; j++) {
            if (i === j) continue;
            const dMaj = domainList[i];
            const dMin = domainList[j];

            const pureMaj = [];
            const pureMin = [];
            const shared = [];

            for (const c of optCourses) {
              const inMaj = c.domains.includes(dMaj);
              const inMin = c.domains.includes(dMin);
              if (inMaj && inMin) shared.push(c);
              else if (inMaj) pureMaj.push(c);
              else if (inMin) pureMin.push(c);
            }

            const pureMajEcts = pureMaj.reduce((s, c) => s + c.ects, 0);
            const pureMinEcts = pureMin.reduce((s, c) => s + c.ects, 0);

            let optMajEcts = pureMajEcts;
            let optMinEcts = pureMinEcts;
            let optMajCourses = [...pureMaj];
            let optMinCourses = [...pureMin];

            if (shared.length > 0) {
              let bestSubScore = -1;
              const totalSub = 1 << Math.min(shared.length, 12);
              for (let mask = 0; mask < totalSub; mask++) {
                let curMajE = pureMajEcts;
                let curMinE = pureMinEcts;
                for (let k = 0; k < shared.length; k++) {
                  if ((mask & (1 << k)) !== 0) curMajE += shared[k].ects;
                  else curMinE += shared[k].ects;
                }
                let s = 0;
                if (curMajE >= 30 && curMinE >= 10) s = 10000 + curMajE + curMinE;
                else if (curMajE >= 30) s = 5000 + curMinE;
                else if (curMinE >= 10) s = 2000 + curMajE;
                else s = curMajE * 2 + curMinE;

                if (s > bestSubScore) {
                  bestSubScore = s;
                  optMajEcts = curMajE;
                  optMinEcts = curMinE;
                  optMajCourses = [...pureMaj];
                  optMinCourses = [...pureMin];
                  for (let k = 0; k < shared.length; k++) {
                    if ((mask & (1 << k)) !== 0) optMajCourses.push(shared[k]);
                    else optMinCourses.push(shared[k]);
                  }
                }
              }
            }

            let pairScore = 0;
            if (optMajEcts >= 30 && optMinEcts >= 10) pairScore = 20000 + optMajEcts + optMinEcts;
            else if (optMajEcts >= 30) pairScore = 10000 + optMinEcts;
            else if (optMinEcts >= 10) pairScore = 5000 + optMajEcts;
            else pairScore = optMajEcts * 2 + optMinEcts;

            if (pairScore > bestScore) {
              bestScore = pairScore;
              bestPair = {
                major: { domain: dMaj, ects: optMajEcts, isSatisfied: optMajEcts >= 30, courses: optMajCourses },
                minor: { domain: dMin, ects: optMinEcts, isSatisfied: optMinEcts >= 10, courses: optMinCourses },
                sharedCourses: shared,
                rawMajEcts: rawByDomain[dMaj],
                rawMinEcts: rawByDomain[dMin]
              };
            }
          }
        }

        return {
          hasOptions: true,
          entries: entries,
          major: bestPair ? bestPair.major : null,
          minor: bestPair ? bestPair.minor : null,
          sharedCourses: bestPair ? bestPair.sharedCourses : [],
          rawMajEcts: bestPair ? bestPair.rawMajEcts : 0,
          rawMinEcts: bestPair ? bestPair.rawMinEcts : 0
        };
      },

      // Analyse globale des exigences et spécialisations pour la phase 2
      get paeExigences() {
        const sel = this.listOfSelected;
        const selSet = new Set(sel);
        const flags = [];
        const blocking = [];
        const derogationsPre = [];

        for (const code of sel) {
          const info = this.COREQUIS[code];
          if (!info) continue;

          // Corequis manquants parmi les acquis
          const missC = (info.coreq || []).filter(c => !this.acquis[c.code.substring(0, 10)]);
          if (missC.length) {
            flags.push({
              course: code,
              title: info.title,
              allPlanned: missC.every(c => selSet.has(c.code.substring(0, 10))),
              missing: missC.map(c => ({
                code: c.code,
                titre: c.title,
                planned: selSet.has(c.code.substring(0, 10))
              })),
            });
          }

          // Prérequis
          for (const p of (info.pre || [])) {
            const pc = p.code.substring(0, 10);
            if (!this.acquis[pc]) {
              if (selSet.has(pc)) {
                // Inscrit en parallèle au PAE : dérogation fin de cycle requise (RGEE Art. 50 § 5)
                derogationsPre.push({
                  course: code,
                  courseTitle: info.title,
                  code: p.code,
                  titre: p.title
                });
              } else {
                // Non acquis et absent du PAE : bloquant strict
                blocking.push({
                  course: code,
                  courseTitle: info.title,
                  code: p.code,
                  titre: p.title
                });
              }
            }
          }
        }

        // Analyse disjointe des options par domaine
        const optAnalysis = this.computeDisjointOptions();
        const e1 = this.ects[1] || 0;
        const e2 = this.ects[2] || 0;
        const tot = Math.round((e1 + e2) * 2) / 2;

        let h = 'Total PAE&nbsp;: <b>' + tot + '</b> cr&eacute;dits (Q1 = ' + e1 + ' cr &middot; Q2 = ' + e2 + ' cr)';

        if (optAnalysis.hasOptions && optAnalysis.entries.length) {
          h += '<br/>Cr&eacute;dits d\\'options par domaine&nbsp;: '
             + optAnalysis.entries.map(([d, v]) => d + '&nbsp;=&nbsp;<b>' + v + '</b>').join(' &middot; ');
          
          if (optAnalysis.major) {
            const maj = optAnalysis.major;
            h += '<br/>Option principale&nbsp;: ' + (maj.isSatisfied
                  ? '<span class="pill good">' + maj.domain + ' : ' + maj.ects + ' cr (&ge; 30)</span>'
                  : '<span class="pill bad">' + maj.domain + ' : ' + maj.ects + ' cr (&lt; 30)</span>');
          }
          if (optAnalysis.minor && optAnalysis.minor.domain) {
            const min = optAnalysis.minor;
            h += ' &nbsp;Mineure secondaire&nbsp;: ' + (min.isSatisfied
                  ? '<span class="pill good">' + min.domain + ' : ' + min.ects + ' cr distincts (&ge; 10)</span>'
                  : '<span class="pill bad">' + min.domain + ' : ' + min.ects + ' cr distincts (&lt; 10)</span>');
          } else {
            h += ' &nbsp;Mineure secondaire&nbsp;: <span class="pill bad">aucun 2<sup>e</sup> domaine distinct</span>';
          }

          // Avertissement explicite de non-cumul si des cours sont partagés entre les deux options sélectionnées
          if (optAnalysis.sharedCourses && optAnalysis.sharedCourses.length > 0 && optAnalysis.major && optAnalysis.minor) {
            const sharedList = optAnalysis.sharedCourses.map(c => '<code>' + c.code + '</code>').join(', ');
            h += '<div style="margin-top: 0.6em; padding: 0.5em 0.8em; background: #fffdf4; border-left: 3px solid #f9ab00; border-radius: 3px; font-size: 12.5px; line-height: 1.45;">'
               + '<div style="display:flex;align-items:flex-start;gap:6px;margin-bottom:4px;"><svg style="width:15px;height:15px;flex-shrink:0;color:#b06000;margin-top:1px;" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495ZM10 5a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 10 5Zm0 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clip-rule="evenodd" /></svg><b>R&egrave;gle facultaire de non-cumul (cours partag&eacute;s)&nbsp;:</b></div>'
               + 'Le(s) cours ' + sharedList + ' appartien(nen)t simultan&eacute;ment &agrave; <em>' + optAnalysis.major.domain + '</em> et <em>' + optAnalysis.minor.domain + '</em>. '
               + 'Au PAE, chaque cours doit &ecirc;tre allou&eacute; &agrave; <b>une seule option</b>.<br/>'
               + 'En les allouant &agrave; votre majeure (' + optAnalysis.major.ects + ' cr), votre mineure ne dispose que de <b>' + optAnalysis.minor.ects + ' cr distincts</b>'
               + (optAnalysis.minor.ects < 10 ? ' (<b>insuffisant</b>&nbsp;: 10 cr distincts requis).' : ' (&ge; 10 cr &check;).')
               + '</div>';
          }
        }

        return { flags, blocking, derogationsPre, report: h };
      },

      // Export calendrier (.ics)
      exportICalendar() {
        let ics = [
          'BEGIN:VCALENDAR',
          'VERSION:2.0',
          'PRODID:-//ULiege FACSA//PAE Planificateur//FR',
          'CALSCALE:GREGORIAN',
          'METHOD:PUBLISH',
          'X-WR-CALNAME:Horaire PAE FACSA',
          'X-WR-TIMEZONE:Europe/Brussels'
        ];

        const q1Base = new Date(2026, 8, 14);
        const q1Until = '20261219T235959Z';
        const q2Base = new Date(2027, 1, 1);
        const q2Until = '20270515T235959Z';

        const pad = (n) => String(n).padStart(2, '0');
        const formatDt = (d, h, m) => `${d.getFullYear()}${pad(d.getMonth()+1)}${pad(d.getDate())}T${pad(h)}${pad(m)}00`;
        const days = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];

        for (const short of this.listOfSelected) {
          const partimDict = this.courses[short] || {};
          for (const [longCode, course] of Object.entries(partimDict)) {
            const quadri = course.quadri;
            const baseDate = quadri === 1 ? q1Base : q2Base;
            const until = quadri === 1 ? q1Until : q2Until;

            for (const slot of (course.slots || [])) {
              if (slot.day > 4) continue;
              const eventDate = new Date(baseDate);
              eventDate.setDate(baseDate.getDate() + slot.day);

              const dtStart = formatDt(eventDate, slot.start.h, slot.start.m);
              const dtEnd = formatDt(eventDate, slot.end.h, slot.end.m);

              ics.push('BEGIN:VEVENT');
              ics.push(`UID:${longCode}-${quadri}-${slot.day}-${slot.start.h}${slot.start.m}@facsa.uliege`);
              ics.push(`DTSTAMP:${formatDt(new Date(), 12, 0)}Z`);
              ics.push(`DTSTART;TZID=Europe/Brussels:${dtStart}`);
              ics.push(`DTEND;TZID=Europe/Brussels:${dtEnd}`);
              ics.push(`RRULE:FREQ=WEEKLY;UNTIL=${until};BYDAY=${days[slot.day]}`);
              ics.push(`SUMMARY:${course.code.substring(0,10)} : ${course.title}`);
              ics.push(`DESCRIPTION:Professeur: ${course.prof || 'Non renseigne'}\\nQuadrimestre: Q${quadri}\\nCredits: ${course.ects || 0} ECTS`);
              ics.push('LOCATION:Campus ULiege Sart Tilman');
              ics.push('END:VEVENT');
            }
          }
        }

        ics.push('END:VCALENDAR');
        const blob = new Blob([ics.join('\\r\\n')], { type: 'text/calendar;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'horaire_facsa.ics';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      },
"""
    src = src.replace(alpine_start, alpine_start + "\n" + app_logic, 1)

    # 15. Sauvegarde automatique
    restore_hook = """
        // Restauration de la sélection depuis localStorage si pas de hash d'URL
        if (!window.location.hash) {
          try {
            const savedSel = JSON.parse(localStorage.getItem('facsa_selected') || '[]');
            if (Array.isArray(savedSel)) {
              for (const code of savedSel) {
                if (code in this.courses) {
                  this.selected[code] = true;
                  this.updateAgenda({ target: { value: code, checked: true } });
                }
              }
            }
          } catch(e) {}
        }
        this.$watch('selected', () => {
          this.updateEcts();
          this.saveStorage();
        });
        this.$watch('phase', () => {
          this.refreshMasterOrder();
          this.saveStorage();
        });
        this.refreshMasterOrder();
"""
    src = src.replace("this.$watch('selected', () => this.updateEcts());", restore_hook, 1)

    return src

if __name__ == "__main__":
    html = build()
    out_root = os.path.join(BASE, "index.html")
    out_hor = os.path.join(HOR, "index.html")

    with open(out_root, "w", encoding="utf-8") as f:
        f.write(html)
    with open(out_hor, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Généré avec succès (UI officielle 100% respectée) :")
    print(f" - {out_root} ({len(html)} octets)")
    print(f" - {out_hor} ({len(html)} octets)")
