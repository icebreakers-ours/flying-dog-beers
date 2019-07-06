e3_rgb = {
    "Aquamarine": "#66FAA2",
    "Black": "#000000",
    "Casablanca": "#FFB868",
    "Cerulean": "#0679AB",
    "Cinnamon": "#765400",
    "Dandelion": "#FFD468",
    "Dark Tangerine": "#FFB700",
    "Flush Orange": "#FF8700",
    "Grey": "#969696",
    "Indigo": "#4458D2",
    "Jade": "#00BF4D",
    "Slate Blue": "#798BFA",
    "Maroon": "#761700",
    "Mercury": "#E6E6E6",
    "Milano Red": "#AF2200",
    "Neon Carrot": "#FFA239",
    "Nutmeg": "#763E00",
    "Pelorous": "#349DCA",
    "Persian Blue": "#132AB7",
    "Persimmon": "#FF5F39",
    "Pirate Gold": "#AF7E00",
    "Prussian Blue": "#01344A",
    "Regal Blue": "#034E6E",
    "Salmon": "#FF8568",
    "Sapphire": "#0A1978",
    "Scarlet": "#FF3100",
    "Shamrock": "#30D773",
    "Sky Blue": "#6CCEF9",
    "Spring Green": "#007E33",
    "Sunglow": "#FFC739",
    "Tawny": "#AF5D00",
}

e3_hues = dict(
    blue2=["#034E6E", "#349DCA", "#0679AB", "#6CCEF9", "#01344A"],
    yellow=["#AF7E00", "#FFC739", "#FFB700", "#FFD468", "#765400"],
    red=["#AF2200", "#FF5F39", "#FF3100", "#FF8568", "#761700"],
    green=["#007E33", "#30D773", "#00BF4D", "#66FAA2"],
    orange=["#AF5D00", "#FFA239", "#FF8700", "#FFB868", "#763E00"],
    blue=["#0A1978", "#4458D2", "#132AB7", "#798BFA"],
    bw=["#E6E6E6", "#969696", "#000000"],
)

e3_palettes = dict(
    dark=["#034E6E", "#AF7E00", "#AF2200", "#007E33", "#AF5D00", "#0A1978"],
    light=["#349DCA", "#FFC739", "#FF5F39", "#30D773", "#FFA239", "#4458D2"],
    deep=["#0679AB", "#FFB700", "#FF3100", "#00BF4D", "#FF8700", "#132AB7"],
    pastel=["#6CCEF9", "#FFD468", "#FF8568", "#66FAA2", "#FFB868", "#798BFA"],
)


def show_palette(colors):
    """Plot a seaborn palplot of a color list with the list incides labeled
    Arguments--
    colors: a list of colors

    """

    from seaborn import palplot
    import matplotlib.pyplot as plt

    palplot(colors)
    ax = plt.gca()
    labs = [int(x) for x in ax.get_xticks() + 0.5]
    ax.set_xticks(labs)
    ax.set_xticklabels(labs, fontsize=16)
    return ax
