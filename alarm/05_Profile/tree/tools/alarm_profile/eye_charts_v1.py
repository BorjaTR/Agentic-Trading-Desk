"""tools/alarm_profile EYE CHARTS v1 (QUANT 22 Oct 2026): the charts for the two eye proofs SCOUT judges (PROOFS_V1 P4_EYE_RUN, P4_EYE_WAVES),
drawn from the proof run's samples (alarms drawn by seed, not chosen). Nothing here computes a value: the marks come from the built values.
  run    EYE_RUN_SAMPLE.tsv -> 12 panels: the push-signed price of the 24 h before each alarm (up = the push), the tool's RUN START (blue)
         and the BURST START (orange, dashed). SCOUT answers per panel: is the blue line where the move began? (YES / NO / UNSURE)
  waves  EYE_WAVES_SAMPLE.tsv -> 12 panels: the forced side's 5 s liquidation rows from 2 min before the onset to the alarm, as bars;
         NO count is shown (the tool's count is in a key SCOUT opens only after answering). SCOUT answers per panel: how many separate waves?
Colors: the dataviz reference palette's first two categorical slots (validated earlier, run_start_chart_v1), text in ink tones.
  python3 -B eye_charts_v1.py run <EYE_RUN_SAMPLE.tsv> <out png>
  python3 -B eye_charts_v1.py waves <EYE_WAVES_SAMPLE.tsv> <out png>"""
import csv, collections, datetime, sys
import numpy as np

SURF, INK, INK2, GRID, BLUE, ORANGE = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df', '#2a78d6', '#eb6834'


def _fig(n, cols=4, h=3.0):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 8, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
                         'text.color': INK})
    rws = (n + cols - 1) // cols
    fig, axes = plt.subplots(rws, cols, figsize=(15, h * rws), facecolor=SURF, squeeze=False)
    return plt, fig, axes, rws


def _style(ax):
    ax.set_facecolor(SURF); ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)


def run_chart(sample, out_png, view='zoom'):
    """v1 samples: panels in time order; v2 samples (a 'chart' column): panels in the sample's drawn order. view 'zoom': from an hour
    (or half the run) before the marked start; view '24h': the whole 24 h before the alarm"""
    by = collections.OrderedDict()
    with open(sample) as f:
        rd = csv.DictReader(f, delimiter='\t'); v2 = 'chart' in rd.fieldnames
        for r in rd:
            by.setdefault(int(r['chart']) if v2 else (r['coin'], int(r['t'])), []).append(r)
    keys = sorted(by) if v2 else sorted(by, key=lambda k: k[1]); plt, fig, axes, rws = _fig(len(keys))
    for i, (ax, k) in enumerate(zip(axes.flat, keys), 1):
        rows = by[k]; t0 = int(rows[0]['t']); st = float(rows[0]['start_t']); bt = float(rows[0]['burst_t']); side = int(rows[0]['side'])
        coin = rows[0]['coin']
        t = np.array([int(r['minute']) for r in rows], float); x = np.array([float(r['x_pct']) if r['x_pct'] not in ('', 'nan') else np.nan for r in rows])
        x = x - x[-1]; keep = (t >= st - max(3600, 0.5 * (t0 - st))) if view == 'zoom' else np.isfinite(t)
        _style(ax); ax.plot((t[keep] - t0) / 60.0, x[keep], color=INK2, lw=1.4)
        ax.axvline((st - t0) / 60.0, color=BLUE, lw=2, label='run start (the tool)')
        ax.axvline((bt - t0) / 60.0, color=ORANGE, lw=2, ls='--', label='liquidations begin (burst start)')
        d = datetime.datetime.fromtimestamp(t0, datetime.timezone.utc)
        ax.set_title('%d. %s %s UTC, %s' % (i, coin, d.strftime('%d %b %H:%M'), 'pushed up' if side > 0 else 'pushed down'), fontsize=8.5,
                     color=INK, loc='left')
        ax.set_xlabel('minutes before the alarm')
    for j in range(rws):
        axes[j][0].set_ylabel('price vs the alarm, % (up = the push)')
    for ax in list(axes.flat)[len(keys):]:
        ax.set_visible(False)
    h, l = axes.flat[0].get_legend_handles_labels()
    fig.suptitle(('P4 EYE RUN: is the blue line where the move began? %d alarms drawn by seed, not chosen (prices before the alarm only; ' + view + ')' if v2 else
                  'P4 EYE RUN: is the blue line where the move began? %d alarms drawn by seed 22102026 (prices before the alarm only)') % len(keys),
                 y=0.995, fontsize=11, color=INK)
    fig.legend(h, l, loc='upper center', ncol=2, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.965))
    fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(out_png, dpi=130, facecolor=SURF)


def waves_chart(sample, out_png):
    by = collections.OrderedDict()
    with open(sample) as f:
        for r in csv.DictReader(f, delimiter='\t'):
            by.setdefault(int(r['chart']), []).append(r)
    keys = sorted(by); plt, fig, axes, rws = _fig(len(keys), h=2.6)
    for ax, k in zip(axes.flat, keys):
        rows = by[k]; t0 = int(rows[0]['t']); side = int(rows[0]['side'])
        te = np.array([int(r['row_end']) for r in rows], float); v = np.array([float(r['forced_usd']) if r['forced_usd'] not in ('', 'nan') else np.nan for r in rows])
        _style(ax); ax.bar((te - t0 - 2.5), np.nan_to_num(v) / 1000.0, width=4.0, color=BLUE)
        if 'onset_t' in rows[0]:                                       # the waves count from the onset row (README: big waves)
            ax.axvline(int(rows[0]['onset_t']) - t0, color=INK2, lw=1.2, ls='--', label='onset (waves count from here)')
        miss = ~np.isfinite(v)
        if miss.any():
            ax.plot(te[miss] - t0 - 2.5, np.zeros(miss.sum()), 'x', color=ORANGE, ms=4, label='no data (hole)')
        d = datetime.datetime.fromtimestamp(t0, datetime.timezone.utc)
        ax.set_title('%d. %s %s UTC, %s forced' % (k, rows[0]['coin'], d.strftime('%d %b %H:%M'), 'shorts' if side > 0 else 'longs'),
                     fontsize=8.5, color=INK, loc='left')
        ax.set_xlabel('seconds before the alarm')
    for j in range(rws):
        axes[j][0].set_ylabel('forced liquidations per 5 s, thousand USD')
    for ax in list(axes.flat)[len(keys):]:
        ax.set_visible(False)
    fig.suptitle('P4 EYE WAVES: how many separate waves of forced liquidations? %d alarms drawn by seed 22102027 (count before opening the key)'
                 % len(keys), y=0.985, fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(out_png, dpi=130, facecolor=SURF)


if __name__ == '__main__':
    {'run': run_chart, 'waves': waves_chart}[sys.argv[1]](*sys.argv[2:])
