import bpy
import bmesh
from Cython.Compiler.Code import modifier_output_mapper
from addons.XF_Tools.operators import *

class RestoreShapeKeyPositionsOperator(bpy.types.Operator):
    bl_idname = "object.restore_shape_key_positions"
    bl_label = "Restore form bond vertex position"
    bl_description = "恢复选中顶点在不同形态键之间的位置"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT'


    def execute(self, context):

        global reference_key_name
        global current_key_name

        # 获取当前活动对象
        obj = context.active_object
        # 参考形态键
        reference_key_name = obj.xffg_key_property.reference_shape_key

        # 当前形态键
        for idx, shape_key in enumerate(obj.data.shape_keys.key_blocks):
            if idx == obj.active_shape_key_index:
                current_key_name = shape_key.name
                break

        print(f"参考形态键: {reference_key_name}", f"当前形态键: {current_key_name}")

        # 存储参考形态键下选中的顶点的位置
        vertex_dict = {}

        # 设置当前形态键为参考形态键
        for idx, shape_key in enumerate(obj.data.shape_keys.key_blocks):
            if shape_key.name == reference_key_name:
                obj.active_shape_key_index = idx
                break # 找到参考形态键后跳出循环

        bpy.context.view_layer.update() # 更新视图层

        # 从编辑模式下的网格获取BMesh对象
        bm = bmesh.from_edit_mesh(obj.data)

        for v in bm.verts:
            if v.select:
                vertex_dict[v.index] = v.co.copy()

        # 释放BMesh资源
        bm.free()

        # 设置当前形态键为current_key_name
        for idx, shape_key in enumerate(obj.data.shape_keys.key_blocks):
            if shape_key.name == current_key_name:
                obj.active_shape_key_index = idx
                break # 找到当前形态键后跳出循环

        bpy.context.view_layer.update() # 更新视图层

        # 重新创建BMesh对象
        bm = bmesh.from_edit_mesh(obj.data)

        # 恢复选中顶点的位置
        for v in bm.verts:
            if v.index in vertex_dict:
                v.co = vertex_dict[v.index]

        bmesh.update_edit_mesh(obj.data) # 更新编辑模式下的网格

        return {'FINISHED'}

# 批量传递形状键
class BatchPassShapeKeysOperator(bpy.types.Operator):
    bl_idname = "object.batch_pass_shape_keys"
    bl_label = "Batch pass shape keys"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 获取活动对象
        a_obj = bpy.context.active_object
        if not a_obj or a_obj.type != 'MESH':
            raise ValueError("活动对象必须是网格对象")

        # 获取选中对象列表
        selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH' and obj != a_obj]

        if not selected_objects:
            raise ValueError("请选中至少一个带有形状键的网格对象")

        # 选中的对象
        b_obj = selected_objects[0]

        # 检查目标对象是否有形状键
        b_obj_key = b_obj.data.shape_keys
        if not b_obj_key or not b_obj_key.key_blocks:
            raise ValueError(f"对象 {b_obj.name} 没有形状键")

        # 传递形状键
        for i, key in enumerate(b_obj_key.key_blocks):
            print(f"正在传递形状键: {key.name} ({i + 1}/{len(b_obj_key.key_blocks)})")

            # 设置源对象的活动形状键
            bpy.context.view_layer.objects.active = b_obj
            b_obj.active_shape_key_index = i

            # 切换到目标对象并传递形状键
            bpy.context.view_layer.objects.active = a_obj
            bpy.ops.object.shape_key_transfer()

        print("形状键传递完成!")

        return {'FINISHED'}

