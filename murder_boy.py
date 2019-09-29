## IMPORTS
import discord
import random
import asyncio
from discord.ext import commands


## CONSTANTS
DISCORD_TOKEN = "NjI3NTU3ODUzNjUzMzY4ODMz.XY-Z4Q.Usfto9vUoWw3qvFxXzKh5Qsn9as"

PLAYER_MIN = 3
PLAYER_MAX = 12

CMD_PRE="🔪 "
PLAYER_ROLE_NAME = "townsperson"
GHOST_ROLE_NAME = "ghost"
GAME_CHANNEL_NAME = "murder-mystery-party"
POLL_TIME_MINUTES = 3


## INSTANCE DATA
# type: discord.ext.commands.Bot
bot = commands.Bot(command_prefix=CMD_PRE)
# type: Boolean
active_game = False
# type: discord.TextChannel
game_channel = None
# type: discord.Role
player_role = None
# type: discord.Role
ghost_role = None
# type: [discord.Member]
players = []
# type: [discord.Member]
hasntActed = []
# type: discord.Member
murderer = None
# type: Boolean
accusing = False

## FUNCTIONS
async def poll(ctx):
    options = {"🇦": "Yes I think they're Guilty!",
                "🇧": "Hot Milky (Not Guilty)!"}
    vote = discord.Embed(title="a", description="b", color=discord.Colour.blue()) # The poll embed, description can be None
    value = "\n".join("- {} {}".format(*item) for item in options.items()) # Add the options to the embed
    vote.add_field(name="c", value=value, inline=True) # c could be: Please vote ... :
    vote.set_footer(text="Time to vote: %s minutes" % (POLL_TIME_MINUTES)) #
    message_1 = await ctx.send(embed=vote)

    for option in options:
        await message_1.add_reaction(emoji=option)
    pollseconds = POLL_TIME_MINUTES * 60
    await asyncio.sleep(pollseconds)
    message_1 = await ctx.get_message(message_1.id)
    counts = {react.emoji: react.count for react in message_1.reactions} # Counts the reactions
    winner = max(options, key=counts.get) # Gets the winner (Reactions with the highest votes)
    await ctx.send("**%s** has won!" % (options[winner])) # Winner message, you can use an embed here aswell for a better design or edit the vote embed.

def setup(bot):
    bot.add_cog(Poll(bot))

## COMAMANDS
@bot.command(name="testpoll")
async def testpoll(ctx):
    await poll(ctx)

@bot.command(name="newgame")
async def newgame(ctx):
    global players
    global player_role
    global ghost_role
    global game_channel
    global active_game

    # clear current players and get ready for a new game
    players.clear()

    try:
        # only create player role if need to
        roles = [role for role in ctx.guild.roles if role.name == PLAYER_ROLE_NAME]
        if len(roles) == 0:
            player_role = await ctx.guild.create_role(name=PLAYER_ROLE_NAME,
                colour=discord.Colour.green(),
                reason="Started a new game")
        else:
            player_role = roles[0]

        # only create ghost role if need to
        roles = [role for role in ctx.guild.roles if role.name == GHOST_ROLE_NAME]
        if len(roles) == 0:
            ghost_role = await ctx.guild.create_role(name=GHOST_ROLE_NAME,
                colour=discord.Colour.dark_red(),
                reason="Started a new game")
        else:
            ghost_role = roles[0]

        # only create channel if need to, purge current's contents
        # and set channel permissions for @everyone & ghosts to read-only, players & bot to read/send
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True,
                send_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True,
                send_messages=True),
            player_role: discord.PermissionOverwrite(read_messages=True,
                send_messages=True),
            ghost_role: discord.PermissionOverwrite(read_messages=True,
                send_messages=False)
        }
        channels = [chan for chan in ctx.guild.text_channels if chan.name == GAME_CHANNEL_NAME]
        if len(channels) == 0:
            game_channel = await ctx.guild.create_text_channel(name=GAME_CHANNEL_NAME,
                overwrites=overwrites,
                reason="Started a new game")
        else:
            game_channel = channels[0]
            await game_channel.purge()
            for ovr in overwrites.keys():
                await game_channel.set_permissions(ovr,
                    overwrite=overwrites[ovr],
                    reason="Started a new game")

        active_game = True
        await ctx.send("A new game of murder mystery is ready to play!")

    except Exception as e:
        print(e)
        await ctx.send("Unable to prepare game :(")


@bot.command(name="join")
async def join(ctx):
    global active_game
    global players

    # check if there is a currently running game
    if not active_game:
        await ctx.send("There is no active game right now, start one with `{}newgame`.".format(CMD_PRE))
        return

    # check player count
    if len(players) >= PLAYER_MAX:
        await ctx.send("You have reached the maximum number of players.")
        return

    try:
        # only add new player to game
        # and add player role to new player
        new_player = ctx.author
        if new_player in players:
            await ctx.send("You're already playing! Also, you cannot leave this game :)")
            return

        players.append(new_player)
        await new_player.add_roles(player_role, reason="Player joined a new game")
        await ctx.send("{} is playing the game!".format(ctx.author.mention))

    except Exception as e:
        print(e)
        await ctx.send("Sorry, I couldn't add you to the game :(")


