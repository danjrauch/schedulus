import click
import simulus
from ttictoc import TicToc


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
    """Main Command."""
    if ctx.invoked_subcommand is None:
        click.echo(click.style('Hello, please invoke a command', fg = 'bright_red'))


def print_message(sim):
    print("Hello world at time", sim.now)
    sim.sched(print_message, sim, offset=10)


@cli.command()
def validate():
    click.secho('Starting Simulation', fg = 'bright_red')

    sim = simulus.simulator()
    sim.sched(print_message, sim, until=10)
    sim.run(100)