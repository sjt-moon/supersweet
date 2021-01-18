from io import StringIO


def drawMatplotLibGraph(fig):
    """Draw a matplotlib fig for Django to show."""
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return data
