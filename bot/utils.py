import os
import discord
from matplotlib import pyplot as plt

from io import BytesIO
from PIL import Image
from mpl_toolkits.axes_grid1 import ImageGrid


async def impersonate_message(target_message: discord.Message, 
                              message_content: str,
                              delete_original=True):
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

    await webhook.send(content=message_content, username=display_name, 
                       avatar_url=avatar_url, wait=True)
    if delete_original:
        await target_message.delete()


def mkdirs(dir):
    try:
        os.makedirs(dir)
    except:
        pass


def bytes_to_image(bytes):
    '''
    Convert bytes to image
    '''
    return Image.open(BytesIO(bytes))


def collate(images, cols=2, rows=2, titles=None):
    '''
    Collate images into a grid
    '''
    fig = plt.figure(figsize=(cols, rows))
    grid = ImageGrid(fig, 111, nrows_ncols=(rows, cols), axes_pad=0.3)

    for idx, ax in enumerate(grid):
        # Iterating over the grid returns the Axes.
        if idx < len(images):
            im = images[idx]
            ax.imshow(im)
            if titles is not None:
                ax.set_title(titles[idx])
                ax.title.set_fontsize(6)
        ax.axis('off')
    return fig