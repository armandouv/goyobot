import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

################################
description = "Un bot que ayuda a verificar miembros del servidor de Internships UNAM"
TOKEN = str(os.getenv("DISCORD_TOKEN"))
MOD_CHANNEL_ID = int(os.getenv("MOD_CHANNEL_ID"))

# EMOJIS🥶🥶🥶🥶
EMOJI_CHECKMARK = "✅"
EMOJI_ENVELOPE = "✉️"
EMOJI_EYES = "👀"
EMOJI_DELETE = "❌"

# discord stuff
client = discord.Client()
Embed = discord.Embed
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix="$", description=description, intents=intents)

################################
# MESSAGES #

# Reactions to verify user
BOT_NAME = "goyo"

VERIFIED_MESSAGE = (
    "¡Tu cuenta ha sido verificada! Ahora puedes ver todos los canales del servidor. :)"
)
FURTHER_VERIFICATION = (
        "Nos gustaria preguntarte algunas cosas sobre tu prueba de verificación.\n"
        "\n¡No te preocupes! Un moderador se pondrá en contacto contigo pronto.\n\nRecuerda, ¡también puedes enviarnos "
        "un mensaje con `$%s dm_mods` + el mensaje que quieres enviar! " % BOT_NAME
)

DOES_NOT_SATISFY = (
    "Los moderadores recibieron tu documento, pero no pueden verificarte por ahora.\n"
    "Razón: *Por favor asegúrate de que el documento que presentas compruebe tu inscripción en la UNAM. "
    "Recuerda que éste puede ser una foto de tu credencial o de tu historial académico.*"
)

# DMing Bot
INITIAL_GREETING = (
                       "¡Hola! Este es el bot verificador para el servidor de Internships UNAM. Para hacer las cosas "
                       "más fáciles para los moderadores y acelerar el proceso de verificación, **por favor envía aquí "
                       "una foto de tu credencial de la UNAM, o bien, de tu historial académico. "
                       "Asegúrate de que tu nombre completo sea legible. Puedes ocultar tu foto y número de cuenta si así lo deseas.**\n\n"
                       "Después de enviar esto, un moderador revisará el documento que enviaste, y yo mismo te haré saber cuando tu "
                       "acceso haya sido aprobado, o bien, si se requiere otra acción de tu parte para verificarte. Si necesitas "
                       "asistencia, por favor escribe `$%s dm_mods`, para que alguien te ayude. También puedes enviar un mensaje "
                       "personalizado a los moderadores al escribir el comando anterior, seguido del mensaje que quieres.\n\n"
                       "¡El equipo de moderación te desea lo mejor, y espera que tengas una cacería de internships exitosa!\n\n"
                       "**¡GOOOOYAAA!**"
                   ) % (
                       BOT_NAME
                   )

HELP_IS_ON_WAY = (
    "¡Ayuda en camino! Por favor espera a que uno de nuestros moderadores te contacte. "
)

PROOF_RECEIVED = "Documento recibido. Los moderadores lo revisarán pronto :)"

COMMAND_HELP = (
        "\n\n**Comandos disponibles:**\n\n`$%s verify` para obtener las instrucciones de verificación.\n\n`$%s "
        "dm_mods` para hablar con un "
        "moderador.\n\n"
        "También puedes enviar un mensaje personalizado a los moderadores al escribir el comando anterior, seguido del "
        "mensaje que deseas enviarnos. " % (BOT_NAME, BOT_NAME)
)

INVALID_COMMAND = "Chale, no entendí eso. ¿Tas bien?\n** **\n"

# Notifying mods about user
NOTIFICATION_VERIFY = (
    "<@%s> ha solicitado que la imagen de arriba se use como prueba de verificación."
    "\n%s Para aprobar al usuario"
    "\n%s Para hacerle saber que l@ contactarás para obtener más información."
    "\n%s Si su prueba es inválida."
    "\n%s Para eliminar el mensaje."
)

NOTIFICATION_HELP = (
    "El usuario <@%s> ha solicitado que un moderador lo contacte por ayuda.  "
)

BOT_JOKE_PHRASE = (
    "Pinches Pumas ya ganen por favor o me voy a Tigres. :("
)


