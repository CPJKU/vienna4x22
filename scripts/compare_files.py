import partitura as pt
import os
import glob
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":

    old_fn = "../match_original_files/Mozart_K331_1st-mov_p01.match"

    new_fn = "../match/Mozart_K331_1st-mov_p01.match"

    score_fn = "../musicxml/Mozart_K331_1st-mov.musicxml"

    midi_fn = "../midi/Mozart_K331_1st-mov_p01.mid"

    score = pt.load_musicxml(score_fn)
    perf = pt.load_performance_midi(midi_fn)

    perf_new, alignment_new, score_new = pt.load_match(new_fn, create_score=True)

    perf_old, alignment_old, score_old = pt.load_match(old_fn, create_score=True)

    # Do not take into account sound off
    perf_new[0].sustain_pedal_threshold = 127
    perf_old[0].sustain_pedal_threshold = 127
    perf[0].sustain_pedal_threshold = 127


    pnew_na = perf_new.note_array()
    pold_na = perf_old.note_array()
    pmidi_na = perf.note_array()

    pnew_onsets = pnew_na["onset_sec"]
    pold_onsets = pnew_na["onset_sec"]

    notes_old_new_crit = len(pnew_na) == len(pold_na)
    notes_old_midi_crit = len(pnew_na) == len(pmidi_na)



    onset_crit = np.allclose(pnew_onsets - pnew_onsets.min(), pold_onsets - pold_onsets.min())

    onset_midi_crit = np.allclose(pnew_onsets - pnew_onsets.min(), )

    pitch_crit = np.allclose(pnew_na["pitch"], pold_na["pitch"])

    duration_crit = np.allclose(pnew_na["duration_sec"], pold_na["duration_sec"])