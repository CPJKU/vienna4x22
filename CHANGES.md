# Changes

## 13.06.2025

* Fixed score onset time of notes in match files for `Mozart_K331_1st-mov` and `Chopin_op38`. Due to a bug in partitura, symbolic score time in the match files was incorrectly represented in quarters instead of beats. This bug affected the `Mozart_K331_1st-mov` and `Chopin_op38` files which have a time signature of 6/8. This issue was addressed with [PR #454 in partitura](https://github.com/CPJKU/partitura/pull/454).

## 07.03.24

* Update starting time of MIDI and and Matchfiles to start with the audio files. This was done automatically by shifting the note onset/offset times and MIDI controls (pedals) using the (`shift_files_to_audio.py`) script.

* Add script to setup the audio files (`setup_audio.py`).

## 14.06.23

### Bugs

* B1. incorrect clock_unit property (4000, should be 480)
* B2. for Chopin_op38: last performed midi note missing in all match files except for last one (in last performance, last four notes are omitted)
* B3. for Chopin_op10_no3: voice-overlap score notes are missing in match files (those notes should get a new id, and should be aligned as deletions with score attribution 'voice_overlap')
* B4. Missing MIDI performance notes in match file:
  * for Chopin_op38: each MIDI performance has notes (except for the last one addressed in B2) that are missing in alignment. Similarly most match alignments have score notes marked as deletions
  * for Mozart_K331_1st-mov perf15 has non-aligned midi note n488
  * for Schubert_D783_no15 perf2 has non-aligned midi note n334, perf6 has non-aligned midi note n328

### Changes made

* C1. (fix for B2) Recreated match files for Chopin_op38 adding missing last performed note and 480 clock clock_unit
* C2. (fix for B1) Recreated match files for all pieces with 480 clock_unit

### Notes on B3 and B4

* B3: musicxml has no 'voice_overlap' tag or attribute, any solution (change in save_match/matchfile_from_alignment) would involve an additional function param (i.e., ids/indices of score notes where voice_overlap attribute should be added)
* B4: see updated_match_alignments/_missing_notes.txt for list of missing notes for each performance/piece (created after fix for B2, voice_overlap_notes for Chopin_op10_no3 not included)

ph, 14.06.23

## 01.12.2022

* Updated match files to version 1.0.0 using the script `to_match_v100.py`.

## 03.02.2022

* Added MIDI files from the original repository for convenience.

## 04.11.2019

### History and Scope

* This repository was created by Maarten Grachten and Carlos Cancino-Chacón as part of the materials for the tutorial on [Computational Modeling of Musical Expression: Perspectives, Datasets, Analysis and Generation](https://ismir2019.ewi.tudelft.nl/index2547.html?q=tutorials) at ISMIR 2019. 

* The original version of the data in this repository included a slightly modified version of the original match files (changes documented below). The score-to-performance alignments themselves were not modified. The match files were updated to include pedal information, similar to those in the Magaloff and Zeilinger dataset (private datasets available at the Institute of Computational Perception at JKU Linz).

* The initial contents of this repository only included match files, MusicXML files and image files, but no MIDI or audio files.

### Changes

* **MusicXML files**. The original dataset does not include symbolic scores in MusicXML format. Instead, the score information was entirely contained in the Match files. We created the MusicXML files from the score information in the original Match files using partitura version 0.2.0. We decided to go this route instead of getting MusicXML files from other sources, since that would have required basically to re-align the performances with the scores.

  * Dynamics markings, legato slurs, etc. were added manually on the MusicXML files directly.
  * Minimal correction of the stem directions and ensuring the order of attributes in the MusicXML file were done using the `move_stems.sh` and `fix_xml_note_attributes.py` scripts.

* **Unifying match file version**. In the original dataset, `Chopin_op10_no3` and `Chopin_op38` files are in the original match file version 1, while `Mozart_K331_1st-mov` and `Schubert_D783_no15` are version 5. Note however that the version 5 files in this dataset do not include pedal information that is available in other version 5 files (in the Magaloff and Zeilinger datasets). All files were converted to the same match file version.

* **Fixing/Adding sound off information**. The original `Chopin_op10_no3` and `Chopin_op38` version 1 match files did not include sound off information (i.e., implied note duration taking into account performed pedal). The original `Mozart_K331_1st-mov` and `Schubert_D783_no15` in version 5 have incorrect sound off information (the sound off in the files is identical to the note off). The new version adds the missing sound off to the `Chopin_op10_no3` and `Chopin_op38` files, and corrects the information for `Mozart_K331_1st-mov` and `Schubert_D783_no15`.

* **Unifying formatting of note ids**. For `Mozart_K331_1st-mov` and `Schubert_D783_no15` match files files, the note IDs were updated to start with `n` (e.g., `1` -> `n1`). This makes the IDs in the matchfile consistent with the IDs in the created MusicXML files.

* **Add images of the scores**. Added png and pdf images of the scores (necessary for the visualizations in the Jupyter notebooks in the ISMIR 2019 tutorial). Images were taken from scores in the public domain available on IMSLP.

* **Pedal information**. To be consistent with the match files in the Magaloff and Zeilinger datasets, pedal information was added to the matchfiles. The pedal information was taken from the MIDI files.

* **Removed redundant Meta lines** for `Mozart_K331_1st-mov` and `Schubert_D783_no15` encoding time signature and key signature information (information already contained in the info lines at the beginning).
