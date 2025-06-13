# Changes

## 13.06.2025

* Fixed score onset time of notes in match files for `Mozart_K331_1st-mov` and `Chopin_op38`. Due to a bug in partitura, symbolic score time in the match files was incorrectly represented in quarters instead of beats. This bug affected the `Mozart_K331_1st-mov` and `Chopin_op38` files which have a time signature of 6/8. This issue was addressed with [PR #454 in partitura](https://github.com/CPJKU/partitura/pull/454).

## 07.03.24

* Update starting time of MIDI and and Matchfiles to start with the audio files. This was done automatically by shifting the note onset/offset times and MIDI controls (pedals).

* Add script to setup the audio files.

## 14.06.23

### Bugs

* B1. incorrect clock_unit property (4000, should be 480)
* B2. for Chopin_op38: last performed midi note missing in all match files except for last one (in last performance, last four notes are ommitted)
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

* Update Match files to version 1.0.0.

## 03.02.2022

* Add MIDI files from the original repository for convenience.

## 04.11.2019

This repository was created for the tutorial on Expressive Music Performance presented at ISMIR. It includes a slightly modified version of the original Matchfiles (changes documented below). The alignments themselves where not modified. The match files were updated to include pedal information, similar to those in the Magaloff dataset (a proprietary dataset).

* The repository only includes match files, MusicXML files and image files. This repository **does not include the audio files**.

### Changes

* **MusicXML files**. The original dataset does not include symbolic scores in MusicXML format. Instead, the score information is entirely represented in the Match files. We created the MusicXML files from the score information in the original Match files using partitura version 0.2.0. We decided to go this route instead of getting MusicXML files from other sources, since that would have required matching the notes in the. The trade-off is that information like beaming, etc. is missing.

  * Dynamics markings, legato slurs, etc. were added manually on the MusicXML files directly.
  * Minimal correction of the stem directions and ensuring the order of attributes in the MusicXML file were done using the `move_stems.sh` and `fix_xml_note_attributes.py` scripts.

* **Fixing formatting of note ids**. For Mozart and Schubert files, the note IDs were updated to start with `n` (e.g., `1` -> `n1`). This change was done to be consistent with the Magaloff and Zeilinger Datasets

* **Add images of the scores** Add png and pdf images of the scores (necessary for the visualizations in the Jupyter notebooks in the ISMIR 2019 tutorial).

* **Add pedal information**. To be consistent with Match file format 5.0, add pedal information to the match files.
