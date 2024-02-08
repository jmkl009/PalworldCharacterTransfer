import copy
import json
import os
from sys import exit

import SaveConverter
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from lib.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from lib.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS
from lib.gvas import GvasHeader, GvasFile
from lib.archive import *
from typing import Any, Callable
import io
import struct
from typing import Sequence
from time import time

STRUCT_START = b'\x0f\x00\x00\x00StructProperty\x00'
MAP_START = b'\x0c\x00\x00\x00MapProperty\x00'
ARRAY_START = b'\x0e\x00\x00\x00ArrayProperty\x00'


class SkipFArchiveWriter(FArchiveWriter):
    data: io.BytesIO
    size: int
    custom_properties: dict[str, tuple[Callable, Callable]]
    debug: bool

    def __init__(
            self,
            custom_properties: dict[str, tuple[Callable, Callable]] = {},
            debug: bool = os.environ.get("DEBUG", "0") == "1",
    ):
        self.data = io.BytesIO()
        self.custom_properties = custom_properties
        self.debug = debug

    def curr_properties(self, properties):
        for key in properties:
            self.fstring(key)
            self.property(properties[key])

    def write_sections(self, props, section_ranges, bytes):
        props = [{k: v} for k, v in props.items()]
        prop_bytes = []
        for prop in props:
            self.curr_properties(prop)
            prop_bytes.append(self.bytes())
            self.data = io.BytesIO()
        # print(prop_bytes[0])
        bytes_concat_array = []
        last_end = 0
        for prop_byte, (section_start, section_end) in zip(prop_bytes, section_ranges):
            bytes_concat_array.append(bytes[last_end:section_start])
            bytes_concat_array.append(prop_byte)
            # print(prop_byte[:100], prop_byte[-100:])
            # print(bytes[section_start:section_start+100], bytes[section_end-100:section_end])
            last_end = section_end
        bytes_concat_array.append(bytes[last_end:])
        output = b''
        for byte_segment in bytes_concat_array:
            output += byte_segment
        return output


class SkipFArchiveReader(FArchiveReader):

    def __init__(
            self,
            data,
            type_hints: dict[str, str] = {},
            custom_properties: dict[str, tuple[Callable, Callable]] = {},
            debug=False,
            allow_nan=True
    ):
        self.size = len(data)
        self.orig_data = data
        self.data = io.BytesIO(data)
        self.type_hints = type_hints
        self.debug = debug
        self.custom_properties = custom_properties
        self.allow_nan = allow_nan

    def curr_property(self, path: str = "") -> dict[str, Any]:
        properties = {}
        name = self.fstring()
        type_name = self.fstring()
        size = self.u64()
        properties[name] = self.property(type_name, size, f"{path}.{name}")
        return properties

    def internal_copy(self, data, debug: bool) -> "FArchiveReader":
        return SkipFArchiveReader(
            data,
            self.type_hints,
            self.custom_properties,
            debug=debug,
            allow_nan=self.allow_nan,
        )

    def properties_until_end(self, path: str = "") -> dict[str, Any]:
        properties = {}
        while True:
            name = self.fstring()
            if name == "None":
                break
            type_name = self.fstring()
            size = self.u64()
            # print(name, path)
            properties[name] = self.property(type_name, size, f"{path}.{name}")
        return properties

    def encode(self, property_name):
        return struct.pack('i', len(property_name) + 1) + property_name.encode('ascii') + b'\x00'

    def find_property_start(self, property_name, type_start=STRUCT_START, offset=0):
        return self.orig_data[offset:].find(self.encode(property_name) + type_start) + offset

    def load_section(self, property_name, type_start=STRUCT_START, path='.worldSaveData'):
        start_index = self.find_property_start(property_name, type_start)
        # print(self.orig_data[start_index: start_index + 100])
        self.data.seek(start_index, 0)
        # c = time.time()
        # return self.curr_property(path=path), c
        return self.curr_property(path=path)

    def load_sections(self, prop_types, path='.worldSaveData'):
        properties = {}
        end_idx = 0
        section_ranges = []
        for prop, type_start in prop_types:
            start_idx = self.find_property_start(prop, type_start, offset=end_idx)
            if start_idx == end_idx - 1:
                raise ValueError(f"Property {prop} not found")
            self.data.seek(start_idx, 0)
            start_timer = time()
            properties.update(self.curr_property(path=path))
            end_timer = time()
            end_idx = self.data.tell()
            print(f"Property {prop} loaded in {end_timer - start_timer} seconds")
            section_ranges.append((start_idx, end_idx))
        return properties, section_ranges


