# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
# https://github.com/Korchy/1d_np_scripts

#
#   Modified NP_Scripts
#

bl_info = {
    'name': 'NP Anchor',
    'author': 'Okavango with CoDEmanX, lukas_t, matali, Blenderartists community',
    'version': (0, 1, 0),
    'blender': (2, 79, 0),
    'location': 'View3D',
    'description': 'Translate objects using anchor and target points - install, assign shortcut, save user settings',
    'category': '3D View'}

import bpy
import bgl
import blf
import copy
import bmesh
import mathutils
from bpy_extras import view3d_utils
from bpy.app.handlers import persistent
from mathutils import Vector, Matrix
from blf import ROTATION
from math import radians
from bpy.props import *
import bpy.types


class LayoutNPPanel(bpy.types.Panel):
    bl_label = "NP_Scripts "
    bl_idname = "Paul_Operator_NP"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = '1D'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=False)
        row.operator("object.np_anchor_translate_007", text='ZZ move')
        row = col.row(align=False)
        row.operator("object.np_point_copy_002", text='ZX copy')
        row = col.row(align=False)
        row.operator("object.np_test", text='Test')


# Defining the main class - the macro:
class NPTest(bpy.types.Operator):
    bl_idname = 'object.np_test'
    bl_label = 'NP TEST'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('='*100)
        # bpy.ops.view3d.cursor3d()
        # bpy.context.space_data.c
        print(bpy.context.area.spaces.active.cursor_location)
        print('='*100)
        return {'FINISHED'}

# Defining the main class - the macro:
class NPAnchorTranslate007(bpy.types.Macro):
    bl_idname = 'object.np_anchor_translate_007'
    bl_label = 'NP Anchor Translate 007'
    bl_options = {'REGISTER', 'UNDO'}


# Defining the main class - the macro:
class NPPointCopy002(bpy.types.Macro):
    bl_idname = 'object.np_point_copy_002'
    bl_label = 'NP Point Copy 002'
    bl_options = {'REGISTER', 'UNDO'}


# Defining the storage class that will serve as a varable-bank for exchange among the classes. Later, this bank will recieve more variables with their values for safe keeping, as the program goes on:
class Storage:
    use_snap = None
    snap_element = None
    snap_target = None
    take = None
    place = None
    takeloc3d = (0.0, 0.0, 0.0)
    placeloc3d = (0.0, 0.0, 0.0)
    dist = None
    mode = 'MOVE'
    flag = 'NONE'
    deltavec = Vector((0, 0, 0))
    deltavec_safe = Vector((0, 0, 0))
    icon = [[23, 34], [23, 32], [19, 32], [19, 36], [21, 36], [21, 38], [25, 38], [25, 34], [23, 34], [23, 36], [21, 36]]
    __cursor3d_location = None
    __anchorname = '1D_NP_Place'
    __anchor = None
    __anchoroffset = None
    __selectionlocation = None
    __mode = ['NONE']   # list with NONE, TRANSLATE, NAVIGATE

    @staticmethod
    def anchor():
        if __class__.__anchorname not in bpy.data.objects:
            bpy.ops.mesh.primitive_cube_add(enter_editmode=True)
            bpy.ops.mesh.select_all
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.object.mode_set(mode='OBJECT')
            __class__.__anchor = bpy.context.object
            __class__.__anchor.name = __class__.__anchorname
            __class__.__anchor.hide_render = True
        else:
            __class__.__anchor = bpy.data.objects[__class__.__anchorname]
        if __class__.__anchor.hide:
            __class__.__anchor.hide = False
        if not __class__.__anchor.layers[bpy.context.screen.scene.active_layer]:
            __class__.__anchor.layers[bpy.context.screen.scene.active_layer] = True
        return __class__.__anchor

    @staticmethod
    def anchortomousecursor():
        __class__.savecursor3dposition()
        bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')
        selections = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        __class__.__anchor.select = True
        bpy.ops.view3d.snap_selected_to_cursor()
        for obj in selections:
            obj.select = True
        __class__.restorecursor3dposition()

    @staticmethod
    def removeanchor(type='SOFT'):
        if __class__.__anchor and __class__.__anchor.name == __class__.__anchorname:
            if type == 'SOFT':
                __class__.__anchor.hide = True
            elif type == 'HARD':
                selections = bpy.context.selected_objects
                bpy.ops.object.select_all(action='DESELECT')
                __class__.__anchor.select = True
                bpy.ops.object.delete('EXEC_DEFAULT')
                for obj in selections:
                    obj.select = True

    @staticmethod
    def savecursor3dposition():
        __class__.__cursor3d_location = list(bpy.context.area.spaces.active.cursor_location)

    @staticmethod
    def restorecursor3dposition():
        if __class__.__cursor3d_location:
            bpy.context.area.spaces.active.cursor_location = __class__.__cursor3d_location
            __class__.__cursor3d_location = None

    @staticmethod
    def fixanchoroffset():
        # offset between selection and anchor
        anchor = __class__.anchor()
        __class__.__anchoroffset = anchor.location - __class__.__selectionlocation

    @staticmethod
    def fixselectionlocation():
        __class__.savecursor3dposition()
        selections = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        selob = Storage.selob
        for ob in selob:
            ob.select = True
        bpy.ops.view3d.snap_cursor_to_selected()
        __class__.__selectionlocation = Vector(bpy.context.area.spaces.active.cursor_location)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selections:
            obj.select = True
        __class__.restorecursor3dposition()

    @staticmethod
    def selectiontoanchor():
        __class__.savecursor3dposition()
        anchor = __class__.anchor()
        bpy.context.area.spaces.active.cursor_location = list(anchor.location - __class__.__anchoroffset)
        anchor.select = False
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        anchor.select = True
        __class__.restorecursor3dposition()

    @staticmethod
    def selectiontostartlocation():
        __class__.savecursor3dposition()
        bpy.context.area.spaces.active.cursor_location = list(__class__.__selectionlocation)
        bpy.ops.object.select_all(action='DESELECT')
        selob = Storage.selob
        for ob in selob:
            ob.select = True
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        __class__.restorecursor3dposition()

    @staticmethod
    def getmode(offset=0):
        return __class__.__mode[-1 + offset]

    @staticmethod
    def setmode(mode):
        __class__.__mode.append(mode)

    @staticmethod
    def clear():
        __class__.__mode = ['NONE']

# Defining the first of the operational classes for aquiring the list of selected objects and storing them for later re-calls:
class NPATGetSelection(bpy.types.Operator):
    bl_idname = 'object.np_at_get_selection'
    bl_label = 'NP AT Get Selection'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        # First, storing all of the system preferences set by the user, that will be changed during the process, in order to restore them when the operation is completed:
        Storage.use_snap = bpy.context.tool_settings.use_snap
        Storage.snap_element = bpy.context.tool_settings.snap_element
        Storage.snap_target = bpy.context.tool_settings.snap_target
        Storage.pivot_point = bpy.context.space_data.pivot_point
        Storage.trans_orient = bpy.context.space_data.transform_orientation
        # Reading and storing the selection:
        selob = bpy.context.selected_objects
        Storage.selob = selob
        # Deselecting objects in prepare for other proceses in the script:
        for ob in selob:
            ob.select = False
        return {'FINISHED'}


# Deleting dummy object and activating anchor for it's use in the select-point process:
class NPATActivateAnchor(bpy.types.Operator):
    bl_idname = 'object.np_at_activate_anchor'
    bl_label = 'NP AT Activate Anchor'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        anchor = Storage.anchor()
        bpy.context.scene.objects.active = anchor
        anchor.select = True
        # Preparing for the move operator, that will enable us to carry the anchor to desired point for the translation. For this, we need to enable the specific snap parameters:
        bpy.context.tool_settings.use_snap = True
        bpy.context.tool_settings.snap_element = 'VERTEX'
        bpy.context.tool_settings.snap_target = 'ACTIVE'
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
        bpy.context.space_data.transform_orientation = 'GLOBAL'
        # print('050')
        return {'FINISHED'}


# Defining the operator that will let the user translate the anchor to the desired point. It also uses some listening operators that clean up the leftovers should the user interrupt the command. Many thanks to CoDEmanX and lukas_t:

def draw_callback_px(self, context):
    sel = bpy.context.selected_objects
    lensel = len(sel)

    if lensel == 1:
        main = 'SELECT ANCHOR POINT'

    else:
        main = 'SELECT TARGET POINT'

    font_id = 0
    bgl.glColor4f(1, 1, 1, 0.25)
    blf.size(font_id, 88, 72)
    blf.position(font_id, 5, 75, 0)
    blf.draw(font_id, 'N')
    blf.size(font_id, 28, 72)
    blf.position(font_id, 22, 75, 0)
    blf.draw(font_id, 'P')
    bgl.glColor4f(1, 1, 1, 1)
    blf.position(font_id, 75, 125, 0)
    blf.size(font_id, 16, 72)
    blf.draw(font_id, main)
    bgl.glColor4f(0, 0.5, 0, 1)
    blf.size(font_id, 11, 72)
    blf.position(font_id, 75, 105, 0)
    blf.draw(font_id, 'LMB - select, CTRL - snap')
    blf.position(font_id, 75, 90, 0)
    blf.draw(font_id, 'MMB - change axis')
    blf.position(font_id, 75, 75, 0)
    blf.draw(font_id, 'NUMPAD - value')
    bgl.glColor4f(1, 0, 0, 1)
    blf.position(font_id, 75, 55, 0)
    blf.draw(font_id, 'ESC, RMB - quit')


