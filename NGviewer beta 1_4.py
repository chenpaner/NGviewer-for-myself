bl_info = {
    "name": "NGviewer在 3D 视口中显示节点组的输入",
    "author": "Andrew Stevenson,cp",
    "version": (1, 4),
    "blender": (2, 80, 0),
    "location": "View3D > N-Panel > tools >NGviewer",
    "doc_url":"https://github.com/strike-digital",
    "description": "easily edit node group perameters from the 3D view",
    "category": "Node",
}

import bpy
import nodeitems_utils 
from bpy.types import Panel
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )

#Feel free to change this but it would be great for me if you would consider buying the addon first ;)
is_trial = False


def draw_trial(col):
    row = col.row(align=True)
    row.operator('wm.url_open',
                 text="",
                 icon='FUND',
                 emboss=False).url = "https://gumroad.com/l/qWuvv"
    row.alert = True
    row.label(text="Trial Version")

def node_group_enum(self, context):#这个方法用于生成一个枚举列表，用于显示在面板上的节点组选择下拉框
    enum_items = []
    node_group_names = []
    node_group_labels = []
    ng_tool = bpy.context.scene.ng_tool
    #nodes = bpy.data.materials[ng_tool.material].node_tree.nodes
    nodes = bpy.context.active_object.active_material.node_tree.nodes

    for node in nodes:
        if node.type == 'GROUP':
            usable_inputs = 0
            if not ng_tool.show_non_input_groups:
                for input in node.inputs:
                    if input.enabled and not input.is_linked:
                        usable_inputs += 1
                if len(node.inputs) == usable_inputs:
                    node_group_names.append(node.name)
                    node_group_labels.append(node.label)
            else:
                node_group_names.append(node.name)
                node_group_labels.append(node.label)

    for group, label in zip(node_group_names, node_group_labels):

        if label == "":
            enum_items.append((group,
                            group,
                            group,
                            ))
        else:
            enum_items.append((group,
                            label,
                            group,
                            ))
    return enum_items

# 保存字符串引用的全局变量
enum_strings = []

def get_node_group_names(self, context):
    node_group_names = []
    #nodes = bpy.data.materials[ng_tool.material].node_tree.nodes
    nodes = bpy.context.active_object.active_material.node_tree.nodes
    for node in nodes:
        if node.type == 'GROUP':
            node_group_name = node.node_tree.name  # 获取节点组的名字
            full_name = f"{node.name} ({node_group_name})"
            node_group_names.append((full_name, full_name, ""))
            # 将字符串保存到全局变量中，不然无法显示中文
            enum_strings.append(full_name)
    
    return node_group_names

def draw_sockets(self, context):#绘制节点输入框，显示节点组的输入端口信息
    layout = self.layout
    ng_tool = bpy.context.scene.ng_tool
    #node_tree = bpy.data.materials[ng_tool.material].node_tree
    node_tree = bpy.context.active_object.active_material.node_tree
    #group_node = node_tree.nodes[ng_tool.node_group]

    selected_option = ng_tool.selected_node_group
    if selected_option:
        node_name, group_name = selected_option.split(' (')
        node = bpy.context.active_object.active_material.node_tree.nodes.get(node_name)
        if node:

            group_node = node_tree.nodes[node_name]
            
            layout.label(text="Inputs:")
            if ng_tool.edit_node_links:#如果编辑节点链接被启用用bl默认的方式显示节点组，名字会自动翻译
                for socket in group_node.inputs: 
                    if  socket.is_linked:  
                        col = layout.column(align = True)
                        boxcol = col.box().column(align = True)# 在列中创建一个框，并在框内创建一个列
                        row = boxcol.column()# 在框列中创建一行
                        #row.label(text = socket.name)
                        row.template_node_view(node_tree, group_node, socket)
                    else:
                        boxcol = layout.column(align = True)# 在布局中创建一个新列
                        boxcol.template_node_view(node_tree, group_node, socket) # 使用节点视图模板绘制节点输入
            else:# 如果编辑节点链接未启用
                for input in group_node.inputs:   
                    if  input.is_linked:
                        linked_nodes = []
                        for link in input.links:
                            linked_nodes.append(link.from_node.name)
                        if linked_nodes:
                            connected_nodes_text = ", ".join(linked_nodes)
                        col = layout.column(align = True)
                        col.label(text =input.name+ f"【Link:{connected_nodes_text}】")  # 在行中添加标签，显示输入名称
                    elif input.hide_value :
                        col.label(text =input.name+ "【Hide】")
                    else: 
                        if input.type == "RGBA":
                            layout.prop(input, 'default_value', text=input.name)
                            col = layout.column(align = True)
                        else:
                            col.prop(input, 'default_value', text=input.name)

