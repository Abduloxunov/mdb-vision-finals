"""Whole-car assessment: several photos of one vehicle -> combined damage report.

Two applications share this flow:
- sell:  a seller uploads photos; buyers get a condition report listing every detected damage.
- fleet: a driver sends photos and/or describes a problem; the report gives urgency and who to contact.
"""
import base64, io, json, math, re, time
import retrieve
import openrouter_client
from pipeline import LABELS, ROOT

MODES = {'sell', 'fleet'}
VIEWS = ('front', 'rear', 'left', 'right', 'interior', 'other')
MAX_PHOTOS = 10
# Damage class -> component used for retrieval. Shown to the user as a suggestion, not a confirmed fact.
LABEL_PART = {'dent': 'body', 'scratch': 'body', 'crack': 'body', 'lamp broken': 'lamp', 'tire flat': 'tire'}
URGENCY_RANK = {'stop_engine': 5, 'emergency_if_hazard': 5, 'stop_and_assess': 4,
                'prompt_inspection': 3, 'inspect': 2, 'precaution': 1}
VERDICTS = {
    'red': ('Stop and get help', 'At least one finding is serious if its condition is confirmed. Do not keep driving until it is checked.'),
    'orange': ('Get it inspected soon', 'Findings need a professional inspection before they get worse.'),
    'green': ('Plan a routine check', 'Findings look cosmetic or minor, but a mechanic should confirm.'),
    'none': ('No damage detected', 'No supported damage was found at this sensitivity. Hidden faults are still possible.'),
}
# Repair type keywords -> published service names in kb/workshops.md.
SERVICE_HINTS = [('body', 'Body repair'), ('paint', 'Body repair'), ('glass', 'Glass replacement'), ('windscreen', 'Glass replacement'),
                 ('dent', 'Body repair'), ('bumper', 'Body repair'), ('lamp', 'Body repair'),
                 ('tyre', 'Tyre fitting'), ('tire', 'Tyre fitting'), ('wheel', 'Alignment'),
                 ('electr', 'Electrical diagnostics'), ('charg', 'Electrical diagnostics'),
                 ('engine', 'Maintenance'), ('cool', 'Maintenance'), ('brake', 'Maintenance'), ('fluid', 'Maintenance')]
CHEVROLET = ('chevrolet', 'cobalt', 'nexia', 'lacetti', 'gentra', 'damas', 'spark', 'malibu', 'tracker', 'onix', 'captiva', 'labo')


def decode(encoded):
    from PIL import Image, ImageOps, UnidentifiedImageError
    if not isinstance(encoded, str) or not encoded or len(encoded) > 12 * 1024 * 1024:
        raise ValueError('Each photo must be under 8 MB.')
    if ',' in encoded:
        encoded = encoded.split(',', 1)[1]
    try:
        raw = base64.b64decode(encoded, validate=True)
        if len(raw) > 8 * 1024 * 1024:
            raise ValueError('Each photo must be under 8 MB.')
        with Image.open(io.BytesIO(raw)) as source:
            if source.format not in {'JPEG', 'PNG', 'WEBP'}:
                raise ValueError('Use JPEG, PNG or WebP photos.')
            if source.width * source.height > 24000000:
                raise ValueError('A photo has too many pixels; resize it first.')
            image = ImageOps.exif_transpose(source).convert('RGB')
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, base64.binascii.Error):
        raise ValueError('A photo could not be read. Use JPEG, PNG or WebP.') from None
    if min(image.size) < 96:
        raise ValueError('A photo is too small (needs at least 96 pixels per side).')
    image.thumbnail((1600, 1600))
    return image


def part_for(label, view):
    if label == 'glass shatter':
        return 'windshield' if view in {'front', 'rear'} else 'side_window'
    return LABEL_PART[label]


def brand_of(vehicle):
    v = vehicle.casefold()
    if 'byd' in v:
        return 'BYD'
    if any(name in v for name in CHEVROLET):
        return 'Chevrolet'
    return ''


