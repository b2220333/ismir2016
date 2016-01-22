import DeepInstruments as di
import librosa
import numpy as np
import os
import shutil


def chunk_stems(dataset_path,
                decision_hop,
                decision_length,
                training_or_test):
    activation_hop = 2048
    test_stems, training_stems = di.singlelabel.get_stems()
    if training_or_test == "training":
        stems = training_stems
    elif training_or_test == "test":
        stems = test_stems
    else:
        raise ValueError("Input to chunk_waveforms must be training or test")
    for instrument_id in range(len(stems)):
        instrument_name = di.singlelabel.names[instrument_id]
        instrument_id_str = repr('%(i)02d' % {"i": instrument_id})[1:-1]
        instrument_folder = instrument_id_str + "_" + instrument_name
        instrument_folder_path = os.path.join(dataset_path,
                                              training_or_test,
                                              instrument_folder)
        try:
            os.makedirs(instrument_folder_path)
        except OSError:
            shutil.rmtree(instrument_folder_path)
            os.makedirs(instrument_folder_path)
        for file_id in range(len(stems[instrument_id])):
            file_id_str = repr('%(i)02d' % {"i": file_id})[1:-1]
            stem = stems[instrument_id][file_id]
            track_name = stem.track.name
            stem_name = stem.name
            file_folder = file_id_str + "_" + track_name + "_" + stem_name
            file_folder_path = os.path.join(dataset_path,
                                            training_or_test,
                                            instrument_folder,
                                            file_folder)
            try:
                os.makedirs(file_folder_path)
            except OSError:
                shutil.rmtree(file_folder_path)
                os.makedirs(file_folder_path)
            Y = np.vstack(stem.track.activations_data)[:, stem.name[1:]]
            half_x_hop = int(0.5 * decision_length)
            Y_hop = int(0.5 * float(decision_hop) / activation_hop)
            Y_id = Y_hop
            chunk_id = 0
            sr, x = stem.audio_data
            while Y_id < (len(Y) - 2*Y_hop):
                if Y[Y_id] > 0.5:
                    x_id = int(Y_id * activation_hop)
                    x_range = xrange(x_id-half_x_hop, x_id+half_x_hop)
                    x_chunk = np.mean(x[x_range, :], axis=1)
                    chunk_id_str = repr('%(i)03d' % {"i": chunk_id})[1:-1]
                    chunk_str = instrument_name + \
                                "_" + \
                                track_name + \
                                "_" + \
                                stem_name + \
                                "_chunk" + \
                                chunk_id_str + \
                                ".wav"
                    chunk_path = os.path.join(dataset_path,
                                              training_or_test,
                                              instrument_folder,
                                              file_folder,
                                              chunk_str)
                    print(chunk_path)
                    librosa.output.write_wav(chunk_path,
                                             x_chunk,
                                             sr=44100,
                                             norm=False)
                    Y_id += Y_hop
                    chunk_id += 1
                Y_id += Y_hop


def chunk_waveforms(dest_path, decision_hop, decision_length, source_path):
    subdirs = [subdir for (path,subdir,names) in os.walk(source_path)][0]
    for subdir in subdirs:
        instrument_name = subdir[3:]
        source_instrument_path = os.path.join(source_path, subdir)
        dest_instrument_path = os.path.join(dest_path, "test", subdir)
        source_file_names = [name for (p,s,name)
                             in os.walk(source_instrument_path)][0]
        for file_id in range(len(source_file_names)):
            source_file_name = source_file_names[file_id]
            dest_file_folder = source_file_name[:-4] # remove WAV extension
            dest_folder_path = os.path.join(dest_instrument_path,
                                            dest_file_folder)
            os.makedirs(dest_folder_path)
            source_file_path = os.path.join(source_instrument_path,
                                            source_file_name)
            waveform, sr = librosa.core.load(source_file_path,
                                             sr=44100,
                                             mono=True)
            chunk_id = 0
            x_id = 0
            while x_id+decision_length < len(waveform):
                x_range = xrange(x_id, x_id + decision_length)
                chunk = waveform[x_range]
                chunk_norm = np.linalg.norm(chunk)
                if chunk_norm > 1.0: # silence threshold
                    chunk_id += 1
                    chunk_id_str = repr('%(i)03d' % {"i": chunk_id})[1:-1]
                    chunk_str = instrument_name + \
                                "_" + \
                                dest_file_folder + \
                                "_chunk" + \
                                chunk_id_str + \
                                ".wav"
                    chunk_path = os.path.join(dest_folder_path,
                                              chunk_str)
                    librosa.output.write_wav(chunk_path,
                                             chunk,
                                             sr=44100,
                                             norm=False)
                x_id += decision_hop



def export_singlelabel_dataset():
    dest_path = os.path.join(os.path.expanduser("~"),
                                "datasets",
                                "medleydb-single-instruments")
    decision_hop = 65536
    decision_length = 131072
    chunk_stems(dest_path, decision_hop, decision_length, "training")
    chunk_stems(dest_path, decision_hop, decision_length, "test")
    solosDb_path = os.path.join(os.path.expanduser("~"),
                                "datasets",
                                "solosDb_for_ismir2016")
    chunk_waveforms(dest_path, decision_hop, decision_length, solosDb_path)