class NodeGroupSettings(bpy.types.PropertyGroup):

    selected_node_group: bpy.props.EnumProperty(
        items=get_node_group_names,
    )


    edit_node_links: BoolProperty(
        name="切换显示方式(以BL默认方式显示)",
        description="取消勾选后以自定义方式排布！",
        default=True,
    )




# class PANEL_PT_ng_node_panel(Panel):
#     """Creates a Panel in the node"""
#     bl_space_type = "NODE_EDITOR"
#     bl_idname = "PANEL_PT_ng_node_panel"
#     bl_region_type = "UI"
#     bl_label = "NGviewer"
#     bl_context = "objectmode"
#     bl_category = "Node"

#     def draw(self, context):
#         layout = self.layout
#         ng_tool = bpy.context.scene.ng_tool
#         col = layout.column(align = True)
#         col.alignment = "CENTER"
#         # col.label(text = """WARNING: Dont use this button """,icon = "ERROR")
#         # col.label(text = """while not in the node group """)
#         # col.label(text = """edit mode, as it will mess some stuff up""")
#         col.label(text = "使用这个按钮之前确保你在节点组里面")
#         row = col.row(align = True)
#         row.scale_y = 2
#         row.scale_x = 2
#         row.operator("object.new_box", icon = "ADD")
#         row.prop(ng_tool, "show_node_box_info", text = "", icon = "QUESTION")
#         if ng_tool.show_node_box_info:
#             info_box = col.box()
#             info_box.label(text = "添加群组:")
#             info_box = info_box.column(align = False)
#             info_box.scale_y = 0.8
#             info_box.label(text = "1.在下面的‘界面’面板中")
#             info_box.label(text = "    选择要添加到组中的节点输入")
#             info_box.label(text = "2.按“新建盒子组”按钮并输入该组的名称")
#             info_box.label(text = "3.如果您只想名称与所选输入相同")
#             info_box.label(text = "    不要在框中输入任何内容")
            
