import bpy

class key_property(bpy.types.PropertyGroup):
    # 参考形态键名称
    reference_shape_key: bpy.props.StringProperty(
        name="参考形态键",
        description="选择作为参考的形态键",
        default=""
    )

class MMD_RigidBody_Property(bpy.types.PropertyGroup):

    # 刚体质量
    rigid_body_mass: bpy.props.FloatProperty(
        name="刚体质量",
        description="设置刚体的质量",
        default=8.0
    )

    # 刚体质量偏差值
    rigid_body_mass_offset: bpy.props.FloatProperty(
        name="刚体质量偏差值",
        description="设置刚体质量的偏差值",
        default=0.15,
    )

    # 刚体质量衰减
    rigid_body_mass_decay: bpy.props.FloatProperty(
        name="刚体质量衰减",
        description="设置刚体质量的衰减值",
        default=0.5,
    )