def skip_decode(
        reader: SkipFArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name == "ArrayProperty":
        array_type = reader.fstring()
        value = {
            "skip_type": type_name,
            "array_type": array_type,
            "id": reader.optional_guid(),
            "value": reader.read(size),
            "size": size
        }
    elif type_name == "MapProperty":
        key_type = reader.fstring()
        value_type = reader.fstring()
        _id = reader.optional_guid()
        value = {
            "skip_type": type_name,
            "key_type": key_type,
            "value_type": value_type,
            "id": _id,
            "value": reader.read(size),
        }
    elif type_name == "StructProperty":
        value = {
            "skip_type": type_name,
            "struct_type": reader.fstring(),
            "struct_id": reader.guid(),
            "id": reader.optional_guid(),
            "value": reader.read(size),
        }
    else:
        raise Exception(
            f"Expected ArrayProperty or MapProperty or StructProperty, got {type_name} in {path}"
        )
    return value


def skip_encode(
        writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if "skip_type" not in properties:
        if properties['custom_type'] in PALWORLD_CUSTOM_PROPERTIES is not None:
            return PALWORLD_CUSTOM_PROPERTIES[properties["custom_type"]][1](
                writer, property_type, properties
            )
    if property_type == "ArrayProperty":
        del properties["custom_type"]
        del properties["skip_type"]
        writer.fstring(properties["array_type"])
        writer.optional_guid(properties.get("id", None))
        writer.write(properties["value"])
        return len(properties["value"])
    elif property_type == "MapProperty":
        del properties["custom_type"]
        del properties["skip_type"]
        writer.fstring(properties["key_type"])
        writer.fstring(properties["value_type"])
        writer.optional_guid(properties.get("id", None))
        writer.write(properties["value"])
        return len(properties["value"])
    elif property_type == "StructProperty":
        del properties["custom_type"]
        del properties["skip_type"]
        writer.fstring(properties["struct_type"])
        writer.guid(properties["struct_id"])
        writer.optional_guid(properties.get("id", None))
        writer.write(properties["value"])
        return len(properties["value"])
    else:
        raise Exception(
            f"Expected ArrayProperty or MapProperty or StructProperty, got {property_type}"
        )


def decode_group(
        reader: SkipFArchiveReader, type_name: str, size: int, path: str
) -> dict[str, Any]:
    if type_name != "MapProperty":
        raise Exception(f"Expected MapProperty, got {type_name}")
    value = reader.property(type_name, size, path, nested_caller_path=path)
    # Decode the raw bytes and replace the raw data
    group_map = value["value"]
    for group in group_map:
        group_type = group["value"]["GroupType"]["value"]["value"]
        if group_type == "EPalGroupType::Guild":
            group_bytes = group["value"]["RawData"]["value"]
            group["value"]["RawData"]["value"] = decode_bytes(
                reader, group_bytes, group_type
            )
    return value


def decode_bytes(
        parent_reader: SkipFArchiveReader, group_bytes: Sequence[int], group_type: str
) -> dict[str, Any]:
    reader = parent_reader.internal_copy(group_bytes, debug=False)
    reader.skip(4)  # Number of bytes skipped.
    group_data = {
        "group_type": group_type,
        "group_id": reader.guid(),
        "group_name": reader.fstring(),
        "individual_character_handle_ids": reader.tarray(instance_id_reader),
    }
    org = {
        "org_type": reader.byte(),
        "base_ids": reader.tarray(uuid_reader),
    }
    group_data |= org
    guild: dict[str, Any] = {
        "base_camp_level": reader.i32(),
        "map_object_instance_ids_base_camp_points": reader.tarray(uuid_reader),
        "guild_name": reader.fstring(),
    }
    group_data |= guild
    guild = {
        "admin_player_uid": reader.guid(),
        "players": [],
    }
    player_count = reader.i32()
    for _ in range(player_count):
        player = {
            "player_uid": reader.guid(),
            "player_info": {
                "last_online_real_time": reader.i64(),
                "player_name": reader.fstring(),
            },
        }
        guild["players"].append(player)
    group_data |= guild
    if not reader.eof():
        raise Exception("Warning: EOF not reached")
    return group_data


def encode_group(
        writer: FArchiveWriter, property_type: str, properties: dict[str, Any]
) -> int:
    if property_type != "MapProperty":
        raise Exception(f"Expected MapProperty, got {property_type}")
    del properties["custom_type"]
    group_map = properties["value"]
    for group in group_map:
        group_type = group["value"]["GroupType"]["value"]["value"]
        if group_type == "EPalGroupType::Guild":
            group["value"]["RawData"]["value"] = encode_bytes(group["value"]["RawData"]["value"])
    return writer.property_inner(property_type, properties)


def encode_bytes(p: dict[str, Any]) -> bytes:
    outer_writer = FArchiveWriter()
    writer = FArchiveWriter()
    writer.guid(p["group_id"])
    writer.fstring(p["group_name"])
    writer.tarray(instance_id_writer, p["individual_character_handle_ids"])
    writer.byte(p["org_type"])
    writer.tarray(uuid_writer, p["base_ids"])
    writer.i32(p["base_camp_level"])
    writer.tarray(uuid_writer, p["map_object_instance_ids_base_camp_points"])
    writer.fstring(p["guild_name"])
    writer.guid(p["admin_player_uid"])
    writer.i32(len(p["players"]))
    for i in range(len(p["players"])):
        writer.guid(p["players"][i]["player_uid"])
        writer.i64(p["players"][i]["player_info"]["last_online_real_time"])
        writer.fstring(p["players"][i]["player_info"]["player_name"])
    encoded_bytes = writer.bytes()
    outer_writer.u32(len(encoded_bytes))
    outer_writer.write(encoded_bytes)
    return outer_writer.bytes()


PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.CharacterSaveParameterMap.Value.RawData"] = (skip_decode, skip_encode)
PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.DynamicItemSaveData.DynamicItemSaveData.RawData"] = (
    skip_decode, skip_encode)
PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.DynamicItemSaveData.DynamicItemSaveData.ID"] = (skip_decode, skip_encode)
PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.CharacterContainerSaveData.Value.Slots"] = (skip_decode, skip_encode)
PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.CharacterContainerSaveData.Value.RawData"] = (skip_decode, skip_encode)
PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.ItemContainerSaveData.Value.BelongInfo"] = (skip_decode, skip_encode)
PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.ItemContainerSaveData.Value.Slots"] = (skip_decode, skip_encode)
PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.ItemContainerSaveData.Value.RawData"] = (skip_decode, skip_encode)

PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.GroupSaveDataMap"] = (decode_group, encode_group)
PALWORLD_CUSTOM_PROPERTIES[".worldSaveData.GroupSaveDataMap.Value.RawData"] = (skip_decode, skip_encode)

OwnerPlayerUIdSearchPrefix = b'\x0f\x00\x00\x00OwnerPlayerUId\x00\x0f\x00\x00\x00StructProperty\x00\x10\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00Guid\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
LocalIdSearchPrefix = b'\x16\x00\x00\x00LocalIdInCreatedWorld\x00\x0f\x00\x00\x00StructProperty\x00\x10\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00Guid\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


def find_id_match_prefix(encoded_bytes, prefix):
    start_idx = encoded_bytes.find(prefix) + len(prefix)
    return UUID(encoded_bytes[start_idx:start_idx + 16])


def find_all_ids_match_prefix(encoded_bytes, prefix):
    last_idx = 0
    start_idx = encoded_bytes.find(prefix)
    ids = []
    while start_idx != last_idx - 1:
        start_idx += len(prefix)
        last_idx = start_idx + 16
        ids.append(UUID(encoded_bytes[start_idx:last_idx]))
        start_idx = encoded_bytes[last_idx:].find(prefix) + last_idx
    return ids


def main():
    global host_sav_path, level_sav_path, t_level_sav_path, t_host_sav_path, host_json, level_json, targ_json, targ_lvl
    
    if None in [host_sav_path, level_sav_path, t_level_sav_path, t_host_sav_path]:
        messagebox.showerror(message='Please have all files selected before starting transfer.')
        return

    # Warn the user about potential data loss.
    response = messagebox.askyesno(title='WARNING', message='WARNING: Running this script WILL change your save files and could \
potentially corrupt your data. It is HIGHLY recommended that you make a backup \
of your save folder before continuing. Press Yes if you would like to continue.')
    if not response:
        return

    host_json_cache = copy.deepcopy(host_json)
    level_json_cache = copy.deepcopy(level_json)


    host_guid = UUID.from_str(os.path.basename(host_sav_path).split('.')[0])
    targ_guid = UUID.from_str(os.path.basename(t_host_sav_path).split('.')[0])

    host_instance_id = host_json["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]

    count = 0
    found = 0
    expected_containers = 7
    exported_map = {}
    param_maps = []
    palcount = 0
    for character_save_param in level_json["CharacterSaveParameterMap"]["value"]:
        instance_id = character_save_param["key"]["InstanceId"]["value"]
        if instance_id == host_instance_id:
            exported_map = character_save_param
            count = count + 1
            found = 1
            print('found instance')
        elif character_save_param["key"]["PlayerUId"]["value"] in ["00000000-0000-0000-0000-000000000000",
                                                                   "00000000-0000-0000-0000-000000000001"]:
            if find_id_match_prefix(character_save_param['value']['RawData']['value'],
                                    OwnerPlayerUIdSearchPrefix) == host_guid:
                param_maps.append(character_save_param)
                palcount += 1

    if not found:
        print("Couldn't find character instance data to export")
        exit()
    print("Found Character Parameter Map")
    print(f"Read {palcount} pals from source save")

    print("Searching for container data")
    inv_info = host_json["SaveData"]["value"]["inventoryInfo"]["value"]
    inv_main = inv_info["CommonContainerId"]
    inv_key = inv_info["EssentialContainerId"]
    inv_weps = inv_info["WeaponLoadOutContainerId"]
    inv_armor = inv_info["PlayerEquipArmorContainerId"]
    inv_foodbag = inv_info["FoodEquipContainerId"]
    inv_pals = host_json["SaveData"]["value"]["PalStorageContainerId"]
    inv_otomo = host_json["SaveData"]["value"]["OtomoCharacterContainerId"]

    host_main = {}
    host_key = {}
    host_weps = {}
    host_armor = {}
    host_foodbag = {}
    host_pals = {}
    host_otomo = {}
    count = 0

    for container in level_json["CharacterContainerSaveData"]["value"]:
        container_id = container["key"]["ID"]["value"]
        if container_id == inv_pals["value"]["ID"]["value"]:
            print("Found host pal inventory")
            host_pals = container
            count = count + 1
        elif container_id == inv_otomo["value"]["ID"]["value"]:
            print("Found host otomo inventory")
            host_otomo = container
            count = count + 1
        if count >= 2:
            print("Found all pal containers")
            break

    dynamic_guids = set()
    for container in level_json["ItemContainerSaveData"]["value"]:
        container_id = container["key"]["ID"]["value"]
        if container_id == inv_main["value"]["ID"]["value"]:
            print("Found host main inventory")
            dynamic_guids |= set(find_all_ids_match_prefix(container['value']['Slots']['value'], LocalIdSearchPrefix))
            host_main = container
            count = count + 1
        elif container_id == inv_key["value"]["ID"]["value"]:
            print("Found host key inventory")
            # Potentially do not need the following line as there might not be a dyanmic key item
            dynamic_guids |= set(find_all_ids_match_prefix(container['value']['Slots']['value'], LocalIdSearchPrefix))
            host_key = container
            count = count + 1
        elif container_id == inv_weps["value"]["ID"]["value"]:
            print("Found host weapon inventory")
            dynamic_guids |= set(find_all_ids_match_prefix(container['value']['Slots']['value'], LocalIdSearchPrefix))
            host_weps = container
            count = count + 1
        elif container_id == inv_armor["value"]["ID"]["value"]:
            print("Found host armor inventory")
            dynamic_guids |= set(find_all_ids_match_prefix(container['value']['Slots']['value'], LocalIdSearchPrefix))
            host_armor = container
            count = count + 1
        elif container_id == inv_foodbag["value"]["ID"]["value"]:
            print("Found host food bag inventory")
            dynamic_guids |= set(find_all_ids_match_prefix(container['value']['Slots']['value'], LocalIdSearchPrefix))
            host_foodbag = container
            count = count + 1
        if count >= expected_containers:
            print("Found all target containers")
            break
    dynamic_guids.remove(UUID(b'\x00' * 16))

    dynamic_container_level_json = level_json['DynamicItemSaveData']['value']['values']
    level_additional_dynamic_containers = []
    for dynamic_container in dynamic_container_level_json:
        LocalIdInCreatedWorld = find_id_match_prefix(dynamic_container['ID']['value'], LocalIdSearchPrefix)
        if LocalIdInCreatedWorld in dynamic_guids:
            level_additional_dynamic_containers.append((dynamic_container, LocalIdInCreatedWorld))

    if count < expected_containers:
        print("Missing container info! Only found " + str(count))
        exit()

    # host_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"] = targ_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"]
    # host_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"] = targ_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]

    char_instanceid = targ_json["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]

    print("Transferring profile data...")
    if "TechnologyPoint" in host_json["SaveData"]["value"]:
        targ_json["SaveData"]["value"]["TechnologyPoint"] = host_json["SaveData"]["value"]["TechnologyPoint"]
    else:
        if "TechnologyPoint" in targ_json["SaveData"]["value"]:
            targ_json["SaveData"]["value"]["TechnologyPoint"]["value"] = 0

    if "bossTechnologyPoint" in host_json["SaveData"]["value"]:
        targ_json["SaveData"]["value"]["bossTechnologyPoint"] = host_json["SaveData"]["value"]["bossTechnologyPoint"]
    else:
        if "bossTechnologyPoint" in targ_json["properties"]["SaveData"]["value"]:
            targ_json["SaveData"]["value"]["bossTechnologyPoint"]["value"] = 0
    targ_json["SaveData"]["value"]["UnlockedRecipeTechnologyNames"] = host_json["SaveData"]["value"][
        "UnlockedRecipeTechnologyNames"]
    if 'RecordData' in host_json["SaveData"]["value"]:
        targ_json["SaveData"]["value"]["RecordData"] = host_json["SaveData"]["value"]["RecordData"]
        targ_json["SaveData"]["value"]["PlayerCharacterMakeData"] = host_json["SaveData"]["value"]["PlayerCharacterMakeData"]

    for i, char_save_instance in enumerate(targ_lvl["CharacterSaveParameterMap"]["value"]):
        instance_id = char_save_instance["key"]["InstanceId"]["value"]
        if instance_id == char_instanceid:
            print("Existing character parameter map found, overwriting")
            char_save_instance['value'] = exported_map['value']
            break
    if i == len(targ_lvl["CharacterSaveParameterMap"]["value"]):
        print("Couldn't find character paramater map, aborting")
        exit()

    print("Searching for target containers")

    inv_info = targ_json["SaveData"]["value"]["inventoryInfo"]["value"]
    inv_main = inv_info["CommonContainerId"]
    inv_key = inv_info["EssentialContainerId"]
    inv_weps = inv_info["WeaponLoadOutContainerId"]
    inv_armor = inv_info["PlayerEquipArmorContainerId"]
    inv_foodbag = inv_info["FoodEquipContainerId"]

    host_inv_pals = inv_pals
    host_inv_otomo = inv_otomo
    inv_pals = targ_json["SaveData"]["value"]["PalStorageContainerId"]
    inv_otomo = targ_json["SaveData"]["value"]["OtomoCharacterContainerId"]

    group_id = None
    targ_uid = targ_json["SaveData"]["value"]["IndividualId"]["value"]["PlayerUId"]["value"]
    for group_data in targ_lvl["GroupSaveDataMap"]["value"]:
        if group_data["value"]["GroupType"]["value"]["value"] == "EPalGroupType::Guild":
            if targ_uid in [player_item['player_uid'] for player_item in
                            group_data["value"]["RawData"]["value"]["players"]]:
                group_id = group_data["value"]["RawData"]["value"]['group_id']
                guild_items_json = group_data["value"]["RawData"]["value"]["individual_character_handle_ids"]
                break

    if group_id is None:
        print('Guild ID not found, aboorting')
        exit()
    guild_item_instances = set()
    for guild_item in guild_items_json:
        guild_item_instances.add(str(guild_item['instance_id']))

    for pal_param in param_maps:
        pal_data = pal_param['value']['RawData']['value']
        slot_id_idx = pal_data.find(b'\x07\x00\x00\x00SlotID\x00\x0f\x00\x00\x00StructProperty\x00')
        if slot_id_idx == -1:
            continue
        pal_container_id_bytes = pal_data[slot_id_idx + 217:slot_id_idx + 233]
        pal_data_bytearray = bytearray(pal_data)
        if pal_container_id_bytes == host_inv_pals["value"]["ID"]["value"].raw_bytes:
            pal_data_bytearray[slot_id_idx + 217:slot_id_idx + 233] = inv_pals["value"]["ID"]["value"].raw_bytes
        elif pal_container_id_bytes == host_inv_otomo["value"]["ID"]["value"].raw_bytes:
            pal_data_bytearray[slot_id_idx + 217:slot_id_idx + 233] = inv_otomo["value"]["ID"]["value"].raw_bytes
        player_uid_start_idx = pal_data.find(OwnerPlayerUIdSearchPrefix) + len(OwnerPlayerUIdSearchPrefix)
        pal_data_bytearray[player_uid_start_idx:player_uid_start_idx + 16] = targ_uid.raw_bytes
        pal_data_bytearray[-16:] = group_id.raw_bytes
        pal_param['value']['RawData']['value'] = bytes(pal_data_bytearray)
        # print(UUID(pal_data[-16:]), UUID(pal_param['value']['RawData']['value'][-16:]))
        if pal_param["key"]["InstanceId"]["value"] not in guild_item_instances:
            guild_items_json.append(
                {"guid": pal_param["key"]["PlayerUId"]["value"], "instance_id": pal_param["key"]["InstanceId"]["value"]})


    new_character_save_param_map = []
    removed = 0
    for entity in targ_lvl["CharacterSaveParameterMap"]["value"]:
        if find_id_match_prefix(entity['value']['RawData']['value'], OwnerPlayerUIdSearchPrefix) == targ_uid:
            removed += 1
            continue
        new_character_save_param_map.append(entity)
    new_character_save_param_map += param_maps
    targ_lvl["CharacterSaveParameterMap"]["value"] = new_character_save_param_map
    print(f"Removed {removed} pals from the original character in the target world")
    print(f"Appended {len(param_maps)} pals of data from the source character")


    count = 0
    # TODO: check if direct overwrite is working or not.
    for container in targ_lvl["CharacterContainerSaveData"]["value"]:
        container_id = container["key"]["ID"]["value"]
        if container_id == inv_pals["value"]["ID"]["value"]:
            container['value'] = host_pals["value"]
            count += 1
        elif container_id == inv_otomo["value"]["ID"]["value"]:
            container['value'] = host_otomo["value"]
            count += 1
        if count >= 2:
            print("Found all pal containers")
            break


    for container in targ_lvl["ItemContainerSaveData"]["value"]:
        container_id = container["key"]["ID"]["value"]
        if container_id == inv_main["value"]["ID"]["value"]:
            print("Found main inventory in target")
            container["value"] = host_main["value"]
            count += 1
        elif container_id == inv_key["value"]["ID"]["value"]:
            print("Found key inventory in target")
            container["value"] = host_key["value"]
            count += 1
        elif container_id == inv_weps["value"]["ID"]["value"]:
            print("Found weapon inventory in target")
            container["value"] = host_weps["value"]
            count += 1
        elif container_id == inv_armor["value"]["ID"]["value"]:
            print("Found armor inventory in target")
            container["value"] = host_armor["value"]
            count += 1
        elif container_id == inv_foodbag["value"]["ID"]["value"]:
            print("Found food bag inventory in target")
            container["value"] = host_foodbag["value"]
            count += 1
        if count >= expected_containers:
            print("Found all target containers")
            break

    target_dynamic_containers = targ_lvl['DynamicItemSaveData']['value']['values']
    repeated_indices = set()
    for i, target_dynamic_container in enumerate(target_dynamic_containers):
        target_guid = find_id_match_prefix(target_dynamic_container['ID']['value'], LocalIdSearchPrefix)
        if target_guid in dynamic_guids:
            for j, (dynamic_container, container_local_id) in enumerate(level_additional_dynamic_containers):
                if target_guid == container_local_id:
                    target_dynamic_containers[i] = dynamic_container
                    repeated_indices.add(j)
                    break
    targ_lvl['DynamicItemSaveData']['value']['values'] += [container for i, (container, local_id) in
                                                           enumerate(level_additional_dynamic_containers) if
                                                           i not in repeated_indices]

    output_data = SkipFArchiveWriter(custom_properties=PALWORLD_CUSTOM_PROPERTIES).write_sections(targ_lvl, target_section_ranges, target_raw_gvas)

    gvas_to_sav(t_level_sav_path, output_data)
    targ_json_gvas.properties = copy.deepcopy(targ_json)
    gvas_to_sav(t_host_sav_path, targ_json_gvas.write())

    host_json = host_json_cache
    level_json = level_json_cache

    print("Saved all data successfully. PLEASE DON'T BREAK")
    messagebox.showinfo(message='Transfer finished! You may continue transferring more players or close the windows now.')


def sav_to_gvas(file):
    with open(file, 'rb') as f:
        data = f.read()
        raw_gvas, _ = decompress_sav_to_gvas(data)
    return raw_gvas


def gvas_to_sav(file, gvas_data):
    if (
        "Pal.PalWorldSaveGame" in target_header.save_game_class_name
        or "Pal.PalLocalWorldSaveGame" in target_header.save_game_class_name
        ):
        save_type = 0x32
    else:
        save_type = 0x31
    sav_file_data = compress_gvas_to_sav(
        gvas_data, save_type
    )
    with open(file, 'wb') as out:
        out.write(sav_file_data)


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
        loaded_file = sav_to_gvas(path)
    return loaded_file

def source_player_file():
    global host_sav_path, source_player_path_label, host_json
    tmp = select_file()
    if tmp:  # If a file was selected, update the label
        basename = os.path.basename(tmp).split('.')[0]
        if len(basename) != 32 or not ishex(basename):
            messagebox.showerror(message="Selected file is not a player save file! They are of the format: {PlayerID}.sav")
            return
        raw_gvas = load_file(tmp)
        if not raw_gvas:
            messagebox.showerror(message="Invalid files, files must be .sav")
            return
        host_json = GvasFile.read(raw_gvas).properties
        source_player_path_label.config(text=tmp)
        host_sav_path = tmp

def source_level_file():
    global level_sav_path, source_level_path_label, level_json
    tmp = select_file()
    if tmp:
        if not tmp.endswith('Level.sav') and not tmp.endswith('Level.sav.json'):
            messagebox.showerror("Incorrect file", "This is not the right file. Please select the Level.sav file.")
            return
        raw_gvas = load_file(tmp)
        if not raw_gvas:
            messagebox.showerror(message="Invalid files, files must be .sav")
            return
        level_json, _ = SkipFArchiveReader(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES).load_sections([
            ('CharacterSaveParameterMap', MAP_START),
            ('ItemContainerSaveData', MAP_START),
            ('DynamicItemSaveData', ARRAY_START),
            ('CharacterContainerSaveData', MAP_START),
            ('GroupSaveDataMap', MAP_START)],
            path='.worldSaveData'
        )
        source_level_path_label.config(text=tmp)
        level_sav_path = tmp

def target_player_file():
    global t_host_sav_path, target_player_path_label, targ_json_gvas, targ_json, target_json_cache
    tmp = select_file()
    if tmp:
        basename = os.path.basename(tmp).split('.')[0]
        if len(basename) != 32 or not ishex(basename):
            messagebox.showerror(message="Selected file is not a player save file! They are of the format: {PlayerID}.sav")
            return
        raw_gvas = load_file(tmp)
        if not raw_gvas:
            messagebox.showerror(message="Invalid files, files must be .sav")
            return
        targ_json_gvas = GvasFile.read(raw_gvas)
        targ_json = targ_json_gvas.properties
        target_player_path_label.config(text=tmp)
        t_host_sav_path = tmp

def target_level_file():
    global t_level_sav_path, target_level_path_label, targ_lvl, target_level_cache, target_section_ranges, target_header, target_raw_gvas
    tmp = select_file()
    if tmp:
        if not tmp.endswith('Level.sav') and not tmp.endswith('Level.sav.json'):
            messagebox.showerror("Incorrect file", "This is not the right file. Please select the Level.sav file.")
            return
        raw_gvas = load_file(tmp)
        if not raw_gvas:
            messagebox.showerror(message="Invalid files, files must be .sav")
            return
        reader = SkipFArchiveReader(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
        target_header = GvasHeader.read(reader)
        target_raw_gvas = raw_gvas
        targ_lvl, target_section_ranges = reader.load_sections([
            ('CharacterSaveParameterMap', MAP_START),
            ('ItemContainerSaveData', MAP_START),
            ('DynamicItemSaveData', ARRAY_START),
            ('CharacterContainerSaveData', MAP_START),
            ('GroupSaveDataMap', MAP_START)],
            path='.worldSaveData'
        )
        target_level_path_label.config(text=tmp)
        t_level_sav_path = tmp

def on_exit():
    global level_sav_path, host_sav_path, t_level_sav_path, t_host_sav_path
    print("Application is closing")
    root.destroy()  # Ensures the application window closes cleanly

level_sav_path, host_sav_path, t_level_sav_path, t_host_sav_path = None, None, None, None
level_json, host_json, targ_lvl, targ_json = None, None, None, None
target_section_ranges, target_header, target_raw_gvas, targ_json_gvas = None, None, None, None

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