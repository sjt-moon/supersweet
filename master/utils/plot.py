from matplotlib import pyplot as plt


def plotLine(df, col1, col2, **kwargs):
    x = df[col1]
    y = df[col2]
    fig = plt.figure()
    plt.legend()
    plt.xlabel(col1)
    plt.ylabel(col2)
    if 'title' in kwargs:
        plt.title(kwargs['title'])
    else:
        plt.title('Visualization between %s and %s' % (col1, col2))
    plt.plot(x, y)
    return fig
