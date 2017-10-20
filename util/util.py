import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.figure import Figure


def plot_flight_to_label(filename, size_ts, size_lat_lon):

    data = load_flights([filename])[0]

    fig_ts = Figure(figsize=size_ts, dpi=100)
    ax = fig_ts.add_subplot(411)
    ax.plot(data["AltGPS"])
    ax.set_ylabel("AltGPS (m)")
    ax.tick_params(labelbottom='off')

    ax = fig_ts.add_subplot(412, sharex=ax)
    ax.plot(data["Roll"], color="darkgreen")
    ax.set_ylabel("Roll")
    ax.tick_params(labelbottom='off')

    ax = fig_ts.add_subplot(413, sharex=ax)
    ax.plot(data["Pitch"], color="dodgerblue")
    ax.set_ylabel("Pitch")
    ax.tick_params(labelbottom='off')

    ax = fig_ts.add_subplot(414, sharex=ax)
    ax.plot(data["HDG"], color="tomato")
    ax.set_ylabel("Heading")
    ax.set_xlabel("Index")

    fig_ts.set_tight_layout(True)

    size_lat_lon = min(size_lat_lon), min(size_lat_lon)
    fig_lat_lon = Figure(figsize=size_lat_lon, dpi=100)
    ax = fig_lat_lon.add_subplot(111)
    ax.plot(data["Longitude"], data["Latitude"])
    ax.set_aspect('equal', 'datalim')
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    fig_lat_lon.set_tight_layout(True)

    return fig_ts, fig_lat_lon


def plot_flights(file_names, shape, figsize):

    all_data = load_flights(file_names)

    gs = GridSpec(nrows=shape[0], ncols=shape[1])
    fig = Figure(figsize=figsize, dpi=100)

    for i, data in enumerate(all_data):
        row = i // shape[1]
        col = i % shape[1]
        ax = fig.add_subplot(gs[row, col])
        ax.plot(data["AltGPS"])
        ax.set_xlabel("Index")
        ax.set_ylabel("AltGPS (m)")
        ax.set_title(file_names[i])

    fig.set_tight_layout(True)

    return fig


def load_flights(file_names):
    dfs = []
    file_names = set(file_names)
    for file_name in file_names:
        try:
            df = pd.read_csv(file_name, skiprows=2, encoding="latin1")
            df = df[["AltGPS", "Roll", "Pitch", "HDG", "Latitude", "Longitude"]]
        except KeyError:
            df = pd.read_csv(file_name, skiprows=1, encoding="latin1")
            df = df[["AltGPS", "Roll", "Pitch", "HDG", "Latitude", "Longitude"]]
        except:
            print("Unexpected error while opening file '{}'".format(file_name))
            raise
        dfs.append(df)
    return dfs
