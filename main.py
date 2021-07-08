import discord, logging, json, os
from discord import user
from dotenv import load_dotenv
from discord.ext import commands
from discord import Client
from pymongo import database
from models import hyonix, databaseMongo


load_dotenv(os.path.join(os.getcwd(), ".env"))

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
HYONIX_TOKEN = os.getenv("HYONIX_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEV_ID = os.getenv("DEV_ID")


logging.basicConfig(datefmt="%I:%M:%S", format=f"[%(levelname)s] [%(asctime)s.%(msecs)03d] - > %(message)s",level=logging.INFO)
bot = commands.Bot(command_prefix='!', heartbeat_timeout=30, self_bot=False)
bot.remove_command('help')



@bot.event
async def on_ready():
    logging.info(f'{bot.user} bot is now online!')


# COMMANDS
# @bot.command()
# @discord.ext.commands.core.has_permissions(administrator=True)
# async def entry(ctx, member:discord.Member, serverid:int):
#     # create a connection to the DB
#     database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)

#     # retrieve info from hyonix
#     hyonix_api = hyonix.HyonixAPI(HYONIX_TOKEN)
    
#     serverInformation = hyonix_api.getServerDetails(serverid=serverid)

#     #  make sure there is a server with that ID passed
#     if serverInformation == None:
#         logging.info("Server ID is not valid, please provide a valid ID.")
#         await ctx.channel.send("Invalid Server ID, please provide a valid Server ID.")
#         return


#     # check if user is already stored in db
#     current_user = database.checkCurrentUser(member.id)

#     # if current user already stored dont enter a new one
#     if current_user == True:
#         # send msg to client & just append to their current entry
#         logging.info("A User with that ID is already stored. Updating their current servers.")
#         updated = hyonix_api.updateUser(member.id, serverInformation)
#         if updated == True:
#             await ctx.channel.send("Successfully updated the Users current / active servers.")
#             return
#         else:
#             await ctx.channel.send("Unknown error updating the users information. Making Developer aware.")
#             developer = bot.get_user(DEV_ID)
#             await developer.create_dm().send(f"Error occured updating User: {member.mention}")
#             return

#     # if ths user is not in the DB
#     else:
#         # assure that the entry was entered to DB
#         entered = database.entry(member.name, member.id, serverInformation)
#         if entered == True:
#             logging.info("Successfully added a new entry to the DB.")
#             await ctx.channel.send("Successfully added a new entry to the database.")
#             return
        
#         #  if the entry was unsuccessfull
#         else:
#             await ctx.channel.send("Unknown error creating a new users database entry. Making Developer aware.")
#             developer = bot.get_user(DEV_ID)
#             await developer.create_dm().send(f"Error occured creating a new entry for User: {member.mention}")
#             return


@bot.command()
@discord.ext.commands.core.has_permissions(administrator=True)
async def adduser(ctx):

    # Retrieve the User associated with said server
    await ctx.channel.send("What user is being added?")
    # assure that the response is a user being provided.
    def check(response):
        if response.mentions[0] and response.author == ctx.author:
            # print("True")
            return True
        else:
            return False
    userResponse = await bot.wait_for('message', check=check)
    member = userResponse.mentions[0]


    #  retrieve the SERVER ID
    def checkserver(response_):
        if int(response_.content) and response_.author == ctx.author:
            return True
        else:
            return False
    await ctx.channel.send("What is the Servers ID?")
    serverID = await bot.wait_for('message', check=checkserver)


    # retrieve the next due date
    await ctx.channel.send("When is the next due date? *(format: mm-dd-yyyy)*")
    def checkDate(response):
        return response.author == ctx.author
    due_date_r = await bot.wait_for('message', check=checkDate)

    due_date = due_date_r.content

    
    # create a connection to the DB
    database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)

    # retrieve info from hyonix
    hyonix_api = hyonix.HyonixAPI(HYONIX_TOKEN)

    serverInformation = hyonix_api.getServerDetails(serverid=serverID.content)


    current_user = database.checkCurrentUser(member.id)
    


    if serverInformation == None:
        logging.info("Server ID is not valid, please provide a valid ID.")
        await ctx.channel.send("Invalid Server ID, please provide a valid Server ID.")
        return

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
            developer = await bot.fetch_user(DEV_ID)
            dmChan = await developer.create_dm()
            msg = f"Error occured updating User: {member.mention}"
            await dmChan.send(msg)
            return

    # if ths user is not in the DB
    else:
        # assure that the entry was entered to DB
        entered = database.entry(member.name, member.id, serverInformation, due_date)
        if entered == True:
            logging.info("Successfully added a new entry to the DB.")
            await ctx.channel.send("Successfully added a new entry to the database.")
            return
        
        #  if the entry was unsuccessfull
        else:
            await ctx.channel.send("Unknown error creating a new users database entry. Making Developer aware.")
            developer = await bot.fetch_user(DEV_ID)
            dmChan = await developer.create_dm()
            msg = f"Error occured creating a new entry for User: {member.mention}"
            dmChan.send(msg)
            return


