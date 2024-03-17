
from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
from aiortc import RTCPeerConnection, RTCSessionDescription
import cv2 as cv


from deepface import DeepFace
import uuid
import asyncio
import time

from openai import OpenAI
from pathlib import Path
from playsound import playsound

#openAI key also after this event judging i am deleting the key
client = OpenAI(api_key="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")

 

# creates a Flask application 
app = Flask(__name__, static_url_path='/static') 

#for tracking of RTCPeerConnection instances
pcs = set()

async def playsound_async(speech_file_path):
    playsound(speech_file_path)

def positivity():

    print("making request")

    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You give random positive complements "},
        {"role": "user", "content": "Say something short to cheer me up"},

    ]
    )

    print(response.choices[0].message.content)

    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create( model="tts-1", voice="shimmer", input= response.choices[0].message.content)

    response.stream_to_file(speech_file_path)

    playsound(speech_file_path)

    
    return response.choices[0].message.content





@app.route('/get_text', methods=['POST'])
def ChatGPT():
    
    positivity()
    
    return 'Success', 200


#Host index with a cute animal
@app.route("/") 
def home():
    response = client.images.generate(
    model="dall-e-3",
    prompt="a very adorable cute little animal",
    size="1024x1024",
    quality="standard",
    n=1,
    )
    url =  response.data[0].url 
    return render_template('index.html', URL = url) 


# generates the stream frame by frame
def generate_frames():
    em_count = 0
    current = None
    display = "Neutral"
    camera = cv.VideoCapture(0)
    last_pull = time.time()

    while True:

        ret, frame = camera.read()

        frame = cv.flip(frame, 1)

        if not ret:
            break
        else:

            try:
                emotion = DeepFace.analyze(frame, actions=["emotion"])

                #prints out dominant emotion
                em = emotion[0]["dominant_emotion"]
                print(em)
                
                #add the confident score to the display variable
                match em:
                    case "happy":
                        display = em + " " + str(emotion[0]["emotion"][em])
                    case "sad":
                        display = em + " " + str(emotion[0]["emotion"][em])
                    case "angry":
                        display = em + " " + str(emotion[0]["emotion"][em])
                    case "neutral":
                        display = em + " " + str(emotion[0]["emotion"][em])
                    case "digust":
                        display = em + " " + str(emotion[0]["emotion"][em])
                    case "fear":
                        display = em + " " + str(emotion[0]["emotion"][em])
                    case "surprise":
                        display = em + " " + str(emotion[0]["emotion"][em])
                    
                
                
                org = (50, 50) 
                fontScale = 1
                color = (255, 0, 0) 
                thickness = 2

                
                frame = cv.putText(frame, str(display), org, cv.FONT_HERSHEY_SIMPLEX , fontScale, color, thickness, cv.LINE_AA)  

                print(em, current)

                em_count += 1

                print(em_count)
                if em_count > 20:
                    if current != em or current != "happy":
                        current = em
                        elapsed_time = time.time() - last_pull 
                        print(elapsed_time)
                        em_count = 0

                        #if ensure that a pull can only happen at most every 30 seconds
                        if elapsed_time > 20:
                            positivity()
                            last_pull = time.time()
                            elapsed_time = 0
                            print("reset")

                            
                            

            except:
                emotion = None




            ret, buffer = cv.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # Concatenate frame and yield for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
            



#Route the video to the html file
@app.route('/')
def index():
    return redirect(url_for('video_feed'))


async def offer_async():
    params = await request.json
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    # Create an RTCPeerConnection instance
    pc = RTCPeerConnection()

    # Generate a unique ID for the RTCPeerConnection
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pc_id = pc_id[:8]

    # Create and set the local description
    await pc.createOffer(offer)
    await pc.setLocalDescription(offer)

    # Prepare the response data with local SDP and type
    response_data = {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

    return jsonify(response_data)



# Wrapper function for running the asynchronous offer function
def offer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    future = asyncio.run_coroutine_threadsafe(offer_async(), loop)
    return future.result()


# Route to handle the offer request
@app.route('/offer', methods=['POST'])
def offer_route():
    return offer()



# Route to stream video frames
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# run the application 
if __name__ == "__main__": 
    app.run(debug = True) 