import discord
from discord.ext import commands, tasks
import asyncio
import json
import os

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

CHANNEL_ID = 1319078639454912603
SCORE_FILE = "xo_scores.json"

game_active = False
player1 = None
player2 = None
current_turn = None
board = [" " for _ in range(9)]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents)

# Učitavanje rezultata iz fajla
if os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "r") as f:
        scores = json.load(f)
else:
    scores = {}

def save_scores():
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f)

class TicTacToeButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(label="_", style=discord.ButtonStyle.success, row=y)
        self.x = x
        self.y = y
        self.index = y * 3 + x

    async def callback(self, interaction: discord.Interaction):
        global current_turn, board, player1, player2

        if interaction.user != current_turn:
            await interaction.response.send_message("Nije tvoj potez!", ephemeral=True)
            return

        if board[self.index] != " ":
            await interaction.response.send_message("Polje je već zauzeto!", ephemeral=True)
            return

        symbol = "X" if interaction.user == player1 else "O"
        board[self.index] = symbol
        self.label = symbol
        self.style = discord.ButtonStyle.success
        self.disabled = True

        winner = check_winner()
        if winner:
            await interaction.response.edit_message(content=f"🎉 Pobjednik je {interaction.user.mention}!", view=self.view)
            self.view.disable_all_buttons()
            scores[str(interaction.user.id)] = scores.get(str(interaction.user.id), 0) + 1
            save_scores()
            return

        if " " not in board:
            await interaction.response.edit_message(content=f"🤝 Neriješeno!", view=self.view)
            self.view.disable_all_buttons()
            return

        current_turn = player2 if current_turn == player1 else player1
        await interaction.response.edit_message(content=f"🎮 Na potezu: {current_turn.mention}", view=self.view)

class TicTacToeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))

    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True

class JoinButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.joined = []

    @discord.ui.button(label="Pridruži se igri", style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        global player1, player2, game_active, current_turn, board

        if interaction.user in self.joined:
            await interaction.response.send_message("Već si ušao u igru!", ephemeral=True)
            return

        self.joined.append(interaction.user)

        if not player1:
            player1 = interaction.user
            await interaction.response.send_message(f"🎮 {player1.mention} je prvi igrač!", ephemeral=False)
        elif not player2:
            player2 = interaction.user
            await interaction.response.send_message(f"🎮 {player2.mention} je drugi igrač!", ephemeral=False)
            game_active = True
            current_turn = player1
            board = [" " for _ in range(9)]
            self.disable_all_items()

            await interaction.channel.send(
                content=f"🎮 Na potezu: {current_turn.mention}",
                view=TicTacToeView()
            )

    def disable_all_items(self):
        for item in self.children:
            item.disabled = True

@bot.event
async def on_ready():
    print(f"✅ Bot aktivan kao {bot.user}")
    tic_tac_toe_loop.start()

@tasks.loop(hours=2)
async def tic_tac_toe_loop():
    await send_ttt_panel()

@bot.command(name="startx")
async def startx(ctx):
    await send_ttt_panel(ctx.channel)

@bot.command(name="rang")
async def rang(ctx):
    if not scores:
        await ctx.send("📊 Nema još rezultata.")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="🏆 Rang lista Tic-Tac-Toe", color=0x00ff00)
    for idx, (user_id, score) in enumerate(sorted_scores[:10], start=1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(name=f"#{idx} {user.name}", value=f"Pobjede: {score}", inline=False)
    await ctx.send(embed=embed)

async def send_ttt_panel(channel=None):
    global player1, player2, game_active
    player1 = None
    player2 = None
    game_active = False

    if channel is None:
        channel = bot.get_channel(CHANNEL_ID)

    if channel:
        embed = discord.Embed(
            title="🎮 X i O Hajmoo!",
            description="*Prva dva igrača koji kliknu dugme ulaze u igru*!",
            color=0x5865F2
        )
        await channel.send(embed=embed, view=JoinButton())

def check_winner():
    # Win conditions
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    for combo in wins:
        a, b, c = combo
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

bot.run(TOKEN)