import cv2 as cv
from deepface import DeepFace

import threading as thread

from openai import OpenAI

from pathlib import Path
from playsound import playsound
import time

#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

client = OpenAI(api_key="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")



"""
def cute_animal():
    DATA_DIR = Path.cwd() / "responses"

    DATA_DIR.mkdir(exist_ok=True)

    prompt ="small cute animal"

    response = client.images.generate(
    model="dall-e-2",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    response_format="b64_json",
    )

    

    file_name = DATA_DIR / f"{prompt[:5]}-{response['created']}.json"

    with open(file_name, mode="w", encoding="utf-8") as file:
        json.dump(response, file)

    cv.imshow("cute animal", image)
"""

class video:

    def __init__(self):
        self.play = False
        self.run = True
        self.start()
    
    def start(self):
        t1 = thread.Thread(target = self.cam)
        t2 = thread.Thread(target = self.positivity)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def positivity(self):
        while self.run:
            
            if self.play:
                response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You give random positive complements that are EXTREMELY FLOWERY"},
                    {"role": "user", "content": "Say something to cheer me up"},

                ]
                )

                print(response.choices[0].message.content)

                speech_file_path = Path(__file__).parent / "speech.mp3"
                response = client.audio.speech.create(
                model="tts-1",
                voice="shimmer",
                input= response.choices[0].message.content
                )

                response.stream_to_file(speech_file_path)

                playsound(speech_file_path)
                time.sleep(50)
                print("ready")
                self.play = False


    def cam(self):
        current = None
        display = "Neutral"
        cam = cv.VideoCapture(0)
        em_count = 0
        current = None

        while True:
            
            ret, frame = cam.read()

            if not ret:
                print("no cam")
                break

            frame = cv.flip(frame, 1)

            try:
                emotion = DeepFace.analyze(frame, actions=["emotion"])
                
                """
                sample of emotion

                [
                    {'emotion': {'angry': 5.2184805274009705, 'disgust': 0.07660617702640593, 
                        'fear': 3.776206821203232, 'happy': 0.00255140785156982, 'sad': 41.4758563041687, 'surprise': 0.0030215645892894827, 
                        'neutral': 49.447277188301086}, 'dominant_emotion': 'neutral', 
                    'region': {'x': 193, 'y': 173, 'w': 169, 'h': 169, 'left_eye': (55, 66), 
                        'right_eye': (111, 59)}, 'face_confidence': 0.95}
                ]
                """

                #prints out dominant emotion
                #print(emotion[0]["dominant_emotion"])
                em = emotion[0]["dominant_emotion"]
                
                print(em)
                
                
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

                if em_count >= 60:
                    if current != em:
                        current = em
                        if current != "happy":
                            
                            self.play = True
                            
                    
                    
                    
                    em_count = 0

                


            except:
                print("No face")
                emotion = None

            
            cv.imshow("feed", frame)

            if cv.waitKey(1) == ord("q"):
                break

        cam.release()



def main():
    vid = video()



# run the application 
if __name__ == "__main__": 
    main()