# mmd骨骼对应刚体选择
class MMD_RigidBody_Selection_to_the_Skeleton(bpy.types.Operator):
    bl_idname = "object.mmd_rigid_body_selection_to_the_skeleton"
    bl_label = "MMD Rigid Body Selection Corresponding to the Skeleton"
    bl_description = "根据MMD模型的骨骼选择对应的刚体"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # 获取当前活动对象
        context_arm = bpy.context.active_object

        # 获取选中骨骼列表
        selected_bones = [bone for bone in context_arm.data.bones if bone.select]

        for bone in selected_bones:

            # 获取当前活动骨骼
            context_bone = context_arm.data.bones[bone.name]

            # 获取当前活动骨骼子级
            context_bone_children = context_bone.children

            # 列表长度
            context_bone_children_len = len(context_bone_children)


            # 处理当前活动骨骼
            for rigid_body in bpy.data.objects:
                if rigid_body.rigid_body is not None:
                    if rigid_body.mmd_rigid.bone == context_bone.name:
                        # 选择rigid_body
                        rigid_body.select_set(True)
                        print(context_bone.name)
                        # 只处理第一个
                        break

            # 处理当前活动骨骼子级
            while context_bone_children_len > 0:
                context_bone = context_bone_children[0]
                context_bone_children = context_bone.children
                context_bone_children_len = len(context_bone_children)

                for rigid_body in bpy.data.objects:
                    if rigid_body.rigid_body is not None:
                        if context_bone_children:
                            if rigid_body.mmd_rigid.bone == context_bone.name:
                                # 选择rigid_body
                                rigid_body.select_set(True)
                                print(context_bone.name)
                                # 只处理第一个
                                break
                        else:
                            if rigid_body.mmd_rigid.bone == context_bone.name:
                                # 选择rigid_body
                                rigid_body.select_set(True)
                                print(context_bone.name)
                                # 只处理第一个
                                break
        print('-' * 20)

        context_arm.select_set(False)

        return {'FINISHED'}

# 按MMD骨骼链选择刚体约束
class MMD_Bone_Chain_Select_Rigid_Body_Constraint(bpy.types.Operator):
    bl_idname = "object.mmd_bone_chain_select_rigid_body_constraint"
    bl_label = "MMD Bone Chain Select Rigid Body Constraint"
    bl_description = "根据MMD模型的骨骼链选择对应的刚体约束"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 获取当前活动对象
        context_arm = bpy.context.active_object

        # 获取选中骨骼列表
        selected_bones = [bone for bone in context_arm.data.bones if bone.select]

        for bone in selected_bones:

            # 获取当前活动骨骼
            context_bone = context_arm.data.bones[bone.name]

            # 获取当前活动骨骼子级
            context_bone_children = context_bone.children

            # 列表长度
            context_bone_children_len = len(context_bone_children)

            # 处理当前活动骨骼
            for rigid_body in bpy.data.objects:
                if rigid_body.rigid_body is not None:
                    if rigid_body.mmd_rigid.bone == context_bone.name:
                        for joint in bpy.data.objects:
                                            if joint.rigid_body_constraint:
                                                 if joint.rigid_body_constraint.object2:
                                                      if joint.rigid_body_constraint.object2.name == rigid_body.name:
                                                         joint.select_set(True)
                        print(context_bone.name)
                        # 只处理第一个
                        break

            # 处理当前活动骨骼子级
            while context_bone_children_len > 0:
                context_bone = context_bone_children[0]
                context_bone_children = context_bone.children
                context_bone_children_len = len(context_bone_children)

                for rigid_body in bpy.data.objects:
                    if rigid_body.rigid_body is not None:
                        if context_bone_children:
                            if rigid_body.mmd_rigid.bone == context_bone.name:

                                for joint in bpy.data.objects:
                                            if joint.rigid_body_constraint:
                                                 if joint.rigid_body_constraint.object1:
                                                      if joint.rigid_body_constraint.object1.name == rigid_body.name:
                                                         joint.select_set(True)

                                print(context_bone.name)
                                # 只处理第一个
                                break
                        else:
                            if rigid_body.mmd_rigid.bone == context_bone.name:

                                for joint in bpy.data.objects:
                                    if joint.rigid_body_constraint:
                                         if joint.rigid_body_constraint.object2:
                                              if joint.rigid_body_constraint.object2.name == rigid_body.name:
                                                 joint.select_set(True)

                                print(context_bone.name)
                                # 只处理第一个
                                break
        print('-' * 20)

        context_arm.select_set(False)

        return {'FINISHED'}

