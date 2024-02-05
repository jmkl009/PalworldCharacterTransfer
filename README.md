# PalworldCharacterTransfer

This script transfers character between worlds in Palworld, which allows friends to transfer their characters to each other's server without losing one's progress.

The script transfers the character and all its pals on your team and in your inventory, items on the character, and progress.
It does **not** transfer map objects, items in chests and pals working at your base.
Move items into your inventory / pals into your team if you want to transfer them.

This is best suited if you want to join your friend's world with your pals and progress.

## How to use this script

Running python char-export.py opens a graphical user interface to select source/target player saves and source/target level.sav files.

```
python3 ./
```

If you do not have Python installed, you can download a packaged .exe executable from the [release page](https://github.com/jmkl009/PalworldCharacterTransfer/releases).

Download the latest `char-export.zip`, unpack it and run `char-export.exe`

## Wehre to find the save-**files**

The save files are usually located at
C:\Users\<username>\AppData\Local\Pal\Saved\SaveGames\<SteamID>\<Original Server Folder>
for co-op saves.

For server saves, go to the dedicated server's file location through steam.

You need at least 4 files to complete the transfer: The source player character save file in Players/ folder, the source world's level.sav file, the target player character save file, and the target world's Level.sav file

https://tree.nathanfriend.io/?s=(%27options!(%27fancy!true~fullPathE~trailingSlashE~rootDotE)~N(%27N%27SaQGamesHRsteam-id%3EH*RwJ-id%3EBbackupBLKI*****FThe%20wJ%20%2F%20lKCBLKMetaIBPlayersB*00000...0001AhostB*12345...6789AguestBWJOptionIH%27)~Qrsion!%271%27)U%20AIFcharacterC%20of%20BH***C%20saQ-fileE!falseFU%3C-%20H%5CnI.savJorldKeQlNsource!QveR*%3CU*%20%01URQNKJIHFECBA*

SaveGames
└── <steam-id>
    └── <world-id>
        ├── backup
        ├── Level.sav             <- The world / level save-file
        ├── LevelMeta.sav
        ├── Players
        │   ├── 00000...0001.sav   <- character save-file of host
        │   └── 12345...6789.sav   <- character save-file of guest
        └── WorldOption.sav


## How to identify the player save-files

You want to make sure you can find the character save on the server, by first taking note of the exsiting characters in the Player/ folder and look for the additional one after you create one of your own on the server.

For local co-op saves, if you are the host, the character file is always 000000...001.sav

For other player's save, just know that their ID does not change across worlds, and therefore their character file's name is the same for your co-op world and for the server's world.

**Note: The player from the old world must be at least LV 2, and each player who wants to transfer their saves to a new world must first create a character in the new world, so that a target player save is present for transferring!**

## Credits

Credit to https://www.reddit.com/r/Palworld/comments/19dhpjn/server_to_server_character_transfer_script/ and https://github.com/EternalWraith/PalEdit/tree/main

## Chinese Translation

这个脚本用于在 Palworld 世界间转移角色，允许朋友们将他们的角色转移到彼此的服务器上，而不会失去任何进度。

该脚本将角色及其所有队伍和终端中的伙伴、角色身上的物品以及进度转移，但不会转移任何地图对象、原世界中箱子里的物品以及基地中工作的伙伴。（如果你想将它们一起转移，请将它们移动到身上/终端中）

如果你想带着你的伙伴和进度加入朋友的世界，这将是最适合的选择。

脚本使用方式为运行 python char-export-zh.py 又或者解压 char-export-zh.zip 并运行 char-export-zh.exe

对于合作模式的存档，存档文件通常位于
C:\Users<用户名>\AppData\Local\Pal\Saved\SaveGames\<SteamID>\<世界文件夹>

对于服务器存档，请通过 Steam 进入服务器的文件位置。

你需要至少 4 个文件来完成转移：源玩家角色存档文件（在 Players/中），源世界的 level.sav 文件，目标玩家角色存档，以及目标世界的 Level.sav 文件

注意：旧世界的玩家至少需达到 2 级，每个想将存档转移到新世界的玩家必须首先在新世界创建一个角色，以便有一个目标玩家存档用于转移！

你需要确保能在目标世界的存档文件里能找到你的角色存档，你可以首先记下 Player/文件夹中现有的角色，然后在目标世界上创建自己的角色后查找新增的角色存档。

对于本地合作模式的存档，如果你是主机，角色文件始终是 000000...001.sav

**对于其他玩家的存档**，只需知道他们的 ID 在不同世界间不会改变，因此他们在你的合作世界和服务器世界的角色文件名是相同的。
