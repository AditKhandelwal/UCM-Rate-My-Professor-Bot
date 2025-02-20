import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from main import getProfessorInfo
import json

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="rmp", description="Enter a UCM Professor's Name")
@app_commands.describe(prof_name="UCM RMP Info")
async def echo_command(interaction: discord.Interaction, prof_name: str):
    data = json.loads(getProfessorInfo(prof_name))
    embed = create_professor_embed(data)
    await interaction.response.send_message(embed=embed)


bot.run(DISCORD_TOKEN)


# Suppose 'data' is the dictionary from json.loads(prof_info_str)
def create_professor_embed(data: dict) -> discord.Embed:
    """
    Build and return a Discord embed from the professor info dict.
    """
    # Basic embed setup
    embed = discord.Embed(
        title="Rate My Professor Info",
        description=f"Legacy ID: {data['legacyId']}",
        color=discord.Color.blue()  # pick any color you like
    )

    # Department, would-take-again, difficulty
    department = data.get("department", "N/A")
    would_take_again = data.get("wouldTakeAgain", "N/A")
    difficulty = data.get("difficulty", "N/A")

    embed.add_field(name="Department", value=department, inline=True)
    embed.add_field(name="Would Take Again", value=would_take_again, inline=True)
    embed.add_field(name="Difficulty", value=difficulty, inline=True)

    # Top tags
    top_tags = data.get("topTags", [])
    if top_tags:
        embed.add_field(
            name="Top Tags",
            value=", ".join(top_tags),  # e.g. "Lecture heavy, Group projects, ..."
            inline=False
        )

    # Latest Ratings
    latest_ratings = data.get("latestRatings", [])
    for i, rating in enumerate(latest_ratings, start=1):
        date = rating.get("date", "N/A")
        course = rating.get("course", "N/A")
        quality = rating.get("quality", "N/A")
        diff = rating.get("difficulty", "N/A")
        comment = rating.get("comment", "N/A")

        # We'll compile them into a single string
        rating_desc = (
            f"**Date**: {date}\n"
            f"**Course**: {course}\n"
            f"**Quality**: {quality}\n"
            f"**Difficulty**: {diff}\n"
            f"**Comment**: {comment}"
        )
        embed.add_field(name=f"Rating {i}", value=rating_desc, inline=False)

    return embed
