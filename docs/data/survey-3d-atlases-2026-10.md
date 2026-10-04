# Survey: publicly downloadable 3D human brain/spinal-cord atlases, commercial-use licences (2026-10-04)

Scope: atlases **not already in `docs/research-sources.md`** (NextBrain, Harvard AAN v2, MASSP/AHEAD,
CIT168, MIAL, Allen Human Reference Atlas 3D 2020, BigBrain, Tang 2018, Petersen 2019, Julich-Brain,
SUIT, PAM50 are covered there — see §0 for a one-line cross-reference). This file adds: Brainstem
Navigator, THOMAS, Iglesias/FreeSurfer probabilistic atlases, Hammers, AAL3, Harvard-Oxford,
Neuromorphometrics, Brainnetome, MNI-ICBM152 templates, CerebrA, Mindboggle-101, Open Anatomy
(SPL/NAC), Nowinski's commercial atlas, Visible Human, and a closer look at PAM50/SCT content.

Method: direct fetch of official pages/repos (WebFetch/curl), GitHub API (`gh api`), OSF API, Europe
PMC full text. WebSearch used 3 times (Nowinski, Open Anatomy/Slicer licence, Hammers licence). Every
row is marked ✅ (directly opened the primary licence text/field myself this session), ⚠️ (saw it
through a tool-summarized fetch, not independently re-opened), or ❓ (conflicting/unresolved).

---

## 1. Table