@bot.command()
@discord.ext.commands.core.has_permissions(administrator=True)
async def removeuser(ctx):
    # Retrieve the User associated with said server
    await ctx.channel.send("What user is being removed?")
    # assure that the response is a user being provided.
    def check(response):
        if response.mentions[0] and response.author == ctx.author:
            # print("True")
            return True
        else:
            return False
    userResponse = await bot.wait_for('message', check=check)
    member = userResponse.mentions[0]

    # check if the user is stored
    database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)

    current_user = database.checkCurrentUser(member.id)

    if current_user == False:
        await ctx.channel.send("That user is not stored in the database. Please provide a valid user.")
        return

    #  retrieve the users information, see if the have > 1 server associated
    userInformation = database.returnUserInformation(member.id)

    if userInformation == None:
        await ctx.channel.send("Unknown error occured removing server from User from the database. Making Developer aware.")
        developer = await bot.fetch_user(DEV_ID)
        dmChan = await developer.create_dm()
        msg = f"Error occured retrieving server information for User: {member.mention} database."
        await dmChan.send(msg)
        return



    elif userInformation != None:
        if len(userInformation["servers"]) > 1:
            #  ask the admin what server they want removed
            await ctx.channel.send("What server IP would you like removed?")

            def checkServers(response):
                return response.author == ctx.author
            
            userResponse = await bot.wait_for("message", check=checkServers)

            serverIP = userResponse.content

            for server in userInformation["servers"]:
                if serverIP == server["server_ip"]:
                    removed = database.removeServer(discord_id=member.id, server_ip=serverIP)
                    #  check if it was removed succesfully
                    if removed == True:
                        await ctx.channel.send(f"Succesfully removed Server IP: {serverIP}")
                        return
                    else:
                        await ctx.channel.send("Unknown error occured removing server from User from the database. Making Developer aware.")
                        developer = await bot.fetch_user(DEV_ID)
                        dmChan =await developer.create_dm()
                        msg = f"Error occured removing User: {member.mention} server from the database."
                        await dmChan.send(msg)
                        return

            # return a msg if that ip isnt found in loop above
            await ctx.channel.send(f"Provide a valid server IP for user: {member.mention}")
                        
        else:
            removed = database.removeUser(member.id)
            if removed == True:
                await ctx.channel.send("Successfully removed user from the database.")
            else:
                await ctx.channel.send("Unknown error occured removing User from the database. Making Developer aware.")
                developer = await bot.fetch_user(DEV_ID)
                dmChan = await developer.create_dm()
                msg = f"Error occured removing User: {member.mention} from the database."
                await dmChan.send(msg)
                return
    return


@bot.command()
@discord.ext.commands.core.has_permissions(administrator=True)
async def renew(ctx):
    # Retrieve the User associated with said server
    await ctx.channel.send("What user is being renewed?")
    def check(response):
        if response.mentions[0] and response.author == ctx.author:
            return True
        else:
            return False
    userResponse = await bot.wait_for('message', check=check)
    member = userResponse.mentions[0]

    # check if the user is stored
    database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)

    current_user = database.checkCurrentUser(member.id)

    if current_user == False:
        await ctx.channel.send("That user is not stored in the database. Please provide a valid user.")
        return
    
    await ctx.channel.send("What is the new renewal date? *(format: mm-dd-yyyy)*")

    def checkDate(response):
        if len(response.content.split("-")) == 3 and response.author == ctx.author:
            return True
        else:
            return False

    dateResponse = await bot.wait_for("message", check=checkDate)

    # update the database
    renewedStatus = database.renewalDate(member.id, dateResponse.content)

    if renewedStatus == False:
        await ctx.channel.send("Unknown error updating the users renewal date. Making Developer aware.")
        developer = await bot.fetch_user(DEV_ID)
        dmChan = await developer.create_dm()
        msg = f"Error occured updating the renewal date for User: {member.mention}"
        await dmChan.send(msg)
        return
    
    else:
        await ctx.channel.send("Successfully update the next due date for user.")
        return
            

    


@bot.command()
@commands.cooldown(1, 15, commands.BucketType.member)
async def test(ctx):
    logging.info("Test cmd called.")
    msg = f"Test Message. Bot working!"
    developer = await bot.fetch_user(int(DEV_ID))
    dmChan = await developer.create_dm()
    await dmChan.send(msg)
    return


# @bot.command()
# @discord.ext.commands.core.has_permissions(administrator=True)
# async def removeEntry(ctx, member:discord.Member):
#     """Method to remove a user from the database
    
#     Parameters
#     -----------
#     member : discord.Member
#         - discord member that is being removed from the DB
#     """

#     database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)
    
#     removed = False
#     # check if the user is stored in the DB
#     current_user = database.checkCurrentUser(member.id)

