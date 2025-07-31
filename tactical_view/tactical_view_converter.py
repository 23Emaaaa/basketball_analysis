import cv2
import numpy as np


class TacticalViewConverter:
    def __init__(self):
        """
        Inizializza il convertitore con le coordinate 3D standard di un campo da basket FIBA.
        """
        self.court_3d_coordinates = np.array(
            [
                [0, 0, 0],
                [28, 0, 0],
                [28, 15, 0],
                [0, 15, 0],
                [1.25, 7.5, 0],
                [1.25, 6.75, 0],
                [1.25, 8.25, 0],
                [4.5, 6.75, 0],
                [4.5, 8.25, 0],
                [14, 0.75, 0],
                [14, 14.25, 0],
                [0.9, 7.5, 0],
                [14, 7.5, 0],
            ]
        )

        self.basket_3d_coordinates = np.array([[1.575, 7.5, 3.05]])

        self.num_court_3d_points = len(self.court_3d_coordinates)

    def get_perspective_transform_matrix(self, court_keypoints_2d):
        """
        Calcola la matrice di trasformazione prospettica da 3D a 2D.
        """
        valid_indices = [
            i
            for i, kp in enumerate(court_keypoints_2d)
            if kp is not None and i < self.num_court_3d_points
        ]

        if len(valid_indices) < 4:
            return None

        src_points = np.array(
            [court_keypoints_2d[i] for i in valid_indices], dtype=np.float32
        )
        dst_points = np.array(
            [self.court_3d_coordinates[i][:2] for i in valid_indices], dtype=np.float32
        )

        matrix, _ = cv2.findHomography(src_points, dst_points)
        return matrix

    def transform_3d_to_2d(self, points_3d, court_keypoints_2d):
        """
        Converte un set di punti da coordinate 3D del mondo a coordinate 2D del frame.
        """
        if court_keypoints_2d is None or court_keypoints_2d.xy.numel() == 0:
            return None

        keypoints_xy = court_keypoints_2d.xy.cpu().numpy()[0]

        perspective_matrix = self.get_perspective_transform_matrix(keypoints_xy)

        if perspective_matrix is None:
            return None

        try:
            # Inverti la matrice per passare da mondo a immagine
            inv_perspective_matrix = np.linalg.inv(perspective_matrix)

            # Trasforma i punti 3D in coordinate 2D
            transformed_points = cv2.perspectiveTransform(
                points_3d[:, :2].reshape(-1, 1, 2).astype(np.float32),
                inv_perspective_matrix,
            )

            if transformed_points is None:
                return None

            return transformed_points.reshape(-1, 2)

        except np.linalg.LinAlgError:
            # Se la matrice è singolare, cattura l'errore e restituisci None
            # In questo modo il programma non si blocca e continua con il frame successivo
            return None
