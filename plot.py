#!/usr/bin/python3

import json

import click
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class FortioLine:
    def __init__(self, file):
        self.file = file
        with open(self.file, 'r') as f:
            self.raw_data = json.load(f)

        self.title = self.raw_data.get("Labels")
        self.start_time = self.raw_data.get("StartTime")
        self.qps = self.raw_data.get("RequestedQPS")
        self.histogram = self.raw_data.get("DurationHistogram")
        self.percentiles = self.raw_data.get("DurationHistogram").get("Percentiles")

PERCENTILS=[50, 75, 90, 99, 99.9]

@click.command()
@click.option("--graph", type=str, help="graph file name")
@click.argument("files", nargs=-1)
def run(graph, files):
    lines = []
    data_frame = []
    for i in ['percentile'] + PERCENTILS:
        data_frame.append([i])

    for file in files:
        line = FortioLine(file)
        lines.append(line)

        data_frame[0].append(line.title)
        for idx, p in enumerate(PERCENTILS):
            data_frame[idx+1].append(line.percentiles[idx]['Value'] * 1000)

    df = pd.DataFrame(data_frame[1:], columns=data_frame[0], dtype=float)
    print(df)

    sns.set_theme()
    sns.lineplot(
            data=pd.melt(df, ['percentile'], var_name='Connections', value_name='latency (ms)'),
            x='percentile',
            y='latency (ms)',
            hue='Connections',
            style='Connections',
            markers=True,
            dashes=False,
        )
    for item, color in zip(pd.melt(df, ['percentile'], var_name='Connections', value_name='latency (ms)').groupby('Connections'), sns.color_palette()):
        print(item[0])
        print(item[1])
        for x, y, m in item[1][['percentile', 'Connections', 'latency (ms)']].values:
            plt.text(x,m+0.1,"{:.2f}".format(m), color=color)

    plt.savefig(f"{graph}.svg")

if __name__ == '__main__':
    run()

