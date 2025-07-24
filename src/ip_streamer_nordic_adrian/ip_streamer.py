import cv2
from flask import Flask, Response
import time
import sys
from typing import Union
import click




@click.group()
def cli():
    pass




def fps_capper(f, fps: int):
    """
    Decorator to cap the frames per second of a function.
    """
    def uncapped(*args, **kwargs):
        return f(*args, **kwargs)

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        elapsed = time.time() - start_time
        if elapsed < 1.0 / fps:
            time.sleep(1.0 / fps - elapsed)
        return result
    
    if fps <= 0:
        return uncapped
    return wrapper


class IPStreamer:

    def __init__(self, stream : Union[str, int] = 0, fps: int = 60):
        """
        Initializes the IPStreamer with a video source and frames per second.

        Parameters:
            stream (Union[str, int]): The video source, can be a path to a video or an integer for webcam.
            fps (int): Frames per second for the video stream.
        """
        self.stream = stream  
        self.fps = fps
        self._cap = cv2.VideoCapture(self.stream)
        if not self._cap.isOpened():
            raise ValueError(f"Could not open video source: {self.stream}")
        
        print(f"Video source opened: {self.stream}")
        print(f"Frames per second set to: {self.fps if self.fps > 0 else 'uncapped'}")

        if not isinstance(self.stream, str) and self.fps > 0:
            self._cap.set(cv2.CAP_PROP_FPS, self.fps)  # Set FPS for webcam streams
            
            
        self._app = Flask(__name__)
        self._app.add_url_rule('/', 'index', self._index)

    def run(self):
        self._app.run(host='0.0.0.0', port=5000, debug=False)


    def _index(self):
        return Response(self._generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    



    def _generate_one_frame(self):
        """
        Generates a single frame from the video source.
        """
        success, frame = self._cap.read()
        if not success:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the beginning if read fails
            success, frame = self._cap.read()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        return (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    def _generate_frames(self):
        while True:
            yield fps_capper(self._generate_one_frame, self.fps)()
 







#http://127.0.0.1:5000