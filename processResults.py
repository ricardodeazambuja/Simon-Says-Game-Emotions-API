#
# https://github.com/Microsoft/Cognitive-emotion-python
#

import operator
import cv2

def processResults(result, emotion, orig_shape, img, color = (255,0,0)):
    
    """
    Display the obtained results onto the input image
    
    Generates the score
    """
    score = 0
    
    x = img.shape[1]
    y = img.shape[0]
    
    xo = orig_shape[1]
    yo = orig_shape[0]

    for currFace in result:
        faceRectangle = currFace['faceRectangle']
        max_currEmotion = max(currFace['scores'].items(), key=operator.itemgetter(1))[0]
        rnd_emotion = currFace['scores'][emotion]
        score += rnd_emotion

        # Emotion with highest value
        textToWrite = "%s" % ( max_currEmotion )
        cv2.putText( img, textToWrite, 
                    (x*faceRectangle['left']/xo,
                     y*(faceRectangle['top']-10)/yo), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 3)
        
        # Random emotion
        textToWrite = emotion+":"+"{:1.3f}".format(rnd_emotion)
        cv2.putText( img, textToWrite, 
                    (x*faceRectangle['left']/xo,
                     y*(faceRectangle['top'] + faceRectangle['height']+20)/yo), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 3)
        
        faceRectangle = currFace['faceRectangle']
        cv2.rectangle( img,(x*faceRectangle['left']/xo,y*faceRectangle['top']/yo),
                           (x*(faceRectangle['left']+faceRectangle['width'])/xo, 
                            y*(faceRectangle['top'] + faceRectangle['height'])/yo),
                       color = color, thickness = 2 )
        
        if max_currEmotion!=emotion:
            cv2.line( img, (x*faceRectangle['left']/xo,y*faceRectangle['top']/yo),
                           (x*(faceRectangle['left']+faceRectangle['width'])/xo, 
                            y*(faceRectangle['top'] + faceRectangle['height'])/yo), 
                       color = color, thickness = 2)

            cv2.line( img, (x*faceRectangle['left']/xo,
                            y*(faceRectangle['top'] + faceRectangle['height'])/yo),
                           (x*(faceRectangle['left']+faceRectangle['width'])/xo, 
                            y*faceRectangle['top']/yo), 
                       color = color, thickness = 2)
        

        
    return score