import bpy
import mathutils
import math
from math import radians,sin,cos,tan,atan
from mathutils import Vector,Quaternion
import ast, getopt, sys, copy, os
from fractions import Fraction
import numpy as np
from csaps import csaps

bl_info = {
    "name": "2Rays3DTracking",
    "blender": (2, 80, 0),
    "category": "Object",
}

def find_tracked(cam1_pos, cam1_vec, cam2_pos, cam2_vec):
    """GET PLANE"""
    crossed = cam1_vec.cross(cam2_vec)
    A=cam1_vec.y*crossed.z-(cam1_vec.z*crossed.y)
    B=-(cam1_vec.x*crossed.z-(cam1_vec.z*crossed.x))
    C=cam1_vec.x*crossed.y-(cam1_vec.y*crossed.x)
    D=-A*cam1_pos.x-B*cam1_pos.y-C*cam1_pos.z
    
    """GET POINT ON LINE2"""
    LINE2_T=(-A*cam2_pos.x-B*cam2_pos.y-C*cam2_pos.z-D)/(A*cam2_vec.x+B*cam2_vec.y+C*cam2_vec.z)
    POINT2=Vector((
        cam2_pos.x+cam2_vec.x*LINE2_T,
        cam2_pos.y+cam2_vec.y*LINE2_T,
        cam2_pos.z+cam2_vec.z*LINE2_T
        ))
    """GET POINT ON LINE1"""
    LINE1_T=-(cam1_vec.x*(cam1_pos.x-POINT2.x)+cam1_vec.y*(cam1_pos.y-POINT2.y)+cam1_vec.z*(cam1_pos.z-POINT2.z))/(pow(cam1_vec.x,2)+pow(cam1_vec.y,2)+pow(cam1_vec.z,2))
    POINT1=Vector((
        cam1_pos.x+cam1_vec.x*LINE1_T,
        cam1_pos.y+cam1_vec.y*LINE1_T,
        cam1_pos.z+cam1_vec.z*LINE1_T        
        ))
      
    RES_VEC = (POINT1+POINT2)/2
    RES_ARR = []
    RES_ARR.append(RES_VEC.x)
    RES_ARR.append(RES_VEC.y)
    RES_ARR.append(RES_VEC.z)
    return RES_ARR
           
            
