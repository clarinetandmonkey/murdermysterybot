# Murder Mystery Discord Bot

## Bot Usage

### Commands
All commands are prefixed with `:knife: `.

Check back for more information!

## Our Story

### Inspiration
In our Dungeons & Dragons Discord server, our friends love to schedule game nights and get togethers where we play various problem-solving games.  We wanted to make it just a little easier for all of us to do that by bringing the games to Discord!

### What it does
Our Murder Mystery Discord Bot does just that by setting a small game environment for a group of players in a server.  One of them is the killer, but it's up to the others to find out.  But be careful!  The more time they waste, the more players that perish!

### How we built it
This robust [Discord client Python library](https://pypi.org/project/discord.py/) helps us connect to our Discord-based application.  From that, we wrote all the custom logic and command processing to allow users to create, join and play games.

Although we all knew Python very well at the beginning of the day, we learned countless more new features and aspects of the language and library, some of which took quite a bit of head-scratching (darn those `global` variables!).  Asynchronous programming is something is so natural once you understand it, but almost entirely foreign to those who don't know it.  Due to the library's mechanisms, we needed to learn and become comfortable with coding asynchronously so that bot functions would run properly.

The game also received a lot (and a lot) of research and revisions for its gameplay and mechanics.  The game needed to be something doable in the allotted time, but still have some sort of flow and be enjoyable for the players!

### Roadmap
As of right now, we have a strong proof-of-concept that can perform all of the basic functions of the bot.  Smoother game play will come, along with more robust bot commands and a more coherent storyline.
