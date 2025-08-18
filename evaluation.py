import argparse
import json
import pandas as pd
import numpy as np
from utils import read_video
from trackers import PlayerTracker, BallTracker
from configs import PLAYER_DETECTOR_PATH, BALL_DETECTOR_PATH
from ultralytics import YOLO


def calculate_iou(boxA, boxB):
    """
    Calcola l'Intersection over Union (IoU) di due bounding box.
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou


def load_ground_truth(file_path):
    """
    Carica il file di ground truth (JSON o CSV) e lo formatta.
    Questa funzione è un placeholder e dovrà essere adattata
    al formato esatto del tuo file esportato da Roboflow.
    """
    # Esempio di implementazione (da adattare)
    # Si aspetta un formato del tipo: {frame_num: {'ball': [bbox], 'players': [bbox1, bbox2, ...]}}
    ground_truth = {}

    # DA COMPLETARE: Logica per leggere il tuo file specifico
    # Esempio se fosse un JSON:
    # with open(file_path, 'r') as f:
    #     data = json.load(f)
    #     for frame_annotation in data['frames']:
    #         frame_num = frame_annotation['frame_number']
    #         ground_truth[frame_num] = {'ball': [], 'players': []}
    #         for obj in frame_annotation['objects']:
    #             if obj['class_name'] == 'ball':
    #                 ground_truth[frame_num]['ball'].append(obj['bbox'])
    #             elif obj['class_name'] == 'player':
    #                 ground_truth[frame_num]['players'].append(obj['bbox'])

    print(f"Ground truth caricato da: {file_path}. (Logica di parsing da implementare)")
    return ground_truth


def evaluate_ball_detection(gt_frames, pred_frames, iou_threshold=0.5):
    """
    Valuta il rilevamento della palla usando Precision, Recall e F1-Score.
    """
    tp, fp, fn = 0, 0, 0

    for frame_num in gt_frames.keys():
        gt_ball_bbox = gt_frames[frame_num].get("ball", [None])[0]
        pred_ball_bbox = pred_frames[frame_num].get(1, {}).get("bbox")

        if gt_ball_bbox and pred_ball_bbox:
            iou = calculate_iou(gt_ball_bbox, pred_ball_bbox)
            if iou >= iou_threshold:
                tp += 1
            else:
                fp += 1
                fn += 1
        elif gt_ball_bbox and not pred_ball_bbox:
            fn += 1
        elif not gt_ball_bbox and pred_ball_bbox:
            fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return {"precision": precision, "recall": recall, "f1_score": f1_score}


def evaluate_player_tracking(gt_frames, pred_frames, iou_threshold=0.5):
    """
    Valuta il tracciamento dei giocatori calcolando l'errore di posizione medio.
    """
    total_position_error = 0
    matched_players = 0

    for frame_num in gt_frames.keys():
        gt_players = gt_frames[frame_num].get("players", [])
        pred_players_dict = pred_frames[frame_num]
        pred_players = [info["bbox"] for info in pred_players_dict.values()]

        if not gt_players or not pred_players:
            continue

        # Matching tra ground truth e predizioni basato su IoU
        for gt_box in gt_players:
            best_match_iou = -1
            best_match_box = None
            for pred_box in pred_players:
                iou = calculate_iou(gt_box, pred_box)
                if iou > best_match_iou:
                    best_match_iou = iou
                    best_match_box = pred_box

            if best_match_iou >= iou_threshold:
                matched_players += 1
                gt_center = np.array(
                    [(gt_box[0] + gt_box[2]) / 2, (gt_box[1] + gt_box[3]) / 2]
                )
                pred_center = np.array(
                    [
                        (best_match_box[0] + best_match_box[2]) / 2,
                        (best_match_box[1] + best_match_box[3]) / 2,
                    ]
                )
                error = np.linalg.norm(gt_center - pred_center)
                total_position_error += error

    mean_position_error = (
        total_position_error / matched_players if matched_players > 0 else 0
    )
    return {
        "mean_position_error_pixels": mean_position_error,
        "matched_players": matched_players,
    }


def main(input_video_path, ground_truth_path):
    print("1. Caricamento video...")
    video_frames = read_video(input_video_path)

    print("2. Caricamento Ground Truth...")
    ground_truth_data = load_ground_truth(ground_truth_path)

    # Controlla se il ground truth è stato caricato (la funzione è un placeholder)
    if not ground_truth_data:
        print("\nAVVISO: La funzione 'load_ground_truth' non è implementata.")
        print(
            "Modifica 'evaluation.py' per parsare il tuo file di etichettatura specifico."
        )
        return

    print("3. Esecuzione dei tracker del modello...")
    # Rilevamento Palla
    ball_model = YOLO(BALL_DETECTOR_PATH)
    ball_tracker = BallTracker(ball_model)
    ball_tracks = ball_tracker.track_frames(video_frames)

    # Rilevamento Giocatori
    player_tracker = PlayerTracker(PLAYER_DETECTOR_PATH)
    player_tracks = player_tracker.get_object_tracks(video_frames, read_from_stub=False)

    print("4. Valutazione del rilevamento della palla...")
    ball_metrics = evaluate_ball_detection(ground_truth_data, ball_tracks)
    print(f"  - Precision: {ball_metrics['precision']:.4f}")
    print(f"  - Recall:    {ball_metrics['recall']:.4f}")
    print(f"  - F1-Score:  {ball_metrics['f1_score']:.4f}")

    print("\n5. Valutazione del tracciamento dei giocatori...")
    player_metrics = evaluate_player_tracking(ground_truth_data, player_tracks)
    print(
        f"  - Errore di Posizione Medio: {player_metrics['mean_position_error_pixels']:.2f} pixel"
    )
    print(f"  - Giocatori Corrisposti: {player_metrics['matched_players']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Valuta i tracker rispetto a un ground truth."
    )
    parser.add_argument(
        "--input_video", type=str, required=True, help="Percorso del video di input."
    )
    parser.add_argument(
        "--ground_truth_file",
        type=str,
        required=True,
        help="Percorso del file di ground truth (JSON/CSV).",
    )

    args = parser.parse_args()
    main(args.input_video, args.ground_truth_file)
