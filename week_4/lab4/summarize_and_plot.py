"""Summarize discrepancies and generate simple bar plots for lab4."""
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt


def summarize(in_csv: str, out_dir: str):
    df = pd.read_csv(in_csv)
    if 'Discrepancy' not in df.columns or 'file_type' not in df.columns:
        raise SystemExit('Input CSV must have Discrepancy and file_type columns')
    stats = df.groupby(['file_type', 'Discrepancy']).size().unstack(fill_value=0)
    mismatches = stats.get('Yes', pd.Series(dtype=int))
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8,4))
    mismatches.plot(kind='bar', ax=ax)
    ax.set_ylabel('#Mismatches')
    ax.set_title('Mismatches by file type')
    fig.tight_layout()
    out_png = os.path.join(out_dir, 'mismatches_by_file_type.png')
    fig.savefig(out_png)
    print('Wrote', out_png)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--in', dest='in_csv', required=True)
    p.add_argument('--outdir', dest='out_dir', required=True)
    args = p.parse_args()
    summarize(args.in_csv, args.out_dir)
