# PalworldCharacterTransfer
Credit to https://www.reddit.com/r/Palworld/comments/19dhpjn/server_to_server_character_transfer_script/ and https://github.com/EternalWraith/PalEdit/tree/main

This script transfers character between worlds in Palworld, which allows friends to transfer their characters to each other's server without losing one's progress.

The script transfers the character and all its pals on your team and in your inventory, items on the character, and progress only and **does not transfer any map objects, items in chests from the original world, and pals working at your base. (So move them into the inventory if you want them transferred along with you)**


This is best suited if you want to join your friend's world with your pals and progress

Running python char-export.py allows one to select source/target player saves and source/target level.sav files to transfer all data of the player including level, items, and pals across.
Or you can just decompress char-export.zip and run char-export.exe

The save files are usually at
C:\Users\<username>\AppData\Local\Pal\Saved\SaveGames\<SteamID>\<Original Server Folder>
for co-op saves.

For server saves, go to the dedicated server's file location through steam.

You need at least 4 files to complete the transfer: The source player character save file in Players/ folder, the source world's level.sav file, the target player character save file, and the target world's Level.sav file

Note: The player from the old world must be at least LV 2, and each player who wants to transfer their saves to a new world must first create a character in the new world, so that a target player save is present for transferring!

You want to make sure you can find the character save on the server, by first taking note of the exsiting characters in the Player/ folder and look for the additional one after you create one of your own on the server.

For local co-op saves, if you are the host, the character file is always 000000...001.sav

For other player's save, just know that their ID does not change across worlds, and therefore their character file's name is the same for your co-op world and for the server's world.

**Note: The player from the old world must be at least LV 2, and each player who wants to transfer their saves to a new world must first create a character in the new world, so that a target player save is present for transferring!**

这个脚本用于在Palworld世界间转移角色，允许朋友们将他们的角色转移到彼此的服务器上，而不会失去任何进度。

该脚本将角色及其所有队伍和终端中的伙伴、角色身上的物品以及进度转移，但不会转移任何地图对象、原世界中箱子里的物品以及基地中工作的伙伴。（如果你想将它们一起转移，请将它们移动到身上/终端中）

如果你想带着你的伙伴和进度加入朋友的世界，这将是最适合的选择。

脚本使用方式为运行python char-export-zh.py又或者解压char-export-zh.zip并运行char-export-zh.exe

对于合作模式的存档，存档文件通常位于
C:\Users<用户名>\AppData\Local\Pal\Saved\SaveGames\<SteamID>\<世界文件夹>

对于服务器存档，请通过Steam进入服务器的文件位置。

你需要至少4个文件来完成转移：源玩家角色存档文件（在Players/中），源世界的level.sav文件，目标玩家角色存档，以及目标世界的Level.sav文件

注意：旧世界的玩家至少需达到2级，每个想将存档转移到新世界的玩家必须首先在新世界创建一个角色，以便有一个目标玩家存档用于转移！

你需要确保能在目标世界的存档文件里能找到你的角色存档，你可以首先记下Player/文件夹中现有的角色，然后在目标世界上创建自己的角色后查找新增的角色存档。

对于本地合作模式的存档，如果你是主机，角色文件始终是000000...001.sav

对于其他玩家的存档，只需知道他们的ID在不同世界间不会改变，因此他们在你的合作世界和服务器世界的角色文件名是相同的。