def workshops(evidence, vehicle):
    entries = retrieve.blocks(retrieve.BASE / 'workshops.md')
    wanted = {service for r in evidence for key, service in SERVICE_HINTS if key in r['repair_type'].casefold()}
    brand = brand_of(vehicle)
    ranked = []
    for w in entries:
        services = set(w.get('published_services') or [])
        score = 2 * len(services & wanted) + (3 if brand and brand in w.get('brands', []) else 0)
        if brand and brand not in w.get('brands', []):
            continue
        if score:
            ranked.append((score, w))
    ranked.sort(key=lambda item: (-item[0], item[1]['id']))
    return [{'id': w['id'], 'name': w['name'], 'kind': w['kind'], 'brands': w.get('brands', []),
             'address': w.get('address', ''), 'phone': w.get('phone', ''),
             'services': w.get('published_services') or [], 'matched': sorted(set(w.get('published_services') or []) & wanted),
             'source_id': w.get('source_id', ''), 'limitations': w.get('limitations', '')} for _, w in ranked[:3]]


def technicians(evidence, vehicle, findings):
    """Synthetic demo technicians with coordinates, matched by needed service; the browser sorts by distance."""
    path = retrieve.BASE / 'demo-technicians.json'
    if not path.is_file():
        return []
    wanted = {service for r in evidence for key, service in SERVICE_HINTS if key in r['repair_type'].casefold()}
    labels = {d['label'] for d in findings}
    if labels & {'dent', 'scratch', 'crack', 'lamp broken'}:
        wanted.add('Body repair')
    if 'glass shatter' in labels:
        wanted.add('Glass replacement')
    if 'tire flat' in labels:
        wanted.add('Tyre fitting')
    brand = brand_of(vehicle)
    out = []
    for t in json.loads(path.read_text(encoding='utf-8'))['technicians']:
        matched = sorted(set(t['services']) & wanted)
        if not matched or (t['brands'] and brand not in t['brands']):
            continue
        out.append({**t, 'matched': matched, 'demo': True})
    return out


def verdict(evidence, findings):
    if not evidence:
        key = 'none' if not findings else 'orange'
    else:
        top = max(URGENCY_RANK.get(r['urgency']['level'], 2) for r in evidence)
        key = 'red' if top >= 4 else 'orange' if top >= 3 else 'green'
    title, text = VERDICTS[key]
    if key == 'orange' and not evidence:
        text = 'Damage was detected but no matching guidance was found. Have it inspected.'
    worst = max(evidence, key=lambda r: URGENCY_RANK.get(r['urgency']['level'], 2)) if evidence else None
    return {'level': key, 'title': title, 'text': text,
            'driver_condition': worst['urgency']['condition'] if worst else '',
            'first_action': worst['actions'][0] if worst and worst['actions'] else '',
            'repair_type': worst['repair_type'] if worst else '',
            'basis': 'Highest source-informed urgency among matched records; not a calibrated severity prediction.'}


def canonical_vehicle(vehicle, records):
    """'Chevrolet Cobalt 2021' -> 'Cobalt' when a record is scoped to that model name."""
    v = vehicle.casefold()
    models = sorted({m for r in records for m in r['scope']['vehicle_models']}, key=len, reverse=True)
    return next((m for m in models if re.search(r'\b' + re.escape(m.casefold()) + r'\b', v)), vehicle)


def expand_query(query, records):
    """Add knowledge-base terms that a typed word starts with ('overheating' -> 'overheat')."""
    vocab = {t for r in records for term in r['search_terms'] for t in retrieve.tokens(term) if len(t) >= 4}
    words = retrieve.tokens(query)
    extra = sorted({t for w in words for t in vocab if w != t and w.startswith(t)})
    return query + (' ' + ' '.join(extra) if extra else '')


