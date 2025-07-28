class ShotClassifier:
    def __init__(self, court_dimensions):
        self.court_dimensions = court_dimensions

    def classify(self, shot_event, player_position):
        # For now, we'll just classify all shots as 2-point shots
        return {"shot_type": "2-pointer"}
