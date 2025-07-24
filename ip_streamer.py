import cv2
from flask import Flask, Response
import time
import sys

STREAM = 0 # Path to the video file or an int for webcam index
app = Flask(__name__)

def generate_frames(cap: cv2.VideoCapture):
    frame_interval = 1.0 / 60  # 60 FPS
    while True:
        start_time = time.time()
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the first frame if reading fails
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        elapsed = time.time() - start_time
        sleep_time = frame_interval - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
    cap.release()    


@app.route('/')
def index():
    return Response(generate_frames(cv2.VideoCapture(STREAM)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == '__main__':
    if len(sys.argv) > 1:
        STREAM = sys.argv[1]  # Allow passing the video source as a command line argument
    app.run(host='0.0.0.0', port=5000, debug=False)



#http://127.0.0.1:5000