# PalworldCharacterTransfer
Credit to https://www.reddit.com/r/Palworld/comments/19dhpjn/server_to_server_character_transfer_script/ and https://github.com/EternalWraith/PalEdit/tree/main

This script transfers character between worlds in Palworld, which allows friends to transfer their characters to each other's server without losing one's progress.

The script transfers the character and all its pals on your team and in your inventory, items on the character, and progress only and **does not transfer any map objects, items in chests from the original world, and pals working at your base. So move them into the inventory if you want them transferred along with you)**


This is best suited if you want to join your friend's world with your pals and progress

Running python char-export.py allows one to select source/target player saves and source/target level.sav files to transfer all data of the player including level, items, and pals across.
Or you can just decompress char-export.zip and run char-export.exe

The save files are usually at
C:\Users\<username>\AppData\Local\Pal\Saved\SaveGames\<SteamID>\<Original Server Folder>
for co-op saves
For server saves, go to the dedicated server's file location through steam.
You need at least 4 files to complete the transfer: The source player character save file in Players/ folder, the source world's level.sav file, the target player character save file, and the target world's Level.sav file
Note: The player from the old world must be at least LV 2, and each player who wants to transfer their saves to a new world must first create a character in the new world, so that a target player save is present for transferring!
You want to make sure you can find the character save on the server, by first taking note of the exsiting characters in the Player/ folder and look for the additional one after you create one of your own on the server.
For local co-op saves, if you are the host, the character file is always 000000...001.sav
For other player's save, just know that their ID does not change across worlds, and therefore their character file's name is the same for your co-op world and for the server's world.

**Note: The player from the old world must be at least LV 2, and each player who wants to transfer their saves to a new world must first create a character in the new world, so that a target player save is present for transferring!**
