import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import db

# Load Environment Variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX")
USER_ROLE = os.getenv("USER_ROLE")
DB_NAME = os.getenv("DB_NAME")

bot = commands.Bot(command_prefix=PREFIX)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    db.init_db(DB_NAME)


@bot.command(name="create", help="Create a new Leaderboard")
async def create_leaderboard(ctx, leaderboard):
    if verify_role(ctx):
        res = db.create_table(leaderboard)
        await ctx.send(res["message"])


@bot.command(name="add", help="Add Points to a User in a Leaderboard")
async def add_points(ctx, leaderboard, user: discord.Member, amount: int):
    if verify_role(ctx):
        if amount == 0:
            await ctx.send("Amount cannot be 0")
            return

        print(user.id)
        res = db.add_points_to_user(leaderboard, user.id, amount, user.name)

        msg = res["message"] if res["message"] else f"Added {amount} points to {user.name}"
        await ctx.send(msg)


@bot.command(name="remove", help="Remove Points from a User in a Leaderboard")
async def remove_points(ctx, leaderboard, user: discord.Member, amount: int):
    if verify_role(ctx):
        if amount == 0:
            await ctx.send("Amount cannot be 0")
            return

        res = db.add_points_to_user(leaderboard, user.id, -amount, user.name)

        msg = res["message"] if res["message"] else f"Removed {amount} points from {user.name}"
        await ctx.send(msg)


@bot.command(name="show", help="View a Leaderboard")
async def show_leaderboard(ctx, leaderboard):
    if verify_role(ctx):
        res = db.get_leaderboard(leaderboard)
        msg = format_table(leaderboard, res["message"])
        await ctx.send(msg)

# Utility Functions


def verify_role(ctx) -> bool:
    required_role = discord.utils.get(ctx.guild.roles, name=USER_ROLE)
    return required_role in ctx.author.roles


def format_table(leaderboard: str, data: list) -> str:
    msg = f"> **{leaderboard.capitalize()}**\n> \n"

    for idx in range(len(data)):
        item = data[idx]
        msg += f"> {idx+1} - {item[1]} : {item[2]}\n"

    return msg


bot.run(DISCORD_TOKEN)
