import os
import sys
import datetime
import re
import subprocess
from itertools import chain
from twitchio.ext import commands
import operator
import json
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import asyncio
load_dotenv(override=True)

sys.path.append("pitrcade_django")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pollerbot.settings")
import django
django.setup()
from pitrcade.models import Player, PollerbotData, PremadePoll, ConfigSetting
from django.db.utils import IntegrityError

POLL_MODS = ['zinge']

from preferences import preferences
SL_API_URL = 'https://www.streamlabs.com/api/v1.0'
SL_CLIENT_ID = os.getenv('STREAMLABS_CLIENT_ID')
SL_CLIENT_SECRET = os.getenv('STREAMLABS_CLIENT_SECRET')

class Bot(commands.Bot):
    def __init__(self):
        self.poll = None
        self.top_score = 0
        top_score = Player.objects.order_by('-score').first()
        if top_score:
            self.top_score = top_score.score
        super().__init__(irc_token=os.getenv('TMI_TOKEN'),
                        client_id=os.getenv('CLIENT_ID'),
                        nick=os.getenv('BOT_NICK'),
                        prefix=os.getenv('BOT_PREFIX'),
                        initial_channels=[])


    def get_poll_results(self, sorted=False):
        total_votes = len(list(chain.from_iterable(self.poll['options'].values())))
        poll_results = []
        if not total_votes:
            poll_results = ["No votes have been cast"]
        else:
            poll_results = [(o, len(users)) for o, users in self.poll['options'].items()]
            if sorted:
                poll_results.sort(key=operator.itemgetter(1), reverse=True)
                poll_results = [f"{o} ({i} - {i/total_votes*100:.0f}%)" for o, i in poll_results]
            else:
                poll_results = [f"{index+1}. {result[0]} ({result[1]} - {result[1]/total_votes*100:.0f}%)" for index, result in enumerate(poll_results)]
        return poll_results


    async def send(self, ctx, message):
        # Send command wrapper for twitch to auto-split messages that are over
        # the 500 char length limit
        chunks = [message[i:i+500] for i in range(0, len(message), 500)]
        for chunk in chunks:
            await ctx.send(chunk)


    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f'Ready | {self.nick}')
        await self.join_channels([os.getenv('CHANNEL')])
        print(f"Joined channel {os.getenv('CHANNEL')}")


    def token_saver(self, token):
        cs = ConfigSetting.objects.get(pk=preferences.ConfigSetting.pk)
        cs.streamlabs_access_token = json.dumps(token)
        cs.save()


    async def event_message(self, message):
        #Ignore messages from the bot
        if not message.author.name == self.nick.lower():
            #Check for bits for Pitrcade
            message_without_content = message.raw_data.split("PRIVMSG")[0]
            message_content = message.raw_data.split("PRIVMSG")[1].lower()
            matcher = re.search(r";bits=(?P<bits>\d+);", message_without_content)
            if matcher:
                bits = int(matcher.group("bits"))
                bit_tokens = ['quarter', 'arcade', 'multiball']
                # if bits == 25 or (bits % 25 == 0 and any(x in message_content for x in bit_tokens)):
                if bits % 25 == 0:
                    num_plays = int(bits / 25)
                    obj, created = Player.objects.get_or_create(username=message.author.name)
                    game_results = obj.insert_quarter(num_plays)
                    for result in game_results:
                        streamlabs_failure = False
                        try:
                            extra = {
                                'client_id': SL_CLIENT_ID,
                                'client_secret': SL_CLIENT_SECRET,
                            }
                            streamlabs = OAuth2Session(SL_CLIENT_ID, token=json.loads(preferences.ConfigSetting.streamlabs_access_token),
                                                        auto_refresh_kwargs=extra, auto_refresh_url=SL_API_URL + '/token', token_updater=self.token_saver)
                            params = {
                                      "type":"donation",
                                      "image_href": result['image_or_video_alert_url'],
                                      "sound_href": result['sound_alert_url'],
                                      "message": result['message'],
                                      #"user_message": " ",
                                      "duration": result['alert_duration'],
                                      "special_text_color": preferences.ConfigSetting.scoreboard_header_color,
                                      }
                            response = streamlabs.post(SL_API_URL + '/alerts', data=params)
                            if result['echo_in_chat']:
                                await self.send(message.channel, result['message'].replace('*', ''))
                            await asyncio.sleep(0)
                        except:
                            # await self.send(message.channel, result['message'].replace('*', ''))
                            streamlabs_failure = True
                        if result['score'] > self.top_score:
                            self.top_score = result['score']
                            await self.send(message.channel, f'{message.author.name} got the new high score of {self.top_score}!')
                    if streamlabs_failure:
                        await self.send(message.channel, f'RIP Streamlabs: Some of {message.author.name}\'s arcade scores weren\'t displayed, but you can always check the arcade history to see how you did!')
            if self.poll is not None and not message.content.startswith('!'):
                for i, option in enumerate(self.poll['options'].keys()):
                    if message.content.lower() == option.lower() or message.content == str(i + 1):
                        if not self.poll['multi']: # Vote for a single choice
                            if not message.author in list(chain.from_iterable(self.poll['options'].values())):
                                self.poll['options'][option].append(message.author)
                                await self.send(message.channel, f"{message.author.name} voted for {option}")
                            else:
                                await self.send(message.channel, f"{message.author.name} already voted in this poll")
                        else: # Vote for multiple choices
                            if not message.author in self.poll['options'][option]:
                                self.poll['options'][option].append(message.author)
                                await self.send(message.channel, f"{message.author.name} voted for {option}")
                            else:
                                await self.send(message.channel, f"{message.author.name} already voted for {option} in this poll")

            elif message.content == os.getenv('BOT_PREFIX'):
                if self.poll is not None:
                    poll_results = self.get_poll_results()
                    await self.send(message.channel, f"Current results: {self.poll['title']} - {' / '.join(poll_results)}")
                else:
                    await self.send(message.channel, f'There is no current poll. Use "!ppoll help" for more info.')
        await self.handle_commands(message)


    @commands.command(name='new', aliases=['newmulti'])
    async def new_poll(self, ctx, *, args):
        if not ctx.author.is_mod and not ctx.author.name.lower() in POLL_MODS:
            await self.send(ctx, f"Sorry, {ctx.author.name} isn't allowed to moderate polls.")
            return
        if self.poll is not None:
            await self.send(ctx, f'There is an existing poll. Use "!ppoll end" to get results before starting a new one.')
            return
        if not args:
            await self.send(ctx, f'You need to supply a title and options. Use "!ppoll help" for more info.')
            return
        multi = ctx.content.split()[1] == "newmulti"
        args = [a.strip() for a in ctx.content.split('newmulti' if multi else 'new')[1].split('|') if a.strip()]
        if len(args) < 2:
            await self.send(ctx, f'You need at least a title and 1 poll option. Use "!ppoll help" for more info.')
            return
        self.poll = {'title': args[0],
                    'options': dict([(o, []) for o in args[1:]]),
                    'multi': multi}
        formatted_options = [f"{i+1}. {o}" for i, o in enumerate(self.poll['options'].keys())]
        msg = f"Poll: {self.poll['title']} - {' / '.join(formatted_options)}"
        await self.send(ctx, msg)


    @commands.command(name='load')
    async def load_poll(self, ctx, *, args):
        if not ctx.author.is_mod and not ctx.author.name in POLL_MODS:
            await self.send(ctx, f"Sorry, {ctx.author.name} isn't allowed to moderate polls.")
            return
        if self.poll is not None:
            await self.send(ctx, f'There is an existing poll. Use "!ppoll end" to get results before starting a new one.')
            return
        if not args:
            await self.send(ctx, f'You need to supply a premade poll title to load. Use "!ppoll help" for more info.')
            return
        args = args.strip()
        try:
            premade = PremadePoll.objects.get(title=args)
        except PremadePoll.DoesNotExist:
            premade = None
        if not premade:
            await self.send(ctx, f'A premade poll with that title does not exist. Use "!ppoll help" for more info.')
            return
        options = [o.strip() for o in premade.options.split('|') if o.strip()]
        self.poll = {'title': premade.title,
                    'options': dict([(o, []) for o in options]),
                    'multi': premade.multi}
        formatted_options = [f"{i+1}. {o}" for i, o in enumerate(self.poll['options'].keys())]
        msg = f"Poll: {self.poll['title']} - {' / '.join(formatted_options)}"
        await self.send(ctx, msg)


    @commands.command(name='save')
    async def save_poll(self, ctx):
        if not ctx.author.is_mod and not ctx.author.name in POLL_MODS:
            await self.send(ctx, f"Sorry, {ctx.author.name} isn't allowed to moderate polls.")
            return
        if self.poll is None:
            await self.send(ctx, f'There is no active poll to save as a preset. Use "!ppoll help" for more info.')
            return
        premade = PremadePoll(title=self.poll['title'], options='|'.join(self.poll['options']), multi=self.poll['multi'])
        try:
            premade.save()
        except IntegrityError:
            await self.send(ctx, f'A premade poll with this title already exists.')
            return
        msg = f"Active poll '{self.poll['title']}' has been saved as a preset."
        await self.send(ctx, msg)


    @commands.command(name='end')
    async def end_poll(self, ctx):
        if not ctx.author.is_mod and not ctx.author.name in POLL_MODS:
            await self.send(ctx, f"Sorry, {ctx.author.name} isn't allowed to moderate polls.")
            return
        if self.poll is not None:
            poll_results = self.get_poll_results(sorted=True)
            await self.send(ctx, f"Final results: {self.poll['title']} - {' / '.join(poll_results)}")
            self.poll = None
        else:
            await self.send(ctx, f'There is no current poll. Use "!ppoll help" for more info.')


    @commands.command(name='help')
    async def help_poll(self, ctx):
        cmd_prefix = os.getenv('BOT_PREFIX')
        await self.send(ctx, f'"!ppoll new/newmulti TITLE | OPTION 1 | OPTION 2" to start a poll  --  "!ppoll" to check the results on an existing poll  --  "!ppoll save" to save the current poll as a premade  --  "!ppoll load TITLE" to load a premade poll  --  "!ppoll end" to finish a poll and close out the results  --  Once a poll is started, chat can vote by typing either the number or the name of what they want to vote for.')


    @commands.command(name='dsdeaths')
    async def dsdeaths(self, ctx, *, args=""):
        await self.send(ctx, f"This command is now '!ppoll deaths' (instead of dsdeaths). Use '!ppoll deaths help' for commands.")


    @commands.command(name='deaths')
    async def deaths(self, ctx, *, args=""):
        dc_obj, created = PollerbotData.objects.get_or_create(key='death_counter', defaults={'value': 0})
        ldt_obj, created = PollerbotData.objects.get_or_create(key='last_death_timestamp', defaults={'value': datetime.datetime.now().isoformat()})
        death_counter = int(dc_obj.value)
        last_death_timestamp = datetime.datetime.fromisoformat(ldt_obj.value)
        now = datetime.datetime.now()
        time_since_death = now - last_death_timestamp
        if "help" in args:
            await self.send(ctx, f'Death Counter Commands: !ppoll deaths | !ppoll deaths add/subtract | !ppoll deaths set 10 | (This counter is saved when Pollerbot restarts)')
            return
        elif "add" in args or "subtract" in args or "set" in args:
            if "add" in args:
                death_counter += 1
                ldt_obj.value = now.isoformat()
                ldt_obj.save()
            elif "subtract" in args:
                if death_counter > 0:
                    death_counter -= 1
            elif "set" in args:
                deaths = int(args.split()[-1])
                if deaths >= 0:
                    death_counter = deaths
            dc_obj.value = death_counter
            dc_obj.save()
        msg = "Kara has died {} times.".format(death_counter)
        if time_since_death:
            msg += " It's been ~{} minutes since the last death.".format(int(time_since_death.total_seconds() / 60))
        await self.send(ctx, msg)


    @commands.command(name='deathsbot')
    async def deathsbot(self, ctx, *, args=""):
        if not ctx.author.is_mod and not ctx.author.name in POLL_MODS:
            await self.send(ctx, f"Sorry, {ctx.author.name} isn't allowed to moderate deathsbot.")
            return
        if "start" in args:
            subprocess.call("/usr/bin/screen -dr deathsbot -X quit".split())
            subprocess.call("/usr/bin/screen -dmS deathsbot /usr/bin/python3 bot.py", cwd="/home/pi/workspace/opencv_deathtracker", shell=True)
        elif "stop" in args:
            subprocess.call("/usr/bin/screen -dr deathsbot -X quit".split())


if __name__ == "__main__":
    bot = Bot()
    bot.run()