| Atlas | Year / paper | Contents relevant to our gaps | Space / resolution | Format | Download | Licence (verbatim or SPDX + source) | Commercial OK? | Derived from restricted data? |
|---|---|---|---|---|---|---|---|---|
| **Brainstem Navigator** (Bianciardi lab, MGH Martinos) | v1.0, 2024-10-08. DOI 10.25790/bml0cm.96 | In-vivo 7T-derived probabilistic labels for brainstem nuclei: arousal/sleep, autonomic, motor, sensory, limbic groups (reticular formation subdivisions, raphe group, vestibular/cochlear nuclei, superior/inferior olive, etc. — exact list not enumerated on the page itself) | Stereotactic/MNI-compatible; built for 3T/7T | ZIP (atlas labels + templates + alignment scripts) | nitrc.org/projects/brainstemnavig | **No licence text found on the NITRC project page** ❓. Our existing doc (`research-sources.md §2-3`) also reports no licence file located. | **Unclear / likely non-commercial** — needs direct contact with Bianciardi lab | Unknown |
| **THOMAS** thalamic nuclei atlas (Su/Saranathan, *NeuroImage* 2019, 194:272-282) | 2019; superseded by **HIPSTHOMAS** (github.com/thalamicseg/hipsthomasdocker) | 12-14 thalamic substructures incl. habenula, MD, CM, MGN, LGN, pulvinar, VPL, VLp (dorsal/ventral), VLa, VA, AV, mammillothalamic tract | Multiple template resolutions (61×91×62, 93×187×68) | NIfTI | github.com/thalamicseg (old repo now flagged obsolete) | **"© Copyright Manojkumar Saranathan 2021-2025"** — no OSI licence file found ❓ | **Unclear — no open licence**, contact manojsar@email.arizona.edu | Unknown |
| **FreeSurfer probabilistic atlases** (Desikan-Killiany, Destrieux, Iglesias hippocampal subfields, amygdala nuclei, thalamic nuclei, brainstem substructures) | Desikan 2006; Destrieux 2010; Iglesias et al. 2015 (hippocampus/amygdala), 2018 (thalamus, *NeuroImage*), 2015 (brainstem, *NeuroImage*) — all ship inside the FreeSurfer distribution | Hippocampal subfields (~13: CA1-4, subiculum, molecular layer, etc.), amygdala nuclei (~9: lateral, basal, accessory-basal, central, cortical, medial, paralaminar, etc.), thalamic nuclei (~25-50 depending on version), brainstem substructures (medulla, pons, SCP, midbrain) | 1mm MNI305/FreeSurfer space (priors built from ex vivo + in vivo training data) | MGZ/NIfTI, part of FreeSurfer `average/` directory | surfer.nmr.mgh.harvard.edu | **FreeSurfer Software License Agreement v1.0 (2011)**, verbatim Part B §4 (fetched directly from `raw.githubusercontent.com/freesurfer/freesurfer/dev/LICENSE.txt`) ✅: *"The Software has been designed for research purposes only... YOU ACKNOWLEDGE AND AGREE THAT CLINICAL APPLICATIONS ARE NEITHER RECOMMENDED NOR ADVISED. Any commercialization of the Software is at the sole risk of the party or parties engaged in such commercialization."* Grant language (§1-2) explicitly permits incorporating the Software "into proprietary programs" and sublicensing, **provided** the licence text is carried forward on any redistributed copy (§1b) and modifications are clearly marked (§1d). | **Yes, commercial use is explicitly contemplated** (not "non-commercial" — a common misconception; it is "at your own risk," no warranty, and requires carrying the licence text forward). This is probably the single biggest finding of this survey: it unlocks thalamic/hippocampal/amygdala/brainstem **sub**-structure detail beyond NextBrain's labels, under a licence we already treat as safe enough for other project pieces. | Training data for Iglesias priors partly uses other cohorts (Buckner, ADNI-like) but the resulting *atlas priors* ship under the FreeSurfer licence above, not a separate data-use agreement, as far as this session found ⚠️ |
| **Hammers adult brain atlas (Hammersmith, n30r83)** (Hammers 2003, Gousias 2008) | 2003/2008 | 83-95 regions, mostly cortical lobes/gyri + hippocampus, amygdala, basal ganglia as whole structures (not nuclei-level) | Native MRI space + MNI versions | NIfTI/MINC | brain-development.org | **Original: non-commercial only.** Via WebSearch (not independently re-opened this session) ❓: *"Materials may be used for academic, non-commercial research and teaching... does not include commercially-sponsored research or diagnosis/treatment/care of patients."* Copyright (c) Imperial College London 2007. | **No** for the original release | — |
| **"Hammers atlas registered to ICBM"** (third-party Zenodo re-release) | Zenodo record 7930159 | Hammers_67 (67 regions) + Hammers_Lobes, registered to MNI-ICBM-2009c | MNI-ICBM-2009c | NIfTI + MINC | zenodo.org/records/7930159 | **"Creative Commons Attribution 4.0 International"** ✅ (confirmed by opening the Zenodo record directly) | **Licence-conflict flag** ❓: the depositor relicensed a derivative of Imperial College's non-commercial-only data as CC BY 4.0. It is **not established that the depositor held the right to relicense** Imperial's IP this way — treat as a real legal risk, not a clean CC BY source, until Imperial College or the Zenodo depositor confirms the relicensing was authorized. | Yes — built on Imperial College's non-commercial Hammers atlas |
| **AAL3** (Rolls, Huang, Lin, Feng, Joliot, *NeuroImage* 2020, 206:116189) | AAL3v2 readme updated 2024-04-05 to add GPL | **Thalamus parcellation (update aligned to FreeSurfer 7), anterior cingulate subdivisions, and discrete brainstem/subcortical nuclei: nucleus accumbens, substantia nigra, ventral tegmental area, red nucleus, locus coeruleus, raphe nuclei** | MNI single-subject (Colin27-based) space | NIfTI (+ SPM12 toolbox wrapper) | gin.cnrs.fr/en/tools/aal/ | **"Addition of the operating licence 'GNU General Public Licence' in the readme, released 5 April 2024"** ✅ (fetched the GIN-IMN tools page directly, quoted verbatim release note) | **Yes, but copyleft.** GPL permits commercial use, but distributing the atlas files (or works that statically incorporate/derive from them) as part of a product likely requires the combined work to also be GPL-licensed and source-available. Using it only internally (e.g., as a reference to hand-author independent nuclei meshes) avoids the copyleft trigger; shipping the GPL'd NIfTI/label files inside a closed commercial product does not. **This is new, concrete, licence-identified brainstem-nucleus content (SN, VTA, RN, LC, raphe) that our current sources lack at this granularity outside NextBrain's small argmax labels** — worth a closer look even with the copyleft caveat. | Builds on the Colin27 single-subject MNI template (unrestricted) |
| **Harvard-Oxford cortical/subcortical atlas** | distributed with FSL | Probabilistic cortical lobes + subcortical whole-structures (thalamus, caudate, putamen, pallidum, hippocampus, amygdala, accumbens, brainstem) — no nuclei-level detail | MNI152 (1mm/2mm) | NIfTI, bundled with FSL (`$FSLDIR/data/atlases/HarvardOxford`) | fsl.fmrib.ox.ac.uk | **CC BY-SA 4.0** ✅ (confirmed directly via `fsl.fmrib.ox.ac.uk/fsl/docs/license.html`, which explicitly lists "Cerebellum and Harvard-Oxford atlases... released under CC BY-SA 4.0" as the named exceptions to FSL's otherwise non-commercial default licence) | **Yes** (CC BY-SA, share-alike) | No — but obtaining the files requires installing FSL, which has its own (non-commercial) software click-through even though the atlas data itself is separately CC BY-SA |
| **Neuromorphometrics atlas** (used in SPM/BrainCOLOR/CerebrA's subcortical labels) | — | Detailed MGH Center for Morphometric Analysis protocol: full cortical/subcortical/ventricular parcellation from 114 manually labeled scans (ages 5-96) | — | — | neuromorphometrics.com | **Paid licence required.** ✅ Direct quote from the vendor page: *"By purchasing an Academic Subscription, you must... agree to abide by the license (no sharing and no commercial use...)"*; commercial use requires a separate paid commercial licence negotiated directly. | **No** (not free; a paid commercial licence exists but at negotiated cost — $1,500/yr academic tier quoted, commercial tier unspecified) | — |
| **Brainnetome atlas** (Fan et al. 2016) | 2016 | 246 cortical/subcortical subregions, connectivity-based parcellation | — | NIfTI (FSL/FreeSurfer space packages) | atlas.brainnetome.org, nitrc.org/projects/bn_atlas | **Non-commercial, share-alike.** ✅ direct quote from NITRC page: *"...free of charge, subject to proper attribution and an agreement to share alike, for use for non-commercial purposes."* Commercial use requires contacting brainnetome.atlas@nlpr.ia.ac.cn. | **No** without separate commercial agreement | — |
| **MNI-ICBM152 nonlinear atlases (2009a/b/c, sym/asym)** (Fonov et al. 2009/2011) | 2009-2011 | T1/T2/PD templates + tissue probability maps; **not nuclei-level content**, but the standard space itself | 0.5mm (2009b) to 1mm (2009a/c) | MINC/NIfTI | nist.mni.mcgill.ca | **Permissive, BSD/MIT-style** ✅: *"Permission to use, copy, modify, and distribute this software and its documentation for any purpose and without fee is hereby granted, provided that the above copyright notice appear in all copies."* No commercial restriction stated; standard "as-is"/no-warranty disclaimer only. | **Yes** | — |
| **CerebrA** (Manera, Dadar, Fonov, Collins — *Scientific Data* 2020, 7:237; PMC7363886, doi:10.1038/s41597-020-0557-9) | 2020 | **102 labeled regions (51 bilateral)**: cortical labels from the DKT/Mindboggle-101 protocol, subcortical structures following Neuromorphometrics/BrainCOLOR conventions, **plus whole brainstem, ventricles, cerebellar grey/white matter and cerebellar vermis lobules** — all manually edited onto the symmetric MNI-ICBM2009c template | MNI-ICBM2009c, 1mm | MINC1/MINC2/NIfTI | nist.mni.mcgill.ca/?p=904, G-Node 10.12751/g-node.be5e62, TemplateFlow `tpl-MNI152NLin2009cSym` | **CC BY 4.0** ✅ (fetched the paper's full text directly via Europe PMC; data licensed CC BY 4.0, metadata additionally under CC0 per *Scientific Data*'s standard data policy) | **Yes** | Re-uses Mindboggle-101/DKT cortical labels (Apache-2.0 project-level license per OSF, see below) and Neuromorphometrics-style subcortical conventions (not the restricted Neuromorphometrics data itself — this is an independent manual relabeling) |
| **Mindboggle-101 / DKT protocol** (Klein & Tourville 2012) | 2012 | Cortical labeling protocol (DKT31/DKT40) used as the basis for several derivative atlases (incl. CerebrA above); not itself a subcortical/brainstem source | — | NIfTI (via FreeSurfer-compatible annotation) | osf.io/ydyxu, mindboggle.info | **Apache License 2.0** ✅ (confirmed via OSF API: project node's attached `license` resolves to "Apache License 2.0", full text fetched) | **Yes** | — |
| **SPL/NAC Brain Atlas** (Open Anatomy Project, Brigham & Women's Hospital Surgical Planning Lab + Martinos Center) | Ongoing; current release brain-2017-01 | **300+ structures from a single-subject MRI**, explicitly including a **hypothalamic parcellation** and a **cerebellar parcellation**, plus head/neck muscle segmentation and a full anatomical hierarchy | 0.75mm MPRAGE+T2 acquisition (downsampled to 1mm for the web viewer); single healthy 42-year-old male, not population MNI space | Slicer scene / mesh export via OpenAnatomy browser | openanatomy.org/atlases/nac/brain-2017-01.zip | **3D Slicer License, Part B** ✅ (fetched the verbatim text at `raw.githubusercontent.com/Slicer/Slicer/main/License.txt`) — **identical legal template to the FreeSurfer licence above** (same "Brigham and Women's Hospital" / MGH family of research-institution licences): commercialization permitted "at the sole risk" of the commercializer, no warranty, licence text must be carried forward on redistribution. | **Yes, same terms/caveats as FreeSurfer above.** This is a second, independently-confirmed instance of the "research-institution licence actually permits commercialization" pattern — worth treating as a recognized licence family, not a one-off exception. | Single healthy volunteer scan at Martinos Center; no indication of third-party data restrictions |
| **PAM50 / Spinal Cord Toolbox atlas** (De Leener et al., *NeuroImage* 2018) | 2018 | **30 white-matter tracts (15 per side)**: dorsal columns (gracile/cuneate fasciculi), lateral/ventral/ventrolateral corticospinal tracts, ventral spinocerebellar tract, rubrospinal and 4 reticulospinal subdivisions, spinal lemniscus (spinothalamic+spinoreticular), spino-olivary tract, vestibulospinal, tectospinal, MLF. **3 bilateral grey-matter regions** (ventral horn, intermediate zone, dorsal horn — a coarse Rexed-lamina-style division, not full lamina I-X). Discrete+continuous vertebral level files C1-S5 and 30 spinal-level parcellations. | Straightened PAM50/MNI-aligned template space | NIfTI, probabilistic (0-1) | github.com/spinalcordtoolbox/PAM50 | **No licence file** ✅ confirmed via `gh api repos/spinalcordtoolbox/PAM50` → `license: null`; repo root has no LICENSE file (contents: `.distriploy.yml, .gitignore, CHANGES.md, README.md, atlas, histology, scripts, template`). Matches the prior finding in `research-sources.md §2-4`. SCT *software* itself is LGPL-3.0, but it is unclear whether that extends to this data-only repo. | **Unclear — needs direct outreach** to Julien Cohen-Adad (NeuroPoly) or a forum.spinalcordmri.org / GitHub issue, as previously recommended | Unknown |
| **Nowinski "Cerefy"/"Human Brain Atlas" product family** (35+ commercial atlas products, Biomedical Imaging Lab, Singapore/Thieme) | Multiple, ongoing | Cerebral vasculature, stereotactic/functional-neurosurgery atlases, integrated into Medtronic/Brainlab/Elekta surgical workstations | — | — | Not publicly downloadable | **Proprietary commercial licensing** — "licensed to 67 companies and institutions... distributed in about 100 countries" per secondary sources (WebSearch, not independently opened — publisher is Thieme) ⚠️ | **Not applicable — this is a sold product, not an open atlas.** Excluded from our usable-source list; mentioned only because the task asked us to check it. | — |
| **Visible Human Project** (NLM) | Imaging 1994-1995; access policy changed 2019 | Whole-body cryosection/CT/MRI imagery (not itself a brain nuclei segmentation) | Native cryosection resolution | Raw image series | nlm.nih.gov/research/visible/visible_human.html | **Public domain, no licence agreement required since 2019** ⚠️ (tool-summarized fetch, not independently re-opened: *"As of 2019, a license is no longer required to access the VHP datasets"*; previously ~4,000 licensees in 66 countries had to sign one) | **Yes, apparently unrestricted** | — |
| **Rushmore 2020** 50µm brainstem atlas (123 structures) | *Front Neuroanat* 2020 — **already flagged in `research-sources.md`**, re-confirmed here: this is **not a usable 3D source**, only 291 axial plate images as supplementary material, built on restricted Duke CIVM MRI | — | — | — | Paper supplementary only | **N/A — not a volumetric/mesh download** | Built on Duke CIVM data (CC BY-NC-ND / request-only) |

### Already known, not re-surveyed in depth (cross-reference only)

Per the task's own list of sources we already know: **NextBrain** (CC0, backbone), **Harvard AAN v2** (CC0),
**MASSP 2.0/AHEAD** (CC BY 4.0), **CIT168** (CC BY 4.0 — this *is* "Pauli's subcortical atlas," same
OSF record `r2hvk`, no separate "Pauli atlas" exists beyond CIT168 and its predecessor), **MIAL** (CC
BY-SA 4.0), **Allen Human Reference Atlas 3D 2020** (CC BY 4.0), **BigBrain** (CC BY-NC-SA),
**Tang 2018 brainstem tractography** (non-commercial, no redistribution), **Petersen 2019 basal-ganglia
pathways** (CWRU, non-commercial), **Julich-Brain** (CC BY-NC-SA, all versions v2.9-v3.1 per EBRAINS
KG), **SUIT cerebellum** (licence conflict between GitHub README "CC BY" and lab page "CC BY-ND" —
unresolved, same as before). Full detail: `docs/research-sources.md` §2-1 through §2-4.

Also already covered and unchanged: **BodyParts3D/Anatomography** (CC BY 4.0, confirmed by DBCLS's
2025-02-27 licence page), **Z-Anatomy** (CC BY-SA 4.0 per its README).

---

## 2. Notes

**The single most useful finding in this survey is the licence family, not any one atlas.** The
FreeSurfer Software License (2011) and the 3D Slicer License are the *same legal template*, issued by
the same cluster of Harvard-affiliated research hospitals (MGH / Brigham and Women's). Both explicitly
state that commercialization is permitted "at the sole risk" of the commercializing party — this is not
a non-commercial clause, it is a liability disclaimer plus an obligation to carry the licence text
forward on redistribution and clearly mark modifications. This means:
- **FreeSurfer's own distributed probabilistic atlases** (Desikan-Killiany and Destrieux cortical
  parcellations, Iglesias hippocampal-subfield/amygdala-nuclei/thalamic-nuclei/brainstem-substructure
  priors) are usable, under the same risk posture we're presumably already accepting for other FreeSurfer-
  adjacent assets. This adds real nuclei-level detail (thalamus, hippocampus, amygdala) *beyond* what
  NextBrain's argmax volume cleanly resolves, as an independent cross-check or supplementary source.
- **The SPL/NAC Brain Atlas (Open Anatomy Project)** is the same deal: 300+ structures from a single
  well-studied subject, including a **hypothalamic parcellation** and a **cerebellar parcellation** we
  don't otherwise have at that granularity, under the identical licence family.
- Caveat common to both: this is a liability-shifting licence, not a "no strings" permissive licence
  like CC0/MIT. A commercial product built on it should carry the licence text (as the licence itself
  requires) and should not claim FDA clearance or clinical-use status (the licence explicitly disclaims
  this). Legal review before shipping is still warranted — "at your own risk" is literally what it says.

**AAL3's April 2024 GPL addition is new, concrete, and licensed brainstem-nucleus content** we don't
have elsewhere outside NextBrain's very small argmax labels: substantia nigra, VTA, red nucleus, locus
coeruleus, and raphe nuclei, plus an updated thalamus parcellation. The catch is GPL copyleft — safe to
use as a private reference for hand-authoring our own independent meshes/positions, risky to ship the
GPL'd files themselves (or a close derivative) inside a closed-source commercial bundle without also
GPL-licensing that bundle. Worth a legal read before deciding how to use it.

**CerebrA (CC BY 4.0, Manera 2020) is a clean, low-risk source for whole-brainstem and cerebellar vermis
lobule geometry**, even though it doesn't add nuclei-level brainstem detail — useful as a well-licensed,
independently-confirmed outline to validate/complement what we already derive from NextBrain.

**Three dead ends, now closed off with evidence rather than left open:**
- **Neuromorphometrics**: explicitly paid, "no commercial use" on the academic tier, commercial tier
  requires a separate negotiated contract. Not a free source.
- **Brainnetome**: non-commercial + share-alike, commercial use requires contacting the lab directly.
- **Nowinski's atlas family**: a sold, proprietary commercial product (licensed to device makers like
  Medtronic/Brainlab/Elekta) — not an open or downloadable dataset at all. Mentioned only because the
  task asked us to check it; not usable as a data source for our product.

**One real licence-integrity flag to carry forward:** the Zenodo "Hammers atlas registered to ICBM"
(record 7930159) claims CC BY 4.0 for a derivative of Imperial College's original Hammers atlas, which
is itself non-commercial-only. Nothing found this session establishes that the depositor had the right
to relicense Imperial's underlying IP. Treat this Zenodo record as **not actually clean CC BY** until
either Imperial College or the depositor confirms the relicensing was authorized — this is exactly the
kind of "two primary sources disagree" case our existing docs flag with ❓ elsewhere (e.g. SUIT).

**Brainstem Navigator and THOMAS (original)** — both frequently cited in brainstem/thalamus literature —
have **no locatable open-source licence** on their primary distribution pages. THOMAS's maintained
successor (HIPSTHOMAS) likewise shows only a bare copyright notice, no licence file. Both would need
direct email outreach to resolve, same posture as PAM50/SUIT already flagged in our main doc.

**PAM50's actual content is more useful than previously documented in detail**: 30 white-matter tracts
(not just "white matter," but named tracts: MLF, rubrospinal, 4 reticulospinal subdivisions, spinal
lemniscus, vestibulospinal, tectospinal, spino-olivary, dorsal columns, corticospinal x3) plus a
simplified 3-region grey-matter division (ventral horn / intermediate zone / dorsal horn — not full
Rexed laminae I-X, but a usable coarse approximation) and vertebral/spinal level parcellations C1-S5.
This is still the best — arguably only — spinal-cord-internal-structure 3D source found across both
survey sessions. Its licence remains the blocker, not its content.

**MNI-ICBM152 templates** carry a genuinely permissive, BSD/MIT-style licence ("for any purpose and
without fee"), confirmed directly. They don't add nuclei content, but they're a safe, well-licensed
fallback standard space if we ever need a licence-clean alternative to AHEAD's or TemplateFlow's spaces
for any new asset.

---

## 3. What would add the most to our 187-structure model, in licence-safe order

1. **FreeSurfer's Iglesias thalamic-nuclei / hippocampal-subfield / amygdala-nuclei priors** — FreeSurfer
   Software License (commercialization-at-own-risk, same family already implicitly accepted for other
   FreeSurfer-adjacent tooling in this project). Fills in finer thalamic/hippocampal/amygdala detail as
   a cross-check against NextBrain, with a licence posture no worse than what we already rely on.
2. **SPL/NAC Brain Atlas (Open Anatomy Project)** — same licence family (3D Slicer License, Part B).
   Adds a **hypothalamic parcellation** and a **cerebellar parcellation** at single-subject precision,
   300+ total structures, that we don't currently have outside NextBrain/Neudorfer.
3. **CerebrA (Manera 2020)** — clean CC BY 4.0, no caveats. Adds whole-brainstem outline + cerebellar
   vermis lobule geometry on the standard MNI-ICBM2009c space; good as a validated reference shape.
4. **MNI-ICBM152 nonlinear templates** — permissive BSD/MIT-style licence, no caveats. Not new structure
   content, but a safe fallback template space if ever needed.
5. **AAL3 brainstem/subcortical nuclei (SN, VTA, red nucleus, LC, raphe) + updated thalamus** — GPL,
   commercial use allowed but copyleft-encumbered if the data files themselves are redistributed inside
   the product. Best used as a private positional/shape reference for hand-authoring independent assets,
   not as directly shipped geometry, unless a GPL-compatible distribution strategy is deliberately chosen.
6. **Harvard-Oxford (CC BY-SA 4.0)** — clean share-alike licence, but content is whole-structure/lobe
   level, not nuclei detail; low marginal value given NextBrain already covers this granularity.
7. **PAM50 spinal-cord atlas** — by far the best spinal-cord-internal content (30 named WM tracts +
   coarse grey-matter horns + vertebral/spinal levels), but **blocked on an unresolved licence** (no
   LICENSE file in the repo). Worth the outreach to NeuroPoly/Cohen-Adad precisely because the content
   value is high and no comparable alternative was found in either survey session.
8. **Brainstem Navigator, THOMAS/HIPSTHOMAS** — valuable brainstem/thalamic content but both need direct
   licence confirmation from their maintainers before any use; do not build on them speculatively.
9. **Hammers (Zenodo 7930159 "CC BY 4.0" re-release)** — do **not** rely on this claimed licence until
   Imperial College's original non-commercial restriction is confirmed resolved; treat as a red flag,
   not a green light, despite the Zenodo page's own CC BY label.
10. **Neuromorphometrics, Brainnetome, Nowinski's product family** — excluded: paid/non-commercial/
    proprietary respectively, with no free commercial path found.
