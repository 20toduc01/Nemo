import os, discord, pickle

def mkdirs(dir):
    try:
        os.makedirs(dir[:dir.rfind('/')])
    except:
        pass


async def impersonate_message(target_message : discord.Message, message_content):
    '''
    Send a new message with message_content to the same channel
    as target_message, using nickname and avatar of sender.
    The trick is to use/create a webhook for the channel

    Arguments:
        target_message -- The target Message object
        message_content -- Content of the new message

    Returns:
        None
    '''
    webhook = discord.utils.get(await target_message.channel.webhooks())
    display_name = target_message.author.display_name
    avatar_url = target_message.author.avatar_url
    target_channel = target_message.channel

    if webhook is None:
        webhook = await target_channel.create_webhook(name="SpinBot Hook")

    await webhook.send(content=message_content, username=display_name, avatar_url=avatar_url, wait=True)


from PIL import Image
from io import BytesIO

def bytes_to_image(bytes):
    '''
    Convert bytes to image

    Arguments:
        bytes -- Bytes of image

    Returns:
        PIL Image object
    '''
    
    img = Image.open(BytesIO(bytes))
    return img

import numpy as np
def stable_softmax(x):
    z = x - np.max(x, axis=-1, keepdims=True)
    numerator = np.exp(z)
    denominator = np.sum(numerator, axis=-1, keepdims=True)
    softmax = numerator / denominator
    return softmax