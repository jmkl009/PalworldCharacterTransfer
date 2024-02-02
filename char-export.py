# Credit to https://www.reddit.com/r/Palworld/comments/19dhpjn/server_to_server_character_transfer_script/ and https://github.com/EternalWraith/PalEdit
# I have fixed the error of tools not having durability (which causes crossbow, etc. to not load), by adding missing entries in the DynamicItemSaveData section.
# I have also fixed the error of pals not belonging to the same guild and therefore is attackable by adding them to the guild.
# Other fixes include prevention of duplicate and missing pals.
import json
import os
import SaveConverter

from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

def main():
    global host_sav_path, level_sav_path, t_level_sav_path, t_host_sav_path, host_json, level_json, targ_json, targ_lvl
    
    if None in [host_sav_path, level_sav_path, t_level_sav_path, t_host_sav_path]:
        messagebox.showerror(message='Please have all files selected before starting transfer.')
        return
    print(host_sav_path, level_sav_path, t_level_sav_path, t_host_sav_path)

    # Warn the user about potential data loss.
    response = messagebox.askyesno(title='WARNING', message='WARNING: Running this script WILL change your save files and could \
potentially corrupt your data. It is HIGHLY recommended that you make a backup \
of your save folder before continuing. Press Yes if you would like to continue.')
    if not response:
        return


    host_guid = os.path.basename(host_sav_path).split('.')[0]
    targ_guid = os.path.basename(t_host_sav_path).split('.')[0]

    # Apply expected formatting for the GUID.
    host_guid_formatted = '{}-{}-{}-{}-{}'.format(host_guid[:8], host_guid[8:12], host_guid[12:16], host_guid[16:20], host_guid[20:]).lower()

    #Container key at key/struct/struct/id/struct/value/guid

    # host_instance_id = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["IndividualId"]["Struct"]["value"]["Struct"]["InstanceId"]["Struct"]["value"]["Guid"]
    host_instance_id = host_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]

    # Search for and replace the final instance of the 00001 GUID with the InstanceId.
    # instance_ids_len = len(level_json["root"]["prodperties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"])
    instance_ids_len = len(level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"])

    count = 0
    found = 0
    expected_containers = 7
    exported_map = {}
    param_maps = []
    palcount = 0
    for i in range(instance_ids_len):
        # instance_id = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i]["key"]["Struct"]["Struct"]["InstanceId"]["Struct"]["value"]["Guid"]
        instance_id = level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["InstanceId"]["value"]
        if instance_id == host_instance_id:
            #level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i]["key"]["Struct"]["Struct"]["PlayerUId"]["Struct"]["value"]["Guid"] = host_guid_formatted
            # exported_map = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i]
            exported_map = level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]
            count = count + 1
            found = 1
        elif level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["PlayerUId"]["value"] == host_guid_formatted or (
            level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["PlayerUId"]["value"] == "00000000-0000-0000-0000-000000000000" and 
            level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]['value']['RawData']['value']['object']['SaveParameter']['value'].get('OwnerPlayerUId', {'value':''})['value'] == host_guid_formatted):
            param_maps.append(level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i])
            palcount += 1
        # level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]['value']['RawData']['value']['object']['SaveParameter']['value']['OwnerPlayerUId']['value']
        # level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]['value']['RawData']['value']['object']['SaveParameter']['value']['OldOwnerPlayerUId']['value']

    if not found:
        print("Couldn't find character instance data to export")
        exit()
    print("Found Character Parameter Map")
    print("Read " + str(palcount) + " pals from source save")

    print("Searching for container data")
    inv_info = host_json["properties"]["SaveData"]["value"]["inventoryInfo"]
    inv_main = inv_info["value"]["CommonContainerId"]
    inv_key = inv_info["value"]["EssentialContainerId"]
    inv_weps = inv_info["value"]["WeaponLoadOutContainerId"]
    inv_armor = inv_info["value"]["PlayerEquipArmorContainerId"]
    inv_foodbag = inv_info["value"]["FoodEquipContainerId"]
    inv_pals = host_json["properties"]["SaveData"]["value"]["PalStorageContainerId"]
    inv_otomo = host_json["properties"]["SaveData"]["value"]["OtomoCharacterContainerId"]

    host_main = {}
    host_key = {}
    host_weps = {}
    host_armor = {}
    host_foodbag = {}
    host_pals = {}
    host_otomo = {}
    count = 0

    # container_ids_len = len(level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"])
    container_ids_len = len(level_json["properties"]["worldSaveData"]["value"]["CharacterContainerSaveData"]["value"])

    for i in range(container_ids_len):
        # container = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]
        container = level_json["properties"]["worldSaveData"]["value"]["CharacterContainerSaveData"]["value"][i]
        # container_id = container["key"]["Struct"]["Struct"]["ID"]["Struct"]["value"]["Guid"]
        container_id = container["key"]["ID"]["value"]
        # if container_id == inv_pals["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
        if container_id == inv_pals["value"]["ID"]["value"]:
            print("Found host pal inventory")
            host_pals = container
            count = count + 1
        # elif container_id == inv_otomo["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
        elif container_id == inv_otomo["value"]["ID"]["value"]:
            print("Found host otomo inventory")
            host_otomo = container
            count = count + 1
        if count >= 2:
            print("Found all pal containers")
            break

    # container_ids_len = len(level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"])
    container_ids_len = len(level_json["properties"]["worldSaveData"]["value"]["ItemContainerSaveData"]["value"])
    # dynamic_container_level_json = level_json['root']['properties']['worldSaveData']['Struct']['value']['Struct']['DynamicItemSaveData']['Array']['value']['Struct']['value']
    dynamic_container_level_json = level_json['properties']['worldSaveData']['value']['DynamicItemSaveData']['value']['values']    


    dynamic_guids = set()
    for i in range(container_ids_len):
        container = level_json["properties"]["worldSaveData"]["value"]["ItemContainerSaveData"]["value"][i]
        container_id = container["key"]["ID"]["value"]
        if container_id == inv_main["value"]["ID"]["value"]:
            print("Found host main inventory")
            for item in container['value']['Slots']['value']['values']:
                dynamic_guid = item['ItemId']['value']['DynamicId']['value']['LocalIdInCreatedWorld']['value']
                if dynamic_guid != '00000000-0000-0000-0000-000000000000':
                    dynamic_guids.add(dynamic_guid)
            host_main = container
            count = count + 1
        elif container_id == inv_key["value"]["ID"]["value"]:
            print("Found host key inventory")
            host_key = container
            for item in container['value']['Slots']['value']['values']:
                dynamic_guid = item['ItemId']['value']['DynamicId']['value']['LocalIdInCreatedWorld']['value']
                if dynamic_guid != '00000000-0000-0000-0000-000000000000':
                    dynamic_guids.add(dynamic_guid)
            count = count + 1
        elif container_id == inv_weps["value"]["ID"]["value"]:
            print("Found host weapon inventory")
            for item in container['value']['Slots']['value']['values']:
                dynamic_guid = item['ItemId']['value']['DynamicId']['value']['LocalIdInCreatedWorld']['value']
                if dynamic_guid != '00000000-0000-0000-0000-000000000000':
                    dynamic_guids.add(dynamic_guid)
            host_weps = container
            count = count + 1
        elif container_id == inv_armor["value"]["ID"]["value"]:
            print("Found host armor inventory")
            for item in container['value']['Slots']['value']['values']:
                dynamic_guid = item['ItemId']['value']['DynamicId']['value']['LocalIdInCreatedWorld']['value']
                if dynamic_guid != '00000000-0000-0000-0000-000000000000':
                    dynamic_guids.add(dynamic_guid)
            host_armor = container
            count = count + 1
        elif container_id == inv_foodbag["value"]["ID"]["value"]:
            print("Found host food bag inventory")
            for item in container['value']['Slots']['value']['values']:
                dynamic_guid = item['ItemId']['value']['DynamicId']['value']['LocalIdInCreatedWorld']['value']
                if dynamic_guid != '00000000-0000-0000-0000-000000000000':
                    dynamic_guids.add(dynamic_guid)
            host_foodbag = container
            count = count + 1
        elif container_id == inv_foodbag["value"]["ID"]["value"]:
            print("Found host food bag inventory")
            for item in container['value']['Slots']['value']['values']:
                dynamic_guid = item['ItemId']['value']['DynamicId']['value']['LocalIdInCreatedWorld']['value']
                if dynamic_guid != '00000000-0000-0000-0000-000000000000':
                    dynamic_guids.add(dynamic_guid)
            host_foodbag = container
            count = count + 1
        if count >= expected_containers:
            print("Found all target containers")
            break

    level_additional_dynamic_containers = []
    for dynamic_container in dynamic_container_level_json:
        if dynamic_container['ID']['value']['LocalIdInCreatedWorld']['value'] in dynamic_guids:
            level_additional_dynamic_containers.append(dynamic_container)

    if count < expected_containers:
        print("Missing container info! Only found " + str(count))
        exit()

    host_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"] = targ_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"]
    host_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"] = targ_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]

    targ_id_as_bytes = []
    for i in range(8):
        targ_id_as_bytes.append(int(targ_guid[(7-i)*2:(7-i)*2+2],16))
    print("Target ID as bytes is " + str(targ_id_as_bytes))

    instance_ids_len = len(targ_lvl["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"])
    char_instanceid = host_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]

    print("Transferring profile data...")
    if "TechnologyPoint" in host_json["properties"]["SaveData"]["value"]:
        targ_json["properties"]["SaveData"]["value"]["TechnologyPoint"] = host_json["properties"]["SaveData"]["value"]["TechnologyPoint"]
    else:
        if "TechnologyPoint" in targ_json["properties"]["SaveData"]["value"]:
            targ_json["properties"]["SaveData"]["value"]["TechnologyPoint"]["value"] = 0

    if "bossTechnologyPoint" in host_json["properties"]["SaveData"]["value"]:
        targ_json["properties"]["SaveData"]["value"]["bossTechnologyPoint"] = host_json["properties"]["SaveData"]["value"]["bossTechnologyPoint"]
    else:
        if "bossTechnologyPoint" in targ_json["properties"]["SaveData"]["value"]:
            targ_json["properties"]["SaveData"]["value"]["bossTechnologyPoint"]["value"] = 0
    targ_json["properties"]["SaveData"]["value"]["UnlockedRecipeTechnologyNames"] = host_json["properties"]["SaveData"]["value"]["UnlockedRecipeTechnologyNames"]
    targ_json["properties"]["SaveData"]["value"]["RecordData"] = host_json["properties"]["SaveData"]["value"]["RecordData"]
    targ_json["properties"]["SaveData"]["value"]["PlayerCharacterMakeData"] = host_json["properties"]["SaveData"]["value"]["PlayerCharacterMakeData"]

    found = 0
    index = 0
    for i in range(instance_ids_len):
        instance_id = targ_lvl["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["InstanceId"]["value"]
        if instance_id == char_instanceid:
            found = 1
            index = i
            break

    if found > 0:
        print("Existing character parameter map found, overwriting")
        targ_lvl["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][index]["value"] = exported_map["value"]
    else:
        print("Couldn't find character paramater map, aborting")
        exit()

    print("Searching for target containers")
    container_ids_len = len(targ_lvl["properties"]["worldSaveData"]["value"]["CharacterContainerSaveData"]["value"])

    inv_info = targ_json["properties"]["SaveData"]["value"]["inventoryInfo"]
    inv_main = inv_info["value"]["CommonContainerId"]
    inv_key = inv_info["value"]["EssentialContainerId"]
    inv_weps = inv_info["value"]["WeaponLoadOutContainerId"]
    inv_armor = inv_info["value"]["PlayerEquipArmorContainerId"]
    inv_foodbag = inv_info["value"]["FoodEquipContainerId"]

    host_inv_pals = inv_pals
    host_inv_otomo = inv_otomo
    inv_pals = targ_json["properties"]["SaveData"]["value"]["PalStorageContainerId"]
    inv_otomo = targ_json["properties"]["SaveData"]["value"]["OtomoCharacterContainerId"]

    group_id = None
    targ_uid = targ_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["PlayerUId"]["value"]
    for group_data in targ_lvl["properties"]["worldSaveData"]["value"]["GroupSaveDataMap"]["value"]:
        if group_data["value"]["GroupType"]["value"]["value"] == "EPalGroupType::Guild":
            if targ_uid in [player_item['player_uid'] for player_item in group_data["value"]["RawData"]["value"]["players"]]:
                 group_id = group_data["value"]["RawData"]["value"]['group_id']
                 guild_items_json = group_data["value"]["RawData"]["value"]["individual_character_handle_ids"]
                 break
    if group_id is None:
        print('Guild ID not found, aboorting')
        exit()

    print([inv_pals["value"]["ID"]["value"], inv_otomo["value"]["ID"]["value"], host_inv_pals["value"]["ID"]["value"], host_inv_otomo["value"]["ID"]["value"]])

    maps_length = len(param_maps)
    print(targ_uid, host_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["PlayerUId"]["value"], host_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"])
    for pal_param in param_maps:
        pal_content = pal_param['value']['RawData']['value']['object']['SaveParameter']['value']
        pal_container_id = pal_content['SlotID']['value']['ContainerId']['value']['ID']['value']
        if pal_container_id == host_inv_pals["value"]["ID"]["value"]:
            pal_content['SlotID']['value']['ContainerId']['value']['ID']['value'] = inv_pals["value"]["ID"]["value"]
        elif pal_container_id == host_inv_otomo["value"]["ID"]["value"]:
            pal_content['SlotID']['value']['ContainerId']['value']['ID']['value'] = inv_otomo["value"]["ID"]["value"]
        if 'OwnerPlayerUId' in pal_content:
            pal_content['OwnerPlayerUId']['value'] = targ_uid # Player UID
            pal_content['OldOwnerPlayerUIds']['value']['values'] = [targ_uid]
        pal_param['value']['RawData']['value']['group_id'] = group_id
        print(pal_param["key"]["PlayerUId"]["value"], pal_param["value"]['RawData']['value']['object']['SaveParameter']['value']['CharacterID'])
        guild_items_json.append({"guid": "00000000-0000-0000-0000-000000000001", "instance_id": pal_param["key"]["InstanceId"]["value"]})
        #pal_param["key"]["PlayerUId"]["value"] = targ_uid
    new_character_save_param_map = []

    filter_ids = [inv_pals["value"]["ID"]["value"], inv_otomo["value"]["ID"]["value"], host_inv_pals["value"]["ID"]["value"], host_inv_otomo["value"]["ID"]["value"]]
    for entity in targ_lvl["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"]:
        entity_content = entity['value']['RawData']['value']['object']['SaveParameter']['value']
        if 'OwnerPlayerUId' in entity_content and entity_content['OwnerPlayerUId']['value'] == targ_uid: # Is a Pal container that belongs to the target characters
            if entity_content['SlotID']['value']['ContainerId']['value']['ID']['value'] in filter_ids:
                continue
        new_character_save_param_map.append(entity)
    new_character_save_param_map += param_maps
    targ_lvl["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"] = new_character_save_param_map
    print("Appended " + str(maps_length) + " pals of data")

    count = 0
    for i in range(container_ids_len):
        container = targ_lvl["properties"]["worldSaveData"]["value"]["CharacterContainerSaveData"]["value"][i]
        container_id = container["key"]["ID"]["value"]
        if container_id == inv_pals["value"]["ID"]["value"]:
            print("Found pal inventory in target")
            print("Doing it the hard way...")
            pal_length = len(targ_lvl["properties"]["worldSaveData"]["value"]["CharacterContainerSaveData"]["value"][i]["value"]["Slots"]["value"]["values"])
            for j in range(pal_length):
                targ_lvl["properties"]["worldSaveData"]["value"]["CharacterContainerSaveData"]["value"][i]["value"]["Slots"]["value"]["values"][j]["RawData"] = host_pals["value"]["Slots"]["value"]["values"][j]["RawData"]

            #targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]["value"] = host_pals["value"]
            count = count + 1
        elif container_id == inv_otomo["value"]["ID"]["value"]:
            print("Found otomo inventory in target")
            #targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]["value"] = host_otomo["value"]
            print("Doing it the hard way...")
            pal_length = len(targ_lvl["properties"]["worldSaveData"]["value"]["CharacterContainerSaveData"]["value"][i]["value"]["Slots"]["value"]["values"])
            for j in range(pal_length):
                targ_lvl["properties"]["worldSaveData"]["value"]["CharacterContainerSaveData"]["value"][i]["value"]["Slots"]["value"]["values"][j]["RawData"] = host_otomo["value"]["Slots"]["value"]["values"][j]["RawData"]
                print("Writing otomo slot no. " + str(j))
            count = count + 1
        if count >= 2:
            print("Found all pal containers")
            break

    container_ids_len = len(targ_lvl["properties"]["worldSaveData"]["value"]["ItemContainerSaveData"]["value"])

    for i in range(container_ids_len):
        container = targ_lvl["properties"]["worldSaveData"]["value"]["ItemContainerSaveData"]["value"][i]
        container_id = container["key"]["ID"]["value"]
        if container_id == inv_main["value"]["ID"]["value"]:
            print("Found main inventory in target")
            targ_lvl["properties"]["worldSaveData"]["value"]["ItemContainerSaveData"]["value"][i]["value"] = host_main["value"]
            count = count + 1
        elif container_id == inv_key["value"]["ID"]["value"]:
            print("Found key inventory in target")
            targ_lvl["properties"]["worldSaveData"]["value"]["ItemContainerSaveData"]["value"][i]["value"] = host_key["value"]
            count = count + 1
        elif container_id == inv_weps["value"]["ID"]["value"]:
            print("Found weapon inventory in target")
            targ_lvl["properties"]["worldSaveData"]["value"]["ItemContainerSaveData"]["value"][i]["value"] = host_weps["value"]
            count = count + 1
        elif container_id == inv_armor["value"]["ID"]["value"]:
            print("Found armor inventory in target")
            targ_lvl["properties"]["worldSaveData"]["value"]["ItemContainerSaveData"]["value"][i]["value"] = host_armor["value"]
            count = count + 1
        elif container_id == inv_foodbag["value"]["ID"]["value"]:
            print("Found food bag inventory in target")
            targ_lvl["properties"]["worldSaveData"]["value"]["ItemContainerSaveData"]["value"][i]["value"] = host_foodbag["value"]
            count = count + 1
        if count >= expected_containers:
            print("Found all target containers")
            break

    target_dynamic_containers = targ_lvl['properties']['worldSaveData']['value']['DynamicItemSaveData']['value']['values']
    repeated_indices = set()
    for i, target_dynamic_container in enumerate(target_dynamic_containers):
        target_guid = target_dynamic_container['ID']['value']['LocalIdInCreatedWorld']['value']
        if target_guid in dynamic_guids:
            for j, level_additional_dynamic_container in enumerate(level_additional_dynamic_containers):
                if target_guid == level_additional_dynamic_container['ID']['value']['LocalIdInCreatedWorld']['value']:
                    target_dynamic_containers[i] = level_additional_dynamic_container
                    repeated_indices.add(j)
                    break
    targ_lvl['properties']['worldSaveData']['value']['DynamicItemSaveData']['value']['values'] += [container for i, container in enumerate(level_additional_dynamic_containers) if i not in repeated_indices]

    json_to_sav(t_level_sav_path, targ_lvl)
    json_to_sav(t_host_sav_path, targ_json)

    print("Saved all data successfully. PLEASE DON'T BREAK")
    messagebox.showinfo(message='Transfer finished! You may continue transferring more players or close the windows now.')

def sav_to_json(file):
    return SaveConverter.convert_sav_to_json_data(file, file.replace(".sav", ".sav.json"), False)

def json_to_sav(file, json_data):
    SaveConverter.convert_json_data_to_sav(json_data, file)

def clean_up_files(file):
    if os.path.exists(file + '.json'):
        os.remove(file + '.json')

def select_file():
    return askopenfilename(filetypes=[("Palworld Saves", "*.sav *.json")])

def ishex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def load_file(path):
    global status_label, root
    loaded_file = None
    if path.endswith(".sav"):
        status_label.config(text="This save hasn't been decompiled. Decompile it now. It may take a few minutes...")
        root.update_idletasks()
        loaded_file = sav_to_json(path)
    if path.endswith(".sav.json"):
        status_label.config(text="Now loading the file...")
        root.update_idletasks()
        with open(path, "r", encoding="utf8") as f:
            loaded_file = json.load(f)
    status_label.config(text="Select files to transfer")
    return loaded_file



def source_player_file():
    global host_sav_path, source_player_path_label, host_json
    cleanup_path = None
    if host_sav_path:
        cleanup_path = host_sav_path
    host_sav_path = select_file()
    if host_sav_path:  # If a file was selected, update the label
        print(host_sav_path, cleanup_path)
        if cleanup_path and host_sav_path != cleanup_path + '.json':
            clean_up_files(cleanup_path)
        basename = os.path.basename(host_sav_path).split('.')[0]
        if len(basename) != 32 or not ishex(basename):
            messagebox.showerror(message="Selected file is not a player save file! They are of the format: {PlayerID}.sav")
            host_sav_path = None
            return
        host_json = load_file(host_sav_path)
        if not host_json:
            messagebox.showerror(message="Invalid files, files must be either .sav or .sav.json")
            host_sav_path = None
            return
        source_player_path_label.config(text=host_sav_path)
        host_sav_path = host_sav_path[:-5] if host_sav_path.endswith('.json') else host_sav_path

def source_level_file():
    global level_sav_path, source_level_path_label, level_json
    cleanup_path = None
    if level_sav_path:
        cleanup_path = level_sav_path
    level_sav_path = select_file()
    if level_sav_path:
        if cleanup_path and level_sav_path != cleanup_path + '.json':
            clean_up_files(cleanup_path)
        if not level_sav_path.endswith('Level.sav') and not level_sav_path.endswith('Level.sav.json'):
            messagebox.showerror("Incorrect file", "This is not the right file. Please select the Level.sav file.")
            level_sav_path = None
            return
        level_json = load_file(level_sav_path)
        if not level_json:
            messagebox.showerror(message="Invalid files, files must be either .sav or .sav.json")
            level_sav_path = None
            return
        source_level_path_label.config(text=level_sav_path)
        level_sav_path = level_sav_path[:-5] if level_sav_path.endswith('.json') else level_sav_path

def target_player_file():
    global t_host_sav_path, target_player_path_label, targ_json
    cleanup_path = None
    if t_host_sav_path:
        cleanup_path = t_host_sav_path
    t_host_sav_path = select_file()
    if t_host_sav_path:
        if cleanup_path and t_host_sav_path != cleanup_path + '.json':
            clean_up_files(cleanup_path)
        basename = os.path.basename(t_host_sav_path).split('.')[0]
        if len(basename) != 32 or not ishex(basename):
            messagebox.showerror(message="Selected file is not a player save file! They are of the format: {PlayerID}.sav")
            t_host_sav_path = None
            return
        targ_json = load_file(t_host_sav_path)
        if not targ_json:
            messagebox.showerror(message="Invalid files, files must be either .sav or .sav.json")
            t_host_sav_path = None
            return
        target_player_path_label.config(text=t_host_sav_path)
        t_host_sav_path = t_host_sav_path[:-5] if t_host_sav_path.endswith('.json') else t_host_sav_path

def target_level_file():
    global t_level_sav_path, target_level_path_label, targ_lvl
    cleanup_path = None
    if t_level_sav_path:
        cleanup_path = t_level_sav_path
    t_level_sav_path = select_file()
    if t_level_sav_path:
        if cleanup_path and t_level_sav_path != cleanup_path + '.json':
            clean_up_files(cleanup_path)
        if not t_level_sav_path.endswith('Level.sav') and not t_level_sav_path.endswith('Level.sav.json'):
            messagebox.showerror("Incorrect file", "This is not the right file. Please select the Level.sav file.")
            target_level_path_label = None
            return
        targ_lvl = load_file(t_level_sav_path)
        if not targ_lvl:
            messagebox.showerror(message="Invalid files, files must be either .sav or .sav.json")
            t_level_sav_path = None
            return
        target_level_path_label.config(text=t_level_sav_path)
        t_level_sav_path = t_level_sav_path[:-5] if t_level_sav_path.endswith('.json') else t_level_sav_path

def on_exit():
    global level_sav_path, host_sav_path, t_level_sav_path, t_host_sav_path
    # Here you can add any cleanup code or save state before exiting
    print("Application is closing")
    if level_sav_path:
        clean_up_files(level_sav_path)
    if host_sav_path:
        clean_up_files(host_sav_path)
    if t_level_sav_path:
        clean_up_files(t_level_sav_path)
    if t_host_sav_path:
        clean_up_files(t_host_sav_path)
    root.destroy()  # Ensures the application window closes cleanly

level_sav_path, host_sav_path, t_level_sav_path, t_host_sav_path = None, None, None, None
level_json, host_json, targ_lvl, targ_json = None, None, None, None

# main()
root = Tk()
root.title(f"PalTransfer")
root.geometry("")
root.minsize("800", "300")

status_label = Label(root, text="Select files to transfer")
status_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

root.columnconfigure(0, weight=3)
root.columnconfigure(1, weight=1)
Button(
    root,
    text='Select Source Player File',
    command=source_player_file
).grid(row=1, column=1, padx=10, pady=20, sticky="ew")
source_player_path_label = Label(root, text="...", wraplength=600)
source_player_path_label.grid(row=1, column=0, padx=10, pady=20, sticky="ew")

Button(
    root,
    text='Select Source Level File',
    command=source_level_file
).grid(row=2, column=1, padx=10, pady=20, sticky="ew")
source_level_path_label = Label(root, text="...", wraplength=600)
source_level_path_label.grid(row=2, column=0, padx=10, pady=20, sticky="ew")

Button(
    root,
    text='Select Target Player File',
    command=target_player_file
).grid(row=3, column=1, padx=10, pady=20, sticky="ew")
target_player_path_label = Label(root, text="...", wraplength=600)
target_player_path_label.grid(row=3, column=0, padx=10, pady=20, sticky="ew")

Button(
    root,
    text='Select Target Level File',
    command=target_level_file
).grid(row=4, column=1, padx=10, pady=20, sticky="ew")
target_level_path_label = Label(root, text="...", wraplength=600)
target_level_path_label.grid(row=4, column=0, padx=10, pady=20, sticky="ew")

Button(
    root,
    text='Start Transfer!',
    command=main
).grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")

# Register the exit function
root.protocol("WM_DELETE_WINDOW", on_exit)

root.mainloop()