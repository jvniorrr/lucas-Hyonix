import discord, logging, json, os
from dotenv import load_dotenv
from discord.ext import commands
from discord import Client
from models import hyonix, databaseMongo


load_dotenv(os.path.join(os.getcwd(), ".env"))

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
HYONIX_TOKEN = os.getenv("HYONIX_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEV_ID = os.getenv("DEV_ID")


logging.basicConfig(datefmt="%I:%M:%S", format=f"[%(levelname)s] [%(asctime)s.%(msecs)03d] - > %(message)s",level=logging.INFO)
bot = commands.Bot(command_prefix='-', heartbeat_timeout=30, self_bot=False)
bot.remove_command('help')



@bot.event
async def on_ready():
    logging.info(f'{bot.user} bot is now online!')


# COMMANDS
@bot.command()
@discord.ext.commands.core.has_permissions(administrator=True)
async def entry(ctx, member:discord.Member, serverid:int):
    # create a connection to the DB
    database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)

    # retrieve info from hyonix
    hyonix_api = hyonix.HyonixAPI(HYONIX_TOKEN)
    
    serverInformation = hyonix_api.getServerDetails(serverid=serverid)

    #  make sure there is a server with that ID passed
    if serverInformation == None:
        logging.info("Server ID is not valid, please provide a valid ID.")
        await ctx.channel.send("Invalid Server ID, please provide a valid Server ID.")
        return


    # check if user is already stored in db
    current_user = database.checkCurrentUser(member.id)

    # if current user already stored dont enter a new one
    if current_user == True:
        # send msg to client & just append to their current entry
        logging.info("A User with that ID is already stored. Updating their current servers.")
        updated = hyonix_api.updateUser(member.id, serverInformation)
        if updated == True:
            await ctx.channel.send("Successfully updated the Users current / active servers.")
            return
        else:
            await ctx.channel.send("Unknown error updating the users information. Making Developer aware.")
            developer = bot.get_user(DEV_ID)
            await developer.create_dm().send(f"Error occured updating User: {member.mention}")
            return

    # if ths user is not in the DB
    else:
        # assure that the entry was entered to DB
        entered = database.entry(member.name. member.id, serverInformation)
        if entered == True:
            logging.info("Successfully added a new entry to the DB.")
            await ctx.channel.send("Successfully added a new entry to the database.")
            return
        
        #  if the entry was unsuccessfull
        else:
            await ctx.channel.send("Unknown error creating a new users database entry. Making Developer aware.")
            developer = bot.get_user(DEV_ID)
            await developer.create_dm().send(f"Error occured creating a new entry for User: {member.mention}")
            return

@bot.command()
@discord.ext.commands.core.has_permissions(administrator=True)
async def removeEntry(ctx, member:discord.Member):
    """Method to remove a user from the database
    
    Parameters
    -----------
    member : discord.Member
        - discord member that is being removed from the DB
    """

    database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)
    
    removed = False
    # check if the user is stored in the DB
    current_user = database.checkCurrentUser(member.id)

    if current_user == True:
        removed = database.removeUser(member.id)
        if removed == True:
            await ctx.channel.send(f"{member.name} was successfully removed from the database.")
            return
        else:
            await ctx.channel.send("Unknown error occured removing User from the database. Making Developer aware.")
            developer = bot.get_user(DEV_ID)
            await developer.create_dm().send(f"Error occured removing User: {member.mention} from the database.")
            return
    else:
        await ctx.channel.send(f"{member.name} is not stored in the database. Provide a member that has an active sub.")
        return




# COMMANDS SPECIFICALLY FOR USER ACTIONS
@bot.command()
@discord.ext.commands.dm_only()
@commands.cooldown(1, 60 * 5, commands.BucketType.member)
async def restartServer(ctx, server_ip:str):
    """Method to reset a server / reboot it. This force shuts down and starts up."""

    database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)

    hyonix_api = hyonix.HyonixAPI(HYONIX_TOKEN)

    current_user = database.checkCurrentUser(ctx.author.id)

    #  assure that the user is stored in the DB
    if current_user == True:
        # retrieve the users current information
        userInformation = database.returnUserInformation(ctx.author.id)

        for server in userInformation["servers"]:
            if server["server_ip"] == server_ip:
                reset = hyonix_api.serverRestart(server["server_id"])
                if reset == True:
                    await ctx.channel.send(f"Successfully restarted Server: {server_ip}")
                    return