import cv2
import os
from pathlib import Path


def extract_frames_from_videos(input_dir, output_dir, interval_seconds=0.4):
    """
    Estrae i frame dai file video in una directory e li salva come immagini.

    Args:
        input_dir (str): La cartella contenente i file video.
        output_dir (str): La cartella dove salvare i frame estratti.
        interval_seconds (int): L'intervallo in secondi tra le estrazioni dei frame.
    """
    # Crea la directory di output se non esiste
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(f"Directory di output creata: {output_dir}")

    video_files = [
        f for f in os.listdir(input_dir) if f.lower().endswith((".mp4", ".mov"))
    ]
    if not video_files:
        print(f"Nessun file video (.mp4 o .mov) trovato in {input_dir}")
        return

    print(f"Trovati {len(video_files)} video. Inizio estrazione...")

    total_frames_extracted = 0
    for video_file in video_files:
        video_path = os.path.join(input_dir, video_file)
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"Errore: Impossibile aprire il video {video_path}")
            continue

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * interval_seconds)

        frame_count = 0
        extracted_count_per_video = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # Fine del video

            if frame_count % frame_interval == 0:
                output_filename = f"{Path(video_file).stem}_frame_{frame_count}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                cv2.imwrite(output_path, frame)
                extracted_count_per_video += 1

            frame_count += 1

        cap.release()
        print(f"- Estratti {extracted_count_per_video} frame da {video_file}")
        total_frames_extracted += extracted_count_per_video

    print(f"\nEstrazione completata. Totale frame estratti: {total_frames_extracted}")


if __name__ == "__main__":
    # Definisci le cartelle di input e output relative alla root del progetto
    INPUT_VIDEO_DIR = "input_videos"
    OUTPUT_IMAGE_DIR = "roboflow_dataset/images"  # Sottocartella "images" per una migliore organizzazione

    # Esegui la funzione
    extract_frames_from_videos(INPUT_VIDEO_DIR, OUTPUT_IMAGE_DIR)
