import numpy as np


class KalmanFilter:
    """
    Un semplice Filtro di Kalman per tracciare oggetti in 2D.
    """

    def __init__(self):
        # Definizioni del filtro (invariate)
        self.kf = np.array(
            [[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32
        )
        self.state = np.array([0, 0, 0, 0], np.float32)
        self.measurement_matrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.process_noise = np.eye(4, dtype=np.float32) * 1e-2
        self.measurement_noise = np.eye(2, dtype=np.float32) * 1e-1
        self.error_covariance = np.eye(4, dtype=np.float32)

    def predict(self):
        """
        Fase di previsione: stima la posizione attuale basandosi sullo stato precedente.
        """
        self.state = np.dot(self.kf, self.state)
        self.error_covariance = (
            np.dot(np.dot(self.kf, self.error_covariance), self.kf.T)
            + self.process_noise
        )
        return self.state[:2]

    def correct(self, measurement):
        """
        Fase di correzione: aggiorna la previsione con una misurazione reale.
        """
        # --- LA CORREZIONE ---
        # Assicuriamoci che la misurazione sia sempre un array NumPy
        measurement = np.array(measurement, dtype=np.float32)

        # Calcolo del guadagno di Kalman (K)
        innovation_covariance = (
            np.dot(
                np.dot(self.measurement_matrix, self.error_covariance),
                self.measurement_matrix.T,
            )
            + self.measurement_noise
        )
        kalman_gain = np.dot(
            np.dot(self.error_covariance, self.measurement_matrix.T),
            np.linalg.inv(innovation_covariance),
        )

        innovation = measurement - np.dot(self.measurement_matrix, self.state)
        self.state = self.state + np.dot(kalman_gain, innovation)

        self.error_covariance = self.error_covariance - np.dot(
            np.dot(kalman_gain, self.measurement_matrix), self.error_covariance
        )
        return self.state[:2]

    def initialize_state(self, measurement):
        """
        Inizializza lo stato del filtro con la prima misurazione valida.
        """
        # --- LA CORREZIONE ---
        # Assicuriamoci che la misurazione sia sempre un array NumPy
        measurement = np.array(measurement, dtype=np.float32)

        self.state[:2] = measurement.reshape(2)