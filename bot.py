import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# ===== SETTINGS =====
STAFF_ROLE_NAME = "Supervisor"
LOG_CHANNEL_NAME = "staff-logs"
LOG_FILE = "staff_logs.json"

# ===== INTENTS =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ===== LOAD / SAVE =====
def load_logs():
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_logs(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ===== READY =====
@bot.event
async def on_ready():
    print("BOT FILE STARTED")
    await tree.sync()
    print(f"Bot online as {bot.user}")


# ===== AUTO RENAME =====
@bot.event
async def on_member_join(member):
    try:
        await member.edit(nick=f"V12 | {member.name}")
    except:
        pass


# ===== SLASH COMMANDS =====

# --- Add Staff Action ---
@tree.command(name="action", description="Log a staff action")
async def action(interaction: discord.Interaction, member: discord.Member, reason: str):

    role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)
    if role not in interaction.user.roles:
        await interaction.response.send_message("❌ You must be a Supervisor to use this.", ephemeral=True)
        return

    logs = load_logs()
    uid = str(member.id)

    if uid not in logs:
        logs[uid] = {"name": member.name, "actions": 0}

    logs[uid]["actions"] += 1
    save_logs(logs)

    log_channel = discord.utils.get(interaction.guild.text_channels, name=LOG_CHANNEL_NAME)
    if log_channel:
        await log_channel.send(
            f"📌 **Staff Action Logged**\n"
            f"👤 Staff: {member.mention}\n"
            f"📝 Action #: {logs[uid]['actions']}\n"
            f"📄 Reason: {reason}\n"
            f"👮 By: {interaction.user.mention}"
        )

    await interaction.response.send_message(f"✅ Logged action. Total: **{logs[uid]['actions']}**")


# --- Check Logs ---
@tree.command(name="checklogs", description="Check staff logs")
async def checklogs(interaction: discord.Interaction, member: discord.Member):

    role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)
    if role not in interaction.user.roles:
        await interaction.response.send_message("❌ You must be a Supervisor.", ephemeral=True)
        return

    logs = load_logs()
    uid = str(member.id)

    if uid not in logs:
        await interaction.response.send_message("❌ No logs found for this staff.")
        return

    await interaction.response.send_message(
        f"📊 **Staff Logs**\n"
        f"👤 {member.mention}\n"
        f"📝 Total Actions: **{logs[uid]['actions']}**"
    )


# --- Upload All Logs File ---
@tree.command(name="uploadlogs", description="Upload full log file")
async def uploadlogs(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return

    if not os.path.exists(LOG_FILE):
        await interaction.response.send_message("❌ No log file found.")
        return

    await interaction.response.send_message(
        "📤 **Staff Logs File:**",
        file=discord.File(LOG_FILE)
    )


# --- Remove logs for a staff ---
@tree.command(name="removelogs", description="Clear logs for a staff member")
async def removelogs(interaction: discord.Interaction, member: discord.Member):

    role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)
    if role not in interaction.user.roles:
        await interaction.response.send_message("❌ You must be a Supervisor.", ephemeral=True)
        return

    logs = load_logs()
    uid = str(member.id)

    if uid in logs:
        logs.pop(uid)
        save_logs(logs)
        await interaction.response.send_message(f"🗑 Logs cleared for {member.mention}")
    else:
        await interaction.response.send_message("❌ This staff has no logs.")


# ===== RUN BOT =====
bot.run(os.environ["TOKEN"])
