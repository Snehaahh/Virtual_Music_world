import cv2
import numpy as np
import mediapipe as mp
import time
from pygame import mixer


class HandDrums:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Initialize Pygame mixer and load sounds
        mixer.init()
        self.drum_clap = mixer.Sound('batterrm.wav')
        self.drum_snare = mixer.Sound('button-2.ogg')

        # Load and resize drum images
        self.snare_img = cv2.imread('Images/Snare.png', cv2.IMREAD_UNCHANGED)
        self.hihat_img = cv2.imread('Images/Hatt.png', cv2.IMREAD_UNCHANGED)

        # Define drum zones with image dimensions
        self.drum_zones = {
            'snare': {
                'center': None,
                'radius': 60,
                'color': (0, 0, 255),
                'image': self.snare_img,
                'size': (200, 100)  # width, height
            },
            'hihat': {
                'center': None,
                'radius': 60,
                'color': (255, 0, 0),
                'image': self.hihat_img,
                'size': (200, 100)  # width, height
            }
        }

        # Resize images
        for drum in self.drum_zones.values():
            if drum['image'] is not None:
                drum['image'] = cv2.resize(drum['image'], drum['size'])

        # Cooldown timer to prevent rapid-fire drum hits
        self.last_trigger_time = {
            'snare': 0,
            'hihat': 0
        }
        self.cooldown = 0.3  # seconds

    def setup_drum_zones(self, frame_width, frame_height):
        # Set up drum zone positions based on frame size
        # Snare at bottom right
        self.drum_zones['snare']['center'] = (
            int(frame_width * 0.75),  # Move to right side
            int(frame_height * 0.8)  # Move lower down
        )
        # Hi-hat stays at original position
        self.drum_zones['hihat']['center'] = (
            int(frame_width * 0.25),
            int(frame_height * 0.6)
        )

    def detect_hand_gesture(self, hand_landmarks):
        # Get index fingertip position (landmark 8)
        index_tip = hand_landmarks.landmark[8]

        # Get middle fingertip position (landmark 12)
        middle_tip = hand_landmarks.landmark[12]

        # Check if fingers are pointing down (drumming gesture)
        is_drumming = (index_tip.y > hand_landmarks.landmark[5].y and
                       middle_tip.y > hand_landmarks.landmark[9].y)

        return is_drumming

    def check_drum_hit(self, hand_landmarks, frame_width, frame_height):
        # Convert normalized coordinates to pixel coordinates
        index_tip = hand_landmarks.landmark[8]
        x = int(index_tip.x * frame_width)
        y = int(index_tip.y * frame_height)

        current_time = time.time()

        # Check each drum zone
        for drum_name, drum_data in self.drum_zones.items():
            # Calculate if point is within drum image rectangle
            half_width = drum_data['size'][0] // 2
            half_height = drum_data['size'][1] // 2
            center_x, center_y = drum_data['center']

            if (abs(x - center_x) < half_width and
                    abs(y - center_y) < half_height and
                    current_time - self.last_trigger_time[drum_name] > self.cooldown):

                # Play appropriate drum sound
                if drum_name == 'snare':
                    self.drum_clap.play()
                else:
                    self.drum_snare.play()

                self.last_trigger_time[drum_name] = current_time

    def overlay_image(self, frame, img, center, size):
        """Overlay image on frame at specified center position"""
        if img is None:
            return

        # Calculate corners for placement
        half_width = size[0] // 2
        half_height = size[1] // 2
        x1 = max(center[0] - half_width, 0)
        x2 = min(center[0] + half_width, frame.shape[1])
        y1 = max(center[1] - half_height, 0)
        y2 = min(center[1] + half_height, frame.shape[0])

        # Handle edge cases where image might go out of frame
        img_x1 = half_width - (center[0] - x1)
        img_x2 = img_x1 + (x2 - x1)
        img_y1 = half_height - (center[1] - y1)
        img_y2 = img_y1 + (y2 - y1)

        # Create mask for transparent overlay
        if img.shape[2] == 4:  # If image has alpha channel
            alpha = img[img_y1:img_y2, img_x1:img_x2, 3] / 255.0
            alpha = np.expand_dims(alpha, axis=-1)
            img_rgb = img[img_y1:img_y2, img_x1:img_x2, :3]

            # Blend images
            frame[y1:y2, x1:x2] = frame[y1:y2, x1:x2] * (1 - alpha) + img_rgb * alpha
        else:
            # Simple overlay if no alpha channel
            frame[y1:y2, x1:x2] = cv2.addWeighted(
                frame[y1:y2, x1:x2], 0.5,
                img[img_y1:img_y2, img_x1:img_x2], 0.5,
                0
            )

    def draw_drums(self, frame):
        # Overlay drum images
        for drum_data in self.drum_zones.values():
            self.overlay_image(
                frame,
                drum_data['image'],
                drum_data['center'],
                drum_data['size']
            )

    def process_frame(self, frame):
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process hand landmarks
        results = self.hands.process(rgb_frame)

        # Draw drums
        self.draw_drums(frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

                # Check for drumming gesture
                if self.detect_hand_gesture(hand_landmarks):
                    # Check if gesture is in drum zone
                    self.check_drum_hit(
                        hand_landmarks,
                        frame.shape[1],
                        frame.shape[0]
                    )

        return frame


def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)

    # Get frame dimensions
    ret, frame = cap.read()
    if not ret:
        print("Failed to get frame from camera")
        return

    # Initialize HandDrums
    hand_drums = HandDrums()
    hand_drums.setup_drum_zones(frame.shape[1], frame.shape[0])

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip frame horizontally for more intuitive interaction
        frame = cv2.flip(frame, 1)

        # Process frame
        frame = hand_drums.process_frame(frame)



        # Display frame
        cv2.imshow('Hand Drums', frame)

        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()