class Assessor:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def lookup(self, query, **params):
        """Hybrid retrieval with a keyword fallback so a missing vector index never breaks a check."""
        try:
            if self.pipeline.retriever is None:
                from vector_store import VectorKB
                self.pipeline.retriever = VectorKB()
            return self.pipeline.retriever.query(query, **params), 'hybrid'
        except (RuntimeError, OSError, ImportError):
            return retrieve.retrieve(query, **params), 'keyword_fallback'

    def assess(self, data):
        if not self.pipeline.lock.acquire(blocking=False):
            raise BlockingIOError('Another check is running. Please try again in a few seconds.')
        try:
            return self._assess(data)
        finally:
            self.pipeline.lock.release()

    def _assess(self, data):
        start = time.perf_counter()
        if not isinstance(data, dict):
            raise ValueError('Expected an object.')
        mode = data.get('mode', 'sell')
        if mode not in MODES:
            raise ValueError('Choose Sell / Buy or Fleet mode.')
        query = data.get('query', '')
        if not isinstance(query, str) or len(query) > 2000:
            raise ValueError('Describe the problem in at most 2,000 characters.')
        vehicle = data.get('vehicle', '')
        propulsion = data.get('propulsion', '')
        part = data.get('part', '')
        if not isinstance(vehicle, str) or len(vehicle) > 100:
            raise ValueError('Vehicle name is too long.')
        if propulsion not in retrieve.PROPULSIONS | {''}:
            raise ValueError('Choose a valid propulsion.')
        if part not in retrieve.PARTS | {''}:
            raise ValueError('Choose a valid component.')
        context = data.get('context', {})
        if not isinstance(context, dict) or set(context) - {'engine_running', 'parking_brake_released'} or any(not isinstance(v, bool) for v in context.values()):
            raise ValueError('Use yes/no engine and parking-brake answers.')
        if not isinstance(data.get('use_llm', False), bool):
            raise ValueError('Invalid explanation choice.')
        threshold = data.get('threshold', 0.35)
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold) or not 0.1 <= threshold <= 0.9:
            raise ValueError('Sensitivity must be between 0.1 and 0.9.')
        photos = data.get('photos', [])
        if not isinstance(photos, list) or len(photos) > MAX_PHOTOS:
            raise ValueError(f'Upload at most {MAX_PHOTOS} photos.')
        if not photos and not query.strip():
            raise ValueError('Add photos or describe the problem.')

        images = []
        for i, photo in enumerate(photos):
            if not isinstance(photo, dict) or photo.get('view', 'other') not in VIEWS:
                raise ValueError('Choose a side for every photo.')
            try:
                images.append((decode(photo.get('image', '')), photo.get('view', 'other')))
            except ValueError as exc:
                raise ValueError(f'Photo {i + 1}: {exc}') from None

        cv_start = time.perf_counter()
        results, findings = [], []
        detector = self.pipeline.model() if images else None
        for i, (image, view) in enumerate(images):
            prediction = detector.predict(image, threshold=threshold)
            boxes = []
            for box, score, cid in zip(prediction.xyxy, prediction.confidence, prediction.class_id):
                cid, score = int(cid), float(score)
                coords = [float(x) for x in box]
                if not 0 <= cid < len(LABELS) or not math.isfinite(score) or not all(math.isfinite(x) for x in coords):
                    continue
                x1, x2 = sorted(max(0, min(image.width, x)) for x in (coords[0], coords[2]))
                y1, y2 = sorted(max(0, min(image.height, y)) for y in (coords[1], coords[3]))
                if x2 <= x1 or y2 <= y1:
                    continue
                d = {'photo': i, 'view': view, 'label': LABELS[cid], 'part': part_for(LABELS[cid], view),
                     'score': round(score, 3), 'box': [round(v, 1) for v in (x1, y1, x2, y2)]}
                boxes.append(d)
            boxes = sorted(boxes, key=lambda d: -d['score'])[:20]
            findings += boxes
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=82)
            results.append({'index': i, 'view': view, 'size': list(image.size), 'detections': boxes,
                            'image': 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode()})
        cv_seconds = time.perf_counter() - cv_start

        # One retrieval per distinct damage type, plus one for the written problem.
        rag_start = time.perf_counter()
        records, all_sources, _ = retrieve.load()
        model_name = canonical_vehicle(vehicle, records)
        search = expand_query(query, records) if query.strip() else query
        common = dict(vehicle=model_name, propulsion=propulsion, confirmed_manual='', context=context)
        requests = {}
        for d in findings:
            requests.setdefault((d['part'], d['label']), search if d['part'] == part else '')
        bundles, methods = [], set()
        for (p, label), text in requests.items():
            bundle, method = self.lookup(text, part=p, vision_label=label, **common)
            bundles.append(bundle); methods.add(method)
        if search.strip() and part:
            bundle, method = self.lookup(search, part=part, **common)
            bundles.append(bundle); methods.add(method)
        if search.strip():
            # Keyword search over every component (or the chosen one); keep only the strongest matches.
            # Records tied to a specific owner's manual are included when the model name matches,
            # but flagged so the user confirms the model year instead of the record being hidden.
            manuals = sorted({r['scope']['confirmed_manual_source'] for r in records
                              if r['scope']['confirmed_manual_source'] and model_name in r['scope']['vehicle_models']})
            text = []
            for p in ([part] if part else sorted(retrieve.PARTS)):
                text.append(retrieve.retrieve(search, part=p, **common))
                for m in manuals:
                    b = retrieve.retrieve(search, part=p, **{**common, 'confirmed_manual': m})
                    b['evidence'] = [{**r, 'manual_unconfirmed': m} for r in b['evidence'] if r['scope']['confirmed_manual_source'] == m]
                    b['questions'] = ([f"Check that your car's model year is covered by: {all_sources[m]['title']}"] if b['evidence']
                                      else [q for q in b['questions'] if not q.startswith('Confirm that manual')])
                    text.append(b)
            best = max((r['retrieval_score'] for b in text for r in b['evidence']), default=0)
            for b in text:
                b['evidence'] = [r for r in b['evidence'] if r['retrieval_score'] >= best * 0.6]
            bundles += text; methods.add('keyword')
        evidence, questions = {}, []
        for b in bundles:
            for r in b['evidence']:
                evidence.setdefault(r['id'], r)
            questions += [q for q in b['questions'] if not q.startswith('Confirm that manual')]
        evidence = sorted(evidence.values(), key=lambda r: (-URGENCY_RANK.get(r['urgency']['level'], 2), -r.get('retrieval_score', 0)))[:8]
        used = {ref['source_id'] for r in evidence for ref in r['source_refs']}
        merged = {'status': 'evidence_found' if evidence else ('needs_context' if questions else 'no_evidence'),
                  'query': query, 'part': part, 'vehicle': model_name, 'propulsion': propulsion, 'context': context,
                  'vision_label': findings[0]['label'] if findings else '', 'questions': list(dict.fromkeys(questions))[:4],
                  'evidence': evidence, 'sources': [all_sources[s] for s in sorted(used) if s in all_sources],
                  'cost_estimate': None, 'limitations': [], 'method': ', '.join(sorted(methods)) or 'none'}
        rag_seconds = time.perf_counter() - rag_start

        llm_start = time.perf_counter()
        explanation = {'status': 'evidence_only', 'api_called': False}
        if data.get('use_llm') and evidence:
            try:
                explanation = openrouter_client.explain(merged)
            except Exception as exc:  # the report must never fail because of the optional LLM
                explanation = {'status': 'deterministic_fallback', 'error': type(exc).__name__}
        llm_seconds = time.perf_counter() - llm_start

        summary = {}
        for d in findings:
            key = (d['view'], d['label'])
            summary[key] = summary.get(key, 0) + 1
        warnings = []
        if images and not findings:
            warnings.append('No supported damage was detected. This does not prove the car is undamaged.')
        if not images:
            warnings.append('Text-only check: no photo was analysed.')
        if any(v == 'interior' for _, v in images):
            warnings.append('The damage model was trained on exterior photos; interior results are less reliable.')
        result = {'mode': mode, 'vehicle': vehicle, 'query': query, 'photos': results,
                  'findings': findings, 'summary': [{'view': v, 'label': l, 'count': c} for (v, l), c in sorted(summary.items())],
                  'views_damaged': sorted({d['view'] for d in findings}), 'views_checked': sorted({v for _, v in images}),
                  'verdict': verdict(evidence, findings), 'evidence': merged, 'explanation': explanation,
                  'workshops': workshops(evidence, vehicle) if (evidence or findings) else [],
                  'technicians': technicians(evidence, vehicle, findings) if (evidence or findings) else [],
                  'warnings': warnings, 'threshold': threshold,
                  'model': {'name': 'RF-DETR Nano (fine-tuned on CarDD)', 'checkpoint': self.pipeline.checkpoint.name if images else None,
                            'sha256': self.pipeline.identity if images else None},
                  'timing': {'photos': len(images), 'cv_seconds': round(cv_seconds, 3), 'retrieval_seconds': round(rag_seconds, 3),
                             'explanation_seconds': round(llm_seconds, 3), 'total_seconds': round(time.perf_counter() - start, 3)},
                  'limits': ['Detection scores are not calibrated probabilities.',
                             'Photos cannot establish hidden faults, damage depth, repair cost or roadworthiness.',
                             'Workshop entries are published contacts, not verified referrals or quotes.']}
        result['report'] = report(result)
        return result


