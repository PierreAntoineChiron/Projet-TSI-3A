from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D, Text
import numpy as np
import OpenGL.GL as GL
import pyrr

def main():
    viewer = ViewerGL()

    viewer.set_camera(Camera())
    viewer.cam.transformation.translation.y = 2
    viewer.cam.transformation.rotation_center = viewer.cam.transformation.translation.copy()

    program3d_id = glutils.create_program_from_file('shader.vert', 'shader.frag')
    programGUI_id = glutils.create_program_from_file('gui.vert', 'gui.frag')

    m = Mesh.load_obj('Lekirb.obj')
    m.normalize()
    m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
    tr = Transformation3D()
    tr.translation.y = -np.amin(m.vertices, axis=0)[1]
    tr.translation.z = -5
    tr.rotation_center.z = 0.2
    texture = glutils.load_texture('LeKirb.png')
    o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr)
    viewer.add_object(o)

    for i in range(3):
        for j in range(3):
            m = Mesh()
            p0, p1, p2, p3 = [(2*i-3)*25, 0, (2*j-3)*25], [(2*i-1)*25, 0, (2*j-3)*25], [(2*i-1)*25, 0, (2*j-1)*25], [(2*i-3)*25, 0, (2*j-1)*25]
            n, c = [0, 1, 0], [1, 1, 1]
            t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]
            m.vertices = np.array([[p0 + n + c + t0], [p1 + n + c + t1], [p2 + n + c + t2], [p3 + n + c + t3]], np.float32)
            m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
            texture = glutils.load_texture('grass.jpg')
            o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, Transformation3D())
            viewer.add_object(o)


    m =Mesh.load_obj('Lakitu.obj') #Les lakitu x10 (copie intélligente)
    m.normalize()
    m.apply_matrix(pyrr.matrix44.create_from_scale([3, 3, 3, 1]))
    texture = glutils.load_texture('Tex_0002_0.png')
    vao = m.load_to_gpu()
    for lak in range(10):
        tr = Transformation3D()
        o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr)
        viewer.add_object(o)
        tr.translation.y = -60
        tr.translation.z = -10
        tr.rotation_center.z = 0.2

    m =Mesh.load_obj('GreenShell.obj') 
    m.normalize()
    m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
    texture = glutils.load_texture('ItmCommonGShell_auto.png')
    vao = m.load_to_gpu()
    for carap in range(15):
        tr = Transformation3D()
        o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr)
        viewer.add_object(o)
        tr.translation.y = -np.amin(m.vertices, axis=0)[1]
        tr.translation.z = -15
        tr.rotation_center.z = 0.2
    
    viewer.run()


if __name__ == '__main__':
    main()