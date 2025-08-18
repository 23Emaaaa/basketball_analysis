import unittest
import numpy as np
from trackers.ball_tracker import BallTracker
from utils.kalman_filter import KalmanFilter


class MockYOLOModel:
    """
    Classe fittizia per simulare il modello YOLO senza caricarlo realmente.
    """

    def predict(self, frames, conf):
        pass


class TestBallTracker(unittest.TestCase):

    def setUp(self):
        """
        Prepara l'ambiente per ogni test.
        """
        mock_model = MockYOLOModel()
        # Ora il BallTracker è istanziato con un modello fittizio e un filtro nuovo per ogni test
        self.ball_tracker = BallTracker(model=mock_model)

    def test_kalman_filter_is_static_after_one_point(self):
        """
        TEST 1: Verifica che la previsione del filtro sia STATICA dopo un solo rilevamento.
        Questo è il comportamento atteso.
        """
        # Arrange: Palla rilevata, poi non rilevata.
        raw_detections = [[100, 100, 120, 120], None]  # Centro (110, 110)

        # Act
        filtered_tracks = self.ball_tracker._get_kalman_filtered_tracks(raw_detections)

        # Assert
        self.assertEqual(len(filtered_tracks), 2)

        # La posizione predetta per il frame 1 deve essere (quasi) uguale a quella del frame 0
        center_0 = self._get_center_from_tracks(filtered_tracks[0])
        center_1_predicted = self._get_center_from_tracks(filtered_tracks[1])

        self.assertIsNotNone(
            center_1_predicted,
            "Il filtro non ha predetto una posizione per il frame mancante.",
        )
        # Verifichiamo che la posizione predetta sia la stessa, perché la velocità è ancora zero.
        self.assertAlmostEqual(
            center_1_predicted[0],
            center_0[0],
            delta=1,
            msg="La previsione X dopo un punto non è statica.",
        )
        self.assertAlmostEqual(
            center_1_predicted[1],
            center_0[1],
            delta=1,
            msg="La previsione Y dopo un punto non è statica.",
        )

    def test_kalman_filter_is_dynamic_after_two_points(self):
        """
        TEST 2: Verifica che la previsione del filtro sia DINAMICA dopo due rilevamenti.
        Ora il filtro conosce una velocità e deve prevedere il movimento.
        """
        # Arrange: Due rilevamenti, poi un frame mancante.
        raw_detections = [
            [100, 100, 120, 120],  # Centro (110, 110)
            [110, 110, 130, 130],  # Centro (120, 120) -> Movimento di (10, 10)
            None,  # Qui ci aspettiamo una previsione a (130, 130)
        ]

        # Act
        filtered_tracks = self.ball_tracker._get_kalman_filtered_tracks(raw_detections)

        # Assert
        self.assertEqual(len(filtered_tracks), 3)

        center_1_corrected = self._get_center_from_tracks(filtered_tracks[1])
        center_2_predicted = self._get_center_from_tracks(filtered_tracks[2])

        self.assertIsNotNone(
            center_2_predicted,
            "Il filtro non ha predetto una posizione per il terzo frame.",
        )

        # La previsione per il frame 2 deve essere maggiore della posizione del frame 1.
        # Ci aspettiamo che il filtro abbia estrapolato il movimento.
        self.assertGreater(
            center_2_predicted[0],
            center_1_corrected[0],
            "La previsione X non è dinamica.",
        )
        self.assertGreater(
            center_2_predicted[1],
            center_1_corrected[1],
            "La previsione Y non è dinamica.",
        )

        # Verifichiamo che la previsione sia ragionevole (circa 130, 130)
        self.assertAlmostEqual(center_2_predicted[0], 130, delta=5)
        self.assertAlmostEqual(center_2_predicted[1], 130, delta=5)

    def _get_center_from_tracks(self, frame_track):
        """Metodo helper per estrarre il centro da una traccia."""
        if 1 in frame_track and frame_track[1].get("bbox"):
            bbox = frame_track[1]["bbox"]
            return (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
        return None


if __name__ == "__main__":
    unittest.main()
