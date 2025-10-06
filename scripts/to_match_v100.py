import numpy as np
import partitura as pt
from typing import List
from partitura.io.importmatch import (
    load_matchfile,
    performed_part_from_match,
    alignment_from_matchfile,
    load_match,
)

from partitura.io.matchfile_utils import format_pnote_id
from partitura.io.importmatch_old import load_match as load_match_old


import os
import glob


def sanitize_alignment(alignment: List[dict]) -> None:
    """
    Ensure that note ids are strings in alignments.
    These method changes alignments in-place.

    Parameters
    ----------
    alignment : List[dict]
        List of dictionaries containing an alignment.
    """
    for note in alignment:

        score_id = note.get("score_id", None)

        if score_id is not None:
            note["score_id"] = str(score_id)
        perf_id = note.get("performance_id", None)

        if perf_id is not None:
            note["performance_id"] = format_pnote_id(perf_id)


def check_alignment(old_alignment: List[dict], alignment: List[dict]) -> bool:
    check_new_in_old = all([al in old_alignment for al in alignment])

    check_old_in_new = all([al in alignment for al in old_alignment])

    return check_new_in_old and check_old_in_new


def check_performance(old_perf, new_perf):

    old_na = old_perf.note_array()
    new_na = new_perf.note_array()

    nid = np.array([format_pnote_id(pid) for pid in new_na["id"]])
    oid = np.array([format_pnote_id(pid) for pid in old_na["id"]])

    old_sort_idx = np.lexsort(
        [old_na[name] for name in ("velocity", "duration_sec", "pitch", "onset_sec")]
    )

    new_sort_idx = np.lexsort(
        [new_na[name] for name in ("velocity", "duration_sec", "pitch", "onset_sec")]
    )

    old_na = old_na[old_sort_idx]
    new_na = new_na[new_sort_idx]
    nid = nid[new_sort_idx]
    oid = oid[old_sort_idx]

    crit = [
        np.allclose(old_na[name], new_na[name])
        for name in ("onset_sec", "duration_sec", "pitch", "velocity")
    ] + [np.all(nid == oid)]

    if not all(crit):
        print(crit)
    return all(crit)


def check_score(old_score, new_score):

    old_na = old_score.note_array()
    new_na = new_score.note_array()

    new = dict(
        [(n["id"], tuple(n[["duration_beat", "pitch", "onset_beat"]])) for n in new_na]
    )

    old = dict(
        [(n["id"], tuple(n[["duration_beat", "pitch", "onset_beat"]])) for n in old_na]
    )

    crit = [nval == old[k] for k, nval in new.items() if k in old]

    print(sum(crit), len(new), len(old))

    return all(crit)


old_match_dir = "/Users/carlos/Repos/vienna4x22/match"

new_match_dir = "/Users/carlos/Repos/vienna4x22_v100/match_new/"

if not os.path.exists(new_match_dir):
    os.mkdir(new_match_dir)

xml_dir = "/Users/carlos/Repos/vienna4x22/musicxml"

scores_fns = glob.glob(os.path.join(xml_dir, "*.musicxml"))

for sfn in scores_fns:
    piece = os.path.splitext(os.path.basename(sfn))[0]

    score = pt.load_musicxml(sfn)

    print(piece)

    matchfiles = glob.glob(os.path.join(old_match_dir, f"{piece}*.match"))

    assert len(matchfiles) == 22

    for mfn in matchfiles:
        print(os.path.basename(mfn))
        mf = load_matchfile(mfn)

        old_perf, old_alignment = load_match_old(mfn)

        sanitize_alignment(old_alignment)

        alignment = alignment_from_matchfile(mf)

        assert check_alignment(old_alignment, alignment)

        pperf = performed_part_from_match(mf)

        assert check_performance(old_perf, pperf)

        out_fn = os.path.join(new_match_dir, os.path.basename(mfn))

        pt.save_match(
            alignment=alignment,
            performance_data=pperf,
            score_data=score,
            out=out_fn,
            composer=mf.info("composer"),
            performer=mf.info("performer"),
            piece=mf.info("piece"),
            score_filename=os.path.basename(sfn),
            performance_filename=os.path.basename(mfn).replace(".match", ".mid"),
            assume_unfolded=True,
            mpq=mf.info("midiClockRate"),
            ppq=mf.info("midiClockUnits"),
        )

        perf_from_match, new_alignment, score_from_match = load_match(
            out_fn, create_score=True
        )

        assert check_alignment(old_alignment, new_alignment)
        assert check_performance(old_perf, perf_from_match)
        assert check_score(score, score_from_match)
