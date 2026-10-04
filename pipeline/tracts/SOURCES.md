# HCP1065 다운로드 출처 및 목록

확인일: 2026-10-04. 아래 목록은 데이터 다운로드 **전에** GitHub release API에서 조회해 기록했다.

- 원문: https://brain.labsolver.org/hcp_trk_atlas.html
- 릴리스: https://github.com/data-others/atlas/releases/tag/hcp1065
- 메타데이터: https://api.github.com/repos/data-others/atlas/releases/tags/hcp1065
- 라이선스: CC BY-SA 4.0 (원문 Population-Averaged 섹션)
- 공간: ICBM 2009a Nonlinear Asymmetric (원문 명시)
- HCP 이용약관: https://www.humanconnectome.org/study/hcp-young-adult/document/wu-minn-hcp-consortium-open-access-data-use-terms

## 다운로드 전 공개 파일 목록

페이지의 다운로드 링크가 가리키는 `hcp1065` 릴리스 전체 목록. 크기는 GitHub API의 `size`(바이트).

| 파일 | 바이트 | 이번 사용 |
|---|---:|---|
| [1065_subject_tract_in_nifti.zip](https://github.com/data-others/atlas/releases/download/hcp1065/1065_subject_tract_in_nifti.zip) | 755751744 | 미사용 |
| [abbreviation.xlsx](https://github.com/data-others/atlas/releases/download/hcp1065/abbreviation.xlsx) | 13172 | 다운로드 예정 |
| [abbreviation2.xlsx](https://github.com/data-others/atlas/releases/download/hcp1065/abbreviation2.xlsx) | 10764 | 다운로드 예정 |
| [hcp1065_avg_tracts_nifti.zip](https://github.com/data-others/atlas/releases/download/hcp1065/hcp1065_avg_tracts_nifti.zip) | 3372106 | 미사용 |
| [hcp1065_avg_tracts_trk.zip](https://github.com/data-others/atlas/releases/download/hcp1065/hcp1065_avg_tracts_trk.zip) | 587869457 | 다운로드 예정 |
| [hcp1065_avg_tracts_tt.zip](https://github.com/data-others/atlas/releases/download/hcp1065/hcp1065_avg_tracts_tt.zip) | 151947374 | 미사용 |
| [hcp1065_prob_coverage_jpg.zip](https://github.com/data-others/atlas/releases/download/hcp1065/hcp1065_prob_coverage_jpg.zip) | 158135457 | 미사용 |
| [hcp1065_prob_coverage_nifti.zip](https://github.com/data-others/atlas/releases/download/hcp1065/hcp1065_prob_coverage_nifti.zip) | 17353305 | 미사용 |
| [ICBM152_adult.05mm.fz](https://github.com/data-others/atlas/releases/download/hcp1065/ICBM152_adult.05mm.fz) | 48222744 | 미사용 |
| [ICBM152_adult.1mm.fz](https://github.com/data-others/atlas/releases/download/hcp1065/ICBM152_adult.1mm.fz) | 8181706 | 미사용 |
| [ICBM152_adult.ISO.nii.gz](https://github.com/data-others/atlas/releases/download/hcp1065/ICBM152_adult.ISO.nii.gz) | 9234902 | 미사용 |
| [ICBM152_adult.QA.nii.gz](https://github.com/data-others/atlas/releases/download/hcp1065/ICBM152_adult.QA.nii.gz) | 9091716 | 미사용 |
| [tract_to_region_connectome.xlsx](https://github.com/data-others/atlas/releases/download/hcp1065/tract_to_region_connectome.xlsx) | 57152 | 미사용 |
| [tract_to_region_connectome_BM_KL.xlsx](https://github.com/data-others/atlas/releases/download/hcp1065/tract_to_region_connectome_BM_KL.xlsx) | 35250 | 미사용 |
| [tract_to_region_connectome_MMP.xlsx](https://github.com/data-others/atlas/releases/download/hcp1065/tract_to_region_connectome_MMP.xlsx) | 60313 | 미사용 |

TRK 아카이브는 587,869,457바이트(약 561 MiB)로 수 GB가 아니므로 전체 ZIP을 `data/raw/hcp1065/`에 받고 우선 다발만 추출한다. TT 파일은 다운로드하지 않는다. ZIP 내부 파일 목록·압축/비압축 크기와 선택 결과는 다운로드 후 추가한다.

## ZIP 내용과 실제 선택

ZIP 내부 파일명은 긴 이름이 아닌 공식 약어이다. `atlasName`에는 확장자를 뺀 파일명을 보존한다. 긴 명칭은 `abbreviation.xlsx`와 대응한다.

| 내부 경로 | ZIP 내 압축 바이트 | 파일 바이트 (.gz 유지) | 추출 |
|---|---:|---:|---|
| `association/AF_L.trk.gz` | 52073841 | 52242799 | 예 |
| `association/AF_R.trk.gz` | 5114067 | 5135317 | 예 |
| `association/C_FPH_L.trk.gz` | 794146 | 797740 | 예 |
| `association/C_FPH_R.trk.gz` | 176995 | 177728 | 예 |
| `association/C_FP_L.trk.gz` | 11019325 | 11051908 | 예 |
| `association/C_FP_R.trk.gz` | 8754220 | 8765799 | 예 |
| `association/C_PHP_L.trk.gz` | 90816 | 91125 | 예 |
| `association/C_PHP_R.trk.gz` | 477928 | 480079 | 예 |
| `association/C_PH_L.trk.gz` | 321089 | 321387 | 예 |
| `association/C_PH_R.trk.gz` | 269669 | 269820 | 예 |
| `association/C_PO_L.trk.gz` | 1006283 | 1012767 | 예 |
| `association/C_PO_R.trk.gz` | 1087620 | 1090600 | 예 |
| `association/EMC_L.trk.gz` | 8946842 | 8982872 | 아니오 |
| `association/EMC_R.trk.gz` | 15099365 | 15162059 | 아니오 |
| `association/FAT_L.trk.gz` | 12731007 | 12790855 | 아니오 |
| `association/FAT_R.trk.gz` | 4695238 | 4733069 | 아니오 |
| `association/IFOF_L.trk.gz` | 67362266 | 67480522 | 아니오 |
| `association/IFOF_R.trk.gz` | 21363601 | 21394890 | 아니오 |
| `association/ILF_L.trk.gz` | 28976607 | 29128996 | 아니오 |
| `association/ILF_R.trk.gz` | 20125270 | 20204536 | 아니오 |
| `association/MdLF_L.trk.gz` | 2185550 | 2194385 | 아니오 |
| `association/MdLF_R.trk.gz` | 3901023 | 3916233 | 아니오 |
| `association/PAT_L.trk.gz` | 3014576 | 3032082 | 아니오 |
| `association/PAT_R.trk.gz` | 4053508 | 4080169 | 아니오 |
| `association/SLF1_L.trk.gz` | 2406662 | 2412867 | 아니오 |
| `association/SLF1_R.trk.gz` | 5486742 | 5509778 | 아니오 |
| `association/SLF2_L.trk.gz` | 12370741 | 12408901 | 아니오 |
| `association/SLF2_R.trk.gz` | 14863553 | 14938996 | 아니오 |
| `association/SLF3_L.trk.gz` | 2011088 | 2019114 | 아니오 |
| `association/SLF3_R.trk.gz` | 13140354 | 13211156 | 아니오 |
| `association/UF_L.trk.gz` | 5126209 | 5142123 | 예 |
| `association/UF_R.trk.gz` | 9272641 | 9283403 | 예 |
| `association/VOF_L.trk.gz` | 943553 | 947074 | 아니오 |
| `association/VOF_R.trk.gz` | 464517 | 464840 | 아니오 |
| `cerebellum/CB_L.trk.gz` | 45396237 | 45476590 | 아니오 |
| `cerebellum/CB_R.trk.gz` | 15547123 | 15571170 | 아니오 |
| `cerebellum/ICP_L.trk.gz` | 2319149 | 2323451 | 예 |
| `cerebellum/ICP_R.trk.gz` | 1873183 | 1875491 | 예 |
| `cerebellum/MCP.trk.gz` | 2902412 | 2905752 | 예 |
| `cerebellum/SCP.trk.gz` | 1723309 | 1725801 | 예 |
| `cerebellum/V.trk.gz` | 3489403 | 3492479 | 아니오 |
| `commissural/AC.trk.gz` | 30838333 | 30921639 | 아니오 |
| `commissural/CC.trk.gz` | 51042923 | 51294677 | 아니오 |
| `cranial nerve/CNIII_L.trk.gz` | 3232896 | 3252330 | 아니오 |
| `cranial nerve/CNIII_R.trk.gz` | 4101718 | 4119057 | 아니오 |
| `cranial nerve/CNII_L.trk.gz` | 297055 | 297769 | 아니오 |
| `cranial nerve/CNII_R.trk.gz` | 1150622 | 1155699 | 아니오 |
| `cranial nerve/CNVIII_L.trk.gz` | 211300 | 211949 | 아니오 |
| `cranial nerve/CNVIII_R.trk.gz` | 166866 | 167462 | 아니오 |
| `cranial nerve/CNVII_L.trk.gz` | 20871 | 21026 | 아니오 |
| `cranial nerve/CNVII_R.trk.gz` | 19063 | 19121 | 아니오 |
| `cranial nerve/CNV_L.trk.gz` | 107951 | 108369 | 아니오 |
| `cranial nerve/CNV_R.trk.gz` | 195182 | 195944 | 아니오 |
| `projection/AR_L.trk.gz` | 1464515 | 1467139 | 아니오 |
| `projection/AR_R.trk.gz` | 366880 | 368438 | 아니오 |
| `projection/CBT_L.trk.gz` | 240457 | 242424 | 예 |
| `projection/CBT_R.trk.gz` | 921327 | 928624 | 예 |
| `projection/CPT_F_L.trk.gz` | 1418377 | 1425621 | 예 |
| `projection/CPT_F_R.trk.gz` | 6314650 | 6348383 | 예 |
| `projection/CPT_O_L.trk.gz` | 468467 | 469832 | 예 |
| `projection/CPT_O_R.trk.gz` | 329345 | 330185 | 예 |
| `projection/CPT_P_L.trk.gz` | 4441668 | 4448212 | 예 |
| `projection/CPT_P_R.trk.gz` | 4889661 | 4899974 | 예 |
| `projection/CST_L.trk.gz` | 8574064 | 8583309 | 예 |
| `projection/CST_R.trk.gz` | 3688978 | 3699366 | 예 |
| `projection/CS_A_L.trk.gz` | 567659 | 570379 | 아니오 |
| `projection/CS_A_R.trk.gz` | 400757 | 401813 | 아니오 |
| `projection/CS_P_L.trk.gz` | 109311 | 109893 | 아니오 |
| `projection/CS_P_R.trk.gz` | 142859 | 143431 | 아니오 |
| `projection/CS_S_L.trk.gz` | 605147 | 608282 | 아니오 |
| `projection/CS_S_R.trk.gz` | 680186 | 683488 | 아니오 |
| `projection/DRTT_L.trk.gz` | 6551297 | 6563156 | 아니오 |
| `projection/DRTT_R.trk.gz` | 11429369 | 11468342 | 아니오 |
| `projection/F_L.trk.gz` | 682603 | 686210 | 예 |
| `projection/F_R.trk.gz` | 3089091 | 3106507 | 예 |
| `projection/ML_L.trk.gz` | 5451536 | 5455722 | 예 |
| `projection/ML_R.trk.gz` | 4927528 | 4931857 | 예 |
| `projection/OR_L.trk.gz` | 2401714 | 2408829 | 예 |
| `projection/OR_R.trk.gz` | 1399327 | 1402230 | 예 |
| `projection/RST_L.trk.gz` | 3907037 | 3919647 | 아니오 |
| `projection/RST_R.trk.gz` | 5282365 | 5290191 | 아니오 |
| `projection/TR_A_L.trk.gz` | 533031 | 536346 | 아니오 |
| `projection/TR_A_R.trk.gz` | 354114 | 354962 | 아니오 |
| `projection/TR_P_L.trk.gz` | 66598 | 66755 | 아니오 |
| `projection/TR_P_R.trk.gz` | 80629 | 81039 | 아니오 |
| `projection/TR_S_L.trk.gz` | 881789 | 886011 | 아니오 |
| `projection/TR_S_R.trk.gz` | 829961 | 834385 | 아니오 |

추출한 우선 다발: 34개. Spinothalamic tract(STT) 및 Medial longitudinal fasciculus(MLF)는 ZIP 목록에 없음. MCP와 SCP는 좌우 분리 없이 단일 파일로 배포됨. 다른 아틀라스로 대체하거나 임의 분할하지 않음.

## 다운로드 무결성

- `hcp1065_avg_tracts_trk.zip`: 587869457 bytes, SHA-256 `344aad4394f18b8926ed5e1bda911ad56e328c6cf75faa45e1302512ad779c67`
- `abbreviation.xlsx`: 13172 bytes, SHA-256 `ead75629c22adfdec416ebf0de0b854ec3247679da33e50d0e6d9e30eafa71f6`
- `abbreviation2.xlsx`: 10764 bytes, SHA-256 `7325e06cdca5e36e5ac7719261daee3d11a3a1816f47d42e3e57bc17e35344fb`

## 우선 다발의 공식 약어와 원문 긴 이름

`abbreviation.xlsx`의 셀을 그대로 옮김. 실제 파일명은 약어. 아래의 C_FP_R 긴 이름 셀은 원본에서 L로 끝나는 불일치가 있으므로 파일명 R을 기준으로 처리하며 좌표를 바꾸지 않는다.

| atlasName / 파일 약어 | XLSX 원문 긴 이름 |
|---|---|
| `AF_L` | `Arcuate_Fasciculus_L` |
| `AF_R` | `Arcuate_Fasciculus_R` |
| `C_FPH_L` | `Cingulum_Frontal_Parahippocampal_L` |
| `C_FPH_R` | `Cingulum_Frontal_Parahippocampal_R` |
| `C_FP_L` | `Cingulum_Frontal_Parietal_L` |
| `C_FP_R` | `Cingulum_Frontal_Parietal_L` |
| `C_PHP_L` | `Cingulum_Parahippocampal_Parietal_L` |
| `C_PHP_R` | `Cingulum_Parahippocampal_Parietal_R` |
| `C_PH_L` | `Cingulum_Parahippocampal_L` |
| `C_PH_R` | `Cingulum_Parahippocampal_R` |
| `C_PO_L` | `Cingulum_Parolfactory_L` |
| `C_PO_R` | `Cingulum_Parolfactory_R` |
| `UF_L` | `Uncinate_Fasciculus_L` |
| `UF_R` | `Uncinate_Fasciculus_R` |
| `CBT_L` | `Corticobulbar_Tract_L` |
| `CBT_R` | `Corticobulbar_Tract_R` |
| `CPT_F_L` | `Corticopontine_Tract_Frontal_L` |
| `CPT_F_R` | `Corticopontine_Tract_Frontal_R` |
| `CPT_P_L` | `Corticopontine_Tract_Parietal_L` |
| `CPT_P_R` | `Corticopontine_Tract_Parietal_R` |
| `CPT_O_L` | `Corticopontine_Tract_Occipital_L` |
| `CPT_O_R` | `Corticopontine_Tract_Occipital_R` |
| `CST_L` | `Cortico_Spinal_Tract_L` |
| `CST_R` | `Cortico_Spinal_Tract_R` |
| `F_L` | `Fornix_L` |
| `F_R` | `Fornix_R` |
| `ML_L` | `Medial_Lemniscus_L` |
| `ML_R` | `Medial_Lemniscus_R` |
| `OR_L` | `Optic_Radiation_L` |
| `OR_R` | `Optic_Radiation_R` |
| `ICP_L` | `Inferior_Cerebellar_Peduncle_L` |
| `ICP_R` | `Inferior_Cerebellar_Peduncle_R` |
| `MCP` | `Middle_Cerebellar_Peduncle` |
| `SCP` | `Superior_Cerebellar_Peduncle` |