#     if current_user == True:
#         removed = database.removeUser(member.id)
#         if removed == True:
#             await ctx.channel.send(f"{member.name} was successfully removed from the database.")
#             return
#         else:
#             await ctx.channel.send("Unknown error occured removing User from the database. Making Developer aware.")
#             developer = bot.get_user(DEV_ID)
#             await developer.create_dm().send(f"Error occured removing User: {member.mention} from the database.")
#             return
#     else:
#         await ctx.channel.send(f"{member.name} is not stored in the database. Provide a member that has an active sub.")
#         return




# COMMANDS SPECIFICALLY FOR USER ACTIONS
@bot.command()
@discord.ext.commands.dm_only()
@commands.cooldown(1, 60 * 5, commands.BucketType.member)
async def restartserver(ctx, server_ip:str):
    """Method to reset a server / reboot it. This force shuts down and starts up."""

    database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)

    hyonix_api = hyonix.HyonixAPI(HYONIX_TOKEN)

    current_user = database.checkCurrentUser(ctx.author.id)

    #  assure that the user is stored in the DB
    if current_user == True:
        # retrieve the users current information
        userInformation = database.returnUserInformation(ctx.author.id)

        if userInformation == None:
            return



        for server in userInformation["servers"]:
            if server["server_ip"] == server_ip:
                reset = hyonix_api.serverRestart(server["server_id"])
                if reset == True:
                    await ctx.channel.send(f"Successfully restarted Server: {server_ip}")
                    return
        await ctx.channel.send("Provide a valid server IP to perform actions.")
        return

@bot.command()
@discord.ext.commands.dm_only()
@commands.cooldown(1, 60 * 60, commands.BucketType.member)
async def resetpassword(ctx, server_ip:str):
    """Method to reset the password associated with the Administrator User."""

    database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)

    hyonix_api = hyonix.HyonixAPI(HYONIX_TOKEN)

    current_user = database.checkCurrentUser(ctx.author.id)

    #  assure that the user is stored in the DB
    if current_user == True:
        # retrieve the users current information
        userInformation = database.returnUserInformation(ctx.author.id)

        if userInformation == None:
            return

        for server in userInformation["servers"]:
            if server["server_ip"] == server_ip:
                # print(server)
                password, reset = hyonix_api.resetPassword(server['server_id'])
                if reset == True:
                    await ctx.channel.send(f"Successfully reset the password for Server: {server_ip}")

                    # create an embed with the new info
                    hex_color = int(f"0xF9004D", 16)
                    embed = discord.Embed(color=hex_color, title="Renowned Servers", author="Renowned Servers")
                    embed.add_field(name="IP Address", value=f"{server['server_ip']}", inline=False)
                    embed.add_field(name="User", value="Administrator", inline=False)
                    embed.add_field(name="Password", value=f"||`{password}`||", inline=False)
                    await ctx.channel.send(embed=embed)
    
                    return
        await ctx.channel.send("Provide a valid server IP to perform actions.")
        return

@bot.command()
@discord.ext.commands.dm_only()
@commands.cooldown(1, 60 * 60, commands.BucketType.member)
async def duedate(ctx, server_ip:str):
    """Method to reset the password associated with the Administrator User."""

    database = databaseMongo.Database(MONGO_USER, MONGO_PASSWORD)

    current_user = database.checkCurrentUser(ctx.author.id)

    #  assure that the user is stored in the DB
    if current_user == True:
        # retrieve the users current information
        userInformation = database.returnUserInformation(ctx.author.id)

        if userInformation == None:
            return
        hyonix_api = hyonix.HyonixAPI(HYONIX_TOKEN)

        for server in userInformation["servers"]:
            if server["server_ip"] == server_ip:
                dueDate = server["next_billing_date"]
                await ctx.channel.send(f"The next billing date for Server IP: {server_ip} is {dueDate}.")
                return
        await ctx.channel.send("Provide a valid server IP to perform actions.")
        return
            

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = "This command is on cooldown, please try again in {:.0f}s".format(error.retry_after)
        await ctx.channel.send(msg)
        return
    elif isinstance(error, commands.CommandNotFound):
        logging.info(f"{ctx.author} provided an invalid command.")
        return
    elif isinstance(error, commands.TooManyArguments):
        logging.info(f"{ctx.author} provided an too many arguments for a command.")
        await ctx.channel.send("Please invoke the command correctly, and provide valid arguments.")
        return
    elif isinstance(error, commands.CheckFailure):
        logging.info(f"Check failure.")
        return
    elif isinstance(error, commands.UserInputError):
        logging.info(f"User provided invalid input for a command")
        await ctx.channel.send("Please invoke the command correctly, and provide valid arguments.")
        return
    else:
        logging.info("Uncaught exception for a command.")
        developer = await bot.fetch_user(DEV_ID)
        dmChan = await developer.create_dm()
        msg = f"Unknown command error caused by User: {ctx.author.mention}"
        await dmChan.send(msg)
        return



if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)