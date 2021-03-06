"""
Real pose copy addon.

Encodes the matrices of the selected bones in JSON, and places that on the
clipboard. This can be pasted as text into a text file, or, using this same
addon, pasted onto another rig in another Blend file. Bones are mapepd
by name.
"""

bl_info = {
    'name': 'Real pose copy',
    'author': 'Sybren A. Stüvel',
    'version': (1, 0),
    'blender': (2, 77, 0),
    'location': 'Tools Panel > Pose Tools',
    'category': 'Animation',
}

from collections import defaultdict
import json

import bpy
from mathutils import Matrix
from bpy.types import Menu, Panel, UIList


class POSE_OT_copy_as_json(bpy.types.Operator):
    bl_idname = 'pose.copy_as_json'
    bl_label = 'Copy pose as JSON'
    bl_description = 'Copies the matrices of the selected bones as JSON onto the clipboard'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        bone_data = defaultdict(dict)
        for bone in context.selected_pose_bones:
            # Convert matrix to list-of-tuples.
            vals = [tuple(v) for v in bone.matrix_basis]
            bone_data[bone.name]['matrix_basis'] = vals

        context.window_manager.clipboard = json.dumps(bone_data)
        self.report({'INFO'}, 'Selected pose bone matrices copied.')

        return {'FINISHED'}


class POSE_OT_paste_from_json(bpy.types.Operator):
    bl_idname = 'pose.paste_from_json'
    bl_label = 'Paste pose from JSON'
    bl_description = 'Copies the matrices of the selected bones as JSON onto the clipboard'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        # Parse the JSON
        the_json = context.window_manager.clipboard
        try:
            bone_data = json.loads(the_json)
        except ValueError as ex:
            self.report({'ERROR'}, 'No valid JSON on clipboard: %s' % ex)
            return {'CANCELLED'}

        # Apply it to the named bones.
        bones = context.active_object.pose.bones
        for bone_name, data in bone_data.items():
            if bone_name not in bones:
                self.report({'WARNING'}, 'Ignoring matrix for unknown bone %r' % bone_name)
                continue

            bone = bones[bone_name]
            bone.matrix_basis = Matrix(data['matrix_basis'])

        self.report({'INFO'}, 'Pose bone matrices pasted.')
        return {'FINISHED'}


def render_panel(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Real Copy Pose:")
        row = col.row(align=True)
        row.operator("pose.copy_as_json", text="Copy as JSON")
        row.operator("pose.paste_from_json", text="Paste from JSON")


def register():
    from bl_ui.space_view3d_toolbar import VIEW3D_PT_tools_posemode

    bpy.utils.register_class(POSE_OT_copy_as_json)
    bpy.utils.register_class(POSE_OT_paste_from_json)
    VIEW3D_PT_tools_posemode.append(render_panel)


def unregister():
    from bl_ui.space_view3d_toolbar import VIEW3D_PT_tools_posemode

    bpy.utils.unregister_class(POSE_OT_copy_as_json)
    bpy.utils.unregister_class(POSE_OT_paste_from_json)
    VIEW3D_PT_tools_posemode.remove(render_panel)
