import omni.usd
import omni.kit.commands

# Replace character name
root_path = "/World/CharRoot/Camila/Camila"
a2f_root_path = "/World/Camila_A2F/CharRoot/Camila_A2F/Camila_A2F"
body_path = f"{root_path}/CC_Base_Body/CC_Base_Body/CC_Base_Body"
# other chars may not have the same list of facial hair
# set hair_paths = [] for characters with no facial hair. 
hair_paths = [f"{root_path}/Pelo2/Pelo2/Pelo2"]
skel_path = f"{root_path}/Camila"


selection = omni.usd.get_context().get_selection()
stage = omni.usd.get_context().get_stage()


# step 1: jaw shapes
# skin and facial hair
omni.kit.commands.execute(
    "TransferRigCommand",
    source_mesh=f"{a2f_root_path}/CC_Base_Body/CC_Base_Body",
    destination_prims=[body_path] + hair_paths,
    do_skin=False,
    do_blendshape=True,
    blendshape_list=["Jaw_Open_0"],
    max_dist = 10.0
    )


# teeth
omni.kit.commands.execute(
    "TransferRigCommand",
    source_mesh=f"{a2f_root_path}/CC_Base_Teeth_Lower/CC_Base_Teeth_Lower",
    destination_prims=[f"{root_path}/CC_Base_Teeth/CC_Base_Teeth/CC_Base_Teeth"],
    do_skin=False,
    do_blendshape=True,
    blendshape_list=["TeethMerged_Open_Mouth"],
    max_dist = 0.0001
    )


# tongue
omni.kit.commands.execute(
    "TransferRigCommand",
    source_mesh=f"{a2f_root_path}/CC_Base_Tongue/CC_Base_Tongue",
    destination_prims=[f"{root_path}/CC_Base_Tongue/CC_Base_Tongue/CC_Base_Tongue"],
    do_skin=False,
    do_blendshape=True,
    blendshape_list=["TongueMerged_Open_Mouth"],
    max_dist = 0.0001
    )


# step 2: combine shapes for arkit
selection.set_selected_prim_paths([root_path], True)
omni.kit.commands.execute(
    "ExecuteToolboxCommand",
    module_name="omni.anim.toolbox.arkit_RL",
    function_name="merge_RL_ARKit_shapes",
    kwargs={}
)


# step 3: prepare skel Animation
selection.set_selected_prim_paths([body_path], True)
omni.kit.commands.execute(
    "ExecuteToolboxCommand",
    module_name="omni.anim.toolbox.usdSkel",
    function_name="create_bs_SkelAnimation",
    kwargs={}
)
omni.kit.commands.execute("CopyPrim", path_from="/World/bs_anim", path_to="/World/bs_anim_arkit")
omni.kit.commands.execute(
    "ExecuteToolboxCommand",
    module_name="omni.anim.toolbox.arkit_RL",
    function_name="set_RL_ARKit_Shapes",
    kwargs={}
)
omni.kit.commands.execute("MovePrim", path_from="/World/bs_anim", path_to="/World/bs_anim_full")


# step 4: SkelAnimation without bs timesamples
sa_path = f"{skel_path}/Animation"
sa_clean_path = f"{sa_path}_clean"
omni.kit.commands.execute(
    "CopyPrim",
    path_from=sa_path,
    path_to=sa_clean_path,
    duplicate_layers=True,
    combine_layers=True,
    flatten_references=True
)
sa_clean_prim = stage.GetPrimAtPath(sa_clean_path)
sa_full_prim = stage.GetPrimAtPath("/World/bs_anim_full")
for attr in ["blendShapes", "blendShapeWeights"]:
    sa_clean_prim.GetAttribute(attr).Clear()
    sa_clean_prim.GetAttribute(attr).Set(sa_full_prim.GetAttribute(attr).Get())
skel_prim = stage.GetPrimAtPath(skel_path)
skel_prim.GetRelationship("skel:animationSource").SetTargets([sa_clean_path])


# step 5: transfer skin to facial hair
omni.kit.commands.execute(
    "TransferRigCommand",
    source_mesh=body_path,
    destination_prims=hair_paths,
    do_skin=True,
    do_blendshape=False
    )