class NPATRunTranslate(bpy.types.Operator):
    bl_idname = 'object.np_at_run_translate'
    bl_label = 'NP AT Run Translate'
    bl_options = {'REGISTER', 'INTERNAL'}

    count = 0

    def modal(self, context, event):
        self.count += 1
        if Storage.getmode() == 'NONE':
            Storage.anchortomousecursor()
        # print('080')
        if self.count == 1:
            if Storage.getmode() == 'SELECT':
                Storage.fixselectionlocation()
                Storage.fixanchoroffset()
                Storage.setmode('TRANSLATE')
            elif Storage.getmode() == 'NONE':
                Storage.setmode('SELECT')
            bpy.ops.transform.translate('INVOKE_DEFAULT')
        elif event.type in ('LEFTMOUSE', 'RET', 'NUMPAD_ENTER') and event.value == 'RELEASE':
            if Storage.getmode() == 'TRANSLATE':
                Storage.clear()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        elif event.type in ('SPACE'):
            if event.value == 'RELEASE':
                Storage.setmode('NAVIGATE')
                Storage.selectiontostartlocation()
            elif event.value == 'PRESS':
                Storage.setmode(Storage.getmode(-1))
                Storage.selectiontoanchor()
                bpy.ops.transform.translate('INVOKE_DEFAULT')
                return {'INTERFACE'}
        elif event.type in ('RIGHTMOUSE'):
            if Storage.getmode() != 'NAVIGATE':
                # Storage.selectiontoanchor()
                bpy.ops.transform.translate('INVOKE_DEFAULT')
        elif event.type in ('ESC'):
            Storage.clear()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            # Storage.removeanchor('SOFT')
            Storage.selectiontostartlocation()
            bpy.context.tool_settings.use_snap = Storage.use_snap
            bpy.context.tool_settings.snap_element = Storage.snap_element
            bpy.context.tool_settings.snap_target = Storage.snap_target
            bpy.context.space_data.pivot_point = Storage.pivot_point
            bpy.context.space_data.transform_orientation = Storage.trans_orient
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # print("START_____")
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    # Reselecting the objects from the list of originaly selected objects:


class NPATReselectStored(bpy.types.Operator):
    bl_idname = "object.np_at_reselect_stored"
    bl_label = "NP AT Reselect Stored"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        selob = Storage.selob
        for ob in selob:
            ob.select = True
        bpy.context.tool_settings.use_snap = True
        bpy.context.tool_settings.snap_element = 'VERTEX'
        bpy.context.tool_settings.snap_target = 'ACTIVE'
        bpy.context.space_data.pivot_point = 'ACTIVE_ELEMENT'
        bpy.context.space_data.transform_orientation = 'GLOBAL'
        return {'FINISHED'}


# Deleting the anchor after succesfull translation:
class NPATDeleteAnchor(bpy.types.Operator):
    bl_idname = "object.np_at_delete_anchor"
    bl_label = "NP AT Delete Anchor"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        # Storage.removeanchor('SOFT')
        bpy.context.tool_settings.use_snap = Storage.use_snap
        bpy.context.tool_settings.snap_element = Storage.snap_element
        bpy.context.tool_settings.snap_target = Storage.snap_target
        bpy.context.space_data.pivot_point = Storage.pivot_point
        bpy.context.space_data.transform_orientation = Storage.trans_orient
        return {'FINISHED'}


# -----------------------------------,

# Defining the scene update algorithm that will track the positions of the object during modal transforms, which is otherwise impossible:

@persistent
def scene_update_NPPC(context):
    # print('00_SceneUpdate_START')

    if bpy.data.objects.is_updated:
        # print('up1')
        mode = Storage.mode
        flag = Storage.flag
        # print(mode, flag)
        take = Storage.take
        place = Storage.place
        if flag in ('RUNTRANSZERO', 'RUNTRANSFIRST', 'RUNTRANSNEXT', 'NAVTRANSZERO', 'NAVTRANSFIRST', 'NAVTRANSNEXT'):
            print('up2')
            Storage.takeloc3d = take.location
            Storage.placeloc3d = place.location
    # print('up3')
    # print('00_SceneUpdate_FINISHED')


# Defining the first of the operators from the macro, that will gather the list of selected objects and system preferences set by the user. Some of the system settings will be changed during the process, and will be restored when macro is completed:

class NPPCReadContext(bpy.types.Operator):
    bl_idname = 'object.np_pc_read_context'
    bl_label = 'NP PC Read Context'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        # Storing all of the system settings that might change during process:
        print('01_ReadContext_START', ';', 'flag = ', Storage.flag)
        Storage.use_snap = copy.deepcopy(bpy.context.tool_settings.use_snap)
        Storage.snap_element = copy.deepcopy(bpy.context.tool_settings.snap_element)
        Storage.snap_target = copy.deepcopy(bpy.context.tool_settings.snap_target)
        Storage.pivot_point = copy.deepcopy(bpy.context.space_data.pivot_point)
        Storage.trans_orient = copy.deepcopy(bpy.context.space_data.transform_orientation)
        Storage.acob = bpy.context.active_object
        print('Storage.acob = ', Storage.acob)
        print('Context mode = ', bpy.context.mode)
        if bpy.context.mode == 'OBJECT':
            Storage.edit_mode = 'OBJECT'
        elif bpy.context.mode in (
        'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_TEXT', 'EDIT_ARMATURE', 'EDIT_METABALL', 'EDIT_LATTICE'):
            Storage.edit_mode = 'EDIT'
        elif bpy.context.mode == 'POSE':
            Storage.edit_mode = 'POSE'
        elif bpy.context.mode == 'SCULPT':
            Storage.edit_mode = 'SCULPT'
        elif bpy.context.mode == 'PAINT_WEIGHT':
            Storage.edit_mode = 'WEIGHT_PAINT'
        elif bpy.context.mode == 'PAINT_TEXTURE':
            Storage.edit_mode = 'TEXTURE_PAINT'
        elif bpy.context.mode == 'PAINT_VERTEX':
            Storage.edit_mode = 'VERTEX_PAINT'
        elif bpy.context.mode == 'PARTICLE':
            Storage.edit_mode = 'PARTICLE_EDIT'
            # Reading and storing the selection:
        print('selected: ', bpy.context.selected_objects)
        if bpy.context.selected_objects == []:
            self.report({'WARNING'}, "Please select objects first")
            print('01_ReadContext_CANCELLED')
            return {'CANCELLED'}
        else:
            Storage.selob = bpy.context.selected_objects
        # Changing to OBJECT mode which will be the context for the procedure:
        if bpy.context.mode not in ('OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT')
        # De-selecting objects in prepare for other processes in the script:
        bpy.ops.object.select_all(action='DESELECT')
        print('01_ReadContext_FINISHED', ';', 'flag = ', Storage.flag)
        return {'FINISHED'}

    # Defining the operator that will read the mouse position in 3D when the command is activated and store it as a location for placing the 'take' and 'place' points under the mouse:


class NPPCReadMouseloc(bpy.types.Operator):
    bl_idname = 'object.np_pc_read_mouseloc'
    bl_label = 'NP PC Read Mouseloc'
    bl_options = {'INTERNAL'}

    def modal(self, context, event):
        print('02_ReadMouseloc_START', ';', 'flag = ', Storage.flag)
        region = context.region
        rv3d = context.region_data
        co2d = ((event.mouse_region_x, event.mouse_region_y))
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, co2d)
        enterloc = view3d_utils.region_2d_to_origin_3d(region, rv3d, co2d) + view_vector / 5
        print('enterloc = ', enterloc)
        Storage.enterloc = copy.deepcopy(enterloc)
        print('02_RadMouseloc_FINISHED', ';', 'flag = ', Storage.flag)
        return {'FINISHED'}

    def invoke(self, context, event):
        print('02_ReadMouseloc_INVOKE_START', ';', 'flag = ', Storage.flag)
        args = (self, context)
        context.window_manager.modal_handler_add(self)
        print('02_ReadMouseloc_INVOKED_FINISHED', ';', 'flag = ', Storage.flag)
        return {'RUNNING_MODAL'}


# Defining the operator that will generate 'take' and 'place' points at the spot marked by mouse and select them, preparing for translation:

class NPPCAddHelpers(bpy.types.Operator):
    bl_idname = 'object.np_pc_add_helpers'
    bl_label = 'NP PC Add Helpers'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        print('03_AddHelpers_START', ';', 'flag = ', Storage.flag)
        enterloc = Storage.enterloc
        bpy.ops.object.add(type='MESH', location=enterloc)
        take = bpy.context.active_object
        take.name = 'NP_PC_take'
        Storage.take = take
        bpy.ops.object.add(type='MESH', location=enterloc)
        place = bpy.context.active_object
        place.name = 'NP_PC_place'
        Storage.place = place
        take.select = True
        place.select = True
        # bpy.context.scene.objects.active = place
        bpy.context.tool_settings.use_snap = True
        bpy.context.tool_settings.snap_element = 'VERTEX'
        bpy.context.tool_settings.snap_target = 'ACTIVE'
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
        bpy.context.space_data.transform_orientation = 'GLOBAL'
        Storage.flag = 'RUNTRANSZERO'
        print('03_AddHelpers_FINISHED', ';', 'flag = ', Storage.flag)
        return {'FINISHED'}


# Defining the operator that will let the user translate take and place points to the desired 'take' location. It also uses some listening operators that clean up the leftovers should the user interrupt the command. Many thanks to CoDEmanX and lukas_t:

