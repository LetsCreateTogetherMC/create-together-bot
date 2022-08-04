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
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    db.init_db(DB_NAME)

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the cogwheels"))


@bot.command(name="create", help="Create a new Leaderboard")
async def create_leaderboard(ctx, leaderboard, symbol=":coin:"):
    if verify_role(ctx):
        res = db.create_table(leaderboard, symbol)

        embed = generate_embed(res["success"], res["message"])
        await ctx.send(embed=embed)


@bot.command(name="add", help="Add Points to a User in a Leaderboard")
async def add_points(ctx, leaderboard, user: discord.Member, amount: int):
    if verify_role(ctx):
        if amount == 0:
            await ctx.send("Amount cannot be 0")
            return

        user_name: str = f"{user.display_name}#{user.discriminator}"
        res = db.add_points_to_user(
            leaderboard, user.id, amount, user_name)

        msg = res["message"] if res["message"] else f"Added {amount} {res['symbol']} to {user_name}"

        embed = generate_embed(res["success"], msg)
        await ctx.send(embed=embed)


@bot.command(name="remove", help="Remove Points from a User in a Leaderboard")
async def remove_points(ctx, leaderboard, user: discord.Member, amount: int):
    if verify_role(ctx):
        if amount == 0:
            await ctx.send("Amount cannot be 0")
            return

        res = db.add_points_to_user(
            leaderboard, user.id, -amount, user.display_name)

        msg = res["message"] if res["message"] else f"Removed {amount} {res['symbol']} from {user.display_name}"

        embed = generate_embed(res["success"], msg)
        await ctx.send(embed=embed)


@bot.command(name="show", help="View a Leaderboard")
async def show_leaderboard(ctx, leaderboard=""):
    if verify_role(ctx):
        if not leaderboard:
            res = db.get_leaderboards()
            msg = format_leaderboard_list(res["message"])
            await ctx.send(embed=msg)
        else:
            res = db.get_leaderboard(leaderboard)
            msg = format_rankings(leaderboard, res["message"], res["symbol"])
            await ctx.send(embed=msg)


@bot.command(name="clear", help="Removes all the leaderboards")
async def clear(ctx, leaderboard=""):
    if verify_role(ctx):
        if not leaderboard:
            res = db.clear_db()

            msg = generate_embed(res["success"], res["message"])
            await ctx.send(embed=msg)
        else:
            res = db.delete_leaderboard(leaderboard)

            msg = generate_embed(res["success"], res["message"])
            await ctx.send(embed=msg)


@bot.command(name="help", help="Shows the help message")
async def help(ctx):
    if verify_role(ctx):
        msg = generate_help_embed()

        await ctx.send(embed=msg)

# Utility Functions


def verify_role(ctx) -> bool:
    required_role = discord.utils.get(ctx.guild.roles, name=USER_ROLE)
    return required_role in ctx.author.roles


def format_rankings(leaderboard: str, data: list, symbol: str) -> discord.Embed:
    embed = discord.Embed(
        colour=0x0084ff,
        title=f"{leaderboard.capitalize()} Rankings"
    )

    for idx in range(len(data)):
        item = data[idx]

        embed.add_field(
            name=f"{idx + 1} - {item[1]}",
            value=f"{symbol} {item[2]}",
            inline=False
        )

    if len(data) == 0:
        embed.add_field(
            name="",
            value="*Its lonely here...*"
        )

    return embed


def format_leaderboard_list(tables: list) -> discord.Embed:
    embed = discord.Embed(
        title="Leaderboards",
        colour=0x0084ff
    )

    idx = 1

    for table in tables:
        table_name = table[0]

        if table_name == "global":
            continue

        symbol = db.get_symbol(table_name)
        embed.add_field(
            name=f"{idx} - {table_name.capitalize()}",
            value=symbol,
            inline=False
        )
        idx += 1

    return embed


def generate_embed(success: bool, message: str) -> discord.Embed:
    embed = discord.Embed(
        colour=0x0084ff if success else 0x991b1b,
        description=message,
    )

    return embed


def generate_help_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Help",
        colour=0x0084ff
    )

    help_data = {
        "create": "Creates a leaderboard.\nSyntax - `create <leaderboard-name> <point-symbol>`\nDefault: `symbol`: :coin:",
        "add": "Adds points to a player on a leaderboard.\nSyntax - `add <leaderboard> <player> <amount>`",
        "remove": "Removes points from a player on a leaderboard.\nSyntax - `remove <leaderboard> <player> <amount>`",
        "show": "Shows the rankings of a leaderboard\nSyntax - `show <leaderboard>`\nIf no leaderboard is provided, show a list of leaderboards instead",
        "clear": "Deletes a leaderboard\nSyntax - `clear <leaderboard>`\nIf no leaderboard is provided, deletes all the leaderboards insted",
        "help": "Shows this message"
    }

    for command in help_data:
        embed.add_field(
            name=command,
            value=help_data[command],
            inline=False
        )

    return embed


bot.run(DISCORD_TOKEN)
