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
        
        self.i_frame_on = True
        self.hit = False
        self.pdv = 20

    def run(self):
        # boucle d'affichage
        while not glfw.window_should_close(self.window):
            # nettoyage de la fenêtre : fond et profondeur
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self.update_key()

           # if self.lakitu_init == 0:
            #    self.objs[10].transformation.translation += \
           #         pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[10].transformation.rotation_euler), pyrr.Vector3([0, -60,-5]))
           #     self.lakitu_init = 1

            if self.unalive !=2:
                self.gravity()
                self.mvt_carapace()

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
        # Modifie la variable pour le prograself.cam.transformation.rotation_euler[pyrr.euler.index().roll] -= 0.1mme courant
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

            if glfw.KEY_SPACE in self.touch and self.touch[glfw.KEY_SPACE] > 0 :
                global var_saut
                posy = self.objs[0].transformation.translation.y
                posy_sol = self.objs[1].transformation.translation.y
                if var_saut == 0:
                    var_saut = 500

        if glfw.KEY_Y in self.touch :
            self.cam.transformation.rotation_euler = self.objs[0].transformation.rotation_euler.copy() 
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.rotation_euler[pyrr.euler.index().roll] = 0.35
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 4, 15])

    def saut(self):
        global current_time, var_saut
        last_time = current_time
        current_time = glfw.get_time()

        if var_saut !=0:
            dt = current_time - last_time
            acceleration = var_saut - 100
            vitesse = 5 + acceleration * dt
            pos = vitesse * dt
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, pos, 0]))
            var_saut -= 10
            if var_saut == 0 :
                var_saut = -1

    def gravity(self): #pas le film
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
        posx = self.objs[0].transformation.translation.x
        posy = self.objs[0].transformation.translation.y
        posz = self.objs[0].transformation.translation.z

        posxlakitu = self.objs[self.lakitu_init].transformation.translation.x
        posylakitu = self.objs[self.lakitu_init].transformation.translation.y
        poszlakitu = self.objs[self.lakitu_init].transformation.translation.z
        
        print(round(posxlakitu,3),round(posx,3),round(posylakitu,3),round(posy,3),round(poszlakitu,3),round(posz,3))

        if posylakitu <= -59:
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


    def collision_sol(self):
        global var_saut
        posx = self.objs[0].transformation.translation.x
        posy = self.objs[0].transformation.translation.y
        posz = self.objs[0].transformation.translation.z

        posy_sol = self.objs[1].transformation.translation.y

        if posx >= -75 and posx <= 75 and posz >= -75 and posz <= 75:
            if posy - 1.905898094177246 < posy_sol:
                self.objs[0].transformation.translation += \
                    pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0.024, 0]))

                var_saut = 0

    def mvt_carapace(self):
        for k in range(20,len(self.objs)):
            if len(self.carap_dx) < len(self.objs):
                self.carap_dx.append(0.2 + 0.5*random.random())
            if len(self.carap_dz) < len(self.objs):
                self.carap_dz.append(0.2 + 0.5*random.random())

            posx_carap = self.objs[k].transformation.translation.x
            posz_carap = self.objs[k].transformation.translation.z

            if posx_carap > 75 or posx_carap < -75:
                self.carap_dx[k-20] = -self.carap_dx[k-20]
            if posz_carap > 75 or posz_carap < -75:
                self.carap_dz[k-20] = -self.carap_dz[k-20]
            self.objs[k].transformation.translation += \
                        pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[k].transformation.rotation_euler), pyrr.Vector3([self.carap_dx[k-20], 0, self.carap_dz[k-20]]))
                        
    def collision_kirb_carap(self):
        global current_time,temps_touche
        last_time = current_time
        current_time = glfw.get_time()
        
        posx = self.objs[0].transformation.translation.x
        posy = self.objs[0].transformation.translation.y
        posz = self.objs[0].transformation.translation.z
        rayon_kirb = 1.9
        rayon_carap = 1.7
        
        for k in range(20,len(self.objs)):
            posx_carap = self.objs[k].transformation.translation.x
            posy_carap = self.objs[k].transformation.translation.y
            posz_carap = self.objs[k].transformation.translation.z
            
            dist = np.sqrt((posx-posx_carap)**2 + (posy-posy_carap)**2 + (posz-posz_carap)**2)
        
            if self.i_frame_on:
                if current_time - temps_touche > 25 * (current_time - last_time) * 5000:
                    self.i_frame_on = False
                else:
                    pass
                
            elif (dist < rayon_kirb + rayon_carap) and (self.i_frame_on == False) :
                self.hit = True
                self.i_frame_on = True
                temps_touche = glfw.get_time()
                self.pdv -=1
                
            else:
                self.hit = False

              
        print(self.hit,self.i_frame_on,self.pdv)