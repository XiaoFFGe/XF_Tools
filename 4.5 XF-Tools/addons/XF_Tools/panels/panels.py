import bpy

from ..operators.operators import BatchPassShapeKeysOperator, RestoreShapeKeyPositionsOperator, \
    MMD_RigidBody_Selection_to_the_Skeleton, MMD_RigidBody_Adjust_Mass_Level, \
    MMD_Bone_Chain_Select_Rigid_Body_Constraint, Merge_Bone_Weights, set_child_bone_to_child, \
    RMD_RigidBody_Chain_Connection, Fix_Bone_Chain_End, Merge_Bone_Weights_Child, Merge_Bone_Weights_Chain
from ....common.i18n.i18n import i18n
from ....common.types.framework import reg_order
import bmesh


class BasePanel(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "XF Tools"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True


# 骨骼工具
@ reg_order(0)
class Bone_Tools_Panel(BasePanel, bpy.types.Panel):
    bl_label = "Bone Tools"
    bl_idname = "OBJECT_PT_bone_tools"

    def draw(self, context):
        layout = self.layout

        layout.label(text=i18n("Weight:"))
        layout.operator(Merge_Bone_Weights.bl_idname)
        layout.operator(Merge_Bone_Weights_Child.bl_idname)
        layout.operator(Merge_Bone_Weights_Chain.bl_idname)

        layout.label(text=i18n("Edit:"))
        layout.operator(set_child_bone_to_child.bl_idname)
        layout.operator(Fix_Bone_Chain_End.bl_idname)

# MMD 刚体工具
@reg_order(1)
class MMD_RigidBody_Panel(BasePanel, bpy.types.Panel):
    bl_label = "MMD Rigid Body Tools"
    bl_idname = "OBJECT_PT_mmd_rigid_body"

    def draw(self, context):

        layout = self.layout

        layout.label(text=i18n("Rigid Body Selection:"))

        layout.operator(MMD_RigidBody_Selection_to_the_Skeleton.bl_idname)
        layout.operator(MMD_Bone_Chain_Select_Rigid_Body_Constraint.bl_idname)

        layout.label(text=i18n("Rigid Body Mass:"))
        if context.active_object:
            layout.prop(context.active_object.xffg_mmd_rigid_body_property, "rigid_body_mass", text=i18n("Rigid Body Mass"))
            layout.prop(context.active_object.xffg_mmd_rigid_body_property, "rigid_body_mass_offset", text=i18n("Rigid Body Mass Offset"))
            layout.prop(context.active_object.xffg_mmd_rigid_body_property, "rigid_body_mass_decay", text=i18n("Rigid Body Mass Decay"))
        layout.operator(MMD_RigidBody_Adjust_Mass_Level.bl_idname)

        layout.label(text=i18n("Rigid-body loom:"))
        layout.operator(RMD_RigidBody_Chain_Connection.bl_idname)

@reg_order(2)
class RestoreShapeKeyPositionsPanel(BasePanel, bpy.types.Panel):
    bl_label = "Restore form bond vertex position"
    bl_idname = "OBJECT_PT_restore_shape_key_positions"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # 选中的模型
        layout.label(text="选中的模型：" + obj.name if obj else "未选中模型")
        # 在編编辑模式下选中的顶点有多少个
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_vertices = [v for v in bm.verts if v.select]
            layout.label(text="选中的顶点数：" + str(len(selected_vertices)))

        # 参考形态键
        if obj:
            layout.prop(obj.xffg_key_property, "reference_shape_key")

        # 恢复形态键顶点位置按钮
        layout.operator(RestoreShapeKeyPositionsOperator.bl_idname)

@reg_order(3)
class BatchPassShapeKeysPanel(BasePanel, bpy.types.Panel):
    bl_label = "Batch pass shape keys"
    bl_idname = "OBJECT_PT_batch_pass_shape_keys"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        selected_objects = bpy.context.selected_objects

        # 参考模型
        layout.label(text=i18n("Reference model:") + selected_objects[0].name if selected_objects else i18n("No reference model"))
        # 选中的模型
        layout.label(text=i18n("Selected model:") + obj.name if obj else i18n("No selected model"))
        # 批量传递形状键按钮
        layout.operator(BatchPassShapeKeysOperator.bl_idname)