class PANEL_PT_ng_node_panel1(Panel):
    """Creates a Panel in the Tool panel"""
    bl_space_type = "VIEW_3D"
    bl_idname = "PANEL_PT_ng_node_panel1"
    bl_region_type = "UI"
    bl_label = "NGviewer"
    bl_category = "NGviewer"
    # ng_tool = bpy.context.scene.ng_tool
    #  if ng_tool.category is "Tool":
    #     bl_category = "Tool"
    # else:
    #     bl_category = "NGviewer"

    def draw(self, context): 
        ng_tool = bpy.context.scene.ng_tool

        layout = self.layout
 
       
        if is_trial:
            draw_trial(layout)

        try:
            
            #check for active object
            if bpy.context.active_object is not None:
                material_slots = bpy.context.active_object.material_slots

                #check for material slots
                if len(material_slots) != 0:

                    #check for materials

                    #if bpy.data.materials[ng_tool.material] is not None and bpy.context.active_object.active_material is not None:
                    if  bpy.context.active_object.active_material is not None:
                        col = layout.column(align = True)
                        row = col.split(factor=0.3, align=True)
                        row.scale_y = 1.2
                        row.scale_x = 1.13
                        #row.prop(ng_tool, "material")
                        row.popover(panel="NODE_PT_material_slots")
                        row.label(text=bpy.context.active_object.active_material.name)
                        # row.prop(ng_tool, "show_material_settings", text="", icon='PREFERENCES')


                        # #material settings panel
                        # if ng_tool.show_material_settings:
                        #     box = col.box()
                        #     boxcol = box.column(align = True)
                        #     boxcol.prop(ng_tool, "show_non_group_materials")
                        #     boxcol.prop(ng_tool, "grumpy")

                        col.separator()

                        #check for node tree
                        #if bpy.data.materials[ng_tool.material].node_tree is not None:
                        if bpy.context.active_object.active_material.node_tree is not None: 
                            node_groups = []
                            #nodes = bpy.data.materials[ng_tool.material].node_tree.nodes
                            nodes = bpy.context.active_object.active_material.node_tree.nodes

                            #check for node groups
                            for node in nodes:
                                if node.type == 'GROUP':
                                    node_groups.append(node.name)
                        
                            if len(node_groups) != 0:

                                #node_tree = bpy.data.materials[ng_tool.material].node_tree
                                #group_node = node_tree.nodes[ng_tool.node_group]
                                #def_input_boxes(group_node)

                                
                                row = col.row(align = True)
                                
                                row.scale_y = 1.2
                                row.scale_x = 1.13

                                #row.prop(ng_tool, "node_group", icon = "NODETREE")
                                row.prop(ng_tool, "selected_node_group",  text="", icon = "NODETREE")
                                # #row.prop(ng_tool, "show_group_settings", text="", icon='PREFERENCES')

                                # #group settings panel
                                # if ng_tool.show_group_settings:
                                box = col.box()
                                boxcol = box.column(align = True)
                                #boxcol.prop(ng_tool, "show_non_input_groups")
                                boxcol.prop(ng_tool, "edit_node_links")
                          
                                        

                                draw_sockets(self,context)

                            else:
                                layout.label(text = "No node groups in this material " )            
                        else:
                            layout.label(text = "No active node tree " )
                    # else:
                    #     layout.label(text = "No active material " + face)
                else:
                    layout.label(text = "No material slots " ) 
            else:
                layout.label(text = "No object selected " ) 
        except KeyError:
            layout.label(text = "Please select a material ")

class NG_OT_add_box_separator(bpy.types.Operator):
    """add a new box including the active group node input"""
    bl_label = "New box group"
    bl_idname = "object.new_box"
    bl_description = "add a new box including the active group node input"
    bl_options = {"REGISTER", "UNDO"}

    name : StringProperty(
        name = "Box title",
        default = "",
        description = "Box title",)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "name")

    def execute(self, context):
        bpy.ops.node.tree_socket_add(in_out='IN')
        bpy.ops.node.tree_socket_move(direction='UP')
        node =  bpy.context.active_object.active_material.node_tree.nodes.active
        if node.type == 'GROUP':
            #stupid hack becuase I can't figure out how to get active node group name
            for group in bpy.data.node_groups:
                if len(group.inputs) == len(node.inputs) and group.inputs[0].name == node.inputs[0].name: 
                    name = group.name
                    index = bpy.data.node_groups[name].active_input.numerator
                    break
            
            node.inputs[index].hide_value = True
            if self.name != "":
                node.inputs[index].name = self.name
                bpy.data.node_groups[name].inputs[index].name = self.name
        return{'FINISHED'}


classes = (
    NodeGroupSettings,
    PANEL_PT_ng_node_panel1,
    #NGPreferences,
    #PANEL_PT_ng_node_panel,
    NG_OT_add_box_separator,
    #MySettings
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ng_tool = bpy.props.PointerProperty(type=NodeGroupSettings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ng_tool


if __name__ == "__main__":
    register()
    
