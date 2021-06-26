import asyncio
import json
import os

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions

class Information:
    def __init__(self):
        self.file = "information.json"
        self.default_questions = ["What is your discord username (e.g. User#0000)?",
                        "Why were you banned?",
                        "Did you deserve it?",
                        "What will you do to prevent getting banned again?",
                        "How long has it been since you were banned?",
                        "Any other information?"]
        self.load()
        
        print(f"information: {self.info}")

    def load(self):
        if os.stat(self.file).st_size == 0:
            self.info = {}
        else:
            with open(self.file, "r") as f:
                self.info = json.load(f)
    
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.info, f, indent=4)
    
    def create_server_info(self, server_id):
        self.info[str(server_id)] = {
            "questions" : self.default_questions,
        }

        self.save()

intents = discord.Intents.default()
intents.members = True

bot = Bot(command_prefix='$', intents=intents)
TOKEN = open("token.txt").read()
info = Information()

async def start_appeal(user, server_id):

    server_info = info.info[str(server_id)]

    def message_check(m):

        return m.author.id == user.id 
    
    def reaction_check(r, u):

        return u.id == user.id and r.message.id == reply.id

    for i, question in enumerate(server_info["questions"]):

        timeout = False
        while True:

            embed=discord.Embed(title=f"Question {i+1}", description=question, color=0xff0000)
            await user.send(embed=embed)

            msg = await bot.wait_for("message", check=message_check)

            embed = discord.Embed(title="Do you want to submit this answer?", description=msg.content, color=0xff0000)
            reply = await msg.reply(embed=embed)

            await reply.add_reaction("✅")
            await reply.add_reaction("❌")
            
            try:

                reaction, user = await bot.wait_for('reaction_add', timeout=60, check=reaction_check)

                if reaction.emoji == "✅":

                    break
                elif reaction.emoji == "❌":

                    continue

            except asyncio.TimeoutError:

                embed = discord.Embed(title="Ban appeal timeout", description="Ticket ended due to inactivity", color=0xff0000)
                await user.send(embed=embed)

                timeout = True
                break
        
        if timeout:

            break      
        
@bot.event
async def on_ready():
	print(f'Bot connected as {bot.user}')

@bot.event
async def on_guild_join(guild):
    info.create_server_info(guild.id)

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == "🔴" and user.id != bot.user.id:
        await reaction.remove(user)
        await start_appeal(user, reaction.message.guild.id)
    
@bot.command()
@has_permissions(manage_channels=True)  
async def set(ctx, channel_id=None, server_name=None):

    try:
        channel = bot.get_channel(int(channel_id))
    except:
        channel = ctx.channel

    if server_name is None:
        server = ctx.guild.name
    else:
        server = server_name
    
    embed = discord.Embed(title=f"Ban appeals for **{server}**", description=f"To create a ban appeal for **{server}**, react with 🔴", color=0xff0000)
    message = await ctx.send(embed=embed)
    await message.add_reaction("🔴")
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

@set.error
async def set_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.message.reply("You need to have the **Manage Channels** Permission to run this command")


bot.run(TOKEN)




