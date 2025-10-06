from typing import List, Tuple
import partitura as pt
import os
import glob
import matplotlib.pyplot as plt
import numpy as np

import requests
import zipfile
import tempfile
import warnings
import pandas as pd
import shutil
import re
import csv

warnings.filterwarnings(
    "ignore",
    module="partitura",
)


score_pattern = re.compile(r"^(.+?)_p(\d{2})\.")


MUSICXML_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "musicxml",
)

MATCH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "match",
)

MIDI_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "midi",
)

# If the original files have not been setup,
# they will be downloaded and unzipped in this directory
ORIGINAL_FILES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "original_files",
)


def download_and_unzip(url: str, extract_to: str) -> None:
    """
    Download a ZIP file from a URL, extract its contents to a specified directory,
    and remove macOS auxiliary files such as '__MACOSX' and '._*'.

    Parameters
    ----------
    url : str
        The URL pointing to the ZIP file to download.
    extract_to : str
        The local directory path where the contents of the ZIP file should be extracted.
    """
    os.makedirs(extract_to, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
        print(f"Downloading from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)

        tmp_file_path = tmp_file.name

    print(f"Extracting contents to {extract_to}...")
    with zipfile.ZipFile(tmp_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    os.remove(tmp_file_path)

    # Remove macOS-specific files and folders
    macosx_path = os.path.join(extract_to, "__MACOSX")
    if os.path.exists(macosx_path):
        print("Removing macOS __MACOSX metadata folder...")
        shutil.rmtree(macosx_path)

    print("Removing '._*' macOS metadata files...")
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.startswith("._"):
                full_path = os.path.join(root, file)
                os.remove(full_path)

    print("Download, extraction, and cleanup completed.")


def get_controls(controls: list[dict]) -> set[tuple]:
    """
    Get MIDI control changes as a set for easier comparison.

    Parameters
    ----------
    controls: list[dict]
        A list of dictionaries containing MIDI control information, as provided by
        the `controls` property of a `partitura.performance.PerformedPart` object.

    Returns
    -------
    projected_set : set[tuple]
        A set of tuples containig information for comparison. The time of the control
        messages was rounded to milliseconds to avoid incorrect comparisons due to
        rounding errors.
    """
    projected_set = {
        (
            c["number"],
            np.round(c["time"], 3),
            c["value"],
        )
        for c in controls
    }
    return projected_set


def get_score_info(note_array: np.ndarray) -> dict:
    """
    Get information to check:

    * MIDI pitch
    * onset in beats
    * duration in beats
    * pitch spelling: step, alter, octave
    * key signature: number of fifths and mode
    * time signature: beats, beat type

    Parameters
    ----------
    note_array: np.ndarray
        Structured note array with note level information

    Returns
    -------
    dict
        A dictionary where the keys are note ids and the info represents
        information for the corresponding score note
    """
    df = pd.DataFrame(note_array)
    df["nid"] = (
        df["id"].astype(str).apply(lambda x: x if x.startswith("n") else f"n{x}")
    )
    return dict(
        zip(
            df["nid"],
            zip(
                df["pitch"],
                df["onset_beat"],
                df["duration_beat"],
                df["step"],
                df["alter"],
                df["octave"],
                df["ks_fifths"],
                df["ks_mode"],
                df["ts_beats"],
                df["ts_beat_type"],
            ),
        )
    )

def get_perf_info(note_array: np.ndarray) -> dict:
    """
    Get information to check:

    * MIDI pitch
    * onset in beats
    * duration in beats
    * pitch spelling: step, alter, octave
    * key signature: number of fifths and mode
    * time signature: beats, beat type

    Parameters
    ----------
    note_array: np.ndarray
        Structured note array with note level information

    Returns
    -------
    dict
        A dictionary where the keys are note ids and the info represents
        information for the corresponding score note
    """
    df = pd.DataFrame(note_array)
    df["nid"] = (
        df["id"].astype(str).apply(lambda x: x if x.startswith("n") else f"n{x}")
    )
    return dict(
        zip(
            df["nid"],
            zip(
                df["pitch"],
                df["onset_sec"],
                df["duration_sec"],
                df["velocity"],
            ),
        )
    )


def check_piece(
    new_fn: str,
    score: pt.score.Score,
    midi_fn: str,
    old_fn: str,
    old_midi_fn: str,
) -> Tuple[
    List[bool],
    List[bool],
    List[bool],
]:
    """
    Check piece.
    """

    # score = pt.load_musicxml(score_fn)
    perf = pt.load_performance_midi(midi_fn)
    perf_midi_old = pt.load_performance_midi(old_midi_fn)

    perf_new, alignment_new, score_new = pt.load_match(
        new_fn,
        create_score=True,
    )

    perf_old, alignment_old, score_old = pt.load_match(
        old_fn,
        create_score=True,
    )

    musicxml_sna = score.note_array(
        include_key_signature=True,
        include_pitch_spelling=True,
        include_time_signature=True,
    )
    matchnew_sna = score_new.note_array(
        include_key_signature=True,
        include_pitch_spelling=True,
        include_time_signature=True,
    )
    matchold_sna = score_old.note_array(
        include_key_signature=True,
        include_pitch_spelling=True,
        include_time_signature=True,
    )

    musicxml_info = get_score_info(musicxml_sna)
    matchnew_info = get_score_info(matchnew_sna)
    matchold_info = get_score_info(matchold_sna)

    # Do not take into account sound off
    perf_new[0].sustain_pedal_threshold = 127
    perf_old[0].sustain_pedal_threshold = 127
    perf[0].sustain_pedal_threshold = 127
    perf_midi_old[0].sustain_pedal_threshold = 127

    controls_new = get_controls(perf_new[0].controls)
    controls_midi = get_controls(perf[0].controls)
    # controls_midi_old = get_controls(perf_midi_old[0].controls)

    pnew_na = perf_new.note_array()
    pold_na = perf_old.note_array()
    pmidi_na = perf.note_array()
    pmidiold_na = perf_midi_old.note_array()

    pnew_onsets = pnew_na["onset_sec"]
    pold_onsets = pold_na["onset_sec"]
    pmidi_onsets = pmidi_na["onset_sec"]
    pmidiold_onsets = pmidiold_na["onset_sec"]

    # Fix note id formatting for old files that don't start with "n"
    # This needs to be done for the origi
    for al in alignment_old:
        if "score_id" in al:
            if not al["score_id"].startswith("n"):
                al["score_id"] = f"n{al['score_id']}"

    # check that all score notes in the original match files are in the MusicXML
    musicxml_oldmatch_crit = all([note in musicxml_info for note in matchold_info])

    # check that all score notes in the original match files are in matchfiles v1.0.0
    match_oldmatch_crit = all([note in matchnew_info for note in matchold_info])

    # check that alignments are the same
    # i.e., check that all elements in the old alignment (original match files)
    # are in the new alignment (matchfiles v1.0.0)
    in_new_alignment_crit = all([al in alignment_new for al in alignment_old])

    # Check that all onsets in the match file correspond to onsets in the midi file
    try:
        onset_midi_crit_new_midi = np.allclose(pnew_onsets, pmidi_onsets)
    except ValueError:
        onset_midi_crit_new_midi = False

    # Check that matchfiles v1.0.0 include the same control messages as the MIDI
    cc_new_midi_crit = all([cc in controls_midi for cc in controls_new])
    # Check that the new MIDI files have the same number of control messages as the original MIDI files
    # (since the control messages were adjusted in time)
    cc_midi_midiold_crit = len(perf[0].controls) == len(perf_midi_old[0].controls)

    # Check that all onsets in the new MIDI files correspond to the onsets in
    # the original midi files (relative to the first note)
    try:
        onset_midi_midiold_crit = np.allclose(
            pmidi_onsets - pmidi_onsets.min(),
            pmidiold_onsets - pmidiold_onsets.min(),
        )
    except:
        onset_midi_midiold_crit = False

    # Check that the number of performance notes in all alignments are the same
    notes_old_new_crit = len(pnew_na) == len(pold_na)
    notes_old_midi_crit = len(pnew_na) == len(pmidi_na)
    notes_midiold_midi_crit = len(pmidi_na) == len(pmidiold_na)

    # Check that the onsets in the original match files and the onsets in the
    # match files v1.0.0 are the same up, relative to the first onset
    try:
        onset_crit = np.allclose(
            pnew_onsets - pnew_onsets.min(),
            pold_onsets - pold_onsets.min(),
        )
    except ValueError:
        onset_crit = False

    # Check that all pitches in the match file v1.0.0 to pitches in
    # the original match file
    try:
        pitch_crit = np.allclose(pnew_na["pitch"], pold_na["pitch"])
    except ValueError:
        pitch_crit = False

    # check that durations of the notes
    try:
        duration_crit = np.allclose(
            pnew_na["duration_sec"],
            pmidi_na["duration_sec"],
        )
    except ValueError:
        duration_crit = False

    perf_checks = [
        cc_new_midi_crit,
        cc_midi_midiold_crit,
        onset_midi_crit_new_midi,
        # onset_midi_midiold_crit,
        notes_old_midi_crit,
        notes_old_new_crit,
        notes_midiold_midi_crit,
        # onset_crit,
        pitch_crit,
        duration_crit,
    ]

    score_checks = [
        musicxml_oldmatch_crit,
        match_oldmatch_crit,
    ]

    alignment_checks = [
        in_new_alignment_crit,
    ]

    return perf_checks, score_checks, alignment_checks


if __name__ == "__main__":

    if not os.path.exists(ORIGINAL_FILES_DIR):
        original_match_url = "http://repo.mdw.ac.at/projects/IWK/the_vienna_4x22_piano_corpus/data/match.zip"
        download_and_unzip(
            url=original_match_url,
            extract_to=ORIGINAL_FILES_DIR,
        )

        original_midi_url = "http://repo.mdw.ac.at/projects/IWK/the_vienna_4x22_piano_corpus/data/midi.zip"
        download_and_unzip(
            url=original_midi_url,
            extract_to=ORIGINAL_FILES_DIR,
        )

    new_fn = "../match/Mozart_K331_1st-mov_p01.match"

    score_files = glob.glob(os.path.join(MUSICXML_DIR, "*.musicxml"))

    scores = dict()
    for sfn in score_files:
        scores[os.path.splitext(os.path.basename(sfn))[0]] = pt.load_musicxml(sfn)


    new_match_files = glob.glob(os.path.join(MATCH_DIR, "*.match"))
    new_match_files.sort()

    for new_fn in new_match_files:

        score_name = score_pattern.search(os.path.basename(new_fn)).group(1)

        score = scores[score_name]

        midi_fn = os.path.join(
            MIDI_DIR,
            os.path.basename(new_fn).replace(".match", ".mid"),
        )

        old_fn = os.path.join(
            ORIGINAL_FILES_DIR,
            "match",
            os.path.basename(new_fn),
        )

        old_midi_fn = os.path.join(
            ORIGINAL_FILES_DIR,
            "midi",
            os.path.basename(midi_fn),
        )

        perf_checks, score_checks, alignment_checks = check_piece(
            new_fn=new_fn,
            score=score,
            midi_fn=midi_fn,
            old_fn=old_fn,
            old_midi_fn=old_midi_fn,
        )

        if all(perf_checks) and all(score_checks) and all(alignment_checks):
            print(new_fn, "passed")
        else:
            print(new_fn, "failed")

        csv_file = "compare_results.csv"
        header = ["filename"] + [f"check_{i}" for i in range(len(perf_checks + score_checks + alignment_checks))]

        if not os.path.exists(csv_file):
            with open(csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)

        row = [new_fn] + list(perf_checks + score_checks + alignment_checks)
        with open(csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)
