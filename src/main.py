import click
from ttictoc import TicToc
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
@click.option('--backfill', '-b', type=click.Choice(['none', 'easy']))
def run(type, path, backfill):
    """Run the scheduler."""
    sched = schedulus.Schedulus(400)
    sched.read_jobs(path)
    sched.run(type, backfill)