# mmd刚体质量层级调整
class MMD_RigidBody_Adjust_Mass_Level(bpy.types.Operator):

    bl_idname = "object.mmd_rigid_body_adjust_mass_level"
    bl_label = "MMD Rigid Body Adjust Mass Level"
    bl_description = "根据MMD模型的骨骼调整对应的刚体质量层级"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # 获取当前活动对象
        context_arm = bpy.context.active_object

        # 获取刚体质量
        mass = context_arm.xffg_mmd_rigid_body_property.rigid_body_mass
        # 获取刚体质量偏差值
        mass_offset = context_arm.xffg_mmd_rigid_body_property.rigid_body_mass_offset

        # 获取选中骨骼列表
        selected_bones = [bone for bone in context_arm.data.bones if bone.select]

        for bone in selected_bones:

            # 获取当前活动骨骼
            context_bone = bone

            # 获取当前活动骨骼子级
            context_bone_children = context_bone.children

            # 列表长度
            context_bone_children_len = len(context_bone_children)

            # 处理当前活动骨骼
            for rigid_body in bpy.data.objects:
                if rigid_body.rigid_body is not None:
                    if rigid_body.mmd_rigid.bone == context_bone.name:
                        rigid_body.rigid_body.mass = mass
                        print(context_bone.name)
                        # 只处理第一个
                        break

            y = 1

            # 处理当前活动骨骼子级
            while context_bone_children_len > 0:
                context_bone = context_bone_children[0]
                context_bone_children = context_bone.children
                context_bone_children_len = len(context_bone_children)
                y += context_arm.xffg_mmd_rigid_body_property.rigid_body_mass_decay

                new_mass = (mass + mass_offset) / y

                for rigid_body in bpy.data.objects:
                    if rigid_body.rigid_body is not None:
                        if context_bone_children:
                            if rigid_body.mmd_rigid.bone == context_bone.name:
                                rigid_body.rigid_body.mass = new_mass
                                print(context_bone_children[0].name, new_mass)
                                # 只处理第一个
                                break
                        else:
                            if rigid_body.mmd_rigid.bone == context_bone.name:
                                rigid_body.rigid_body.mass = new_mass
                                print(context_bone.name, new_mass)
                                # 只处理第一个
                                break

        print('-' * 20)

        return {'FINISHED'}

# 选择子级骨骼的子级
class set_child_bone_to_child(bpy.types.Operator):
    bl_idname = "object.set_child_bone_to_child"
    bl_label = "Set Child Bone to Child"
    bl_description = "选择子级骨骼的子级"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # 获取当前活动对象
        context_arm = bpy.context.active_object

        # 获取选中骨骼列表
        selected_bones = ot_set_edit_bones(context_arm)

        for bone in selected_bones:

            # 获取当前活动骨骼
            context_bone = bone

            # 获取当前活动骨骼子级
            context_bone_children = context_bone.children

            # 列表长度
            context_bone_children_len = len(context_bone_children)

            if context_bone_children and context_bone_children[0].children:
                # 处理当前活动骨骼
                Child2 = context_bone_children[0].children[0]
                Child2.select = True

                # 处理当前活动骨骼子级
                while context_bone_children_len > 0:

                    if context_bone_children[0].children:
                        context_bone = context_bone_children[0].children[0]

                        context_bone_children = context_bone.children
                        context_bone_children_len = len(context_bone_children)

                        if context_bone_children and context_bone_children[0].children:
                            # 处理当前活动骨骼
                            Child2 = context_bone_children[0].children[0]
                            if Child2.children:
                                Child2.select = True
                    else:
                        # 如果没有子骨骼，退出循环
                        break


        return {'FINISHED'}

# 合并子级骨骼权重
class Merge_Bone_Weights_Child(bpy.types.Operator):

    bl_idname = "object.merge_bone_weights_child"
    bl_label = "Merge Bone Weights Child"
    bl_description = "合并选中的子级骨骼权重"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.mode_set(mode='EDIT')

        # 获取当前活动对象
        context_arm = bpy.context.active_object

        selected_objects = bpy.context.selected_objects

        if context_arm in selected_objects:
            selected_objects.remove(context_arm) # 移除当前活动对象

        if not selected_objects:
            self.report({'ERROR'}, "请选中网格模型")
            return {'CANCELLED'}

        # 获取选中骨骼列表
        selected_bone_names = ot_set_edit_bones(context_arm, bone_names=True)

        print(selected_bone_names)

        for bone_name in selected_bone_names:

            # 获取当前活动骨骼
            context_bone = context_arm.data.edit_bones.get(bone_name)

            if context_bone and context_bone.children:

                # 获取当前活动骨骼子级
                context_bone_children = context_bone.children

                merge_bone_weights(context_bone, context_bone_children[0], context_arm, selected_objects, tail=True)

        return {'FINISHED'}

