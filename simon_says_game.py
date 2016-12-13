import os
import time

import matplotlib.pyplot as plt

import cv2
import numpy

from processRequest import processRequest

from processResults import processResults

from matplotlib2opencv import annotate_mpl2cv, anything2cv

from Webcam2HTTP import snapshot_generator


class SimonSaysEmotionsGame(object):
    
    def __init__(self, n_rounds, key):
        
        self.emotions = ['sadness','neutral','contempt','disgust','anger','surprise','fear','happiness']
        
        self.team1_data = []
        self.team2_data = []
        
        self.team1_score = []
        self.team2_score = []
        
        self.key = key
        self.headers = dict()
        self.headers['Ocp-Apim-Subscription-Key'] = self.key
        self.headers['Content-Type'] = 'application/octet-stream'
        
        self.img_changed = True # saves cpu
        
        self.img_changed_1 = False # controls when to redo the avatars
        self.img_changed_2 = False # controls when to redo the avatars
        
        self.snp = None # webcam OpenCV interface
        
        self.game_state = 'init'
        
        self.splash = cv2.imread("splash_window.png") # loads the splash window
        self.instr = cv2.imread("instr_window.png") # loads the "instructions" window
        self.instr
        
        # families = ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']
        self.text_font = {'family': 'fantasy',
                          'color':  'red',
                          'weight': 'bold',
                          'size': 30,
                          }
        
        # Splash window with msg to continue
        self.splash_c = annotate_mpl2cv(self.splash.copy(),"Press \'C\' to continue...",280,450,self.text_font)
        
        # Splash window with instructions
        self.instr_text = "Instructions:\n"
        self.instr_text += "- Two teams.\n"
        self.instr_text += "- Total of "+str(n_rounds)+" rounds.\n"
        self.instr_text += "- Random emotions.\n"
        self.instr_text += "PRESS \'Q\' TO QUIT ANYTIME!"
        self.instr_1 = annotate_mpl2cv(self.instr.copy(),self.instr_text,70,600,self.text_font)
        
        # Splash window without anything 
        # (just because my module matplotlib2opencv still far from perfect...)
        self.splash =  annotate_mpl2cv(self.splash.copy(),"",0,0,self.text_font) # to match...
            
    def start_window(self, width = 1024, height = 768):
        self.shape = (height,width)
        self.window_name = "GameWindow"
        cv2.startWindowThread()
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL) # cv2.WINDOW_AUTOSIZE

        # adjusts the splash windows to the game resolution
        self.splash = cv2.resize(self.splash, (self.shape[1],self.shape[0]))
        self.splash_c = cv2.resize(self.splash_c, (self.shape[1],self.shape[0]))
        self.instr_1 = cv2.resize(self.instr_1, (self.shape[1],self.shape[0]))

        
    def start_webcam(self, device_number, debug=False, filename=None):
        
        #         if debug:
        #             camera_res = cv2.imread(filename).shape
        #         else:
        #             # verifies camera resolution and closes the camera
        #             capture = cv2.VideoCapture(device_number)
        #             camera_res = capture.read()[1].shape
        #             capture.release()

        #         print "camera_res:",camera_res
        
        #         # adjusts the splash windows to the camera resolution
        #         self.splash = cv2.resize(self.splash, (camera_res[1],camera_res[0]))
        #         self.splash_c = cv2.resize(self.splash_c, (camera_res[1],camera_res[0]))
        #         self.instr_1 = cv2.resize(self.instr_1, (camera_res[1],camera_res[0]))
        
        self.snp = snapshot_generator(device=device_number,debug=debug,filename=filename)
        if self.snp==-1:
            print "Snapshot error!"
            self.exit()
        return 0
        
    def run(self):
        '''
        Here the key pressed is collected and the game state changed.
        '''
        # initialised the blink variable because the first state
        # has a blinking message.
        self.blink = time.time()
        try:
            while True:
                key = cv2.waitKey(1) & 0xFF # the argument for waitKey is ms
                # if the keys 'q' or 'Q' are pressed, stop the loop
                if key == ord('q') or key == ord('Q'):
                    break
                    
                # Calls a method according to game_state.
                # Looks crazy, but it's pure python coolness :D
                # http://stackoverflow.com/a/3071
                methodtocall=getattr(self, 'state_'+self.game_state)
                methodtocall(key)
                # A simpler solution is to pass the method directly...
                    
        except KeyboardInterrupt:
            self.exit()
            
        finally:
            self.exit()
            
    def state_init(self,key):
        '''
        Shows the splash window with blinking message
        '''
        # If C (continue) is pressed, jumps to instructions
        if key == ord("c") or key == ord("C"):
            self.game_state = 'instr'
        else:
            # Generates a blinking effect 
            # (can break if the computer is too slow)
            if (time.time()-self.blink)<=1:
                self.curr_image = self.splash_c
                self.img_changed = True
            elif 2>(time.time()-self.blink)>1:
                self.curr_image = self.splash
                self.img_changed = True
            elif 3>(time.time()-self.blink)>2:
                self.blink = time.time()

            # Only changes de message when the timer goes off
            if self.img_changed:
                cv2.imshow(self.window_name,self.curr_image)
                self.img_changed = False
            
    def state_instr(self,key):
        '''
        Shows the instructions
        '''
        if key == ord("c") or key == ord("C"):
            self.game_state = 'snps1'
        else:
            if not self.img_changed:
                self.curr_image = self.instr_1
                cv2.imshow(self.window_name,self.curr_image)
                self.img_changed = True
        
        
    def state_snps1(self,key):
        '''
        Takes the snapshot from team 1
        '''
        if key == ord("c") or key == ord("C"):
            self.game_state = 'snps2'
            self.team1 = cv2.resize(self.team1.copy(),
                                    (self.shape[1]/2,self.shape[0]/2))
            
            cv2.putText(self.team1, "TEAM 1 - trials: "+str(len(self.team1_data))
                        +" - score:"+"{:2.2f}".format(sum(self.team1_score)), (20,40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 4)
        else:
            img, self.curr_image = self.snp(ret_orig=True)
            
            self.team1 = self.curr_image.copy()
            
            self.curr_image = cv2.resize(self.curr_image, (self.shape[1],self.shape[0]))
            
            cv2.putText(self.curr_image, "Team 1: verify your image!", (10,100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 4)
            cv2.putText(self.curr_image, "Press \'C\' to continue...", (10,150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 4)

            cv2.imshow(self.window_name,self.curr_image)

    def state_snps2(self,key):
        '''
        Takes the snapshot from team 2
        '''
        if key == ord("c") or key == ord("C"):
            self.game_state = 'main'
            self.team2 = cv2.resize(self.team2.copy(),
                                    (self.shape[1]/2,self.shape[0]/2))
            
            cv2.putText(self.team2, "TEAM 2 - trials: "+str(len(self.team2_data))
                        +" - score:"+"{:2.2f}".format(sum(self.team2_score)), (20,40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 4)
        else:
            img, self.curr_image = self.snp(ret_orig=True)
            
            self.team2 = self.curr_image.copy()
            
            self.curr_image = cv2.resize(self.curr_image, (self.shape[1],self.shape[0]))
            
            cv2.putText(self.curr_image, "Team 2: verify your image!", (10,100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 4)
            cv2.putText(self.curr_image, "Press \'C\' to continue...", (10,150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 4)

            cv2.imshow(self.window_name,self.curr_image)
        
    def state_main(self,key):
        '''
        MAIN SCREEN
        Shows the avatars / stats / and controls the game
        '''
        if key == ord("1"):
            self.rnd_emotion = self.emotions[numpy.random.randint(0,len(self.emotions))]
            self.game_state = 'cap1'
            self.blink = time.time()
        elif key == ord("2"):
            self.rnd_emotion = self.emotions[numpy.random.randint(0,len(self.emotions))]
            self.game_state = 'cap2'
            self.blink = time.time()
        else:
            if self.img_changed:
                self.curr_image = numpy.zeros((self.splash.shape[0],
                                               self.splash.shape[1],
                                               self.splash.shape[2]),
                                              dtype=numpy.uint8)
                
                if self.img_changed_1:
                    s=processResults(self.team1_data[-1][0], 
                                     self.team1_data[-1][1], 
                                     self.team1_data[-1][2],
                                     self.team1, (0,0,255))
                    self.team1_score.append(s)

                    self.team1 = cv2.resize(self.team1,
                                            (self.shape[1]/2,self.shape[0]/2))

                    cv2.putText(self.team1, "TEAM 1 - trials: "+str(len(self.team1_data))
                                +" - score:"+"{:2.2f}".format(sum(self.team1_score)), (20,40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 4)

                    self.img_changed_1 = False

                if self.img_changed_2:
                    s=processResults(self.team2_data[-1][0], 
                                     self.team2_data[-1][1], 
                                     self.team2_data[-1][2], 
                                     self.team2, (0,255,0))
                    self.team2_score.append(s)

                    self.team2 = cv2.resize(self.team2,
                                            (self.shape[1]/2,self.shape[0]/2))

                    cv2.putText(self.team2, "TEAM 2 - trials: "+str(len(self.team2_data))
                                +" - score:"+"{:2.2f}".format(sum(self.team2_score)), (20,40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 4)
                    
                    self.img_changed_2 = False
                                
                self.curr_image[0:self.team1.shape[0],0:self.team1.shape[1]]=self.team1[:]
                self.curr_image[0:self.team2.shape[0],self.team1.shape[1]:2*self.team2.shape[1]]=self.team2[:]

                # call statistics
                stats_img = self.stats((self.curr_image.shape[0]-self.team1.shape[0],self.curr_image.shape[1]))
                
                if len(stats_img):
                    self.curr_image[self.curr_image.shape[0]-stats_img.shape[0]:,:]=stats_img[:]
                    
                cv2.imshow(self.window_name,self.curr_image)
                self.img_changed = False
                
    def stats(self, shape):
        mplfunc_list = []
        args_list = []
        
        if self.team1_score:
            mplfunc_list.append(plt.plot)
            args_list.append((self.team1_score,'ro-'))

        if self.team2_score:
            mplfunc_list.append(plt.plot)
            args_list.append((self.team2_score,'gs-'))

        if mplfunc_list:
            mplfunc_list.append(plt.xlim)
            args_list.append((-0.1,max([len(self.team1_data),len(self.team2_data)])+1))
            return anything2cv(shape,mplfunc_list,args_list)
        else:
            return []


    def state_cap1(self,key):
        '''
        CAPTURES / PROCESS IMAGE TEAM 1
        '''        
        # Captures the image and returns the encoded and the opencv versions
        img, self.curr_image = self.snp(ret_orig=True) 
        
        self.local_shape = self.curr_image.shape
        
        self.curr_image = cv2.resize(self.curr_image,(self.shape[1],self.shape[0]))
        
        self.team1 = self.curr_image.copy()
        
        msg_pos = (self.shape[1]/2-30,self.shape[0]/2)
        
        if (time.time()-self.blink)<=2:
            cv2.putText(self.curr_image, "Ready...", (msg_pos[0]-30,msg_pos[1]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 4)
            cv2.putText(self.curr_image, "Emotion: "+self.rnd_emotion, (msg_pos[0]-200,msg_pos[1]+50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 6)
            cv2.imshow(self.window_name,self.curr_image)
            
        elif 2.25>=(time.time()-self.blink)>2:
            cv2.putText(self.curr_image, "Go!", (msg_pos[0]-30,msg_pos[1]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 4)
            cv2.imshow(self.window_name,self.curr_image)
            
            self.img_changed = True
            
        elif (time.time()-self.blink)>2.25:
            if self.img_changed:
                cv2.putText(self.curr_image, "Enjoy yourself while you wait...", 
                            (msg_pos[0]-350,msg_pos[1]), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 4)
                cv2.imshow(self.window_name,self.curr_image)
                
                self.img = img
                
                self.img_changed = False # starts the process only once

            else:
                result = processRequest(None, self.img, self.headers, None, self.key)
                if len(result):
                    self.team1_data.append([result,self.rnd_emotion,self.local_shape])
                    self.img_changed_1 = True
                    self.img_changed = True
                    self.game_state = 'main' # goes back to MAIN SCREEN
                else:
                    print "No results!"
                    self.blink = time.time()

    def state_cap2(self,key):
        '''
        CAPTURES / PROCESS IMAGE TEAM 2
        '''
        # Captures the image and returns the encoded and the opencv versions
        img, self.curr_image = self.snp(ret_orig=True)
       
        self.local_shape = self.curr_image.shape
        
        self.curr_image = cv2.resize(self.curr_image,(self.shape[1],self.shape[0]))
                
        self.team2 = self.curr_image.copy()
        
        msg_pos = (self.shape[1]/2-30,self.shape[0]/2)
        
        if (time.time()-self.blink)<=2:
            cv2.putText(self.curr_image, "Ready...", (msg_pos[0]-30,msg_pos[1]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 4)
            cv2.putText(self.curr_image, "Emotion: "+self.rnd_emotion, (msg_pos[0]-200,msg_pos[1]+50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 6)
            cv2.imshow(self.window_name,self.curr_image)
            
        elif 2.25>=(time.time()-self.blink)>2:
            cv2.putText(self.curr_image, "Go!", (msg_pos[0]-30,msg_pos[1]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 4)
            cv2.imshow(self.window_name,self.curr_image)
            
            self.img_changed = True
            
        elif (time.time()-self.blink)>2.25:
            if self.img_changed:
                cv2.putText(self.curr_image, "Enjoy yourself while you wait...", 
                            (msg_pos[0]-350,msg_pos[1]), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 4)
                cv2.imshow(self.window_name,self.curr_image)
                
                self.img = img
                
                self.img_changed = False # starts the process only once
                
            else:
                result = processRequest(None, self.img, self.headers, None, self.key)
                if len(result):
                    self.team2_data.append([result,self.rnd_emotion,self.local_shape])
                    self.img_changed_2 = True
                    self.img_changed = True
                    self.game_state = 'main' # goes back to MAIN SCREEN
                else:
                    print "No results!"
                    self.blink = time.time()

    def exit(self):
        cv2.destroyAllWindows()
        if self.snp:
            self.snp(False)
        return -1
    
if __name__=="__main__":
    your_ms_emotion_api_key = '5ceba3e8d9724c729dbd425823ed8020'
    game = SimonSaysEmotionsGame(10, key = your_ms_emotion_api_key)
    if not game.start_webcam(0):#, debug=True, filename = os.getcwd()+'/group6.jpg'):
        game.start_window()
        game.run()