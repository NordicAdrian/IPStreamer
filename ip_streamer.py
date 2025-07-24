import cv2
from flask import Flask, Response
import time


STREAM = "C:\\Users\\adria\\dev\\nordic3DET\\data\\Eye_Rec_Asgeir.avi" # Path to the video file or an int for webcam index
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


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(cv2.VideoCapture(STREAM)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
    <html>
      <body>
        <h1>IP Camera Stream</h1>
        <img src="/video_feed">
      </body>
    </html>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)


#http://127.0.0.1:5000/video_feed