################################


@client.event
async def on_ready():
    print("Sesión iniciada como {0.user}".format(client))


@client.event
async def on_raw_reaction_add(reaction):
    """
    Help mods attribute "verified" role by simply clicking on a react button
    :param _user: [unused param]
    :param reaction: a reaction object to the message. Includes
        - reaction.count , the amount of people having reacted with this emoji
        - reaction.message , the message object within the reaction (see param of on_message for more info)
            - reaction.message.mentions , helping us identify the user tagged in the message, if any
    """
    if reaction.channel_id != MOD_CHANNEL_ID or reaction.user_id == client.user.id:
        return

    channel = await client.fetch_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    guild = await client.fetch_guild(reaction.guild_id)

    if (
            message.mentions
    ):
        userino = message.mentions[0]
        memberino = await guild.fetch_member(userino.id)
        if str(reaction.emoji) == EMOJI_CHECKMARK:
            role = discord.utils.get(guild.roles, name="Verificado")
            await memberino.add_roles(role)
            await userino.send(VERIFIED_MESSAGE)
            await message.delete()

        elif str(reaction.emoji) == EMOJI_ENVELOPE:
            await userino.send(FURTHER_VERIFICATION)

        elif str(reaction.emoji) == EMOJI_EYES:
            await userino.send(DOES_NOT_SATISFY)

        elif str(reaction.emoji) == EMOJI_DELETE:
            await message.delete()


@client.event
async def on_message(message):
    """
    The core exchange between bot and a user
    :param message: the message object sent to the bot. Includes
        - message.channel
        - message.content (the string of a message)
        - message.attachments , a list of attachments such as a picture, a link, etc
        - message.author , the user object that sent the message
    """
    mod_channel = client.get_channel(MOD_CHANNEL_ID)

    if message.author == client.user:
        return
    if message.content.startswith("$%s tell me a joke" % BOT_NAME):  # little easter egg
        await message.channel.send(BOT_JOKE_PHRASE)

    elif isinstance(message.channel, discord.channel.DMChannel):
        # send proof to mod channel, notify mods, and offer reaction options
        if len(message.attachments) != 0:
            await message.channel.send(PROOF_RECEIVED)
            attachment = await message.attachments[0].to_file()
            last_message = await mod_channel.send(
                content=NOTIFICATION_VERIFY
                        % (
                            message.author.id,
                            EMOJI_CHECKMARK,
                            EMOJI_ENVELOPE,
                            EMOJI_EYES,
                            EMOJI_DELETE,
                        ),
                file=attachment,
            )
            await last_message.add_reaction(EMOJI_CHECKMARK)
            await last_message.add_reaction(EMOJI_ENVELOPE)
            await last_message.add_reaction(EMOJI_EYES)
            await last_message.add_reaction(EMOJI_DELETE)

        # display info for user wanting to verify themselves or to message mods.
        elif str(message.content).lower().startswith("$%s verify" % BOT_NAME):
            await message.channel.send(INITIAL_GREETING)

        elif str(message.content).lower().startswith("$%s dm_mods" % BOT_NAME):
            await message.channel.send(HELP_IS_ON_WAY)
            await mod_channel.send(NOTIFICATION_HELP % message.author.id)

            if len(message.content.strip()) > len("$%s dm_mods" % BOT_NAME) + 1:
                # if user has attached an additional message
                await mod_channel.send(
                    'También envió el siguiente mensaje: "%s"'
                    % message.content[len("$%s dm_mods" % BOT_NAME) + 1:]
                )

        elif str(message.content).lower().startswith("$%s" % BOT_NAME) or not str(
                message.content
        ).lower().startswith("$%s" % BOT_NAME):
            if (
                    not str(message.content).lower().startswith("$%s" % BOT_NAME)
                    or len(message.content) > len("$%s" % BOT_NAME) + 1
            ):
                await message.channel.send(INVALID_COMMAND)
            await message.channel.send(COMMAND_HELP)

    elif message.content.startswith(
            "$%s" % BOT_NAME
    ):  # if users try to call it outside of DMs.
        await message.channel.send(
            "Todavia no respondo a comandos normales fuera de DMs. :("
        )


client.run(TOKEN)
