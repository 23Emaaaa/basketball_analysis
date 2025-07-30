class ShotClassifier:
    def __init__(self, court_dimensions):
        self.court_dimensions = court_dimensions
        # Placeholder for the 3-point line x-coordinate
        self.three_point_line_x = (
            250  # This should be calculated based on court_dimensions
        )

    def classify(self, shot_event, player_position):
        # player_position is a bbox [x1, y1, x2, y2]
        # We take the bottom center of the bbox as the player's position
        x = (player_position[0] + player_position[2]) / 2

        shot_type = "2-pointer"
        if x < self.three_point_line_x:
            shot_type = "3-pointer"

        return {"shot_type": shot_type}
