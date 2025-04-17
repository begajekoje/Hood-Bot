import discord
from discord.ext import commands

TOKEN = "MTM2MjM0NTg1NjU3NzA0NDY0MQ.GQ_4Rk.ZF_qLNg9TsyzBJhWb4X1tqcpl3sA1Hu00Io_RA"
PRIJAVA_CHANNEL_ID = 1328892431290335292
LOG_CHANNEL_ID = 1362340161974829098

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot aktivan kao {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == PRIJAVA_CHANNEL_ID:
        content = message.content

        if all(kljuc in content for kljuc in [
            "Discord korisničko ime:",
            "Datum i vrijeme izricanja kazne:",
            "Vrsta kazne:",
            "Razlog kazne:",
            "Dokazi:"
        ]):
            await message.delete()

            linije = content.splitlines()
            podaci = {}
            for linija in linije:
                if ":" in linija:
                    kljuc, vrijednost = linija.split(":", 1)
                    podaci[kljuc.strip()] = vrijednost.strip()

            # Custom emoji ID-ovi (VEĆ tvoj set)
            emoji_user = "<:Korisnik:1362341811527618590>"
            emoji_time = "<a:arrow:1341588341358989382>"
            emoji_warn = "<a:arrow:1341588341358989382>"
            emoji_reason = "<a:arrow:1341588341358989382>"
            emoji_proof = "<a:arrow:1341588341358989382>"
            emoji_title = "<:Info:1334186844782465097>"

            embed = discord.Embed(
                title=f"{emoji_title} Nova prijava kazne",
                color=0xff0000
            )
            embed.add_field(name=f"{emoji_user} Discord korisnik", value=podaci.get("Discord korisničko ime", "N/A"), inline=False)
            embed.add_field(name=f"{emoji_time} Datum i vrijeme", value=podaci.get("Datum i vrijeme izricanja kazne", "N/A"), inline=False)
            embed.add_field(name=f"{emoji_warn} Vrsta kazne", value=podaci.get("Vrsta kazne", "N/A"), inline=False)
            embed.add_field(name=f"{emoji_reason} Razlog", value=podaci.get("Razlog kazne", "N/A"), inline=False)
            embed.add_field(name=f"{emoji_proof} Dokazi", value=podaci.get("Dokazi", "N/A"), inline=False)
            embed.set_footer(text=f"Poslao: {message.author}", icon_url=message.author.avatar.url if message.author.avatar else None)

            await message.channel.send(embed=embed)

            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(
                    f"""📥 Prijavu poslao: {message.author.mention}
```{content}```"""
                )

    await bot.process_commands(message)

@bot.command(name="prijava")
async def prijava(ctx):
    try:
        await ctx.message.delete()

        embed = discord.Embed(
            title="<:Info:1334186844782465097> Prijava kazne – Obrazac",
            description=(
                "*Popuni sljedeće podatke i pošalji kao poruku:*\n\n"
                "*Discord korisničko ime:*\n"
                "*Datum i vrijeme izricanja kazne:*\n"
                "*Vrsta kazne:*\n"
                "*Razlog kazne:*\n"
                "*Dokazi:*"
            ),
            color=0x2ecc71
        )
        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("⛔ Nemam permisije da izbrišem tvoju komandu ili pošaljem poruku.")

bot.run(TOKEN)