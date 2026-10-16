#!/usr/bin/env python3
"""Extract the official mini archive, audit PCM, and split by speaker/duplicate group.

Standard-library only. Custom split, NOT Google's official full-corpus benchmark split.
Run from any working directory; all output paths are relative to the project root.
"""
import argparse
import array
import audioop
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORDS = {'down', 'go', 'left', 'no', 'right', 'stop', 'up', 'yes'}
SOURCE = 'https://storage.googleapis.com/download.tensorflow.org/data/mini_speech_commands.zip'


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--keyword', choices=sorted(WORDS), default='stop')
    ap.add_argument('--seed', default='siri-experiment-01-v1')
    args = ap.parse_args()
    archive = ROOT / 'data/downloads/mini_speech_commands.zip'
    raw = ROOT / 'data/raw'
    out = ROOT / 'data/manifests'
    reports = ROOT / 'data/reports'
    for directory in (raw, out, reports):
        directory.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        # Explicit allowlist: do not extract __MACOSX or arbitrary archive paths.
        for member in z.infolist():
            parts = Path(member.filename).parts
            wanted = (len(parts) == 3 and parts[0] == 'mini_speech_commands'
                      and parts[1] in WORDS and parts[2].endswith('.wav'))
            readme = parts == ('mini_speech_commands', 'README.md')
            if not (wanted or readme):
                continue
            target = raw.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(member) as src, target.open('wb') as dst:
                shutil.copyfileobj(src, dst)

    rows, rejected = [], []
    for path in sorted((raw / 'mini_speech_commands').glob('*/*.wav')):
        relative = str(path.relative_to(ROOT))
        try:
            if '_nohash_' not in path.stem:
                raise ValueError('Unknown speaker filename format')
            with wave.open(str(path), 'rb') as f:
                rate, channels, width = f.getframerate(), f.getnchannels(), f.getsampwidth()
                frames = f.getnframes()
                pcm = f.readframes(frames)
                if (rate, channels, width, f.getcomptype()) != (16000, 1, 2, 'NONE'):
                    raise ValueError('Unexpected PCM format')
                if len(pcm) != frames * channels * width or frames == 0:
                    raise ValueError('Truncated or empty audio')
            rms = audioop.rms(pcm, 2)
            if rms == 0:
                raise ValueError('Zero RMS; unusable for this speech baseline')
            samples = array.array('h', pcm)
            if sys.byteorder != 'little':
                samples.byteswap()
            word = path.parent.name
            rows.append({
                'audio_path': relative, 'word': word,
                'speaker_id': path.stem.split('_nohash_')[0],
                'is_keyword': int(word == args.keyword),
                'duration_seconds': frames / rate, 'sample_rate': rate,
                'channels': channels, 'sample_width_bytes': width,
                'pcm_sha256': hashlib.sha256(pcm).hexdigest(),
                'rms_dbfs': 20 * math.log10(rms / 32768),
                'peak_amplitude': audioop.max(pcm, 2) / 32768,
                'dc_offset': audioop.avg(pcm, 2) / 32768,
                'saturation_fraction': sum(x in (-32768, 32767) for x in samples) / frames,
                'keyword_start_seconds': None, 'keyword_end_seconds': None,
                'alignment_status': 'not_available',
                'source': 'Google Mini Speech Commands', 'license': 'CC BY 4.0',
            })
        except (ValueError, wave.Error, EOFError) as exc:
            rejected.append({'audio_path': relative, 'reason': str(exc)})

    by_hash = defaultdict(list)
    for row in rows:
        by_hash[row['pcm_sha256']].append(row)
    conflicting = {h for h, items in by_hash.items() if len({r['word'] for r in items}) > 1}
    for row in rows:
        if row['pcm_sha256'] in conflicting:
            rejected.append({'audio_path': row['audio_path'], 'reason': 'Identical PCM has conflicting word labels'})
    rows = [r for r in rows if r['pcm_sha256'] not in conflicting]

    # Duplicate-linked speakers form a single indivisible split group.
    parent = {r['speaker_id']: r['speaker_id'] for r in rows}
    def find(s):
        while parent[s] != s:
            parent[s] = parent[parent[s]]
            s = parent[s]
        return s
    for h, items in by_hash.items():
        if h in conflicting:
            continue
        speakers = sorted({r['speaker_id'] for r in items})
        for s in speakers[1:]:
            parent[find(s)] = find(speakers[0])
    components = defaultdict(list)
    for speaker in sorted(parent):
        components[find(speaker)].append(speaker)
    assignments = {}
    for speakers in components.values():
        token = args.seed + ':' + ','.join(speakers)
        fraction = int(hashlib.sha256(token.encode()).hexdigest()[:16], 16) / 2**64
        split = 'train' if fraction < .8 else 'validation' if fraction < .9 else 'test'
        for speaker in speakers:
            assignments[speaker] = split
    for row in rows:
        row['split'] = assignments[row['speaker_id']]

    summary = {}
    for split in ('train', 'validation', 'test'):
        items = [r for r in rows if r['split'] == split]
        with (out / f'{split}.jsonl').open('w') as f:
            for row in items:
                f.write(json.dumps(row) + '\n')
        summary[split] = {
            'clips': len(items), 'speakers': len({r['speaker_id'] for r in items}),
            'keyword_clips': sum(r['is_keyword'] for r in items),
            'other_word_clips': sum(1-r['is_keyword'] for r in items),
            'audio_minutes': sum(r['duration_seconds'] for r in items) / 60,
            'other_word_minutes': sum(r['duration_seconds'] for r in items if not r['is_keyword']) / 60,
            'word_counts': dict(sorted(Counter(r['word'] for r in items).items())),
        }
        assert summary[split]['keyword_clips'] > 0 and summary[split]['other_word_clips'] > 0
    splits = list(summary)
    for i, first in enumerate(splits):
        for second in splits[i+1:]:
            for key in ('speaker_id', 'pcm_sha256'):
                assert not ({r[key] for r in rows if r['split'] == first}
                            & {r[key] for r in rows if r['split'] == second}), (first, second, key)

    durations = sorted(r['duration_seconds'] for r in rows)
    report = {
        'source_url': SOURCE, 'archive_sha256': digest_file(archive),
        'archive_bytes': archive.stat().st_size, 'keyword': args.keyword, 'seed': args.seed,
        'split_method': 'Custom deterministic SHA256 speaker-component split, expected 80/10/10; not official Google split',
        'valid_clips': len(rows), 'rejected_clips': len(rejected),
        'unique_speakers': len(parent), 'split_groups': len(components),
        'duration_seconds': {'min': min(durations), 'median': durations[len(durations)//2], 'max': max(durations)},
        'clips_shorter_than_one_second': sum(d < 1 for d in durations),
        'clips_with_saturated_samples': sum(r['saturation_fraction'] > 0 for r in rows),
        'clips_below_minus_50_dbfs': sum(r['rms_dbfs'] < -50 for r in rows),
        'rms_dbfs_range': [min(r['rms_dbfs'] for r in rows), max(r['rms_dbfs'] for r in rows)],
        'duplicate_pcm_groups': sum(len(v) > 1 for v in by_hash.values()),
        'conflicting_label_duplicate_groups': len(conflicting),
        'cross_split_speaker_overlap': 0, 'cross_split_exact_pcm_overlap': 0,
        'splits': summary,
        'limitations': ['Word labels only; no verified keyword boundaries or phonetic-state alignments',
                       'Other-word clips are not silence and not representative continuous background',
                       'Exact hashes do not detect near-duplicates or unidentified repeat contributors',
                       'No model trained; no manual audio-quality or label audit performed'],
    }
    write_json(reports / 'mini_speech_commands_eda.json', report)
    write_json(reports / 'rejected_audio.json', rejected)
    lines = ['# Mini Speech Commands: measured EDA', '',
             f"Target keyword: **{args.keyword}**. Valid clips: **{len(rows)}**; speaker IDs: **{len(parent)}**.", '',
             '| Split | Clips | Speakers | Positive | Other words | Minutes |',
             '| --- | ---: | ---: | ---: | ---: | ---: |']
    for split, s in summary.items():
        lines.append(f"| {split} | {s['clips']} | {s['speakers']} | {s['keyword_clips']} | {s['other_word_clips']} | {s['audio_minutes']:.2f} |")
    lines += ['', 'Custom deterministic speaker-group split, approximately 80/10/10. Exact duplicate audio links speakers into the same split group. This is not the official full-corpus split.', '',
              f"Duration range: {min(durations):.3f}–{max(durations):.3f} seconds. Shorter than one second: {report['clips_shorter_than_one_second']} clips.", '',
              f"Rejected clips: {len(rejected)}. Exact duplicate PCM groups: {report['duplicate_pcm_groups']}. Clips with saturated samples: {report['clips_with_saturated_samples']} (flagged, not automatically rejected).", '',
              f"Low-level clips below -50 dBFS: {report['clips_below_minus_50_dbfs']} (heuristic review flag; not automatically removed).", '',
              'Checked: zero speaker-ID overlap and zero exact-PCM overlap across splits. Duplicate clips within a split are retained and should be deduplicated or weighted before final benchmarking.', '',
              '## Word counts', '', '| Word | Train | Validation | Test |', '| --- | ---: | ---: | ---: |']
    for word in sorted(WORDS):
        lines.append('| ' + word + ' | ' + ' | '.join(str(summary[s]['word_counts'].get(word, 0)) for s in splits) + ' |')
    lines += ['', '## Limits', ''] + ['- ' + x for x in report['limitations']]
    lines += ['', 'Do not infer phoneme states from whole-file thirds: files can include silence. Obtain or inspect speech boundaries before approximate temporal labels, and use forced alignment for phonetic labels.', '',
              f'Archive SHA256: `{report["archive_sha256"]}`. This is a locally computed provenance hash, not an independently published checksum.', '']
    (reports / 'mini_speech_commands_eda.md').write_text('\n'.join(lines))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
