import numpy as np
import soundfile as sf
from scipy.io.wavfile import write
import os

# ============================================================
# Parameter
# ============================================================

sample_rate = 8000
frequency = 1000
duration = 20

# Zielpegel in dBFS
levels_db = [-60,-55,-50,-45,-40,-35,-30,-25, -24, -18, -12, -6, 0]

# Ordner
import_folder = "import"
export_folder = "export"


# ============================================================
# Hilfsfunktion: Audio auf Zielpegel skalieren
# ============================================================

def scale_to_dbfs(audio, db):

    # Maximale Amplitude bestimmen
    max_amplitude = np.max(np.abs(audio))

    # Stille Datei
    if max_amplitude == 0:
        return np.zeros_like(audio)

    # Auf 0 dBFS normalisieren
    normalized = audio / max_amplitude

    # Zielpegel berechnen
    amplitude = 10 ** (db / 20)

    # Auf Zielpegel skalieren
    scaled = normalized * amplitude

    return scaled


# ============================================================
# 1. Sinuswellen erzeugen
# ============================================================

sinus_folder = os.path.join(export_folder, "sinus")
os.makedirs(sinus_folder, exist_ok=True)

for db in levels_db:

    amplitude = 10 ** (db / 20)

    t = np.arange(int(duration * sample_rate)) / sample_rate

    signal = amplitude * np.sin(
        2 * np.pi * frequency * t
    )

    audio_int16 = np.int16(signal * 32767)

    filename = os.path.join(
        sinus_folder,
        f"sinus_{frequency}Hz_{db}dBFS.wav"
    )

    write(filename, sample_rate, audio_int16)

    print(f"Sinus erstellt: {filename}")


# ============================================================
# 2. WAV- und FLAC-Dateien aus "import" verarbeiten
# ============================================================

for filename in os.listdir(import_folder):

    # Nur WAV und FLAC verarbeiten
    if not filename.lower().endswith((".wav", ".flac")):
        continue

    input_path = os.path.join(import_folder, filename)

    # Audio mit SoundFile laden
    audio, original_sample_rate = sf.read(
        input_path,
        dtype="float64"
    )

    # Dateiname ohne Endung
    base_name = os.path.splitext(filename)[0]

    # Eigenen Exportordner erstellen
    output_folder = os.path.join(
        export_folder,
        base_name
    )

    os.makedirs(output_folder, exist_ok=True)

    print(f"\nVerarbeite: {filename}")

    # ========================================================
    # Für jeden Zielpegel eine Datei erzeugen
    # ========================================================

    for db in levels_db:

        scaled_audio = scale_to_dbfs(audio, db)

        # Dateiname
        output_filename = os.path.join(
            output_folder,
            f"{base_name}_{db}dBFS.wav"
        )

        # Als WAV speichern
        sf.write(
            output_filename,
            scaled_audio,
            original_sample_rate,
            subtype="PCM_16"
        )

        print(f"  {db} dBFS -> {output_filename}")


print("\nFertig!")