@bot.command(name="startgame")
async def startgame(ctx):
    global murderer
    global hasntActed
    global players

    #if len(players) < PLAYER_MIN:
    #    await ctx.send("You must have at least {} players.".format(PLAYER_MIN))
    #    return

    # pick murderer
    try:
        murderer = random.choice(players)
        await murderer.send("You are the murderer lol")
        hasntActed = list(players)
        await ctx.send("Someone's been murderered!")
    except Exception as e:
        print(e)
        await ctx.send("Sorry, I couldn't start the game :(")


@bot.command(name="murder")
async def murder(ctx):
    global murderer
    global hasntActed
    global players

    if murderer == None:
        murderer = ctx.author

    msg = "time to murder! Choose who to kill:\n"
    victims = list(players)
    victims.remove(murderer)
    for i in range(0, len(victims)):
        msg += "[{}] {}\n".format(i+1, victims[i].display_name)

    await murderer.send(msg)
    def check(m):
        return m.author != bot.user and m.channel == murderer.dm_channel

    num = await bot.wait_for('message', check=check)
    num = int(num.content)
    # put in error checking here
    murderMethods = ["hit over the head with a decorative rock. ", "pushed down the stairs. ", "poisoned in the ear while taking a nap. ", "gun. "]
    murderMsg = ["But when you heard them lift the rock, you turned and saw ", "But on your way down, standing over you was ", "But you half-awoke to see ", "But who was gun? "]
    # victim becomes ghost
    hapNum = random.choice(range(len(murderMethods)))
    happened = victims[num-1].display_name + " was " + murderMethods[hapNum]
    await victims[num - 1].remove_roles(player_role)
    await victims[num - 1].add_roles(ghost_role, reason=happened)
    # victim gets a message about being killed
    vicMsg = "You were " + murderMethods[hapNum] + murderMsg[hapNum] + murderer.display_name
    # channel gets a message about being killed
    await victims[num - 1].send(vicMsg)
    await ctx.send(happened)


@bot.command(name="takeaction")
async def takeaction(ctx):
    global hasntActed

    # if the user has already taken their action this turn
    if ctx.author not in hasntActed:
        # tell them they can't take an action
        await ctx.send("You've already used your action for this turn.")

    else:

        # otherwise give them a list of actions
        # when they give a number, execute that action
        await ctx.send("You acted.")
        # then, update hasntActed to say that they acted
        hasntActed.remove(ctx.author)
        # if not everyone has acted, print who has yet to act
        if hasntActed:
            msg = "Players who haven't acted yet this round: "
            for player in hasntActed:
                msg += player.display_name + ", "
            msg = msg[0:-2] + "."
        else:
            # otherwise, end the round
            hasntActed = list(players)
            await murder()


@bot.command(name="playing")
async def playing(ctx):
    global active_game
    global players

    if not active_game:
        await ctx.send("No one is playing the Murder Game right now :(\n Use `{}newgame` to start your game".format(CMD_PRE))
        return

    if not players:
        await ctx.send("There are no players in the Murder Game. Use `{}join` to join.".format(CMD_PRE))
        return

    playing_msg = "{} players are in the Murder Game:\n".format(len(players))
    for player in players:
        playing_msg += player.display_name + "\n"
    await ctx.send(playing_msg)


@bot.command(name="menu")
async def menu(ctx):
    #replying in the channel where menu command was invoked
    menu_msg = "Welcome to Murder Boy, the Murder Mystery Discord Game\n"
    menu_msg += "Preface every command to me with {}(note the single trailing space)\n".format(CMD_PRE)
    menu_msg += "`{}menu`: Displays this menu of commands\n".format(CMD_PRE)
    menu_msg += "`{}newgame`: Create a new channel called {} if it does not exist".format(CMD_PRE, GAME_CHANNEL_NAME)
    menu_msg += "`{}join`: Join the game (you cannot unjoin until the game is over)".format(CMD_PRE)
    menu_msg += "`{}startgame`: After all players have joined, use startgame to assign a murderer and see instructions".format(CMD_PRE)
    menu_msg += "`{}playing`: See which players have joined the game".format(CMD_PRE)
    menu_msg += "`{}takeaction`: Actions are limited -- one per player per round. A new round starts when every player has taken an action".format(CMD_PRE)


#One user will accuse another user of being the murderer
#Only one user can be accused at a time
#This will open a vote (going to be using existing poll code)
@bot.command(name="accuse")
async def accuse(ctx, arg):
    global accusing;
    mentions = ctx.message.mentions
    if not active_game:
        await ctx.send("No one is playing the Murder Game right now :(")
        return
    if not mentions:
        await ctx.send("You must @ the player whom you wish to accuse")
        return
    if len(mentions) > 1 or accusing:
        await ctx.send("You can only accuse one player at a time!")
        return
    if ctx.author == mentions[0]:
        await ctx.send("You can't accuse yourself!")
        return
    if not mentions[0] in players:
        await ctx.send("You can only accuse server members that are playing the Murder Game")
        return
    accusing = True
    await ctx.send(ctx.author.display_name + " has accused " + mentions[0].display_name + " of murder!")


@bot.command(name="off")
async def off(ctx):
    global active_game
    global game_channel
    global player_role
    global ghost_role

    # game cleanup
    active_game = False
    if game_channel:
        await game_channel.delete(reason="Ended a game")
    if player_role:
        await player_role.delete(reason="Ended a game")
    if ghost_role:
        await ghost_role.delete(reason="Ended a game")
    exit(0)


## EVENTS
@bot.event
async def on_ready():
    print("Logged in as", bot.user.name, bot.user.id)


## GO-GO BOT RUN
bot.run(DISCORD_TOKEN)
