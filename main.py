from information import Information

import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions

intents = discord.Intents.default()
intents.members = True

bot = Bot(command_prefix="$", intents=intents)
bot.running = []
TOKEN = open("token.txt").read()
info = Information()


async def start_appeal(user, server_id, server):
    if str(user.id) not in bot.running:
        bot.running.append(str(user.id))
    else:
        embed = discord.Embed(
            title=f"Ticket limit reached",
            description="You already have a ban appeal in progress.",
            color=0xFF0000,
        )

        await user.send(embed=embed)

        return

    timeout = False
    server_info = info.info[str(server_id)]
    answers = []

    def message_check(m):

        return m.author.id == user.id and m.channel.id == question_message.channel.id

    def reaction_check(r, u):

        return u.id == user.id and r.message.id == reply.id

    for i, question in enumerate(server_info["questions"]):

        while True:

            embed = discord.Embed(
                title=f"Question {i+1}", description=question, color=0xFF0000
            )
            question_message = await user.send(embed=embed)

            try:

                msg = await bot.wait_for("message", timeout=600, check=message_check)

            except asyncio.TimeoutError:

                embed = discord.Embed(
                    title="Ban appeal timeout",
                    description="Ticket ended due to inactivity",
                    color=0xFF0000,
                )
                await user.send(embed=embed)

                timeout = True
                break

            embed = discord.Embed(
                title="Do you want to submit this answer?",
                description=msg.content,
                color=0xFF0000,
            )
            embed.set_footer(text="React with 🔒 to close the appeal")
            reply = await user.send(embed=embed)

            await reply.add_reaction("✅")
            await reply.add_reaction("❌")
            await reply.add_reaction("🔒")

            try:

                reaction, user = await bot.wait_for(
                    "reaction_add", timeout=60, check=reaction_check
                )

                if reaction.emoji == "✅":
                    answers.append({"question": question, "answer": msg.content})
                    break
                elif reaction.emoji == "❌":

                    continue
                elif reaction.emoji == "🔒":

                    embed = discord.Embed(
                        title="Ban appeal ended",
                        description="Ticket ended due to user request",
                        color=0xFF0000,
                    )
                    await user.send(embed=embed)

                    timeout = True
                    break

            except asyncio.TimeoutError:

                embed = discord.Embed(
                    title="Ban appeal timeout",
                    description="Ticket ended due to inactivity",
                    color=0xFF0000,
                )
                await user.send(embed=embed)

                timeout = True
                break

        if timeout:

            break

    if not timeout:

        end_channel = discord.utils.get(
            server.text_channels, id=int(server_info["end_channel"])
        )

        embed = discord.Embed(
            title="New Ban Appeal",
            description=f"Name: {user.mention}\nID: {user.id}\n",
            color=0xFF0000,
        )

        embed.set_thumbnail(url=user.avatar_url)

        for i, qa in enumerate(answers):
            embed.add_field(
                name=f"Question {i+1}: {qa['question']}",
                value=f"Answer: {qa['answer'][:400]}",
                inline=False,
            )

        await end_channel.send(embed=embed)

        embed = discord.Embed(
            title="Answers submitted successfully",
            description="Thanks for your appeal",
            color=0xFF0000,
        )

        await user.send(embed=embed)

    bot.running.remove(str(user.id))


@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")


@bot.event
async def on_guild_join(guild):
    info.create_server_info(guild.id)


@bot.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == "🔴" and user.id != bot.user.id and reaction.me:
        await reaction.remove(user)
        await start_appeal(user, reaction.message.guild.id, reaction.message.guild)


@bot.command()
@has_permissions(manage_channels=True)
async def setup(ctx):
    setup_questions = [
        {
            "Title": "Start Appeal Channel",
            "Desc": "Which channel would you like the ban appeals to be initiated from:?",
            "Foot": "Give the name of the channel (e.g. 'appeals' or 'start appeal')",
        },
        {
            "Title": "Review Appeal Channel",
            "Desc": "Which channel would you like to review ban appeals in?",
            "Foot": "Give the name of the channel (e.g. 'appeals' or 'review appeals')",
        },
        {
            "Title": "Appeal Topic",
            "Desc": "What is being appealed",
            "Foot": "Give the name of whatever is being appealed (e.g 'minecraft' will show up as 'ban appeals for minecraft')",
        },
    ]

    def reaction_check(r, u):
        return u.id == ctx.author.id and r.message.id == BOT_MESSAGE.id

    def message_check(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.message.channel.id

    embed = discord.Embed(
        title="Interactive Setup",
        description="Would you like to start the interactive setup here?",
        color=0xFF0000,
    )

    BOT_MESSAGE = await ctx.send(embed=embed)

    await BOT_MESSAGE.add_reaction("✅")
    await BOT_MESSAGE.add_reaction("❌")

    try:
        reaction, user = await bot.wait_for(
            "reaction_add", timeout=30, check=reaction_check
        )
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="Error",
            description=f"Setup ended due to inactivity",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
        return

    if reaction.emoji == "❌":
        return
    elif reaction.emoji == "✅":
        pass

    for i, question in enumerate(setup_questions):
        embed = discord.Embed(
            title=question["Title"],
            description=question["Desc"],
            color=0xFF0000,
        )
        embed.set_footer(text=question["Foot"])

        BOT_MESSAGE = await ctx.send(embed=embed)

        try:
            msg = await bot.wait_for("message", timeout=60, check=message_check)

            if i == 0 or i == 1:
                if discord.utils.get(ctx.guild.text_channels, name=msg.content) is None:
                    embed = discord.Embed(
                        title="Error",
                        description=f"{msg.content} is not a channel that exists in this server.",
                        color=0xFF0000,
                    )

                    await ctx.send(embed=embed)

                    return
                else:
                    setup_questions[i]["answer"] = msg.content
            else:
                setup_questions[i]["answer"] = msg.content
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Error",
                description=f"Setup ended due to inactivity",
                color=0xFF0000,
            )
            await ctx.send(embed=embed)
            return

    start_channel = discord.utils.get(
        ctx.guild.text_channels, name=setup_questions[0]["answer"]
    )
    end_channel = discord.utils.get(
        ctx.guild.text_channels, name=setup_questions[1]["answer"]
    )
    name = setup_questions[2]["answer"]
    info.info[str(ctx.guild.id)]["start_channel"] = str(start_channel.id)
    info.info[str(ctx.guild.id)]["end_channel"] = str(end_channel.id)
    info.info[str(ctx.guild.id)]["name"] = name
    info.save()

    embed = discord.Embed(
        title=f"Ban appeals for **{name}**",
        description=f"To create a ban appeal for **{name}**, react with 🔴",
        color=0xFF0000,
    )
    message = await start_channel.send(embed=embed)
    await message.add_reaction("🔴")


@setup.error
async def set_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.message.reply(
            "You need to have the **Manage Channels** Permission to run this command"
        )


bot.run(TOKEN)