class Rays3DTracking_TrackPosition(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.rays3dtracking_trackposition"
    bl_label = "Rays3DTracking_TrackPosition"

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        obj = context.active_object
        if obj.cam1_cam is None or obj.cam2_cam is None or obj.cam1_obj is None or obj.cam2_obj is None or obj.cam1_movie is None or obj.cam2_movie is None:
            return False
        if len(obj.cam1_movie.tracking.tracks)==0 or len(obj.cam2_movie.tracking.tracks)==0:
            return False
        if len(obj.cam1_movie.tracking.tracks[0].markers)<obj.keys_count or len(obj.cam2_movie.tracking.tracks[0].markers)<obj.keys_count:
            return False
            
        """GEOMETRY"""
        if obj.cam1_obj.rotation_euler==obj.cam2_obj.rotation_euler:
            return False
        return True

    def execute(self, context):
        obj = context.active_object
        
        tracked_vecs=[]
        tracked_vecs.append([])
        tracked_vecs.append([])
        tracked_vecs.append([])
        
        a=0
        while a<obj.keys_count:
            marker1=obj.cam1_movie.tracking.tracks[0].markers[a]
            marker2=obj.cam2_movie.tracking.tracks[0].markers[a]
            
            cam1_vec = mathutils.Vector((
                sin(obj.cam1_obj.rotation_euler.x+atan((marker1.co.y-0.5)*1.125*tan(obj.cam1_cam.angle/2)))*-sin(obj.cam1_obj.rotation_euler.z-atan((marker1.co.x-0.5)*2*tan(obj.cam1_cam.angle/2))),
                sin(obj.cam1_obj.rotation_euler.x+atan((marker1.co.y-0.5)*1.125*tan(obj.cam1_cam.angle/2)))*cos(obj.cam1_obj.rotation_euler.z-atan((marker1.co.x-0.5)*2*tan(obj.cam1_cam.angle/2))),
                -cos(obj.cam1_obj.rotation_euler.x+atan((marker1.co.y-0.5)*1.125*tan(obj.cam1_cam.angle/2)))
            ))
            
            cam2_vec = mathutils.Vector((
                sin(obj.cam2_obj.rotation_euler.x+atan((marker2.co.y-0.5)*1.125*tan(obj.cam2_cam.angle/2)))*-sin(obj.cam2_obj.rotation_euler.z-atan((marker2.co.x-0.5)*2*tan(obj.cam2_cam.angle/2))),
                sin(obj.cam2_obj.rotation_euler.x+atan((marker2.co.y-0.5)*1.125*tan(obj.cam2_cam.angle/2)))*cos(obj.cam2_obj.rotation_euler.z-atan((marker2.co.x-0.5)*2*tan(obj.cam2_cam.angle/2))),
                -cos(obj.cam2_obj.rotation_euler.x+atan((marker2.co.y-0.5)*1.125*tan(obj.cam2_cam.angle/2)))
            ))
                        
            tracked_vec=find_tracked(obj.cam1_obj.location,cam1_vec,obj.cam2_obj.location,cam2_vec)
            tracked_vecs[0].append(tracked_vec[0])
            tracked_vecs[1].append(tracked_vec[1])
            tracked_vecs[2].append(tracked_vec[2])
    
            a+=1
        xsites = np.linspace(1., obj.keys_count, obj.keys_count)
        xs = np.linspace(1, obj.keys_count, obj.keys_count)
        ys = csaps(xsites, tracked_vecs,xs,smooth=obj.position_smoothness)
        a=0
        while a<obj.keys_count:
            obj.location = Vector((ys[0][a],ys[1][a],ys[2][a]))
            obj.keyframe_insert(data_path="location", frame=a+1)
            a+=1
                
        return {'FINISHED'}
        
                
class Rays3DTracking_ApplyRotation(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.rays3dtracking_applyrotation"
    bl_label = "Rays3DTracking_ApplyRotation"

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        obj = context.active_object
        if obj.cam_anim_data is None:
            return False
        return True

    def execute(self, context):
        obj = context.active_object;
        
        first_line_text = obj.cam_anim_data.lines[0].body
        first_line = first_line_text.split(' ')
        first_timecode = int(first_line[0])
        data_rotation=[]
        data_rotation.append([])
        data_rotation.append([])
        data_rotation.append([])
        data_rotation.append([])
        
        frame_id=0
        for line in obj.cam_anim_data.lines:
            if (len(line.body)==0):
                break
            line_arr = line.body.split(' ')
            timecode = int(line_arr[0])

            if (1.0*frame_id/obj.fps*1000000000+first_timecode>timecode):
                continue
            
            w = float(line_arr[1])
            x = float(line_arr[2])
            y = float(line_arr[3])
            z = float(line_arr[4])            
                        
            frame_id+=1
            
            data_rotation[0].append(w)
            data_rotation[1].append(x)
            data_rotation[2].append(y)
            data_rotation[3].append(z)
        
        xsites = np.linspace(0., frame_id-1, frame_id)
        xs = np.linspace(0, frame_id-1, frame_id)
        ys = csaps(xsites, data_rotation,xs,smooth=obj.rotation_smoothness)
                
        for a in range(0,frame_id-1):
            obj.rotation_quaternion = Quaternion((ys[0][a],ys[1][a],ys[2][a],ys[3][a]))
            obj.keyframe_insert(data_path="rotation_quaternion", frame=a+1)
        
        return {'FINISHED'}
        
    
class OBJECT_PT_2Rays3DTracking(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = "OBJECT_PT_2Rays3DTracking"
    bl_label = "2Rays3DTracking"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"   
    
    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.prop(obj, "keys_count")
        row = layout.row()
        row.prop(obj, "fps")
        
        row = layout.row()
        row.prop(obj, "cam1_obj")
        row = layout.row()
        row.prop(obj, "cam1_cam")
        row = layout.row()
        row.prop(obj, "cam2_obj")
        row = layout.row()
        row.prop(obj, "cam2_cam")

        row = layout.row()
        row.prop(obj, "cam1_movie")         
        row = layout.row()
        row.prop(obj, "cam2_movie")
        
        row = layout.row()
        row.prop(obj, "position_smoothness")
        
        row = layout.row()
        row.operator("object.rays3dtracking_trackposition",text="Track 3D",icon='TRACKING')
        
        row = layout.row()
        row.prop(obj, "cam_anim_data")
        
        row = layout.row()
        row.prop(obj, "rotation_smoothness")
        
        row = layout.row()
        row.operator("object.rays3dtracking_applyrotation",text="Apply rotation",icon='DRIVER_ROTATIONAL_DIFFERENCE')
        

bpy.types.Object.track_log = bpy.props.StringProperty(name="Target object")
    
bpy.types.Object.cam1_cam = bpy.props.PointerProperty(type=bpy.types.Camera,name="Camera 1")
bpy.types.Object.cam2_cam = bpy.props.PointerProperty(type=bpy.types.Camera,name="Camera 2")

bpy.types.Object.cam1_obj = bpy.props.PointerProperty(type=bpy.types.Object,name="Camera 1")
bpy.types.Object.cam2_obj = bpy.props.PointerProperty(type=bpy.types.Object,name="Camera 2")

bpy.types.Object.cam1_movie = bpy.props.PointerProperty(type=bpy.types.MovieClip,name="Camera 1 Movie")
bpy.types.Object.cam2_movie = bpy.props.PointerProperty(type=bpy.types.MovieClip,name="Camera 2 Movie")

bpy.types.Object.cam_anim_data = bpy.props.PointerProperty(type=bpy.types.Text,name="Rotation data")

bpy.types.Object.keys_count = bpy.props.IntProperty(name="Keys count")
bpy.types.Object.fps = bpy.props.IntProperty(name="FPS",min=1,default=25)
bpy.types.Object.position_smoothness = bpy.props.FloatProperty(name="Position smoothness",min=0,max=1,default=0.1)
bpy.types.Object.rotation_smoothness = bpy.props.FloatProperty(name="Rotation smoothness",min=0,max=1,default=0.1)
    
def register():    
    bpy.utils.register_class(OBJECT_PT_2Rays3DTracking)
    bpy.utils.register_class(Rays3DTracking_TrackPosition)
    bpy.utils.register_class(Rays3DTracking_ApplyRotation)
    


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_2Rays3DTracking)
    bpy.utils.unregister_class(Rays3DTracking_TrackPosition)
    bpy.utils.unregister_class(Rays3DTracking_ApplyRotation)


if __name__ == "__main__":
    register()