class NPPCRunTrans(bpy.types.Operator):
    bl_idname = 'object.np_pc_run_trans'
    bl_label = 'NP PC Run Trans'
    bl_options = {'INTERNAL'}

    print('04_RunTrans_START', ';', 'Storage.flag = ', Storage.flag)
    count = 0

    def modal(self, context, event):
        context.area.tag_redraw()
        flag = Storage.flag
        take = Storage.take
        place = Storage.place
        selob = Storage.selob
        self.count += 1

        if self.count == 1:
            bpy.ops.transform.translate('INVOKE_DEFAULT')
            print('04_RunTrans_count_1_INVOKE_DEFAULT', ';', 'flag = ', Storage.flag)

        elif event.alt and event.type in ('LEFTMOUSE', 'RET', 'NUMPAD_ENTER') and event.value == 'RELEASE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            if flag == 'RUNTRANSFIRST':
                Storage.deltavec_safe = copy.deepcopy(Storage.deltavec)
                print('deltavec_safe = ', Storage.deltavec_safe)
                Storage.ar13d = copy.deepcopy(take.location)
                Storage.ar23d = copy.deepcopy(place.location)
                place.select = False
                bpy.ops.object.duplicate()
                prevob = Storage.prevob
                nextob = Storage.nextob
                Storage.arob = prevob
                Storage.prevob = nextob
                Storage.nextob = bpy.context.selected_objects
                take.location = copy.deepcopy(place.location)
                place.select = True
                Storage.flag = 'RUNTRANSNEXT_break'
            elif flag == 'RUNTRANSNEXT':
                Storage.deltavec_safe = copy.deepcopy(Storage.deltavec)
                print('deltavec_safe = ', Storage.deltavec_safe)
                Storage.ar13d = copy.deepcopy(take.location)
                Storage.ar23d = copy.deepcopy(place.location)
                place.select = False
                bpy.ops.object.duplicate()
                prevob = Storage.prevob
                nextob = Storage.nextob
                Storage.arob = prevob
                Storage.prevob = nextob
                Storage.nextob = bpy.context.selected_objects
                take.location = copy.deepcopy(place.location)
                place.select = True
                Storage.flag = 'RUNTRANSNEXT_break'
            else:
                print('UNKNOWN FLAG')
                Storage.flag = 'EXIT'
            print('04_RunTrans_alt_left_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type in ('LEFTMOUSE', 'RET', 'NUMPAD_ENTER') and event.value == 'RELEASE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            if flag == 'RUNTRANSZERO':
                take.select = False
                place.select = False
                Storage.firsttake3d = copy.deepcopy(take.location)
                for ob in selob:
                    ob.select = True
                bpy.ops.object.duplicate()
                Storage.nextob = bpy.context.selected_objects
                Storage.prevob = selob
                place.select = True
                Storage.flag = 'RUNTRANSFIRST_break'
            elif flag == 'RUNTRANSFIRST':
                Storage.deltavec_safe = copy.deepcopy(Storage.deltavec)
                print('deltavec_safe = ', Storage.deltavec_safe)
                Storage.ar13d = copy.deepcopy(take.location)
                Storage.ar23d = copy.deepcopy(place.location)
                place.select = False
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in Storage.selob:
                    ob.select = True
                bpy.ops.object.duplicate(linked=True)
                value = (place.location - Storage.firsttake3d).to_tuple(4)
                bpy.ops.transform.translate(value=value)
                bpy.ops.object.duplicate()
                prevob = Storage.prevob
                nextob = Storage.nextob
                Storage.arob = prevob
                Storage.prevob = nextob
                Storage.nextob = bpy.context.selected_objects
                take.location = copy.deepcopy(place.location)
                place.select = True
                bpy.context.scene.objects.active = place
                Storage.flag = 'RUNTRANSNEXT_break'
            elif flag == 'RUNTRANSNEXT':
                Storage.deltavec_safe = copy.deepcopy(Storage.deltavec)
                print('deltavec_safe = ', Storage.deltavec_safe)
                Storage.ar13d = copy.deepcopy(take.location)
                Storage.ar23d = copy.deepcopy(place.location)
                place.select = False
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in Storage.selob:
                    ob.select = True
                bpy.ops.object.duplicate(linked=True)
                value = (place.location - Storage.firsttake3d).to_tuple(4)
                bpy.ops.transform.translate(value=value)
                bpy.ops.object.duplicate()
                prevob = Storage.prevob
                nextob = Storage.nextob
                Storage.arob = prevob
                Storage.prevob = nextob
                Storage.nextob = bpy.context.selected_objects
                take.location = copy.deepcopy(place.location)
                place.select = True
                Storage.flag = 'RUNTRANSNEXT_break'
            else:
                print('UNKNOWN FLAG')
                Storage.flag = 'EXIT'
            print('04_RunTrans_left_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type == 'SPACE' and event.value == 'RELEASE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            take.hide = True
            place.hide = True
            self.co2d = ((event.mouse_region_x, event.mouse_region_y))
            co2d = self.co2d
            region = context.region
            rv3d = context.region_data
            away = view3d_utils.region_2d_to_origin_3d(region, rv3d, co2d) - place.location
            away = away.length
            placeloc3d = Storage.placeloc3d
            awayloc = copy.deepcopy(placeloc3d)
            Storage.awayloc = awayloc
            Storage.away = copy.deepcopy(away)
            if flag == 'RUNTRANSZERO':
                Storage.flag = 'NAVTRANSZERO'
            elif flag == 'RUNTRANSFIRST':
                nextob = Storage.nextob
                for ob in nextob:
                    ob.hide = True
                Storage.flag = 'NAVTRANSFIRST'
            elif flag == 'RUNTRANSNEXT':
                nextob = Storage.nextob
                for ob in nextob:
                    ob.hide = True
                Storage.flag = 'NAVTRANSNEXT'
            else:
                print('UNKNOWN FLAG')
                Storage.flag = 'EXIT'
            print('04_RunTrans_space_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type == 'RIGHTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            if flag == 'RUNTRANSZERO':
                Storage.flag = 'EXIT'
            elif flag == 'RUNTRANSFIRST':
                place.select = False
                prevob = Storage.prevob
                nextob = Storage.nextob
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in prevob:
                    ob.select = True
                Storage.flag = 'EXIT'
            elif flag == 'RUNTRANSNEXT':
                place.select = False
                prevob = Storage.prevob
                nextob = Storage.nextob
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in prevob:
                    ob.select = True
                bpy.ops.object.delete('EXEC_DEFAULT')
                Storage.flag = 'ARRAYTRANS'
            else:
                print('UNKNOWN FLAG')
                Storage.flag = 'EXIT'
            print('04_RunTrans_rmb_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type == 'ESC':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            if flag == 'RUNTRANSZERO':
                Storage.flag = 'EXIT'
            elif flag == 'RUNTRANSFIRST':
                place.select = False
                prevob = Storage.prevob
                nextob = Storage.nextob
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in prevob:
                    ob.select = True
                Storage.flag = 'EXIT'
            elif flag == 'RUNTRANSNEXT':
                place.select = False
                prevob = Storage.prevob
                nextob = Storage.nextob
                Storage.selob = prevob
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in prevob:
                    ob.select = True
                Storage.flag = 'EXIT'
            else:
                print('UNKNOWN FLAG')
                Storage.flag = 'EXIT'
            print('04_RunTrans_rmb_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        print('04_RunTrans_count_PASS_THROUGH', ';', 'flag = ', Storage.flag)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # print('04_RunTrans_INVOKE_START')
        flag = Storage.flag
        selob = Storage.selob
        # print('flag = ', flag)
        if context.area.type == 'VIEW_3D':
            if flag in ('RUNTRANSZERO', 'RUNTRANSFIRST', 'RUNTRANSNEXT'):
                args = (self, context)
                self._handle = bpy.types.SpaceView3D.draw_handler_add(DRAW_RunTrans, args, 'WINDOW', 'POST_PIXEL')
                context.window_manager.modal_handler_add(self)
                print('04_RunTrans_INVOKED_RUNNING_MODAL', ';', 'flag = ', Storage.flag)
                return {'RUNNING_MODAL'}
            else:
                # print('04_RunTrans_INVOKE_DECLINED_FINISHED',';','flag = ', flag)
                return {'FINISHED'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            flag = 'WARNING3D'
            Storage.flag = flag
            print('04_RunTrans_INVOKE_DECLINED_FINISHED', ';', 'flag = ', Storage.flag)
            return {'CANCELLED'}

        # Defining the set of instructions that will draw the OpenGL elements on the screen during the execution of RunTrans operator:


def DRAW_RunTrans(self, context):
    print('04_DRAW_RunTrans_START', ';', 'flag = ', Storage.flag)

    addon_prefs = context.user_preferences.addons[__name__].preferences
    badge = addon_prefs.badge
    badge_size = addon_prefs.badge_size
    dist_scale = addon_prefs.dist_scale

    flag = Storage.flag
    takeloc3d = Storage.takeloc3d
    placeloc3d = Storage.placeloc3d
    dist_num = (mathutils.Vector(placeloc3d) - mathutils.Vector(takeloc3d))
    Storage.deltavec = copy.deepcopy(dist_num)
    print('deltavec = ', Storage.deltavec)
    dist_num = dist_num.length * dist_scale
    region = context.region
    rv3d = context.region_data

    if flag in ('RUNTRANSZERO', 'RUNTRANSFIRST', 'RUNTRANSNEXT'):
        takeloc2d = view3d_utils.location_3d_to_region_2d(region, rv3d, takeloc3d)
        placeloc2d = view3d_utils.location_3d_to_region_2d(region, rv3d, placeloc3d)
    if flag == 'NAVTRANSZERO':
        takeloc2d = self.co2d
        placeloc2d = self.co2d
    if flag in ('NAVTRANSFIRST', 'NAVTRANSNEXT'):
        takeloc2d = view3d_utils.location_3d_to_region_2d(region, rv3d, takeloc3d)
        placeloc2d = self.co2d

    if addon_prefs.col_line_main_DEF == False:
        col_line_main = addon_prefs.col_line_main
    else:
        col_line_main = (1.0, 1.0, 1.0, 1.0)

    if addon_prefs.col_line_shadow_DEF == False:
        col_line_shadow = addon_prefs.col_line_shadow
    else:
        col_line_shadow = (0.1, 0.1, 0.1, 0.25)

    if addon_prefs.col_num_main_DEF == False:
        col_num_main = addon_prefs.col_num_main
    else:
        col_num_main = (0.1, 0.1, 0.1, 0.75)

    if addon_prefs.col_num_shadow_DEF == False:
        col_num_shadow = addon_prefs.col_num_shadow
    else:
        col_num_shadow = (1.0, 1.0, 1.0, 1.0)

    if addon_prefs.suffix == 'None':
        suffix = None

    elif addon_prefs.suffix == 'km':
        suffix = ' km'

    elif addon_prefs.suffix == 'm':
        suffix = ' m'

    elif addon_prefs.suffix == 'cm':
        suffix = ' cm'

    elif addon_prefs.suffix == 'mm':
        suffix = ' mm'

    elif addon_prefs.suffix == 'nm':
        suffix = ' nm'

    elif addon_prefs.suffix == "'":
        suffix = "'"

    elif addon_prefs.suffix == '"':
        suffix = '"'

    elif addon_prefs.suffix == 'thou':
        suffix = ' thou'

    dist_num = abs(round(dist_num, 2))
    if suffix is not None:
        dist = str(dist_num) + suffix
    else:
        dist = str(dist_num)
    print('flag = ', flag, 'dist = ', dist, )

    distloc = []
    takex = takeloc2d[0]
    takey = takeloc2d[1]
    placex = placeloc2d[0]
    placey = placeloc2d[1]
    if takex > region.width:
        takex = region.width
    if takex < 0:
        takex = 0
    if takey > region.height:
        takey = region.height
    if takey < 0:
        takey = 0
    if placex > region.width:
        placex = region.width
    if placex < 0:
        placex = 0
    if placey > region.height:
        placey = region.height
    if placey < 0:
        placey = 0
    distloc.append((takex + placex) / 2)
    distloc.append((takey + placey) / 2)

    if flag in ('RUNTRANSNEXT', 'NAVTRANSNEXT'):
        ardist_num = Storage.ar23d - Storage.ar13d
        ardist_num = ardist_num.length * dist_scale
        ar12d = view3d_utils.location_3d_to_region_2d(region, rv3d, Storage.ar13d)
        ar22d = view3d_utils.location_3d_to_region_2d(region, rv3d, Storage.ar23d)
        ardist_num = abs(round(ardist_num, 2))
        if suffix is not None:
            ardist = str(ardist_num) + suffix
        else:
            ardist = str(ardist_num)
        Storage.ardist = ardist
        ardist_loc = (ar12d + ar22d) / 2

    # DRAWING START:
    bgl.glEnable(bgl.GL_BLEND)

    # ON-SCREEN INSTRUCTIONS:
    font_id = 0
    bgl.glColor4f(1, 1, 1, 0.35)
    blf.size(font_id, 88, 72)
    blf.position(font_id, 5, 74, 0)
    blf.draw(font_id, 'N')
    blf.size(font_id, 28, 72)
    blf.position(font_id, 22, 74, 0)
    blf.draw(font_id, 'P')
    blf.enable(font_id, ROTATION)
    bgl.glColor4f(1, 1, 1, 0.40)
    ang = radians(90)
    blf.size(font_id, 19, 72)
    blf.rotation(font_id, ang)
    blf.position(font_id, 78, 73, 0)
    blf.draw(font_id, 'PC 002')
    blf.disable(font_id, ROTATION)
    if flag == 'RUNTRANSZERO':
        main = 'SELECT THE TAKE POINT'
        bgl.glColor4f(0, 0.5, 0, 1)
        blf.size(font_id, 11, 72)
        blf.position(font_id, 93, 105, 0)
        blf.draw(font_id, 'CTRL - snap, LMB - confirm, MMB - lock axis, NUMPAD - value')
        blf.position(font_id, 93, 90, 0)
        blf.draw(font_id, 'SPACE - navigate')
        bgl.glColor4f(1, 0, 0, 1)
        blf.position(font_id, 93, 75, 0)
        blf.draw(font_id, 'ESC / RMB - cancel copy')
    elif flag == 'RUNTRANSFIRST':
        main = 'SELECT THE PLACEMENT POINT'
        bgl.glColor4f(0, 0.5, 0, 1)
        blf.size(font_id, 11, 72)
        blf.position(font_id, 93, 105, 0)
        blf.draw(font_id, 'LMB - confirm, CTRL - snap, ALT - instance, MMB - lock axis, NUMPAD - value')
        blf.position(font_id, 93, 90, 0)
        blf.draw(font_id, 'SPACE - navigate')
        bgl.glColor4f(1, 0, 0, 1)
        blf.position(font_id, 93, 75, 0)
        blf.draw(font_id, 'ESC / RMB - cancel copy')
    elif flag == 'RUNTRANSNEXT':
        main = 'SELECT THE PLACEMENT POINT'
        bgl.glColor4f(0, 0.5, 0, 1)
        blf.size(font_id, 11, 72)
        blf.position(font_id, 93, 105, 0)
        blf.draw(font_id, 'LMB - confirm, CTRL - snap, ALT - instance, MMB - lock axis, NUMPAD - value')
        blf.position(font_id, 93, 90, 0)
        blf.draw(font_id, 'RMB - array last pair')
        blf.position(font_id, 93, 75, 0)
        blf.draw(font_id, 'SPACE - navigate')
        bgl.glColor4f(1, 0, 0, 1)
        blf.position(font_id, 93, 60, 0)
        blf.draw(font_id, 'ESC - cancel current')
    elif flag == 'NAVTRANSZERO':
        main = 'NAVIGATE FOR BETTER PLACEMENT OF TAKE POINT'
        bgl.glColor4f(0, 0.5, 0, 1)
        blf.size(font_id, 11, 72)
        blf.position(font_id, 93, 105, 0)
        blf.draw(font_id, 'MMB, SCROLL - navigate')
        blf.position(font_id, 93, 90, 0)
        blf.draw(font_id, 'LMB, SPACE - leave navigate')
        bgl.glColor4f(1, 0, 0, 1)
        blf.position(font_id, 93, 75, 0)
        blf.draw(font_id, 'ESC / RMB - cancel copy')
    elif flag == 'NAVTRANSFIRST':
        main = 'NAVIGATE FOR BETTER SELECTION OF PLACEMENT POINT'
        bgl.glColor4f(0, 0.5, 0, 1)
        blf.size(font_id, 11, 72)
        blf.position(font_id, 93, 105, 0)
        blf.draw(font_id, 'MMB, SCROLL - navigate')
        blf.position(font_id, 93, 90, 0)
        blf.draw(font_id, 'LMB, SPACE - leave navigate')
        bgl.glColor4f(1, 0, 0, 1)
        blf.position(font_id, 93, 75, 0)
        blf.draw(font_id, 'ESC / RMB - cancel copy')
    elif flag == 'NAVTRANSNEXT':
        main = 'NAVIGATE FOR BETTER SELECTION OF PLACEMENT POINT'
        bgl.glColor4f(0, 0.5, 0, 1)
        blf.size(font_id, 11, 72)
        blf.position(font_id, 93, 105, 0)
        blf.draw(font_id, 'MMB, SCROLL - navigate')
        blf.position(font_id, 93, 90, 0)
        blf.draw(font_id, 'LMB, SPACE - leave navigate')
        blf.position(font_id, 93, 75, 0)
        blf.draw(font_id, 'RMB - array last pair')
        bgl.glColor4f(1, 0, 0, 1)
        blf.position(font_id, 93, 60, 0)
        blf.draw(font_id, 'ESC - cancel current')
    bgl.glColor4f(0.0, 0.0, 0.0, 0.5)
    blf.position(font_id, 93, 124, 0)
    blf.size(font_id, 16, 72)
    blf.draw(font_id, main)
    bgl.glColor4f(1, 1, 1, 1)
    blf.position(font_id, 94, 125, 0)
    blf.size(font_id, 16, 72)
    blf.draw(font_id, main)

    # LINE:
    bgl.glColor4f(*col_line_shadow)
    bgl.glLineWidth(1.4)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    bgl.glVertex2f((takeloc2d[0] - 1), (takeloc2d[1] - 1))
    bgl.glVertex2f((placeloc2d[0] - 1), (placeloc2d[1] - 1))
    bgl.glEnd()
    bgl.glColor4f(*col_line_main)
    bgl.glLineWidth(1.4)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    bgl.glVertex2f(*takeloc2d)
    bgl.glVertex2f(*placeloc2d)
    bgl.glEnd()

    # ARMARKERS:
    markersize = badge_size * 2.5
    triangle = [[0, 0], [-1, 1], [1, 1]]
    if flag in ('RUNTRANSNEXT', 'NAVTRANSNEXT'):
        triangle = [[0, 0], [-1, 1], [1, 1]]
        for co in triangle:
            co[0] = int(co[0] * markersize * 3) + ar12d[0]
            co[1] = int(co[1] * markersize * 3) + ar12d[1]
        bgl.glColor4f(0.4, 0.15, 0.75, 1.0)
        bgl.glBegin(bgl.GL_TRIANGLE_FAN)
        for x, y in triangle:
            bgl.glVertex2f(x, y)
        bgl.glEnd()
        triangle = [[0, 0], [-1, 1], [1, 1]]
        for co in triangle:
            co[0] = int(co[0] * markersize * 3) + ar22d[0]
            co[1] = int(co[1] * markersize * 3) + ar22d[1]
        bgl.glColor4f(0.4, 0.15, 0.75, 1.0)
        bgl.glBegin(bgl.GL_TRIANGLE_FAN)
        for x, y in triangle:
            bgl.glVertex2f(x, y)
        bgl.glEnd()

        # MOUSE BADGE:
    if badge == True:
        square = [[17, 30], [17, 40], [27, 40], [27, 30]]
        rectangle = [[27, 30], [27, 40], [67, 40], [67, 30]]
        icon = copy.deepcopy(Storage.icon)
        print('icon', icon)
        ipx = 29
        ipy = 33
        for co in square:
            co[0] = round((co[0] * badge_size), 0) - (badge_size * 10) + placeloc2d[0]
            co[1] = round((co[1] * badge_size), 0) - (badge_size * 25) + placeloc2d[1]
        for co in rectangle:
            co[0] = round((co[0] * badge_size), 0) - (badge_size * 10) + placeloc2d[0]
            co[1] = round((co[1] * badge_size), 0) - (badge_size * 25) + placeloc2d[1]
        for co in icon:
            co[0] = round((co[0] * badge_size), 0) - (badge_size * 10) + placeloc2d[0]
            co[1] = round((co[1] * badge_size), 0) - (badge_size * 25) + placeloc2d[1]
        ipx = round((ipx * badge_size), 0) - (badge_size * 10) + placeloc2d[0]
        ipy = round((ipy * badge_size), 0) - (badge_size * 25) + placeloc2d[1]
        ipsize = int(6 * badge_size)
        bgl.glColor4f(0.0, 0.0, 0.0, 0.0)
        bgl.glBegin(bgl.GL_TRIANGLE_FAN)
        for x, y in square:
            bgl.glVertex2f(x, y)
        bgl.glEnd()
        if flag in ('RUNTRANSZERO', 'RUNTRANSFIRST', 'RUNTRANSNEXT'):
            bgl.glColor4f(1.0, 0.5, 0.0, 1.0)
            bgl.glBegin(bgl.GL_TRIANGLE_FAN)
            for x, y in rectangle:
                bgl.glVertex2f(x, y)
            bgl.glEnd()
            bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
            blf.position(font_id, ipx, ipy, 0)
            blf.size(font_id, ipsize, 72)
            blf.draw(font_id, 'CTRL+SNAP')
        if flag in ('NAVTRANSZERO', 'NAVTRANSFIRST', 'NAVTRANSNEXT'):
            bgl.glColor4f(0.5, 0.75, 0.0, 1.0)
            bgl.glBegin(bgl.GL_TRIANGLE_FAN)
            for x, y in rectangle:
                bgl.glVertex2f(x, y)
            bgl.glEnd()
            bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
            blf.position(font_id, ipx, ipy, 0)
            blf.size(font_id, ipsize, 72)
            blf.draw(font_id, 'NAVIGATE')
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x, y in icon:
            bgl.glVertex2f(x, y)
        bgl.glEnd()

    # AR NUMERICAL DISTANCE:
    if flag in ('RUNTRANSNEXT', 'NAVTRANSNEXT'):
        print('ardist = ', ardist, 'ardist_loc = ', ardist_loc, 'ardist_num = ', ardist_num)
        bgl.glColor4f(0.4, 0.15, 0.75, 1.0)
        font_id = 0
        blf.size(font_id, 20, 72)
        blf.position(font_id, ardist_loc[0], ardist_loc[1], 0)
        blf.draw(font_id, ardist)

    # NUMERICAL DISTANCE:
    print('dist = ', dist, 'distloc = ', distloc, 'dist_num = ', dist_num)
    bgl.glColor4f(*col_num_shadow)
    if dist_num not in (0, 'a'):
        font_id = 0
        blf.size(font_id, 20, 72)
        blf.position(font_id, (distloc[0] - 1), (distloc[1] - 1), 0)
        blf.draw(font_id, dist)
        bgl.glColor4f(*col_num_main)
        font_id = 0
        blf.size(font_id, 20, 72)
        blf.position(font_id, distloc[0], distloc[1], 0)
        blf.draw(font_id, dist)

        # DRAWING END:
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    print('04_DRAW_RunTrans_FINISHED', ';', 'flag = ', Storage.flag)


# Defining the operator that will enable navigation if user calls it:

class NPPCNavTrans(bpy.types.Operator):
    bl_idname = "object.np_pc_nav_trans"
    bl_label = "NP PC Nav Trans"
    bl_options = {'INTERNAL'}

    print('04a_NavTrans_START', ';', 'flag = ', Storage.flag)

    def modal(self, context, event):
        context.area.tag_redraw()
        flag = Storage.flag
        take = Storage.take
        place = Storage.place

        if event.type == 'MOUSEMOVE':
            self.co2d = ((event.mouse_region_x, event.mouse_region_y))
            region = context.region
            rv3d = context.region_data
            co2d = self.co2d
            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, co2d)
            pointloc = view3d_utils.region_2d_to_origin_3d(region, rv3d, co2d) + view_vector * Storage.away
            Storage.placeloc3d = copy.deepcopy(pointloc)
            print('04a_NavTrans_mousemove', ';', 'flag = ', Storage.flag)

        elif event.type in {'LEFTMOUSE', 'SPACE'} and event.value == 'PRESS':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self.co2d = ((event.mouse_region_x, event.mouse_region_y))
            region = context.region
            rv3d = context.region_data
            co2d = self.co2d
            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, co2d)
            enterloc = view3d_utils.region_2d_to_origin_3d(region, rv3d, co2d) + view_vector * Storage.away
            placeloc3d = Storage.placeloc3d
            navdelta = enterloc - Storage.awayloc
            take.hide = False
            place.hide = False
            print('flag = ', flag)
            if flag == 'NAVTRANSZERO':
                takeloc3d = enterloc
                placeloc3d = enterloc
                take.location = enterloc
                place.location = enterloc
                Storage.flag = 'RUNTRANSZERO'
            elif flag == 'NAVTRANSFIRST':
                takeloc3d = Storage.takeloc3d
                placeloc3d = enterloc
                place.location = enterloc
                nextob = Storage.nextob
                for ob in nextob:
                    ob.hide = False
                place.select = False
                bpy.ops.transform.translate(value=navdelta)
                place.select = True
                Storage.flag = 'RUNTRANSFIRST'
            elif flag == 'NAVTRANSNEXT':
                takeloc3d = Storage.takeloc3d
                placeloc3d = enterloc
                place.location = enterloc
                nextob = Storage.nextob
                for ob in nextob:
                    ob.hide = False
                place.select = False
                bpy.ops.transform.translate(value=navdelta)
                place.select = True
                Storage.flag = 'RUNTRANSNEXT'
            else:
                print('UNKNOWN FLAG')
                Storage.flag = 'EXIT'
            Storage.take = take
            Storage.place = place
            Storage.takeloc3d = takeloc3d
            Storage.placeloc3d = placeloc3d
            print('04a_NavTrans_left_space_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type == 'RIGHTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            take.hide = False
            place.hide = False
            if flag == 'NAVTRANSZERO':
                place.select = False
                Storage.flag = 'EXIT'
            elif flag == 'NAVTRANSFIRST':
                place.select = False
                prevob = Storage.prevob
                nextob = Storage.nextob
                for ob in nextob:
                    ob.hide = False
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in prevob:
                    ob.select = True
                Storage.flag = 'EXIT'
            elif flag == 'NAVTRANSNEXT':
                place.select = False
                prevob = Storage.prevob
                nextob = Storage.nextob
                for ob in nextob:
                    ob.hide = False
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in prevob:
                    ob.select = True
                bpy.ops.object.delete('EXEC_DEFAULT')
                Storage.flag = 'ARRAYTRANS'
            else:
                print('UNKNOWN FLAG')
                Storage.flag = 'EXIT'
            print('04a_NavTrans_rmb_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type == 'ESC':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            take.hide = False
            place.hide = False
            if flag == 'NAVTRANSZERO':
                place.select = False
                Storage.flag = 'EXIT'
            elif flag == 'NAVTRANSFIRST':
                place.select = False
                prevob = Storage.prevob
                nextob = Storage.nextob
                for ob in nextob:
                    ob.hide = False
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in prevob:
                    ob.select = True
                Storage.flag = 'EXIT'
            elif flag == 'NAVTRANSNEXT':
                place.select = False
                prevob = Storage.prevob
                nextob = Storage.nextob
                Storage.selob = prevob
                for ob in nextob:
                    ob.hide = False
                bpy.ops.object.delete('EXEC_DEFAULT')
                for ob in prevob:
                    ob.select = True
                Storage.flag = 'EXIT'
            else:
                print('UNKNOWN FLAG')
                Storage.flag = 'EXIT'
            print('04a_NavTrans_esc_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            print('04a_NavTrans_middle_wheel_any_PASS_THROUGH')
            return {'PASS_THROUGH'}

        print('04a_NavTrans_INVOKED_RUNNING_MODAL', ';', 'flag = ', Storage.flag)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # print('04a_NavTrans_INVOKE_START')
        flag = Storage.flag
        # print('flag = ', flag)
        self.co2d = ((event.mouse_region_x, event.mouse_region_y))
        if flag in ('NAVTRANSZERO', 'NAVTRANSFIRST', 'NAVTRANSNEXT'):
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(DRAW_RunTrans, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            print('04a_run_NAV_INVOKE_a_RUNNING_MODAL', ';', 'flag = ', Storage.flag)
            return {'RUNNING_MODAL'}
        else:
            # print('04a_run_NAV_INVOKE_a_FINISHED',';','flag = ', flag)
            return {'FINISHED'}


# Defining the operator that will enable the return to RunTrans cycle by reseting the 'break' flag:

class NPPCPrepareNext(bpy.types.Operator):
    bl_idname = 'object.np_pc_prepare_next'
    bl_label = 'NP PC Prepare Next'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        print('05_PrepareNext_START', ';', 'flag = ', Storage.flag)
        if Storage.flag == 'RUNTRANSFIRST_break':
            Storage.flag = 'RUNTRANSFIRST'
        if Storage.flag == 'RUNTRANSNEXT_break':
            Storage.flag = 'RUNTRANSNEXT'
        print('05_PrepareNext_FINISHED', ';', 'flag = ', Storage.flag)
        return {'FINISHED'}


# Defining the operator that will collect the necessary data and the generate the array with an input dialogue for number of items:

class NPPCArrayTranslate(bpy.types.Operator):
    bl_idname = "object.np_pc_array_translate"
    bl_label = "NP PC Array Translate"
    bl_options = {'REGISTER', 'INTERNAL'}

    print('06_ArrayTrans_START', ';', 'flag = ', Storage.flag)

    def modal(self, context, event):
        print('06_ArrayTrans_START', ';', 'flag = ', Storage.flag)
        context.area.tag_redraw()
        flag = Storage.flag
        ardict = Storage.ardict
        arob = Storage.arob
        print('ardict = ', ardict)

        if event.type == 'MOUSEMOVE':
            self.co2d = ((event.mouse_region_x, event.mouse_region_y))
            print('04a_NavTrans_mousemove', ';', 'flag = ', Storage.flag)

        elif event.type in ('LEFTMOUSE', 'RIGHTMOUSE') and event.value == 'PRESS':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            Storage.flag = 'EXIT'
            print('06_ArrayTrans_rmb_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.ctrl and event.type == 'WHEELUPMOUSE' or event.type == 'UP_ARROW' and event.value == 'PRESS':
            for ob in arob:
                ar = ardict[ob][0]
                deltavec_start = Vector(ardict[ob][1])
                count = ardict[ob][2]
                if ar.fit_type == 'FIXED_COUNT':
                    ar.count = ar.count + 1
                    count = count + 1
                elif ar.fit_type == 'FIT_LENGTH' and count == 3:
                    ar.fit_type = 'FIXED_COUNT'
                    ar.constant_offset_displace = deltavec_start
                    ar.count = 2
                    count = 2
                elif ar.fit_type == 'FIT_LENGTH' and count > 3:
                    count = count - 1
                    ar.constant_offset_displace.length = ar.fit_length / (count - 1)
                ardict[ob][2] = count
            Storage.fit_type = ar.fit_type
            Storage.count = count
            bpy.context.scene.update()

        elif event.ctrl and event.type == 'WHEELDOWNMOUSE' or event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            for ob in arob:
                ar = ardict[ob][0]
                deltavec_start = Vector(ardict[ob][1])
                count = ardict[ob][2]
                if ar.fit_type == 'FIXED_COUNT' and count > 2:
                    ar.count = ar.count - 1
                    count = count - 1
                elif ar.fit_type == 'FIXED_COUNT' and count == 2:
                    ar.fit_type = 'FIT_LENGTH'
                    ar.fit_length = deltavec_start.length
                    ar.constant_offset_displace.length = ar.fit_length / 2
                    count = 3
                elif ar.fit_type == 'FIT_LENGTH':
                    count = count + 1
                    ar.constant_offset_displace.length = ar.fit_length / (count - 1)
                ardict[ob][2] = count
            Storage.fit_type = ar.fit_type
            Storage.count = count
            bpy.context.scene.update()

        elif event.type in ('RET', 'NUMPAD_ENTER') and event.value == 'PRESS':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            selob = bpy.context.selected_objects
            bpy.ops.object.select_all(action='DESELECT')
            for ob in arob:
                ob.select = True
                bpy.ops.object.modifier_apply(modifier=ardict[ob][0].name)
                ob.select = False
            for ob in selob:
                ob.select = True
            Storage.flag = 'EXIT'
            print('06_ArrayTrans_enter_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.ctrl and event.type == 'TAB' and event.value == 'PRESS':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            if Storage.fit_type == 'FIXED_COUNT':
                value = Storage.ar23d - Storage.ar13d
            else:
                value = (Storage.ar23d - Storage.ar13d) / (Storage.count - 1)
            selob = bpy.context.selected_objects
            bpy.ops.object.select_all(action='DESELECT')
            for ob in arob:
                ob.select = True
                ob.modifiers.remove(ardict[ob][0])
                print('Storage.count', Storage.count)
                for i in range(1, Storage.count):
                    bpy.ops.object.duplicate(linked=True)
                    bpy.ops.transform.translate(value=value)
                bpy.ops.object.select_all(action='DESELECT')
            for ob in selob:
                ob.select = True
            Storage.flag = 'EXIT'
            print('06_ArrayTrans_ctrl_tab_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type == 'TAB' and event.value == 'PRESS':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            if Storage.fit_type == 'FIXED_COUNT':
                value = Storage.ar23d - Storage.ar13d
            else:
                value = (Storage.ar23d - Storage.ar13d) / (Storage.count - 1)
            selob = bpy.context.selected_objects
            bpy.ops.object.select_all(action='DESELECT')
            for ob in arob:
                ob.select = True
                ob.modifiers.remove(ardict[ob][0])
                print('Storage.count', Storage.count)
                for i in range(1, Storage.count):
                    bpy.ops.object.duplicate()
                    bpy.ops.transform.translate(value=value)
                bpy.ops.object.select_all(action='DESELECT')
            for ob in selob:
                ob.select = True
            Storage.flag = 'EXIT'
            print('06_ArrayTrans_tab_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type == 'ESC' and event.value == 'PRESS':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            for ob in arob:
                ob.modifiers.remove(ardict[ob][0])
            Storage.flag = 'EXIT'
            print('06_ArrayTrans_esc_FINISHED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        elif event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            print('06_ArrayTrans_middle_wheel_any_PASS_THROUGH')
            return {'PASS_THROUGH'}

        print('06_ArrayTrans_INVOKED_RUNNING_MODAL', ';', 'flag = ', Storage.flag)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        print('06_ArrayTrans_INVOKE_START')
        flag = Storage.flag
        self.co2d = ((event.mouse_region_x, event.mouse_region_y))
        if flag == 'ARRAYTRANS':
            arob = Storage.arob
            print('deltavec_safe = ', Storage.deltavec_safe)
            ardict = {}
            for ob in arob:
                deltavec = copy.deepcopy(Storage.deltavec_safe)
                print('deltavec = ', deltavec)
                loc, rot, sca = ob.matrix_world.decompose()
                rot = ob.rotation_euler
                rot = rot.to_quaternion()
                sca = ob.scale
                print(loc, rot, sca, ob.matrix_world)
                print('deltavec = ', deltavec)
                deltavec.rotate(rot.conjugated())
                print('sca.length', sca.length)
                deltavec[0] = deltavec[0] / sca[0]
                deltavec[1] = deltavec[1] / sca[1]
                deltavec[2] = deltavec[2] / sca[2]
                print('deltavec = ', deltavec)
                deltavec_trans = deltavec.to_tuple(4)
                arcur = ob.modifiers.new(name='', type='ARRAY')
                arcur.fit_type = 'FIXED_COUNT'
                arcur.use_relative_offset = False
                arcur.use_constant_offset = True
                arcur.constant_offset_displace = deltavec_trans
                arcur.count = 5
                ardict[ob] = []
                ardict[ob].append(arcur)
                ardict[ob].append(deltavec_trans)
                ardict[ob].append(arcur.count)
            Storage.selob = arob
            Storage.ardict = ardict
            Storage.count = 5
            Storage.fit_type = 'FIXED_COUNT'
            selob = Storage.selob
            lenselob = len(selob)
            for i, ob in enumerate(selob):
                ob.select = True
                if i == lenselob - 1:
                    bpy.context.scene.objects.active = ob
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(DRAW_ArrayTrans, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            print('06_ArayTrans_INVOKE_a_RUNNING_MODAL', ';', 'flag = ', Storage.flag)
            return {'RUNNING_MODAL'}
        else:
            print('06_ArrayTrans_INVOKE_DENIED', ';', 'flag = ', Storage.flag)
            return {'FINISHED'}

        # Defining the set of instructions that will draw the OpenGL elements on the screen during the execution of ArrayTrans operator:


def DRAW_ArrayTrans(self, context):
    print('06a_DRAW_ArrayTrans_START', ';', 'flag = ', Storage.flag)

    addon_prefs = context.user_preferences.addons[__name__].preferences
    badge = addon_prefs.badge
    badge_size = addon_prefs.badge_size

    # DRAWING START:
    bgl.glEnable(bgl.GL_BLEND)

    # MOUSE BADGE:
    if badge == True:
        square = [[17, 30], [17, 40], [27, 40], [27, 30]]
        rectangle = [[27, 30], [27, 40], [67, 40], [67, 30]]
        icon = copy.deepcopy(Storage.icon)
        print('icon', icon)
        ipx = 29
        ipy = 33
        for co in square:
            co[0] = round((co[0] * badge_size), 0) - (badge_size * 10) + self.co2d[0]
            co[1] = round((co[1] * badge_size), 0) - (badge_size * 25) + self.co2d[1]
        for co in rectangle:
            co[0] = round((co[0] * badge_size), 0) - (badge_size * 10) + self.co2d[0]
            co[1] = round((co[1] * badge_size), 0) - (badge_size * 25) + self.co2d[1]
        for co in icon:
            co[0] = round((co[0] * badge_size), 0) - (badge_size * 10) + self.co2d[0]
            co[1] = round((co[1] * badge_size), 0) - (badge_size * 25) + self.co2d[1]
        ipx = round((ipx * badge_size), 0) - (badge_size * 10) + self.co2d[0]
        ipy = round((ipy * badge_size), 0) - (badge_size * 25) + self.co2d[1]
        ipsize = int(6 * badge_size)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
        bgl.glBegin(bgl.GL_TRIANGLE_FAN)
        for x, y in square:
            bgl.glVertex2f(x, y)
        bgl.glEnd()
        bgl.glColor4f(0.5, 0.75, 0.0, 1.0)
        bgl.glBegin(bgl.GL_TRIANGLE_FAN)
        for x, y in rectangle:
            bgl.glVertex2f(x, y)
        bgl.glEnd()
        bgl.glColor4f(0.2, 0.15, 0.55, 1.0)
        bgl.glBegin(bgl.GL_TRIANGLE_FAN)
        for x, y in rectangle:
            bgl.glVertex2f(x, (y - (badge_size * 35)))
        bgl.glEnd()
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
        font_id = 0
        blf.position(font_id, ipx, ipy, 0)
        blf.size(font_id, ipsize, 72)
        blf.draw(font_id, 'NAVIGATE')
        blf.position(font_id, ipx, (ipy - (badge_size * 35)), 0)
        blf.size(font_id, ipsize, 72)
        blf.draw(font_id, 'CTRL+SCRL')
        bgl.glColor4f(1, 1, 1, 1)
        blf.position(font_id, ipx, (int(ipy - badge_size * 25)), 0)
        blf.size(font_id, (int(badge_size * 24)), 72)
        if Storage.fit_type == 'FIT_LENGTH':
            blf.draw(font_id, '/' + str(Storage.count))
        else:
            blf.draw(font_id, str(Storage.count))
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x, y in icon:
            bgl.glVertex2f(x, y)
        bgl.glEnd()

        # ON-SCREEN INSTRUCTIONS:
    font_id = 0
    bgl.glColor4f(1, 1, 1, 0.35)
    blf.size(font_id, 88, 72)
    blf.position(font_id, 5, 74, 0)
    blf.draw(font_id, 'N')
    blf.size(font_id, 28, 72)
    blf.position(font_id, 22, 74, 0)
    blf.draw(font_id, 'P')
    blf.enable(font_id, ROTATION)
    bgl.glColor4f(1, 1, 1, 0.40)
    ang = radians(90)
    blf.size(font_id, 19, 72)
    blf.rotation(font_id, ang)
    blf.position(font_id, 78, 73, 0)
    blf.draw(font_id, 'PC 002')
    blf.disable(font_id, ROTATION)

    main = 'SPECIFY NUMBER OF ITEMS IN ARRAY'
    bgl.glColor4f(0, 0.5, 0, 1)
    blf.size(font_id, 11, 72)
    blf.position(font_id, 93, 105, 0)
    blf.draw(font_id, 'MMB, SCROLL - navigate')
    blf.position(font_id, 93, 90, 0)
    blf.draw(font_id, 'CTRL+SCROLL, UPARROW / DOWNARROW - number of items')
    blf.position(font_id, 93, 75, 0)
    blf.draw(font_id,
             'LMB, RMB - confirm and keep array, ENTER - apply as one, TAB - apply as separate, CTRL+TAB - apply as instanced')
    bgl.glColor4f(1, 0, 0, 1)
    blf.position(font_id, 93, 60, 0)
    blf.draw(font_id, 'ESC - cancel array')
    bgl.glColor4f(0.0, 0.0, 0.0, 0.5)
    blf.position(font_id, 93, 124, 0)
    blf.size(font_id, 16, 72)
    blf.draw(font_id, main)
    bgl.glColor4f(1, 1, 1, 1)
    blf.position(font_id, 94, 125, 0)
    blf.size(font_id, 16, 72)
    blf.draw(font_id, main)

    region = context.region
    rv3d = context.region_data
    ar12d = view3d_utils.location_3d_to_region_2d(region, rv3d, Storage.ar13d)
    ar22d = view3d_utils.location_3d_to_region_2d(region, rv3d, Storage.ar23d)
    ardist = Storage.ardist
    ardist_loc = (ar12d + ar22d) / 2

    # ARMARKERS:
    markersize = badge_size * 2.5
    triangle = [[0, 0], [-1, 1], [1, 1]]
    triangle = [[0, 0], [-1, 1], [1, 1]]
    for co in triangle:
        co[0] = int(co[0] * markersize * 3) + ar12d[0]
        co[1] = int(co[1] * markersize * 3) + ar12d[1]
    bgl.glColor4f(0.4, 0.15, 0.75, 1.0)
    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    for x, y in triangle:
        bgl.glVertex2f(x, y)
    bgl.glEnd()
    triangle = [[0, 0], [-1, 1], [1, 1]]
    for co in triangle:
        co[0] = int(co[0] * markersize * 3) + ar22d[0]
        co[1] = int(co[1] * markersize * 3) + ar22d[1]
    bgl.glColor4f(0.4, 0.15, 0.75, 1.0)
    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    for x, y in triangle:
        bgl.glVertex2f(x, y)
    bgl.glEnd()

    # AR NUMERICAL DISTANCE:
    print('ardist = ', ardist, 'ardist_loc = ', ardist_loc)
    bgl.glColor4f(0.4, 0.15, 0.75, 1.0)
    font_id = 0
    blf.size(font_id, 20, 72)
    blf.position(font_id, ardist_loc[0], ardist_loc[1], 0)
    blf.draw(font_id, ardist)

    # DRAWING END:
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    print('06a_DRAW_ArrayTrans_FINISHED', ';', 'flag = ', Storage.flag)


# Deleting the helpers after successful translation, reseting all viewport options and reselecting previously selected objects:

class NPPCCleanExit(bpy.types.Operator):
    bl_idname = "object.np_pc_clean_exit"
    bl_label = "NP PC Clean Exit"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        print('07_CleanExit_START', ';', 'flag = ', Storage.flag)
        flag = Storage.flag
        selob = Storage.selob
        take = Storage.take
        place = Storage.place
        bpy.ops.object.select_all(action='DESELECT')
        take.select = True
        place.select = True
        bpy.ops.object.delete('EXEC_DEFAULT')
        lenselob = len(selob)
        for i, ob in enumerate(selob):
            ob.select = True
            if i == lenselob - 1:
                bpy.context.scene.objects.active = ob
        Storage.take = None
        Storage.place = None
        Storage.takeloc3d = (0.0, 0.0, 0.0)
        Storage.placeloc3d = (0.0, 0.0, 0.0)
        Storage.dist = None
        Storage.mode = 'MOVE'
        Storage.flag = 'NONE'
        Storage.ardict = {}
        Storage.deltavec = Vector((0, 0, 0))
        Storage.deltavec_safe = Vector((0, 0, 0))
        bpy.context.tool_settings.use_snap = Storage.use_snap
        bpy.context.tool_settings.snap_element = Storage.snap_element
        bpy.context.tool_settings.snap_target = Storage.snap_target
        bpy.context.space_data.pivot_point = Storage.pivot_point
        bpy.context.space_data.transform_orientation = Storage.trans_orient
        # if Storage.acob is not None:
        # bpy.context.scene.objects.active = Storage.acob
        # bpy.ops.object.mode_set(mode = Storage.edit_mode)

        print('07_CleanExit_FINISHED', ';', 'flag = ', Storage.flag)
        return {'FINISHED'}


# Defining the settings of the addon in the User preferences / addons tab:

class NPPCPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    dist_scale = bpy.props.FloatProperty(
        name='Unit scale',
        description='Distance multiplier (for example, for cm use 100)',
        default=100,
        min=0,
        step=1,
        precision=3)

    suffix = bpy.props.EnumProperty(
        name='Unit suffix',
        items=(("'", "'", ''), ('"', '"', ''), ('thou', 'thou', ''), ('km', 'km', ''), ('m', 'm', ''), ('cm', 'cm', ''),
               ('mm', 'mm', ''), ('nm', 'nm', ''), ('None', 'None', '')),
        default='cm',
        description='Add a unit extension after the numerical distance ')

    badge = bpy.props.BoolProperty(
        name='Mouse badge',
        description='Use the graphical badge near the mouse cursor',
        default=True)

    badge_size = bpy.props.FloatProperty(
        name='size',
        description='Size of the mouse badge, the default is 2.0',
        default=2,
        min=0.5,
        step=10,
        precision=1)

    col_line_main_DEF = bpy.props.BoolProperty(
        name='Default',
        description='Use the default color',
        default=True)

    col_line_shadow_DEF = bpy.props.BoolProperty(
        name='Default',
        description='Use the default color',
        default=True)

    col_num_main_DEF = bpy.props.BoolProperty(
        name='Default',
        description='Use the default color',
        default=True)

    col_num_shadow_DEF = bpy.props.BoolProperty(
        name='Default',
        description='Use the default color',
        default=True)

    col_line_main = bpy.props.FloatVectorProperty(name='', default=(1.0, 1.0, 1.0, 1.0), size=4, subtype="COLOR", min=0,
                                                  max=1,
                                                  description='Color of the measurement line, to disable it set alpha to 0.0')

    col_line_shadow = bpy.props.FloatVectorProperty(name='', default=(0.1, 0.1, 0.1, 0.25), size=4, subtype="COLOR",
                                                    min=0, max=1,
                                                    description='Color of the line shadow, to disable it set alpha to 0.0')

    col_num_main = bpy.props.FloatVectorProperty(name='', default=(0.1, 0.1, 0.1, 0.75), size=4, subtype="COLOR", min=0,
                                                 max=1,
                                                 description='Color of the number, to disable it set alpha to 0.0')

    col_num_shadow = bpy.props.FloatVectorProperty(name='', default=(1.0, 1.0, 1.0, 1.0), size=4, subtype="COLOR",
                                                   min=0, max=1,
                                                   description='Color of the number shadow, to disable it set alpha to 0.0')

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column()
        col.prop(self, "dist_scale")
        col = split.column()
        col.prop(self, "suffix")
        split = layout.split()
        col = split.column()
        col.label(text='Line Main COLOR')
        col.prop(self, "col_line_main_DEF")
        if self.col_line_main_DEF == False:
            col.prop(self, "col_line_main")
        col = split.column()
        col.label(text='Line Shadow COLOR')
        col.prop(self, "col_line_shadow_DEF")
        if self.col_line_shadow_DEF == False:
            col.prop(self, "col_line_shadow")
        col = split.column()
        col.label(text='Numerical Main COLOR')
        col.prop(self, "col_num_main_DEF")
        if self.col_num_main_DEF == False:
            col.prop(self, "col_num_main")
        col = split.column()
        col.label(text='Numerical Shadow COLOR')
        col.prop(self, "col_num_shadow_DEF")
        if self.col_num_shadow_DEF == False:
            col.prop(self, "col_num_shadow")
        split = layout.split()
        col = split.column()
        col.prop(self, "badge")
        col = split.column()
        if self.badge == True:
            col.prop(self, "badge_size")
        col = split.column()
        col = split.column()


# This is the actual addon process, the algorithm that defines the order of operator activation inside the main macro:
def register():
    bpy.utils.register_class(NPPCPreferences)
    bpy.utils.register_module(__name__)
    bpy.app.handlers.scene_update_post.append(scene_update_NPPC)

    NPAnchorTranslate007.define('OBJECT_OT_np_at_get_selection')
    NPAnchorTranslate007.define('OBJECT_OT_np_at_activate_anchor')
    NPAnchorTranslate007.define('OBJECT_OT_np_at_run_translate')
    NPAnchorTranslate007.define('OBJECT_OT_np_at_reselect_stored')
    NPAnchorTranslate007.define('OBJECT_OT_np_at_run_translate')
    NPAnchorTranslate007.define('OBJECT_OT_np_at_delete_anchor')

    NPPointCopy002.define('OBJECT_OT_np_pc_read_context')
    NPPointCopy002.define('OBJECT_OT_np_pc_read_mouseloc')
    NPPointCopy002.define('OBJECT_OT_np_pc_add_helpers')
    for i in range(1, 50):
        for i in range(1, 10):
            NPPointCopy002.define('OBJECT_OT_np_pc_run_trans')
            NPPointCopy002.define('OBJECT_OT_np_pc_nav_trans')
        NPPointCopy002.define('OBJECT_OT_np_pc_prepare_next')
    NPPointCopy002.define('OBJECT_OT_np_pc_array_translate')
    NPPointCopy002.define('OBJECT_OT_np_pc_clean_exit')


def unregister():
    bpy.utils.unregister_class(NPPCPreferences)
    bpy.utils.unregister_module(__name__)
    # bpy.app.handlers.scene_update_post.remove(scene_update)


if __name__ == "__main__":
    # __name__ = "NP_scripts"
    register()