# 合并骨骼权重
class Merge_Bone_Weights(bpy.types.Operator):

    bl_idname = "object.merge_bone_weights"
    bl_label = "Merge Bone Weights"
    bl_description = "合并骨骼权重"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.mode_set(mode='EDIT')

        # 获取当前活动对象
        context_arm = bpy.context.active_object

        selected_objects = bpy.context.selected_objects

        if context_arm in selected_objects:
            selected_objects.remove(context_arm)  # 移除当前活动对象

        if not selected_objects:
            self.report({'ERROR'}, "请选中网格模型")
            return {'CANCELLED'}

        context_bone = bpy.context.active_bone

        selected_bones = ot_set_edit_bones(context_arm)

        if context_bone:
            selected_bones.remove(context_bone)
            merge_bone_weights(context_bone, selected_bones[0], context_arm, selected_objects)

        return {'FINISHED'}

# 按骨骼链合并骨骼权重
class Merge_Bone_Weights_Chain(bpy.types.Operator):

    bl_idname = "object.merge_bone_weights_chain"
    bl_label = "Merge Bone Weights Chain"
    bl_description = "按骨骼链合并骨骼权重"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    midpoint: bpy.props.BoolProperty(
        name="Midpoint",
        description="是否使用中点",
        default=True
    )

    def execute(self, context):

        bpy.ops.object.mode_set(mode='EDIT')

        # 获取当前活动对象
        context_arm = bpy.context.active_object

        selected_objects = bpy.context.selected_objects

        if context_arm in selected_objects:
            selected_objects.remove(context_arm)  # 移除当前活动对象

        if not selected_objects:
            self.report({'ERROR'}, "请选中网格模型")
            return {'CANCELLED'}

        # 获取选中骨骼列表
        selected_bones = ot_set_edit_bones(context_arm)
        # 获取骨骼链
        bone_chains = get_bone_chains(context_arm, ot_set_edit_bones(context_arm, bone_names=True))
        # 获取当前活动骨骼
        context_bone = bpy.context.active_bone

        selected_bones.remove(context_bone)

        # 排序骨骼链
        for chain in bone_chains:
            if context_bone.name in chain:
                bone_chains.remove(chain)
                bone_chains.insert(0, chain)

                i = False

                for chain1 in bone_chains:
                    if len(chain1) > len(chain):
                        i = True
                        break
                if i:
                    # 最长骨骼链
                    max_chain = max(bone_chains, key=len)
                    bone_chains.remove(max_chain)
                    bone_chains.insert(0, max_chain)
                break # 退出循环

        loom = ot_connect_rigid_body_chain(bone_chains, bone_mode=True) # 连接骨骼链

        for bone1_name, bone2_name in loom.items():
            merge_bone_weights(context_arm.data.edit_bones.get(bone1_name),
                               context_arm.data.edit_bones.get(bone2_name),
                               context_arm, selected_objects,
                               midpoint=self.midpoint)

        return {'FINISHED'}

