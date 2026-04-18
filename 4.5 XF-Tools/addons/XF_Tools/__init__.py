import bpy

from .PropertyGroup.PropertyGroup import key_property, MMD_RigidBody_Property
from .config import __addon_name__
from .i18n.dictionary import dictionary
from ...common.class_loader import auto_load
from ...common.class_loader.auto_load import add_properties, remove_properties
from ...common.i18n.dictionary import common_dictionary
from ...common.i18n.i18n import load_dictionary

# Add-on info
bl_info = {
    "name": "XF Tools",
    "author": "小峰峰哥l",
    "blender": (4, 5, 0),
    "version": (1, 0),
    "description": "This is a template for building addons",
    "warning": "",
    "doc_url": "https://github.com/XiaoFFGe",
    "tracker_url": "https://space.bilibili.com/2109816568?spm_id_from=333.1369.0.0",
    "support": "COMMUNITY",
    "category": "3D View"
}

_addon_properties = {}

def register():
    # Register classes
    auto_load.init()
    auto_load.register()
    add_properties(_addon_properties)

    # Internationalization
    load_dictionary(dictionary)
    bpy.app.translations.register(__addon_name__, common_dictionary)

    bpy.types.Object.xffg_key_property = bpy.props.PointerProperty(type=key_property)
    bpy.types.Object.xffg_mmd_rigid_body_property = bpy.props.PointerProperty(type=MMD_RigidBody_Property)


    print("{} addon is installed.".format(__addon_name__))


def unregister():
    # Internationalization
    bpy.app.translations.unregister(__addon_name__)
    # unRegister classes
    auto_load.unregister()
    remove_properties(_addon_properties)

    del bpy.types.Object.xffg_key_property

    print("{} addon is uninstalled.".format(__addon_name__))
