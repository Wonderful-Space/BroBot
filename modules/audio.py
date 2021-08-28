import asyncio

import discord
import emoji
import youtube_dl
from discord import VoiceClient
from discord.ext.commands import Context

from modules import bot

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
	'format': 'bestaudio/best',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	'source_address': '0.0.0.0'
}

ffmpeg_options = {
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)
		self.data = data
		self.title = data.get('title')
		self.url = ""

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]
		filename = data['url'] if stream else ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


async def _leave_voice_channels():
	for client in bot.voice_clients:
		await client.disconnect()


@bot.command()
async def play(ctx: Context, url: str):
	author = ctx.author

	voice = author.voice
	if not voice:
		await ctx.send(f'{author.mention} is not in a voice channel! Please join a voice channel first.')
		return

	clients = bot.voice_clients
	# If not connected to voice, connect.
	if len(clients) == 0:
		await voice.channel.connect()
		clients = bot.voice_clients

	audio = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
	voice_client: VoiceClient = clients[0]

	# Stop any currently playing audio.
	voice_client.stop()
	# Play requested audio.
	voice_client.play(audio)

	await ctx.message.add_reaction(emoji.emojize(':thumbs_up:'))
	await ctx.send(f'**Now playing:** {audio.title}')


@bot.command()
async def stop(ctx: Context):
	voice_clients = bot.voice_clients
	if len(voice_clients) == 0:
		await ctx.send('No audio playing.')
	else:
		voice_client: VoiceClient = voice_clients[0]
		voice_client.stop()
		await ctx.message.add_reaction(emoji.emojize(':thumbs_up:'))


@bot.command()
async def pause(ctx: Context):
	voice_clients = bot.voice_clients
	if len(voice_clients) == 0:
		await ctx.send('No audio playing.')
	else:
		voice_client: VoiceClient = voice_clients[0]
		voice_client.pause()
		await ctx.message.add_reaction(emoji.emojize(':thumbs_up:'))


@bot.command()
async def resume(ctx: Context):
	voice_clients = bot.voice_clients
	if len(voice_clients) == 0:
		await ctx.send('No audio playing.')
	else:
		voice_client: VoiceClient = voice_clients[0]
		voice_client.resume()
		await ctx.message.add_reaction(emoji.emojize(':thumbs_up:'))
