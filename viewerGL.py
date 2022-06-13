#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
import pyrr
import numpy as np
from cpe3d import Object3D
import random


var_saut = 0
current_time = 0
temps_touche = 0

class ViewerGL:
    def __init__(self):
        # initialisation de la librairie GLFW
        glfw.init()
        # paramétrage du context OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # création et paramétrage de la fenêtre
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(800, 800, 'OpenGL', None, None)
        # paramétrage de la fonction de gestion des évènements
        glfw.set_key_callback(self.window, self.key_callback)
        # activation du context OpenGL pour la fenêtre
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        # activation de la gestion de la profondeur
        GL.glEnable(GL.GL_DEPTH_TEST)
        # choix de la couleur de fond
        GL.glClearColor(0.5, 0.6, 0.9, 1.0)
        print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")

        self.unalive = 0
        self.lock = True
        self.objs = []
        self.touch = {}
        self.lakitu_init = 10
        self.carap_dx = []
        self.carap_dz = []
        self.carap_bleue = []
        
        self.i_frame_on = True
        self.hit = False
        self.pdv = 5
        self.temps = 30
        self.niveau2 = 1

    def run(self):
        # boucle d'affichage
        while not glfw.window_should_close(self.window):
            # nettoyage de la fenêtre : fond et profondeur
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self.finito_pipo()          #Selon la valeur de self.unalive, plusieurs fonction sont activées/désactivées
            self.niveau()
            
            if self.unalive != 3:
                self.affichage_vie()
                self.update_key()

                if self.unalive !=2:
                    self.gravity()
                    self.mvt_carapace()
                    if self.niveau2 >= 3:
                        self.mvt_carapace_bleue()

                    if self.unalive == 0:
                        self.collision_sol()
                        self.saut()
                        self.collision_kirb_carap()

                if self.unalive ==2:
                    self.reanimation()          
                    

            for obj in self.objs:
                GL.glUseProgram(obj.program)
                if isinstance(obj, Object3D):
                    self.update_camera(obj.program)
                obj.draw()

            # changement de buffer d'affichage pour éviter un effet de scintillement
            glfw.swap_buffers(self.window)
            # gestion des évènements
            glfw.poll_events()
        
    def key_callback(self, win, key, scancode, action, mods):
        # sortie du programme si appui sur la touche 'échappement'
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, glfw.TRUE)
        self.touch[key] = action
    
    def add_object(self, obj):
        self.objs.append(obj)

    def set_camera(self, cam):
        self.cam = cam

    def update_camera(self, prog):
        GL.glUseProgram(prog)
        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "translation_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : translation_view")
        # Modifie la variable pour le programme courant
        translation = -self.cam.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "rotation_center_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_view")
        # Modifie la variable pour le programme courant
        rotation_center = self.cam.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(-self.cam.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(prog, "rotation_view")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_view")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)
    
        loc = GL.glGetUniformLocation(prog, "projection")
        if (loc == -1) :
            print("Pas de variable uniforme : projection")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.cam.projection)

    def update_key(self):
        if self.unalive !=2: 
            if glfw.KEY_UP in self.touch and self.touch[glfw.KEY_UP] > 0:
                self.objs[0].transformation.translation += \
                    pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, 0.3]))
            if glfw.KEY_DOWN in self.touch and self.touch[glfw.KEY_DOWN] > 0:
                self.objs[0].transformation.translation -= \
                    pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, 0.3]))
            if glfw.KEY_LEFT in self.touch and self.touch[glfw.KEY_LEFT] > 0:
                self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] -= 0.05
            if glfw.KEY_RIGHT in self.touch and self.touch[glfw.KEY_RIGHT] > 0:
                self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] += 0.05

            if glfw.KEY_I in self.touch and self.touch[glfw.KEY_I] > 0:
                self.cam.transformation.rotation_euler[pyrr.euler.index().roll] -= 0.1
            if glfw.KEY_K in self.touch and self.touch[glfw.KEY_K] > 0:
                self.cam.transformation.rotation_euler[pyrr.euler.index().roll] += 0.1
            if glfw.KEY_J in self.touch and self.touch[glfw.KEY_J] > 0:
                self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] -= 0.1
            if glfw.KEY_L in self.touch and self.touch[glfw.KEY_L] > 0:
                self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += 0.1

            if glfw.KEY_SPACE in self.touch and self.touch[glfw.KEY_SPACE] > 0 : #Crée une impulsion
                global var_saut
                if var_saut == 0:
                    var_saut = 500

        if glfw.KEY_Y in self.touch : #La première fois qu'un appuie sur Y est aussi la dernière car celle ci bloque la camera
            self.cam.transformation.rotation_euler = self.objs[0].transformation.rotation_euler.copy() 
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.rotation_euler[pyrr.euler.index().roll] = 0.35
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 4, 15])

    def saut(self):
        global current_time, var_saut
        last_time = current_time
        current_time = glfw.get_time()

        if var_saut !=0: # tant que la variable var_saut est différente de 0, un saut est en cours d'éxécution
            dt = current_time - last_time       #3 lignes pour une approximation des forces de Newton
            acceleration = var_saut - 300
            vitesse = 5 + acceleration * dt
            pos = vitesse * dt
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, pos, 0]))
            var_saut -= 10
            if var_saut == 0 :
                var_saut = -1

    def gravity(self): # pas le film
        posx = self.objs[0].transformation.translation.x
        posy = self.objs[0].transformation.translation.y
        posz = self.objs[0].transformation.translation.z

        if (posx >= 75 or posx <= -75 or posz >= 75 or posz <= -75 or self.unalive == 1) and (self.unalive != 2):
            self.unalive = 1
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, -0.1, 0]))
        if posy <= -7:
            self.unalive =2

    def reanimation(self):
        posx = self.objs[0].transformation.translation.x #Coordonnées de Kirby
        posy = self.objs[0].transformation.translation.y
        posz = self.objs[0].transformation.translation.z

        posxlakitu = self.objs[self.lakitu_init].transformation.translation.x #Coordonnées de Lakitu
        posylakitu = self.objs[self.lakitu_init].transformation.translation.y
        poszlakitu = self.objs[self.lakitu_init].transformation.translation.z

        if posylakitu <= -59:  #Pour tous les différents mouvements du lakitu (hormis vertical), il est nécessaire de le "tourner" et donc de tourner sa camera
            self.objs[self.lakitu_init].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[self.lakitu_init].transformation.rotation_euler), pyrr.Vector3([posx, 64 + posy, 8 + posz]))

        if posy < 0.02 +1.905898094177246:
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, +0.1, 0]))
            self.objs[self.lakitu_init].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[self.lakitu_init].transformation.rotation_euler), pyrr.Vector3([0, +0.1, 0]))

        elif posx < -25:
            if self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] != np.pi/2:
                self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] = np.pi/2
                self.objs[self.lakitu_init].transformation.rotation_euler[pyrr.euler.index().yaw] = np.pi/2

            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, -0.5]))
            self.objs[self.lakitu_init].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[self.lakitu_init].transformation.rotation_euler), pyrr.Vector3([0, 0, -0.5]))

        elif posx > 25:
            if self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] != np.pi/2:
                self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] = np.pi/2
                self.objs[self.lakitu_init].transformation.rotation_euler[pyrr.euler.index().yaw] = np.pi/2

            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, 0.5]))
            self.objs[self.lakitu_init].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[self.lakitu_init].transformation.rotation_euler), pyrr.Vector3([0, 0, 0.5]))
        
        elif posz < -25:
            if self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] != np.pi:
                self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] = np.pi
                self.objs[self.lakitu_init].transformation.rotation_euler[pyrr.euler.index().yaw] = np.pi

            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, -0.5]))
            self.objs[self.lakitu_init].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[self.lakitu_init].transformation.rotation_euler), pyrr.Vector3([0, 0, -0.5]))

        elif posz > 25:
            if self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] != np.pi:
                self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] = np.pi
                self.objs[self.lakitu_init].transformation.rotation_euler[pyrr.euler.index().yaw] = np.pi

            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, +0.5]))
            self.objs[self.lakitu_init].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[self.lakitu_init].transformation.rotation_euler), pyrr.Vector3([0, 0, +0.5]))
        
        else:
            self.unalive = 0

            self.objs[self.lakitu_init].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[self.lakitu_init].transformation.rotation_euler), pyrr.Vector3([1000,1000,1000]))
            self.lakitu_init +=1
            self.pdv -= 1


    def collision_sol(self):
        global var_saut
        posx = self.objs[0].transformation.translation.x #Coordonnées de Kirby
        posy = self.objs[0].transformation.translation.y
        posz = self.objs[0].transformation.translation.z

        posy_sol = self.objs[1].transformation.translation.y

        if posx >= -75 and posx <= 75 and posz >= -75 and posz <= 75:
            if posy - 1.905898094177246 < posy_sol:             #Le 1.905... est la point central du kirby, ses pieds sont donc plus bas de tant
                self.objs[0].transformation.translation += \
                    pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0.024, 0]))

                var_saut = 0

    def mvt_carapace(self):
        for k in range(20,len(self.objs)-3):
            if len(self.carap_dx) < len(self.objs)-3:           #Attribution à chaque carapace d'une vitesse aléatoire entre -0.3 et 0.7 dans les axes x et z
                self.carap_dx.append(0.2 + 0.5*random.random())
            if len(self.carap_dz) < len(self.objs)-3:
                self.carap_dz.append(0.2 + 0.5*random.random())

            posx_carap = self.objs[k].transformation.translation.x
            posz_carap = self.objs[k].transformation.translation.z

            if posx_carap > 75 or posx_carap < -75:         #Rebondit sur les bords
                self.carap_dx[k-20] = -self.carap_dx[k-20]
            if posz_carap > 75 or posz_carap < -75:
                self.carap_dz[k-20] = -self.carap_dz[k-20]
            self.objs[k].transformation.translation += \
                        pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[k].transformation.rotation_euler), pyrr.Vector3([self.carap_dx[k-20], 0, self.carap_dz[k-20]]))
                        
    def collision_kirb_carap(self):
        global current_time,temps_touche
        last_time = current_time
        current_time = glfw.get_time()
        
        posx = self.objs[0].transformation.translation.x #Coordonnées Kirby
        posy = self.objs[0].transformation.translation.y
        posz = self.objs[0].transformation.translation.z
        rayon_kirb = 1.9
        rayon_carap = 1.7
        
        for k in range(20,len(self.objs)-2):
            posx_carap = self.objs[k].transformation.translation.x  #Coordonnées carapaces
            posy_carap = self.objs[k].transformation.translation.y
            posz_carap = self.objs[k].transformation.translation.z
            
            dist = np.sqrt((posx-posx_carap)**2 + (posy-posy_carap)**2 + (posz-posz_carap)**2) #Distance entre les objets pour des sphères
        
            if self.i_frame_on:
                if current_time - temps_touche > 25 * (current_time - last_time) * 5000: #Environ 25 images
                    self.i_frame_on = False
                else:
                    pass
                
            elif (dist < rayon_kirb + rayon_carap) and (self.i_frame_on == False) : #peut etre touché dans ces conditions
                self.hit = True
                self.i_frame_on = True
                temps_touche = glfw.get_time() #On enregistre le temps auquel le joueur est touché, utile pour la période d'immunité
                self.pdv -=1
                
            else:
                self.hit = False

            
        
    def finito_pipo(self):
        if self.pdv < 1 or self.lakitu_init==20:
            self.unalive = 3
            self.objs[len(self.objs)-1].value = "Perdu!"

    def affichage_vie(self) :
        self.objs[len(self.objs)-1].value = str(self.pdv)

    def niveau(self):
        if glfw.get_time() > self.temps : #Durée d'un niveau
            self.temps += 30
            for i in range(len(self.carap_dx)):  #Augmente la vitesse des carapaces de 0.25 dans les axes x et z
                if self.carap_dx[i] >= 0 :
                    self.carap_dx[i]+=0.25
                if self.carap_dz[i] >= 0 :
                    self.carap_dz[i]+=0.25  
                if self.carap_dx[i] <= 0 :
                    self.carap_dx[i]-=0.25
                if self.carap_dz[i] <= 0 :
                    self.carap_dz[i]-=0.25     
            self.niveau2 +=1
            
            if self.niveau2 >=4 :               #Augmente la vitesse de la carapace bleue
                if self.carap_bleue[0]>0 :
                    self.carap_bleue[0]+=0.25
                if self.carap_bleue[0]<0 :
                    self.carap_bleue[0]-=0.25

                if self.carap_bleue[1]>0 :
                    self.carap_bleue[1]+=0.25
                if self.carap_bleue[1]<0 :
                    self.carap_bleue[1]-=0.25

                if self.carap_bleue[2]>0 :
                    self.carap_bleue[2]+=0.25
                if self.carap_bleue[2]<0 :
                    self.carap_bleue[2]-=0.25
            self.pdv = 5                # Remet les points de vie à 5
            self.objs[len(self.objs)-2].value = str(self.niveau2)


    def mvt_carapace_bleue(self):
                if len(self.carap_bleue) == 0:           #Attribution à la carapace bleue d'une vitesse aléatoire entre -0.3 et 0.7 dans les axes x,y et z
                    self.carap_bleue.append(0.2 + 0.5*random.random()) #Vitesses en x
                    self.carap_bleue.append(0.2 + 0.5*random.random()) #Vitesses en y
                    self.carap_bleue.append(0.2 + 0.5*random.random()) #Vitesses en z

                posx_carap = self.objs[-3].transformation.translation.x
                posy_carap = self.objs[-3].transformation.translation.y
                posz_carap = self.objs[-3].transformation.translation.z

                if posx_carap > 75 or posx_carap < -75:         #Rebondit sur les bords ET le ciel
                    self.carap_bleue[0] = -self.carap_bleue[0]
                if posz_carap > 75 or posz_carap < -75:
                    self.carap_bleue[2] = -self.carap_bleue[2]
                if posy_carap < 0.5 or posy_carap > 10:
                    self.carap_bleue[1] = -self.carap_bleue[1]
                self.objs[-3].transformation.translation += \
                            pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[-3].transformation.rotation_euler), pyrr.Vector3([self.carap_bleue[0],self.carap_bleue[1] , self.carap_bleue[2]]))