def report(r):
    title = 'Vehicle condition report (for buyers)' if r['mode'] == 'sell' else 'Fleet incident report'
    v = r['verdict']
    lines = [f'# CarDoctor: {title}', '', f"Vehicle: {r['vehicle'] or 'not supplied'}",
             f"Photos analysed: {r['timing']['photos']} (sides: {', '.join(r['views_checked']) or 'none'})", '',
             f"## Verdict: {v['title']}", '', v['text']]
    if v['driver_condition']:
        lines += ['', f"Applies when: {v['driver_condition']}", f"First step: {v['first_action']}", f"Repair type: {v['repair_type']}"]
    if r['query'].strip():
        lines += ['', '## Reported problem (unverified)', ''] + ['> ' + line for line in r['query'].splitlines()]
    lines += ['', '## Detected damage', '']
    if r['findings']:
        for d in r['findings']:
            lines.append(f"- Photo {d['photo'] + 1} ({d['view']}): {d['label']} on {d['part'].replace('_', ' ')}, model score {d['score']:.2f}")
    else:
        lines.append('- None detected at this sensitivity.')
    lines += ['', '## Guidance (with sources)', '']
    sources = {s['id']: s for s in r['evidence']['sources']}
    for rec in r['evidence']['evidence']:
        lines.append(f"### {rec['id']}: {rec['title']}")
        lines += [f"- Urgency: {rec['urgency']['level'].replace('_', ' ')}: {rec['urgency']['condition']}",
                  f"- Repair type: {rec['repair_type']}"] + [f'- Action: {a}' for a in rec['actions']]
        for ref in rec['source_refs']:
            s = sources.get(ref['source_id'])
            if s:
                lines.append(f"- Source: [{s['title']}]({s['url']}), {ref['locator']}")
        lines.append('')
    answer = (r['explanation'] or {}).get('answer')
    if answer:
        lines += ['## AI explanation (unreviewed)', ''] + [f"- {c['text']} [{c['record_id']}]" for c in answer['claims']] + ['']
    if r['workshops']:
        lines += ['## Where to get it checked', '']
        for w in r['workshops']:
            lines.append(f"- {w['name']} · {w['phone'] or 'phone n/a'} · {w['address'] or 'address n/a'}")
        lines.append('')
    lines += ['## Limits', ''] + ['- ' + x for x in r['warnings'] + r['limits']]
    lines += ['', f"Model: {r['model']['name']} · SHA-256 {r['model']['sha256'] or 'not run'} · timing {json.dumps(r['timing'])}", '']
    return '\n'.join(lines)
