from common.i18n.dictionary import preprocess_dictionary

dictionary = {
    "zh_CN": {
        ("Operator", "Restore form bond vertex position"): "恢复形态键顶点位置",
        ("*", "Restore form bond vertex position"): "恢复形态键顶点位置",
        ("Operator", "Batch pass shape keys"): "批量传递形状键",
        ("*", "Batch pass shape keys"): "批量传递形状键",
        ("", "Selected model:"): "选中的模型：",
        ("", "No selected model"): "未选中模型",
        ("", "Reference model:"): "参考模型：",
        ("", "No reference model"): "未选择参考模型",
        ("*", "MMD Rigid Body Tools"): "MMD 刚体工具",
        ("Operator", "MMD Rigid Body Selection Corresponding to the Skeleton"): "按MMD骨骼链选择刚体",
        ("Operator", "MMD Bone Chain Select Rigid Body Constraint"): "按MMD骨骼链选择刚体约束",
        ("Operator", "MMD Rigid Body Adjust Mass Level"): "按MMD骨骼链调整刚体质量",
        ("", "Rigid Body Mass:"): "刚体质量：",
        ("", "Rigid Body Mass"): "刚体质量",
        ("", "Rigid Body Selection:"): "刚体选择：",
        ("", "Rigid Body Mass Offset"): "刚体质量偏差值",
        ("", "Rigid Body Mass Decay"): "刚体质量衰减",
        ("Operator", "Merge Bone Weights"): "合并骨骼权重",
        ("Operator", "Merge Bone Weights Child"): "按子级合并骨骼权重",
        ("Operator", "Merge Bone Weights Chain"): "按骨骼链合并骨骼权重",
        ("*", "Bone Tools"): "骨骼工具",
        ("Operator", "Set Child Bone to Child"): "选择子级骨骼的子级",
        ("", "Rigid-body loom:"): "刚体织布机",
        ("Operator", "Rigid Body Chain Connection"): "连接刚体链",
        ("Operator", "Fix Bone Chain End"): "修复骨骼链末端",
        ("", "Weight:"): "权重：",
        ("", "Edit:"): "编辑：",
        ("", ""): "",


    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
