# Research — 22 October 2026

Demand is **inferred** from this workflow: A cue marker can point beyond actual sample frames or refer to an address mode the export pipeline does not support.

[Exact stars-desc GitHub query](https://github.com/search?q=wav%20metadata%20sort%3Astars-desc&type=repositories), observed 2026-10-22T06:18:36.315Z. Highest-star relevant comparable found in the inspected pool: `Borewit/music-metadata`. Keywords are narrow; established comparables were supplemented directly. The difference-constraints keyword results were mostly unrelated and do not establish market coverage.

| Comparable | Stars | Last push | GitHub license metadata | Workflow and setup |
| --- | ---: | --- | --- | --- |
| [Borewit/music-metadata](https://github.com/Borewit/music-metadata) | 1331 | 2026-10-21T17:21:09Z | MIT | Node/TypeScript broad audio metadata extraction and streaming APIs. |
| [tinytag/tinytag](https://github.com/tinytag/tinytag) | 841 | 2026-10-14T11:46:09Z | MIT | Python pip-installed audio metadata reader with small usage examples. |
| [Zeugma440/atldotnet](https://github.com/Zeugma440/atldotnet) | 579 | 2026-09-28T08:45:14Z | MIT | .NET metadata read/write library explicitly documenting RIFF LIST/CUE/SMPL support and examples. |

## Choice and tradeoffs

Map RIFF-WAVE chunk boundaries, resolve direct-data cue byte offsets and report orphan/duplicate/out-of-range marker references. MIDI pedal, subtitles and media catalogs concern other event/metadata models. This inspects real binary WAVE sample/frame references and label linkage.

The established alternatives are broader and may be the right choice for their supported ecosystem. Our small CLI offers one dependency-free runtime and an inspectable JSON report for the stated subset. It sacrifices generality and may reject valid real-world input outside that subset. READMEs/current docs/source and sampled issues were inspected for workflow context; this does not prove competitor feature absence. ATL explicitly supports WAV CUE/LIST, NetworkX explicitly returns negative cycles, and RLEMaskLib performs mask operations without full raster expansion. Our example proves only our behavior.

Installability and first-result instructions are documented above and in upstream READMEs. Competitor clean installs, time to first useful result, reliability, support response and performance were **not measured**. No superiority, adoption or global ranking claim. Stars are research context only. [Exact provenance and sampled issues/PRs](RESEARCH_PROVENANCE.json). Inconclusive GitHub license metadata is not a legal conclusion; NetworkX README states BSD3, Z3 README MIT, and Knossos README EPL. No implementation is reused.

Primary references:
- https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Docs/riffmci.pdf
