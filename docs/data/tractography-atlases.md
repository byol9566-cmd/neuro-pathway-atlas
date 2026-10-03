# Published MNI-space white-matter tractography atlases — survey for pathway animation geometry

Purpose: find published, downloadable, MNI-space tract geometry (streamlines/.trk/.tck, bundle
centrelines, or probabilistic NIfTI maps a centreline can be extracted from) suitable for animating
pathways along their real anatomical course (e.g. CST through internal capsule → cerebral peduncle →
pons → pyramid → decussation → lateral funiculus) in a three.js viewer that may later be sold
commercially.

Verification method: direct fetch of official pages (brain.labsolver.org, fsl.fmrib.ox.ac.uk,
github.com, nitrc.org, humanconnectome.org) via curl/WebFetch, plus Europe PMC abstracts/full text for
two papers. Anything not confirmed this way is marked **unverified**.

## Summary table

| Atlas | Tracts incl. brainstem long tracts | Format / space | Licence (verbatim + URL) | Commercial OK? | Download |
|---|---|---|---|---|---|
| **HCP-842 / HCP-1065 population-averaged tractography atlas** (Yeh, DSI Studio) | ~550 clustered bundles in 6 categories (projection, association, commissural, cerebellar, **brainstem**, cranial nerve). Confirmed via full text: corticospinal, corticobulbar, corticopontine, **medial lemniscus, spinothalamic tract, lateral lemniscus**, superior/middle/inferior cerebellar peduncles, optic radiation, fornix, cingulum. MLF not explicitly confirmed. | TRK / TT (streamlines) + NIFTI (volume). HCP-842: MNI152 coordinate system. HCP-1065: ICBM 2009a Nonlinear Asymmetric space, 1 mm. | **"Creative Commons Attribution-ShareAlike 4.0 International License."** — verbatim from https://brain.labsolver.org/hcp_trk_atlas.html (fetched directly). Page also states: "The data are derived from imaging data of the Human Connectome Project. Using them requires additional acknowledgment." | **Yes, with ShareAlike obligation** — CC BY-SA permits commercial use of derived works, but any redistribution of the geometry (including as part of a shipped product) must itself carry CC BY-SA + attribution. See HCP note below re: the underlying HCP data-use terms. | https://brain.labsolver.org/hcp_trk_atlas.html (also Zenodo/GitHub mirrors linked from that page) |
| **XTRACT atlases** (FSL, de Groot/Warrington/Bryant 2020) | 42-tract human protocol (all split L/R except commissural): AR, AMF, AC, ATR, AF, cingulum (3 subsections), **CST**, forceps major/minor, fornix, frontal aslant, IFOF, ILF, **MCP** (middle cerebellar peduncle only — **no SCP/ICP, no medial lemniscus, no spinothalamic tract, no corticobulbar**), MdLF, Muratoff bundle, optic radiation, striatal bundles, SLF1-3, STR, UF, VOF. Confirmed via https://fsl.fmrib.ox.ac.uk/fsl/docs/diffusion/xtract.html | NIfTI probability maps, adult-human protocols in MNI152 (`$FSLDIR/data/standard/MNI152_T1_1mm`); derived from 1021 HCP subjects. | FSL's **default** licence applies (XTRACT is not in FSL's named exception list). Verbatim from https://fsl.fmrib.ox.ac.uk/fsl/docs/license.html: *"The Software is distributed 'AS IS' under this Licence solely for non-commercial use... You are not permitted under this Licence to use this Software commercially... includes (1) integration of all or part of the source code or the Software into a product for sale or license... or (4) use of the Software to provide any service to an external organisation for which payment is received."* The same page's "Standard Space Atlases" section lists only Cerebellum, Harvard-Oxford (CC BY-SA 4.0) and JHU/Juelich/Striatum/Thalamus (non-commercial) as exceptions — XTRACT is absent, so it falls under the default non-commercial clause. | **No** (non-commercial only, absent a negotiated OUI licence — contact fsl@innovation.ox.ac.uk) | https://open.oxcin.ox.ac.uk/pages/jbayrak/xtract/ (via FSLeyes or direct download) |
| **TractSeg reference bundles** (Wasserthal 2018, 72 bundles) | Includes CST, SCP/MCP/ICP, MLF, optic radiation, fornix, cingulum, corpus callosum (CC_1-7), arcuate, ATR, anterior commissure, and thalamic/striatal projections (per tool's own tract-name list). **No confirmed medial lemniscus, spinothalamic tract, or corticobulbar bundle** — unverified either way since I could not find an official per-bundle anatomical table distinguishing these. | NIfTI (orientation/peak maps) + binary/probability tract masks; trained/validated in HCP's MNI-aligned space, 1.25 mm. | **Code: Apache License 2.0** — verified verbatim via `raw.githubusercontent.com/MIC-DKFZ/TractSeg/master/LICENSE`. This explicitly permits commercial use, modification, and redistribution. **Caveat (unverified):** the 72-bundle reference segmentations were manually/semi-automatically labelled on ~105 HCP subjects; no separate data licence file was found for those reference labels/pretrained weights, so they likely remain subject to the HCP Data Use Terms' redistribution clause (see below), independent of the Apache-2.0 code licence. | **Code: yes.** **Bundle/weight data: likely yes with HCP redistribution caveat — unverified in detail.** | https://github.com/MIC-DKFZ/TractSeg |
| **Pandora white-matter atlas** (Hansen 2021, Vanderbilt, 216 bundles) | 216 fascicles aggregated from 6 methods: AFQ, AFQ-clipped, RecoBundles, TRACULA, **TractSeg**, **XTRACT** — so brainstem coverage is the union of those two methods' limits above (CST, MCP via XTRACT/TractSeg; no confirmed ML/STT/corticobulbar). 2443 subjects. | Volumetric + surface representations in a standard template space (not independently re-verified beyond the project page's own description). | **"This work is licensed under a Creative Commons Attribution 4.0 International License."** — verbatim, confirmed twice: (1) GitHub `license.txt` at https://github.com/MASILab/Pandora-WhiteMatterAtlas (CC-BY-4.0, SPDX via GitHub API), and (2) NITRC project page https://www.nitrc.org/projects/pandora_atlas, which also quotes the CC description: *"This license lets others distribute, remix, tweak, and build upon your work, even commercially, as long as they credit you for the original creation."* | **Yes** — CC BY 4.0, attribution only, no share-alike requirement. | https://www.nitrc.org/projects/pandora_atlas and https://github.com/MASILab/Pandora-WhiteMatterAtlas |
| **Natbrainlab / Catani & Thiebaut de Schotten "Atlas of Human Brain Connections"** | Unverified in detail — this is primarily a printed/e-book atlas (Oxford University Press, ISBN 9780198729372), not an openly downloadable streamline/NIfTI dataset. | Unverified | **Unverified / inaccessible.** The project's own domain, `natbrainlab.co.uk`, currently resolves (as of this fetch) to an unrelated third-party gambling-affiliate site, not the lab's content — i.e. the original atlas-download page could not be reached. No licence text could be confirmed. | **Unverified — not usable as-is.** | Not found at a working URL during this check; book is commercially sold via OUP, not a free geometry download. |
| **JHU ICBM-DTI-81 white-matter labels + JHU tractography atlas** (Mori/Hua/Wakana, distributed via FSL) | Classic 11-tract white-matter probability atlas incl. **corticospinal tract**; inclusion of medial lemniscus / spinothalamic / corticobulbar **unverified** (not confirmed from a page in this session — flagged as unverified rather than assumed). | NIfTI labels/probability maps, MNI152 (ICBM-152) space, distributed inside FSL (`$FSLDIR/data/atlases/JHU`). | **Confirmed non-commercial**, verbatim from https://fsl.fmrib.ox.ac.uk/fsl/docs/license.html: *"The JHU, Juelich, Striatum and Thalamus atlases, whilst not being the property of Oxford, are released under the terms of the main FSL licence above, at the request of their owners. These atlases should therefore not be used for commercial purposes; for such purposes please contact the primary co-ordinator for the relevant atlas: JHU: susumu@mri.jhu.edu"* | **No** | Bundled with FSL install; also indexed on NITRC (specific current NITRC URL could not be resolved in this session — treat as unverified link, but the licence statement above is independently confirmed on the authoritative FSL page). |
| **Tang et al. 2018 brainstem tractography atlas** ("Brainstem Connectome Atlas", NITRC) | **23 brainstem bundles** — confirmed verbatim from the project page: "Major motor tracts: the corticospinal tract (CST), the fronto-pontine tract (FPT), and the parieto-occipito-temporo-pontine tract (POTPT); Major sensory tracts: the medial lemniscus (ML), the spinothalamic tract (STT), and the lateral lemniscus (LL); Cerebellar peduncles: superior cerebellar peduncle (SCP), the middle cerebellar peduncle (MCP), and the inferior cerebellar peduncle (ICP)." This is the most anatomically complete brainstem long-tract set found in the whole survey. | Probabilistic atlas, manually delineated from 1300 ROIs on 20 HCP subjects, **MNI152 space**. | **Confirmed non-commercial**, verbatim "Brainstem Connectome Atlas License" from https://www.nitrc.org/projects/brainstem_atlas/: *"Permission is granted to use this atlas without charge for non-commercial research purposes only. You may make verbatim copies of this atlas for personal use, or for use within your organization, provided that you include copies of all of the original copyright notices and associated disclaimers with each copy of the atlas."* This matches what was already known going in. | **No** | https://www.nitrc.org/projects/brainstem_atlas/ |
| Other dedicated "brainstem fibre tract atlas" on Zenodo | Searched; did not find a distinct open brainstem-tract-geometry atlas beyond Tang 2018 above. Found only nucleus/structure atlases (e.g. "Harvard Ascending Arousal Network Atlas", Zenodo) which are not tractography/fibre-bundle datasets. | — | — | **Unverified / not found** | — |
| **HCP Young Adult Open Access Data Use Terms** (underlying most atlases above) | N/A — governs re-use of HCP-derived data, not a tract atlas itself | N/A | Full verbatim text fetched from https://www.humanconnectome.org/study/hcp-young-adult/document/wu-minn-hcp-consortium-open-access-data-use-terms (Release date Apr 26, 2013). Key clause: *"I may redistribute original WU-Minn HCP Open Access data and any derived data as long as the data are redistributed under these same Data Use Terms."* Plus acknowledgment/citation requirements and a ban on attempting to re-identify subjects. **There is no blanket ban on commercial use** in this text. | **Not blanket-restricted, but share-alike-like**: redistributing HCP-derived data (including a derived tract atlas) requires passing on the same terms to downstream recipients — this is why Yeh's HCP842/1065 atlases are released as CC BY-SA rather than CC BY. A commercial product that *redistributes* the underlying geometry (e.g. lets users export/download the raw streamlines) likely must honor this; embedding the geometry only as rendered/baked animation inside a closed product is a greyer area and was not something this terms document explicitly addresses — **treat as unverified/consult counsel before shipping commercially.** | https://www.humanconnectome.org/study/hcp-young-adult/data-use-terms |