class RMD_RigidBody_Chain_Connection(bpy.types.Operator):
    bl_idname = "object.rmd_rigid_body_chain_connection"
    bl_label = "Rigid Body Chain Connection"
    bl_description = "连接刚体链"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    # 闭合刚体链
    close_chain: bpy.props.BoolProperty(
        name="闭合刚体链",
        description="是否闭合刚体链",
        default=False
    )

    use_bone_rotation: bpy.props.BoolProperty(
        name="使用骨骼旋转",
        description="是否使用骨骼旋转",
        default=False
    )

    limit_linear_lower: bpy.props.FloatVectorProperty(
        name="线性限制下限",
        description="线性限制下限",
        default=(-0.1, -0.1, -0.1),
        min=-100.0,
        max=100.0,
        step=0.1,
        precision=2,
        subtype='XYZ_LENGTH'
    )

    limit_linear_upper: bpy.props.FloatVectorProperty(
        name="线性限制上限",
        description="线性限制上限",
        default=(0.1, 0.1, 0.1),
        min=-100.0,
        max=100.0,
        step=0.1,
        precision=2,
        subtype='XYZ_LENGTH'
    )

    limit_angular_lower: bpy.props.FloatVectorProperty(
        name="角限制下限",
        description="角限制下限",
        default=(-10*(3.1415926/180), -10*(3.1415926/180), -20*(3.1415926/180)),
        min=-100.0,
        max=100.0,
        step=0.1,
        precision=2,
        subtype='EULER',
    )

    limit_angular_upper: bpy.props.FloatVectorProperty(
        name="角限制上限",
        description="角限制上限",
        default=(10*(3.1415926/180), 10*(3.1415926/180), 20*(3.1415926/180)),
        min=-100.0,
        max=100.0,
        step=0.1,
        precision=2,
        subtype='EULER',
    )

    spring_linear: bpy.props.FloatVectorProperty(
        name="线性弹簧系数",
        description="线性弹簧系数",
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=100.0,
        step=0.1,
        precision=2,
        subtype='XYZ_LENGTH'
    )

    spring_angular: bpy.props.FloatVectorProperty(
        name="角弹簧系数",
        description="角弹簧系数",
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=100.0,
        step=0.1,
        precision=2,
        subtype='EULER',
    )

    def execute(self, context):

        global armature

        bpy.ops.object.mode_set(mode='OBJECT')

        active_obj = bpy.context.active_object

        # 只能循环50次, 防止无限循环
        i = 50

        # 循环, 直到找到MMD根对象
        while active_obj.mmd_type != 'ROOT':
            # 循环次数减一
            i -= 1
            if i <= 0:
                self.report({'ERROR'}, f"未找到MMD根对象")
                return {'CANCELLED'}
            active_obj = active_obj.parent

        # 检查活动物体是否是MMD模型
        if active_obj.mmd_type != 'ROOT':
            self.report({'ERROR'}, "请选择MMD根对象")
            return {'CANCELLED'}

        root =  active_obj

        root.mmr_bone.mmr_type = "ROOT"

        for child in root.children:
            # type是"armature"
            if child.type == 'ARMATURE':
                armature = child

        sel_objects = bpy.context.selected_objects

        bone_rigid_body_name = []

        for obj in sel_objects:
            if obj.rigid_body:
                if obj.mmd_rigid.bone:
                    bone_rigid_body_name.append(obj.mmd_rigid.bone)

        bone_chains = get_bone_chains(armature, bone_rigid_body_name) # 获取骨骼链

        loom = ot_connect_rigid_body_chain(bone_chains, sel_objects=sel_objects, close_chain=self.close_chain)

        print(loom)

        for obj_name1, obj_name2 in loom.items():

            rigid_body = bpy.data.objects.get(obj_name1)
            rigid_body2 = bpy.data.objects.get(obj_name2)

            if rigid_body and rigid_body2:
                bpy.ops.object.select_all(action='DESELECT')
                rigid_body.select_set(True)
                rigid_body2.select_set(True)
                bpy.context.view_layer.objects.active = rigid_body2

                bpy.ops.mmd_tools.joint_add(
                    limit_linear_lower=self.limit_linear_lower,
                    limit_linear_upper=self.limit_linear_upper,
                    limit_angular_lower=self.limit_angular_lower,
                    limit_angular_upper=self.limit_angular_upper,
                    spring_linear=self.spring_linear,
                    spring_angular=self.spring_angular,
                    use_bone_rotation=self.use_bone_rotation,
                )

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, width=250)
        return {'RUNNING_MODAL'}

# 修复骨骼链末端
class Fix_Bone_Chain_End(bpy.types.Operator):
    bl_idname = "object.fix_bone_chain_end"
    bl_label = "Fix Bone Chain End"
    bl_description = "修复骨骼链末端"

    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        arm_obj = bpy.context.active_object
        set_bones = ot_set_edit_bones(arm_obj, bone_names=True)
        bone_chains = get_bone_chains(arm_obj, set_bones)

        for chain in bone_chains:

            if len(chain) > 1:
                # 末端骨骼
                end_bone = arm_obj.data.edit_bones.get(chain[-1])
                if end_bone:
                    # 末端骨骼的父级
                    end_bone_parent = end_bone.parent
                    if end_bone_parent:
                        calculate_tail_coordinates(end_bone_parent.name, end_bone.name,
                                                   arm_obj.name,
                                                   scale=False,
                                                   distance=True,
                                                   lengths=True)

        return {'FINISHED'}
