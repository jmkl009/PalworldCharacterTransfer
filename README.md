```
██████╗  █████╗ ██╗     ██╗    ██╗ ██████╗ ██████╗ ██╗     ██████╗       
██╔══██╗██╔══██╗██║     ██║    ██║██╔═══██╗██╔══██╗██║     ██╔══██╗      
██████╔╝███████║██║     ██║ █╗ ██║██║   ██║██████╔╝██║     ██║  ██║      
██╔═══╝ ██╔══██║██║     ██║███╗██║██║   ██║██╔══██╗██║     ██║  ██║      
██║     ██║  ██║███████╗╚███╔███╔╝╚██████╔╝██║  ██║███████╗██████╔╝      
╚═╝     ╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝       
                                                                         
 ██████╗██╗  ██╗ █████╗ ██████╗  █████╗  ██████╗████████╗███████╗██████╗ 
██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
██║     ███████║███████║██████╔╝███████║██║        ██║   █████╗  ██████╔╝
██║     ██╔══██║██╔══██║██╔══██╗██╔══██║██║        ██║   ██╔══╝  ██╔══██╗
╚██████╗██║  ██║██║  ██║██║  ██║██║  ██║╚██████╗   ██║   ███████╗██║  ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                                         
████████╗██████╗  █████╗ ███╗   ██╗███████╗███████╗███████╗██████╗       
╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔════╝██╔════╝██╔══██╗      
   ██║   ██████╔╝███████║██╔██╗ ██║███████╗█████╗  █████╗  ██████╔╝      
   ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██╔══╝  ██╔══╝  ██╔══██╗      
   ██║   ██║  ██║██║  ██║██║ ╚████║███████║██║     ███████╗██║  ██║      
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝      
```

---

### 🗞️ NEWS 

#### New Base Transfer Feature

 The script is now compatible with base transfer methods. (This does not mean it no longer transfers single characters over, just that there is a way to use this alongside base transfer methods.) For those who don't know how to transfer the world with buildings over, simply:

1. Copy your Level.sav file from the old world to the new world.
2. Each player creates a new character in the new world.
3. Transfer each corresponding characters while keeping the old guild ID from the old world, check the "Keep Old Guild ID After Transfer" box at the bottom-left corner of the GUI.

# PalworldCharacterTransfer

- [PalworldCharacterTransfer](#palworldcharactertransfer)
  - [How to use this script](#how-to-use-this-script)
  - [Where to find the save-files](#where-to-find-the-save-files)
  - [An example](#an-example)
  - [How to identify the player save-files](#how-to-identify-the-player-save-files)
  - [How to keep Guild ID after transfer](#how-to-keep-guild-id-after-transfer)
  - [Credits](#credits)
- [Chinese Translation](#chinese-translation)

This script transfers character between worlds in Palworld, which allows friends to transfer their characters to each other's server without losing one's progress.

The script transfers the character and all its pals on your team and in your inventory, items on the character, and progress.
It, alone, does **not** transfer map objects, items in chests and pals working at your base.
Move items into your inventory / pals into your team if you want to transfer them.

This is best suited if you want to join your friend's world with your pals and progress.

## How to use this script

Running python char-export.py opens a graphical user interface to select source/target player saves and source/target level.sav files.

```
python3 ./char-export.py
```

If you do not have Python installed, you can download a packaged .exe standalone-executable from the [release page](https://github.com/jmkl009/PalworldCharacterTransfer/releases).

Download the latest `char-export.zip`, unpack it and run `char-export.exe`

## Where to find the save-files

The save files are usually located at
C:\Users\<username>\AppData\Local\Pal\Saved\SaveGames\<SteamID>\<Original Server Folder>
for co-op saves.

For server saves, go to the dedicated server's file location through steam.

You need at least 4 files to complete the transfer:

- The source player character save file in Players folder
- The source world's level.sav file
- The target player character save file in Players folder
- The target world's Level.sav file

## An example

Lets say we want to transfer the character from a coop world of a friend to our own world.
The friend's world would be the source, our own world the destination.

SaveGames-folder of our friend:
```
SaveGames
└── <steam-id>
    └── <source-world-id>
        ├── backup
        ├── Level.sav  ----------  <- The source world save-file
        ├── LevelMeta.sav
        ├── Players
        │   ├── 00000...0001.sav
        │   └── 12345...6789.sav   <- character save-file we want to transfer
        └── WorldOption.sav
```

Our SaveGames-folder:
```
SaveGames
└── <steam-id>
    └── <destination-world-id>
        ├── backup
        ├── Level.sav  ----------  <- The target world save-file
        ├── LevelMeta.sav
        ├── Players
        │   ├── 00000...0001.sav   <- the target player-placeholder save-file
        │   └── 98765...4321.sav
        └── WorldOption.sav
```

## How to identify the player save-files

You want to make sure you can find the character save on the server, by first taking note of the exsiting characters in the Player/ folder and look for the additional one after you create one of your own on the server.

For local co-op saves, if you are the host, the character file is always 000000...001.sav

For other player's save, just know that their ID does not change across worlds, and therefore their character file's name is the same for your co-op world and for the server's world.

**Note: The player from the old world must be at least LV 2, and each player who wants to transfer their saves to a new world must first create a character in the new world, so that a target player save is present for transferring!**

## How to keep Guild ID after transfer

By default the script sets the guild of the transferred character to the guild of the original character in the new world. If you happen to also have the base transferred from the old world, then you may encounter the issue of not being able to access your base and items.

To keep the old guild ID from the old world, check the "Keep Old Guild ID After Transfer" box at the bottom-left corner.

For those who don't know how to transfer the world with buildings over, simply move your Level.sav file from the old world to the new world.

Without checking ﻿"Keep Old Guild ID After Transfer", then you may encounter the issue of not being able to access your base and items.

## Credits

Thanks to

- https://github.com/cheahjs/palworld-save-tools/tree/main for providing save parsing tools

- https://github.com/magicbear/palworld-server-toolkit/tree/master for speed optimization startegy. The current version achieves 1/3 loading speed improvement over the original strategy.

Thanks @LeonMueller-OneAndOnly for writing this ReadMe

# Chinese Translation

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

鸣谢：

- https://github.com/cheahjs/palworld-save-tools/tree/main 提供存档解析工具

- https://github.com/magicbear/palworld-server-toolkit/tree/master 提供速度优化方案。基于此方案，现版本又将加载速度提升了1/3。