## Notes per atlas

**HCP-842 / HCP-1065 (Yeh, brain.labsolver.org / DSI Studio).** This is the only atlas in the survey
confirmed, by direct page fetch, to (a) contain the actual brainstem long tracts we need
(corticospinal, corticobulbar, corticopontine, medial lemniscus, spinothalamic, lateral lemniscus,
all three cerebellar peduncles) as discrete streamline bundles, (b) sit in an MNI/ICBM152-family
template space, and (c) carry a licence (CC BY-SA 4.0) that explicitly allows commercial use. The
catch is the ShareAlike clause plus the HCP data-use terms' redistribution requirement — if our
product redistributes the tract geometry itself (not just an animation derived from it), downstream
recipients would need the same CC BY-SA terms and the HCP acknowledgment. This is very likely
workable for a learning tool (cite HCP + Yeh, don't claim exclusivity over the raw geometry) but is
not a "no strings" commercial licence.

**XTRACT (FSL).** Good brainstem *coverage is weak* (only CST + MCP among the long/cerebellar tracts
we care about; no medial lemniscus, spinothalamic, or SCP/ICP), and more importantly it inherits
FSL's non-commercial-only default licence — confirmed verbatim on FSL's own licence page, which lists
exactly which atlases are exceptions (Cerebellum, Harvard-Oxford under CC BY-SA; JHU/Juelich/Striatum/
Thalamus under the same non-commercial FSL terms) and XTRACT is in neither list, so the restrictive
default applies. Not usable for a commercial product without contacting OUI.

**TractSeg.** The *code* (Apache-2.0) is commercially usable without restriction — confirmed from the
raw LICENSE file. But TractSeg is fundamentally a segmentation *tool*, not a static downloadable
atlas; its 72 "bundles" are a labelling scheme used to train a neural net on ~105 manually-labelled
HCP subjects. I could not verify a separate, explicit licence for the manually-dissected reference
bundle masks/pretrained weights distributed with the tool; because they derive from HCP subjects they
most plausibly remain under the HCP redistribution clause even though the *code* is Apache-2.0. Also
could not confirm whether its bundle set includes medial lemniscus or spinothalamic tract specifically
— flagged unverified rather than assumed absent.

**Pandora (Vanderbilt).** Clean CC BY 4.0 (attribution-only, explicitly "even commercially") confirmed
in two independent places (GitHub license.txt + NITRC page text). However, its brainstem/long-tract
content is only as good as its weakest contributing method — since it aggregates XTRACT and TractSeg
outputs among others, it likely also lacks dedicated medial lemniscus/spinothalamic bundles. Good
licence, uncertain anatomical completeness for our specific brainstem-tract list; would need to
inspect the actual bundle-name list in the GitHub repo (not done in this pass) before relying on it.

**Natbrainlab / Catani atlas.** This candidate did not pan out as an open geometry source. It is
primarily commercial print/e-book content (OUP), and the lab's own `natbrainlab.co.uk` domain, at
time of this check, serves unrelated third-party (gambling-affiliate) content rather than the lab's
original pages — a strong signal the domain has lapsed/been repurposed. Treat as unusable until a
live, lab-controlled download location can be found.

**JHU ICBM-DTI-81 / JHU tractography atlas.** Licence is unambiguous and confirmed verbatim on FSL's
own licence page: explicitly "should not be used for commercial purposes." Not usable for our
product. I was not able to independently re-verify its exact tract list (brainstem coverage) in this
session — if it ever became relevant via a future commercial licence from JHU, that would need
separate confirmation.

**Tang et al. 2018 brainstem tractography atlas.** Exactly as flagged going in: confirmed
non-commercial-only via the verbatim "Brainstem Connectome Atlas License" text on its NITRC page. It
remains the single most anatomically complete, purpose-built brainstem long-tract resource found
(23 bundles including CST/FPT/POTPT/ML/STT/LL/SCP/MCP/ICP, in MNI152 space, from HCP subjects) — useful
as a *reference/validation* shape to hand-author centrelines against, but not redistributable in a
commercial product.

**HCP Young Adult Data Use Terms.** Confirmed by direct fetch of the terms document. Important
nuance for the whole survey: this is the ultimate upstream licence for almost every atlas above
(HCP842/1065, XTRACT, TractSeg's training subjects, Pandora's inputs, Tang 2018). It does **not**
itself say "no commercial use" — it says any redistribution of HCP-derived data must carry the same
open terms, which is why the HCP-derived atlases that do offer a clear commercial path (Yeh's
HCP842/1065) chose CC BY-SA rather than a plain permissive licence.

## Recommendation for our use case

Staying strictly factual about what was verified:

1. **Primary candidate: HCP-1065 / HCP-842 population-averaged tractography atlas (Yeh,
   brain.labsolver.org).** It is the only atlas confirmed to combine (a) the actual brainstem long
   tracts we need as real geometry (CST, corticobulbar, corticopontine, medial lemniscus,
   spinothalamic, lateral lemniscus, SCP/MCP/ICP, optic radiation, fornix, cingulum), (b) MNI/ICBM152
   space, downloadable TRK + NIfTI, and (c) a licence (CC BY-SA 4.0) that permits commercial use. The
   condition is ShareAlike + HCP's redistribution clause on the *raw geometry* if we ever let it leave
   our product in redistributable form — fine for "animate the pathway in our viewer," worth a closer
   legal look only if we plan to let users export the underlying streamline/NIfTI files.

2. **Second candidate: Pandora white-matter atlas (Hansen 2021, Vanderbilt).** Confirmed CC BY 4.0,
   no ShareAlike, explicitly "even commercially" — the cleanest licence of everything surveyed. Its
   open question (not resolved in this pass) is whether its 216 bundles actually include dedicated
   medial lemniscus/spinothalamic/corticobulbar bundles, since it's built from methods (XTRACT,
   TractSeg) that, individually, were not confirmed to have those. Worth inspecting the bundle-name
   list in the GitHub repo directly before relying on it for brainstem sensory tracts specifically.

3. **Reference-only, not shippable: Tang et al. 2018 brainstem tractography atlas.** Confirmed
   non-commercial. Still valuable as the most anatomically complete, purpose-dissected brainstem
   bundle set (including medial lemniscus and spinothalamic tract, which neither XTRACT nor confirmed
   TractSeg bundles include) — useful as a ground-truth shape reference when hand-authoring or
   QA-checking centrelines extracted from the HCP842/1065 or Pandora data, but it cannot itself be
   redistributed in the commercial product.

Everything else surveyed (XTRACT, JHU ICBM-DTI-81) was confirmed non-commercial-only by licence text
and is not usable for a commercial build without a separately negotiated licence (FSL: OUI; JHU:
susumu@mri.jhu.edu). Natbrainlab/Catani could not be verified at all — its public download page
appears to no longer be lab-controlled.
