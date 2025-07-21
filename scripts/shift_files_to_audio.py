import partitura as pt
import os
import glob
import re
from partitura.utils.fluidsynth import synthesize_fluidsynth
import numpy as np
import matplotlib.pyplot as plt
import madmom

from typing import Optional, Tuple

from scipy.signal import convolve
from numpy.linalg import norm

import warnings

# Ignore all warnings from a specific module
warnings.filterwarnings("ignore", module="partitura")

SAMPLE_RATE = 44100
FRAME_SIZE = 1024
HOP_SIZE = 64

perf_match_pat = re.compile("(.+)_p([0-9]{2})")


def fast_cosine_similarity(X: np.ndarray, kernel: np.ndarray) -> np.ndarray:

    cos_conv = convolve(X, np.flip(kernel) / norm(kernel), mode="valid")

    X_norm_est = np.sqrt(convolve(X**2, np.ones(kernel.shape), mode="valid"))

    cosine_similarity = (cos_conv / (X_norm_est)).sum(1)

    distance = 1 - cosine_similarity

    return distance


if __name__ == "__main__":

    audio_dir = "/Volumes/Rach3M02/vienna4x22/audio"
    match_dir = "../match"
    score_dir = "../musicxml"

    adj_midi_dir = "../midi_adj"

    if not os.path.exists(adj_midi_dir):
        os.mkdir(adj_midi_dir)

    adj_match_dir = "../match_adj"
    if not os.path.exists(adj_match_dir):
        os.mkdir(adj_match_dir)

    window_size_in_sec = 5

    window_size = int(np.ceil(window_size_in_sec * SAMPLE_RATE / HOP_SIZE))

    scores_dict = dict()

    audio_files = glob.glob(os.path.join(audio_dir, "*", "*.wav"))

    # Discard special versions
    audio_files = [
        fn for fn in audio_files if "Chopin_Ballade_special-versions" not in fn or "average" in fn
    ]

    audio_files.sort()

    audio_fn = audio_files[0]

    for audio_fn in audio_files:
        print(f"Processing {audio_fn}...")

        piece = os.path.basename(audio_fn).replace(".wav", "")

        piece_name = perf_match_pat.match(piece).group(1)

        if piece_name not in scores_dict:
            score_fn = os.path.join(
                score_dir,
                f"{piece_name}.musicxml",
            )
            scores_dict[piece_name] = pt.load_musicxml(score_fn)

        score = scores_dict[piece_name]

        match_fn = os.path.join(match_dir, f"{piece}.match")

        out_midi_fn = os.path.join(adj_midi_dir, f"{piece}.mid")
        out_match_fn = os.path.join(adj_match_dir, f"{piece}.match")

        if not os.path.exists(out_midi_fn) and not os.path.exists(out_match_fn) and os.path.exists(match_fn):

            perf, alignment = pt.load_match(match_fn)

            pnote_array = perf.note_array()

            # Set sound off to note off
            for ppart in perf:
                for note in ppart.notes:
                    # fix pedal info
                    note["channel"] = 0
                    note["track"] = 0

                for ctrl in ppart.controls:
                    ctrl["channel"] = 0
                    ctrl["track"] = 0
            # synthesize performance
            synth_perf = synthesize_fluidsynth(
                note_info=perf,
                samplerate=SAMPLE_RATE,
            )

            # Get spectrogram of the synthesized performance
            synth_signal = madmom.audio.FramedSignal(
                synth_perf,
                frame_size=FRAME_SIZE,
                hop_size=HOP_SIZE,
                sample_rate=SAMPLE_RATE,
            )

            synth_spect = madmom.audio.LogarithmicFilteredSpectrogram(synth_signal)

            # Compute spectrogram of the audio recording
            audio_signal = madmom.audio.FramedSignal(
                audio_fn,
                frame_size=FRAME_SIZE,
                hop_size=HOP_SIZE,
                sample_rate=SAMPLE_RATE,
                num_channels=1,
            )

            audio_spect = madmom.audio.LogarithmicFilteredSpectrogram(audio_signal)

            # Get first onset time from the performance in the match file
            synth_frame_times = np.arange(synth_signal.num_frames) * (HOP_SIZE / SAMPLE_RATE)
            note_array = perf.note_array()
            first_onset = note_array["onset_sec"].min()
            first_onset_delta = 0.1 if first_onset > 0 else 0
            synth_start = abs(synth_frame_times - first_onset - first_onset_delta).argmin()

            # select first kernel
            ssw = synth_spect[synth_start : synth_start + window_size]

            # Get time of the first onset in the recording
            audio_start = int(np.ceil(0 * SAMPLE_RATE / HOP_SIZE))
            audio_end = int(np.ceil(10 * SAMPLE_RATE / HOP_SIZE))

            distance = fast_cosine_similarity(audio_spect[audio_start:audio_end], ssw)
            first_onset_audio = distance.argmin() * HOP_SIZE / SAMPLE_RATE
            first_onset_in_frames = distance.argmin()
            window_time = distance.argmin() * HOP_SIZE / SAMPLE_RATE

            time_shift = window_time - first_onset - first_onset_delta

            for note in perf[0].notes:

                note["note_on"] = max(0, note["note_on"] + time_shift)
                note["note_off"] = max(0, note["note_off"] + time_shift)

            for ctrl in perf[0].controls:

                ctrl["time"] = max(0, ctrl["time"] + time_shift)

            for program in perf[0].programs:

                program["time"] = max(0, program["time"] + time_shift)


            print("Save MIDI")
            
            pt.save_performance_midi(
                performance_data=perf,
                out=out_midi_fn,
            )

            # Save match file
            # Get original match file to get meta info
            mf = pt.io.importmatch.load_matchfile(match_fn)
            print("Save match file")
            # Save match file
            pt.save_match(
                alignment=alignment,
                performance_data=perf,
                score_data=score,
                out=out_match_fn,
                mpq=perf[0].mpq,
                ppq=perf[0].ppq,
                piece=mf.info("piece"),
                performer=mf.info("performer"),
                composer=mf.info("composer"),
                score_filename=mf.info("scoreFileName"),
                performance_filename=os.path.basename(out_midi_fn),
                assume_unfolded=True,
                # infer_tempo_indication_from_score=False,
            )