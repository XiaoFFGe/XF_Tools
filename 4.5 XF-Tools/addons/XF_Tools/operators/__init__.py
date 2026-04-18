from itertools import zip_longest

import bpy
import numpy as np


def get_bone_chains(armature, bone_names):
    root_bones = []
    bone_chains = []
    # 找根骨
    for bone_name in bone_names:
        bone = armature.data.bones.get(bone_name)
        if bone:
            if bone.parent:
                if not bone.parent.name in bone_names:
                    root_bones.append(bone.name)
    # 排序骨骼链
    for bone_name in root_bones:
        chain = []
        bone = armature.data.bones.get(bone_name)
        chain.append(bone.name)
        if bone:
            while bone.children:  # 有子级
                bone = armature.data.bones.get(bone.children[0].name)
                if bone.name in bone_names:
                    chain.append(bone.name)
        bone_chains.append(chain)
    return bone_chains

def ot_set_edit_bones(armature, bone_names=False):
    set_bones = []
    for bone in armature.data.edit_bones:
        if bone.select:
            if bone_names:
                set_bones.append(bone.name)
            else:
                set_bones.append(bone)
    return set_bones

def ot_set_pose_bones(armature, bone_names=False):
    set_bones = []
    for bone in armature.pose.bones:
        if bone.select:
            if bone_names:
                set_bones.append(bone.name)
            else:
                set_bones.append(bone)
    return set_bones

def calculate_tail_coordinates(bone_name, bone_name2, arm_obj_name, scale=True, distance=False, lengths=False):
    arm = bpy.data.objects.get(arm_obj_name)

    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')  # 切到编辑模式

    # 确保骨骼存在
    if bone_name not in arm.data.edit_bones or bone_name2 not in arm.data.edit_bones:
        print(f"骨骼 {bone_name} 或 {bone_name2} 不存在于骨架 {arm_obj_name} 中")
        return

    bone1 = arm.data.edit_bones.get(bone_name)
    bone2 = arm.data.edit_bones.get(bone_name2)

    bone1_head = bone1.head  # 头坐标
    bone1_tail = bone1.tail  # 尾坐标

    bone2_length = bone2.length  # 长度
    bone1_length = bone1.length  # 长度

    if distance:
        head1 = np.array([bone1_head.x, bone1_head.y, bone1_head.z])
        tail1 = np.array([bone1_tail.x, bone1_tail.y, bone1_tail.z])

        # 计算方向向量和缩放因子
        direction = tail1 - head1
        length = np.linalg.norm(direction)
        if lengths:
            k = bone1_length / length  # 缩放因子
        else:
            k = bone2_length / length  # 缩放因子

        # 生成两种方向的尾坐标
        scaled_dir1 = direction * k  # 原方向
        scaled_dir2 = -direction * k  # 反方向
        tail2_case1 = tail1 + scaled_dir1
        tail2_case2 = tail1 + scaled_dir2

        # 计算到 head1 的距离
        distance_case1 = np.linalg.norm(head1 - tail2_case1)
        distance_case2 = np.linalg.norm(head1 - tail2_case2)

        if distance_case1 > distance_case2:  # 选择距离更长的
            bone2.tail = tail2_case1
            print(f"Case 1 尾坐标: {np.round(tail2_case1, 4)}, 距离: {np.round(distance_case1, 4)}")
        else:
            bone2.tail = tail2_case2
            print(f"Case 2 尾坐标: {np.round(tail2_case2, 4)}, 距离: {np.round(distance_case2, 4)}")

    if scale:
        bone2.length = bone2_length

    if not distance:
        bone2.tail = bone1_head
        print(f"对齐 {bone_name2} 尾坐标为 {np.round(bone2.tail, 4)}")

def merge_bone_weights(context_bone, bone2, context_arm, selected_objects, tail=False, midpoint=False):

    del_modifier_name = []

    if context_bone:

        if midpoint:
            # 计算中点坐标
            midpoint_tail = calculate_midpoint(context_bone.tail, bone2.tail)
            midpoint_head = calculate_midpoint(context_bone.head, bone2.head)

            # 设置中点坐标
            context_bone.head = midpoint_head
            context_bone.tail = midpoint_tail

        # 合并骨骼
        if tail:
            context_bone.tail = bone2.tail

        context_arm.data.edit_bones[context_arm.data.edit_bones[bone2.name].name].parent = context_bone

        # 合并权重
        modifier = selected_objects[0].modifiers.new(type='VERTEX_WEIGHT_MIX', name='Merge Bone Weights')
        modifier.vertex_group_a = context_bone.name
        modifier.vertex_group_b = bone2.name
        modifier.mix_set = 'ALL'
        modifier.mix_mode = 'ADD'
        modifier.normalize = True

        del_modifier_name.append(modifier.name)

        # 删除子级
        context_arm.data.edit_bones.remove(bone2)

        print(context_bone.name, "合并子级")


    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.context.view_layer.objects.active = selected_objects[0]

    # 确保对象使用单用户数据，避免修改器应用失败
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)

    for modifier_name in del_modifier_name:
        bpy.ops.object.modifier_apply(modifier=modifier_name)
        print(modifier_name, "应用")

    bpy.context.view_layer.objects.active = context_arm

    bpy.ops.object.mode_set(mode='EDIT')


def ot_connect_rigid_body_chain(bone_chains, sel_objects=None, bone_mode=False, close_chain=False):

    if close_chain:
        bone_chains.append(bone_chains[0])

    loom = {}

    for chain in zip_longest(*bone_chains):
        for idx, bone_name in enumerate(chain):
            if bone_name and bone_name != chain[-1]:
                if chain[idx+1]:

                    if bone_mode:
                        loom[bone_name] = chain[idx+1]

                    if sel_objects:
                        obj_name1 = ""
                        obj_name2 = ""

                        for obj in sel_objects:
                            if obj.mmd_rigid.bone == bone_name:
                                obj_name1 = obj.name

                            if obj.mmd_rigid.bone == chain[idx+1]:
                                obj_name2 = obj.name

                        loom[obj_name1] = obj_name2

    return loom

# 计算三维空间中的两点之间的中点坐标
def calculate_midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2,
            (p1[1] + p2[1]) / 2,
            (p1[2] + p2[2]) / 2)