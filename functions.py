from PIL import Image
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
import io

def show_images(query, emote_db):
    """
    Show image in a new window
    """
    result = emote_db.find_emote_by_name(query, mode='contains', fetch_all=True)
    fig = plt.figure(figsize=(5., 5.))
    grid = ImageGrid(fig, 111,  # similar to subplot(111)
                    nrows_ncols=(5, 5), 
                    axes_pad=0.3,  # pad between axes in inch.
                    )
    for index, ax in enumerate(grid):
        # Iterating over the grid returns the Axes.
        if index < len(result):
            im = Image.open(io.BytesIO(result[index][2]))
            ax.imshow(im)
            ax.title.set_text(result[index][1])
            ax.title.set_fontsize(6)
        ax.axis('off')
    plt.savefig(f'output/temp_grid.png', pad_inches=0, bbox_inches='tight')