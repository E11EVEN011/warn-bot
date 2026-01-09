import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# ───── السيرفر الوهمي لخداع Render ─────
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    # Render يطلب العمل على بورت 8080 افتراضياً أو المتغير PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ───── Intents ─────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ───── Role Checks ─────

def can_warn():
    async def predicate(ctx):
        allowed_roles = ["WarnAdmin", "WARNINGS MANAGEMENT"]
        user_roles = [role.name for role in ctx.author.roles]
        return any(role in user_roles for role in allowed_roles)
    return commands.check(predicate)

def can_manage_warns():
    async def predicate(ctx):
        allowed_roles = ["WARNINGS MANAGEMENT"]
        user_roles = [role.name for role in ctx.author.roles]
        return any(role in user_roles for role in allowed_roles)
    return commands.check(predicate)

def can_jail():
    async def predicate(ctx):
        allowed_roles = ["UG MANAGEMENT", "WARNINGS MANAGEMENT"]
        user_roles = [role.name for role in ctx.author.roles]
        return any(role in user_roles for role in allowed_roles)
    return commands.check(predicate)

def get_log_channel(guild):
    return get(guild.text_channels, name="warn-logs")

# ───── Ready ─────
@bot.event
async def on_ready():
    print(f"Ready as {bot.user}")

# ───── Warn Command ─────
@bot.command()
@can_warn()
async def warn(ctx, member: discord.Member, *, reason="بدون سبب"):
    warn_roles = ["Warn1", "Warn2", "Warn3"]
    current = 0

    for i, name in enumerate(warn_roles, start=1):
        role = get(ctx.guild.roles, name=name)
        if role in member.roles:
            current = i

    if current >= 3:
        await ctx.send("❌ العضو عنده 3 تحذيرات بالفعل")
        return

    new_warn = current + 1
    role = get(ctx.guild.roles, name=warn_roles[new_warn - 1])
    await member.add_roles(role)

    action = "لا يوجد إجراء حاليًا"

    if new_warn == 3:
        muted = get(ctx.guild.roles, name="Muted")
        if muted:
            await member.add_roles(muted)
            action = "🔇 تم كتمك تلقائيًا بسبب الوصول لـ 3 تحذيرات"

    try:
        embed = discord.Embed(title="⚠️ تم تحذيرك", color=discord.Color.orange())
        embed.add_field(name="📌 السيرفر", value=ctx.guild.name, inline=False)
        embed.add_field(name="🔢 رقم التحذير", value=str(new_warn), inline=True)
        embed.add_field(name="📝 السبب", value=reason, inline=False)
        embed.add_field(name="⚖️ الإجراء", value=action, inline=False)
        await member.send(embed=embed)
    except: pass

    await ctx.send(f"⚠️ {member.mention} أخذ تحذير رقم {new_warn}")

    log = get_log_channel(ctx.guild)
    if log:
        embed = discord.Embed(title="⚠️ تحذير جديد", color=discord.Color.orange(), timestamp=datetime.utcnow())
        embed.add_field(name="👤 العضو", value=member.mention, inline=False)
        embed.add_field(name="🔢 رقم التحذير", value=str(new_warn), inline=True)
        embed.add_field(name="📝 السبب", value=reason, inline=False)
        embed.add_field(name="🛡️ الإداري", value=ctx.author.mention, inline=False)
        await log.send(embed=embed)

# ───── Clear Warns ─────
@bot.command()
@can_manage_warns()
async def clearwarns(ctx, member: discord.Member):
    for name in ["Warn1", "Warn2", "Warn3"]:
        role = get(ctx.guild.roles, name=name)
        if role in member.roles:
            await member.remove_roles(role)
    await ctx.send(f"🧹 تم مسح تحذيرات {member.mention}")

# ───── Jail ─────
@bot.command()
@can_jail()
async def jail(ctx, member: discord.Member, *, reason="بدون سبب"):
    jail_role = get(ctx.guild.roles, name="Jail")
    if not jail_role:
        await ctx.send("❌ رول Jail غير موجود")
        return
    await member.add_roles(jail_role)
    await ctx.send(f"⛓️ {member.mention} دخل السجن | السبب: {reason}")

# ───── UnJail ─────
@bot.command()
@can_manage_warns()
async def unjail(ctx, member: discord.Member):
    jail_role = get(ctx.guild.roles, name="Jail")
    if jail_role:
        await member.remove_roles(jail_role)
        await ctx.send(f"🔓 {member.mention} خرج من السجن")

# ───── Run ─────
keep_alive() # هذا السطر يبدأ السيرفر الوهمي قبل تشغيل البوت
bot.run(os.getenv("TOKEN"))