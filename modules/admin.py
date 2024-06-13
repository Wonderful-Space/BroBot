import re

from discord.ext.commands import Context

from database.db import update_currency
from env import ADMIN_IDS
from modules import bot


QUOTES_CHANNEL_ID = 871496158474821654


def _check_admin(user_id: int) -> bool:
	return user_id in ADMIN_IDS


@bot.command()
async def purge(ctx: Context):
	author = ctx.author
	if not ctx.channel.id == QUOTES_CHANNEL_ID:
		if _check_admin(author.id):
			# only 100 messages
			await ctx.channel.purge()
			await ctx.send(f'{author.mention} Purge successful.')
		else:
			await ctx.send(f'{author.mention} You do not have permission to do that.')
	else:
		await ctx.send(f'{author.mention} HAHAHAHAHAHA. You thought you could purge the quotes!\n'
					   f'@everyone Look at them. Laugh at them. Shame them.')


@bot.command()
async def testgrant(ctx: Context):
	key = ctx.author.id
	update_currency(key, 100000, test=True)
	await ctx.send(f'{ctx.author.mention} was granted 100,000 test diggities.')


@bot.command()
async def grant(ctx: Context):
	author = ctx.author
	if _check_admin(author.id):
		target = re.findall(r'<@(\d*)>', ctx.message.content) or None
		target = target[0]
		update_currency(target, 1000)
		await ctx.send(f"{ctx.author.mention} gave <@{target}> **1000 diggities**.")
	else:
		await ctx.send(f'{author.mention} You do not have permission to do that.')
