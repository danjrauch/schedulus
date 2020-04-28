import click
import random
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc
import pandas as pd
import src.schedulus as schedulus


def command_required_option_from_option(master, requires):
    class CommandOptionRequiredClass(click.Command):
        def invoke(self, ctx):
            if ctx.params[master] is not None:
                for require in requires:
                    if ctx.params[require.lower()] is None:
                        raise click.ClickException('With {}={} must specify option --{}'.format(master, ctx.params[master], require))
            super(CommandOptionRequiredClass, self).invoke(ctx)
    return CommandOptionRequiredClass


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Main command."""
    if ctx.invoked_subcommand is None:
        click.echo(click.style('Hello, please invoke a command', fg = 'bright_red'))


@cli.command(cls=command_required_option_from_option('type', ['path', 'backfill']))
@click.argument('type', type=click.Choice(['fcfs']))
@click.option('--path', '-p', type=click.Path(exists=True, dir_okay=True))
@click.option('--backfill', '-b', type=click.Choice(['none', 'easy', 'all']))
@click.option('--nodes', '-n', required=True, type=int)
def run(type, path, backfill, nodes):
    """Run the scheduler."""
    schedulers = []

    if backfill is 'all':
        for backfill_type in ['none', 'easy']:
            schedulers.append(schedulus.Schedulus(nodes, backfill_type, path))
            schedulers[-1].read_jobs(path)
            schedulers[-1].run(type)
    else:
        schedulers.append(schedulus.Schedulus(nodes, backfill, path))
        schedulers[-1].read_jobs(path)
        schedulers[-1].run(type)

    # plot_stat(schedulers, 'num_running_jobs')
    plot_job_wait(schedulers)

    # for scheduler in schedulers:
    #     tot = 0
    #     n = 0
    #     for k, v in scheduler.stats.items():
    #         tot += v['utilization']
    #         n += 1
    #     print(f'Approximate Average Utilization for {scheduler.backfill} = {tot/n}')


def plot_stat(schedulers, stat):
    if not schedulers:
        return

    fig = go.Figure()

    for scheduler in schedulers:
        xs = [k for k, v in scheduler.stats.items()]
        ys = [v[stat] for k, v in scheduler.stats.items()]

        k = len(xs) * 1 // 100
        indicies = sorted(random.sample(range(len(xs)), k))
        xs = [xs[i] for i in indicies]
        ys = [ys[i] for i in indicies]

        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            name=scheduler.backfill,
            mode='lines+markers',
            marker_color=random.choice(pc.DEFAULT_PLOTLY_COLORS)
        ))

    # Set options common to all traces with fig.update_traces
    # fig.update_traces(mode='markers', marker_line_width=2, marker_size=10)
    fig.update_layout(title=stat,
                      xaxis_title='Time (secs)',
                      yaxis_title=stat,
                      yaxis_zeroline=False,
                      xaxis_zeroline=False,
                      xaxis_tickangle=-45)

    fig.show()
    if not os.path.exists('data/output/plots'):
        os.makedirs('data/output/plots')
    fig.write_image(f'data/output/plots/{stat}.jpeg')


def plot_job_wait(schedulers):
    if not schedulers:
        return

    fig = go.Figure()

    k = len(schedulers[0].jobs) * 10 // 100
    job_ids = sorted(random.sample(schedulers[0].jobs.keys(), k))

    for scheduler in schedulers:
        xs = []
        ys = []
        for job_id in job_ids:
            xs.append(job_id)
            ys.append(scheduler.jobs[job_id].wait)

        fig.add_trace(go.Bar(
            x=xs,
            y=ys,
            name=scheduler.backfill,
            marker_color=random.choice(pc.DEFAULT_PLOTLY_COLORS)
        ))

    fig.update_layout(title='Wait Times per Job',
                      xaxis_title='Job ID',
                      yaxis_title='Wait Time (secs)',
                      barmode='group',
                      xaxis_tickangle=-45)

    fig.show()
    if not os.path.exists('data/output/plots'):
        os.makedirs('data/output/plots')
    fig.write_image(f'data/output/plots/wait.jpeg')