import  cv2 as cv2
import pytesseract as text
from os import name

if name == 'nt':
    text.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract"

def frameFromVideo(frame_relative_pos:int, cam:cv2.VideoCapture):
    currentFrameNo = 0
    ret = True
    while(currentFrameNo < frame_relative_pos and ret):
        ret, frame = cam.read()
        currentFrameNo+=1
    
    if not ret:
        cam.release()
        cv2.destroyAllWindows()
        return False, None, None
    
    ret, frame = cam.read()
    return ret, frame, cam

def textFromVideo(file_path:str, mandatoryPhrases:list, runFromFrame:int, uptoFrame:int):
    cam = cv2.VideoCapture(file_path)
    ret = True
    mandatory = True
    texts = []
    while(uptoFrame > runFromFrame and ret):
        ret, frame, cam = frameFromVideo(runFromFrame, cam)
        try:
            s = text.image_to_string(frame)
        except:
            s = ""
        if all(phrase.lower() in s.lower() for phrase in mandatoryPhrases):
            texts.append(str(text.image_to_string(frame)))
            mandatory = True
        else:
            mandatory = False
        runFromFrame += 1
    if ret:
        cam.release()
        cv2.destroyAllWindows()
    return ret and mandatory, list(set(texts))

def videoLength (file_path):
    data = cv2.VideoCapture(file_path) 

    frames = data.get(cv2.CAP_PROP_FRAME_COUNT) 
    fps = int(data.get(cv2.CAP_PROP_FPS)) 

    seconds = int(frames / fps) 
    return seconds
