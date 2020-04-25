import os
from itertools import chain
from twitchio.ext import commands
from dotenv import load_dotenv

load_dotenv()


POLL_MODS = ['zinge']


class Bot(commands.Bot):
    def __init__(self):
        self.poll = None
        self.stats = {}
        super().__init__(irc_token=os.getenv('TMI_TOKEN'),
                        client_id=os.getenv('CLIENT_ID'),
                        nick=os.getenv('BOT_NICK'),
                        prefix=os.getenv('BOT_PREFIX'),
                        initial_channels=[])

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f'Ready | {self.nick}')
        await self.join_channels([os.getenv('CHANNEL')])
        print(f"Joined channel {os.getenv('CHANNEL')}")

    async def event_message(self, message):
        if not message.author.name == self.nick.lower():
            if self.poll is not None and not message.content.startswith('!'):
                for i, option in enumerate(self.poll['options'].keys()):
                    if message.content.lower() == option.lower() or message.content == str(i + 1):
                        if not message.author in list(chain.from_iterable(self.poll['options'].values())):
                            self.poll['options'][option].append(message.author)
                            await message.channel.send(f"{message.author.name} voted for {option}")
                        else:
                            await message.channel.send(f"{message.author.name} already voted in this poll")
            elif message.content == os.getenv('BOT_PREFIX'):
                if self.poll is not None:
                    total_votes = len(list(chain.from_iterable(self.poll['options'].values())))
                    formatted_options = [f"{o} ({len(users)/total_votes*100}%)" for o, users in (self.poll['options'].items())]
                    await message.channel.send(f"Current results: {self.poll['title']} - {' / '.join(formatted_options)}")
                else:
                    await message.channel.send('There is no current poll. Use "!poll new TITLE | OPTION 1 | OPTION 2 | etc" to start one.')
        await self.handle_commands(message)

    @commands.command(name='new')
    async def new_poll(self, ctx, *, args):
        if not ctx.author.is_mod and not ctx.author.name in POLL_MODS:
            await ctx.send(f"Sorry, {ctx.author.name} isn't allowed to moderate polls.")
            return
        if self.poll is not None:
            await ctx.send('There is an existing poll. Use "!poll end" to get results before starting a new one.')
            return
        if not args:
            await ctx.send('You need to supply a title and options. - !poll new TITLE | OPTION 1 | OPTION 2 | etc')
            return
        args = [a.strip() for a in args.split('|') if a.strip()]
        if len(args) < 2:
            await ctx.send('You need at least a title and 1 poll option - !poll new TITLE | OPTION 1 | OPTION 2 | etc')
            return
        self.poll = {'title': args[0],
                    'options': dict([(o, []) for o in args[1:]])}
        formatted_options = [f"{i+1}. {o}" for i, o in enumerate(self.poll['options'].keys())]
        msg = f"Poll: {self.poll['title']} - {' / '.join(formatted_options)}"
        await ctx.send(msg)

    @commands.command(name='end')
    async def end_poll(self, ctx):
        if not ctx.author.is_mod and not ctx.author.name in POLL_MODS:
            await ctx.send(f"Sorry, {ctx.author.name} isn't allowed to moderate polls.")
            return
        if self.poll is not None:
            total_votes = len(list(chain.from_iterable(self.poll['options'].values())))
            formatted_options = [f"{o} ({len(users)/total_votes*100}%)" for o, users in (self.poll['options'].items())]
            await ctx.send(f"Final results: {self.poll['title']} - {' / '.join(formatted_options)}")
            self.poll = None
        else:
            await ctx.send('There is no current poll. Use "!poll new TITLE | OPTION 1 | OPTION 2 | etc" to start one.')

    @commands.command(name='help')
    async def help_poll(self, ctx):
        cmd_prefix = os.getenv('BOT_PREFIX')
        await ctx.send(f'"{cmd_prefix} new TITLE | OPTION 1 | OPTION 2" to start a poll  --  "{cmd_prefix}" to check the results on an existing poll  --  "{cmd_prefix} end" to finish a poll and close out the results  --  Once a poll is started, chat can vote by typing either the number or the name of what they want to vote for.')

    @commands.command(name='dsdeaths')
    async def dsdeaths(self, ctx, *, args=""):
        if not "dsdeaths" in self.stats:
            self.stats["dsdeaths"] = 0
        if "help" in args:
            await ctx.send('Temporary Dark Soul Death Commands: !ppoll dsdeaths | !ppoll dsdeaths add/subtract | !ppoll dsdeaths set 10')
            return
        elif "add" in args:
            self.stats["dsdeaths"] += 1
        elif "subtract" in args:
            if self.stats["dsdeaths"] > 0:
                self.stats["dsdeaths"] -= 1
        elif "set" in args:
            deaths = int(args.split()[-1])
            if deaths >= 0:
                self.stats["dsdeaths"] = deaths
        await ctx.send('Pitr has died {} times in Dark Souls.'.format(self.stats["dsdeaths"]))


if __name__ == "__main__":
    bot = Bot()
    bot.run()
