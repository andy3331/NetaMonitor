This monitors NETA northhampton vape menu.
It then posts the menu, and new items to a discord channel of your choosing.
  
12/25/19 - I havent set up scheduling, I'm just running it off a daily scheduled task locally (kicks off script at 9 am every day.)

Also I have moved my webhook urls to productionwebhook.txt and testwebhook.txt files. This is so I don't have my discord webhooks exposed in GIT.  

To use elsewhere you would need to create a discord webhook on your server and paste into one of these files.

To point to which key to use, change environment variable to prod or test.