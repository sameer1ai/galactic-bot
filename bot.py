import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# ================= SETTINGS =================
STAFF_ROLE_NAME = "Supervisor"
LOG_CHANNEL_NAME = "staff-logs"
LOG_FILE = "staff_logs.json"

# ================= INTENTS =================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# ================= BOT CLASS =================
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync slash commands globally
        await self.tree.sync()

bot = MyBot()

# ================= LOG FUNCTIONS =================
def load_logs():
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_logs(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Bot online as {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        await member.edit(nick=f"V12 | {member.name}")
    except:
        pass

# ================= SLASH COMMANDS =================

# /ping
@bot.tree.command(name="ping", description="Check if bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# /action → add +1 log (Supervisor only)
@bot.tree.command(name="action", description="Add +1 log to a staff member")
@app_commands.describe(member="Select staff member", reason="Reason for action")
async def action(interaction: discord.Interaction, member: discord.Member, reason: str):
    if STAFF_ROLE_NAME not in [r.name for r in interaction.user.roles]:
        await interaction.response.send_message(
            "❌ You need Supervisor role.", ephemeral=True
        )
        return

    logs = load_logs()
    uid = str(member.id)

    if uid not in logs:
        logs[uid] = {"name": member.name, "actions": 0}

    logs[uid]["actions"] += 1
    save_logs(logs)

    log_channel = discord.utils.get(
        interaction.guild.text_channels, name=LOG_CHANNEL_NAME
    )

    if log_channel:
        await log_channel.send(
            f"📌 **Staff Action Logged**\n"
            f"👤 Staff: {member.mention}\n"
            f"📝 Logs: **{logs[uid]['actions']}**\n"
            f"📄 Reason: {reason}\n"
            f"👮 By: {interaction.user.mention}"
        )

    await interaction.response.send_message(
        f"✅ Log added\n"
        f"👤 {member.mention}\n"
        f"📊 Total Logs: **{logs[uid]['actions']}**"
    )

# /uploadlogs → set logs manually (Admin only)
@bot.tree.command(name="uploadlogs", description="Set logs for a staff member (Admin)")
@app_commands.describe(member="Select user", logs="Set logs number")
async def uploadlogs(interaction: discord.Interaction, member: discord.Member, logs: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Admin only.", ephemeral=True
        )
        return

    if logs < 0:
        await interaction.response.send_message(
            "❌ Logs cannot be negative.", ephemeral=True
        )
        return

    data = load_logs()
    data[str(member.id)] = {
        "name": member.name,
        "actions": logs
    }
    save_logs(data)

    await interaction.response.send_message(
        f"✅ Logs updated successfully\n"
        f"👤 User: {member.mention}\n"
        f"📊 Logs: **{logs}**"
    )

# /removelogs → remove logs (Admin only)
@bot.tree.command(name="removelogs", description="Remove logs from a staff member (Admin)")
@app_commands.describe(member="Select user", logs="Number of logs to remove")
async def removelogs(interaction: discord.Interaction, member: discord.Member, logs: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Admin only.", ephemeral=True
        )
        return

    if logs <= 0:
        await interaction.response.send_message(
            "❌ Logs must be greater than 0.", ephemeral=True
        )
        return

    data = load_logs()
    uid = str(member.id)

    if uid not in data:
        await interaction.response.send_message(
            "❌ This user has no logs.", ephemeral=True
        )
        return

    data[uid]["actions"] = max(0, data[uid]["actions"] - logs)
    save_logs(data)

    await interaction.response.send_message(
        f"➖ **Logs Removed Successfully**\n"
        f"👤 User: {member.mention}\n"
        f"📉 Removed: **{logs}**\n"
        f"📊 Remaining Logs: **{data[uid]['actions']}**"
    )

# /checklogs → view logs
@bot.tree.command(name="checklogs", description="Check logs of a staff member")
@app_commands.describe(member="Select user")
async def checklogs(interaction: discord.Interaction, member: discord.Member):
    logs = load_logs()
    uid = str(member.id)

    if uid not in logs:
        await interaction.response.send_message(
            "❌ No logs found for this user.", ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"📊 **Staff Logs**\n"
        f"👤 User: {member.mention}\n"
        f"📊 Logs: **{logs[uid]['actions']}**"
    )

# ================= RUN BOT =================
bot.run(os.environ["TOKEN"])
