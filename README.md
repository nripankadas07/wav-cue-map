# wav-cue-map

Map RIFF-WAVE chunk boundaries, resolve direct-data cue byte offsets and report orphan/duplicate/out-of-range marker references.

For audio export developers inspecting cue offsets and associated labels in a small WAV file.

## Quickstart

Python3.10+; no runtime dependencies or external service. The wheel build needs setuptools and wheel from the normal Python registry. Linux shell:

```sh
git clone https://github.com/nripankadas07/wav-cue-map.git
cd wav-cue-map
python -m venv .venv
. .venv/bin/activate
python -m pip install .
wav-cue-map --make-example demo.wav
wav-cue-map demo.wav
```

The generated real eight-frame WAV resolves cue1 to frame3 and links its entry label. [Expected report](example-output.json).

## Input and interpretation

Generate the invented WAV with `--make-example`; the command refuses to overwrite existing files. Inspection is read only.

Little-endian RIFF WAVE<=16MiB, exact declared file length, one fmt and one data chunk,16/18-byte conventional PCM or IEEE float fmt,<=64 channels; PCM8/16/24/32-bit or float32/64-bit. Validate block alignment,byte rate,frame divisibility,chunk boundaries/padding. <=5000 chunks per container,5000 cues and5000 labels. Resolve only cue data addresses with chunkStart=blockStart=0. Unknown chunks are opaque and listed; LIST/adtl labl is read. Text is shown as lossy UTF8 with original hex; CSET not interpreted. No playback, audio decoding, RF64/RIFX, wavl/playlist,extensible/compressed addressing, fact validation or full WAV validity claim. Unsupported cue addresses are findings, unsupported fmt is an error. Refuses example overwrite.

Exit0 means analysis completed, including any infeasibility, NOT_LINEARIZABLE, UNKNOWN or reference finding. Inspect the report fields; exit0 is not a health assertion. Exit2 means malformed/unsupported input or I/O failure, with JSON error on stderr and no partial report. No live-system operations, network requests or credential reads occur. Reports may expose supplied identifiers and bytes; review before sharing.

## Verification

```sh
python -m unittest -v
python -m compileall -q wav_cue_map.py
python -m pip wheel --no-deps . -w dist
```

Actual stdlib wave oracle, byte offset resolution, duplicate/orphan/out-of-range addresses, odd chunks/padding, truncation, float and invalid format checks. [Validation record](VALIDATION.md). CI runs Python3.10/3.12/3.14 on Linux and the installed console outside checkout. Windows/macOS, production workloads and competitor performance remain untested.

## Scope and provenance

Alpha utility. Original AI-assisted code and invented fixtures; standard algorithms independently reimplemented. No third-party implementation/prose copied. MIT. [Candidate brief](BRIEF.json), [research](RESEARCH.md), [support](SUPPORT.md), [contributing](CONTRIBUTING.md), [security](SECURITY.md).

MIDI pedal, subtitles and media catalogs concern other event/metadata models. This inspects real binary WAVE sample/frame references and label linkage.
