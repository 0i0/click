Documenting Scripts
===================

Click makes it very easy to document your command line tools.  First of
all it automatically generates help pages for you.  While these are
currently not customizable in layout, all the texts can be changed.

Help Texts
----------

Commands and options accept help arguments.  In case of commands the doc
string of the function is automatically used if provided.

Simple example::

    @click.command()
    @click.option('--count', default=1, help='number of greetings')
    @click.argument('name')
    def hello(count, name):
        """This script prints hello NAME COUNT times."""
        for x in range(count):
            print('Hello %s!' % name)

And what it looks like::

    $ python hello.py --help
    Usage: hello.py [OPTIONS] NAME

    This script prints hello NAME COUNT times.

    Options:
      --count=COUNT  number of greetings
      --help         Show this message and exit.

Arguments cannot be documented this way.  This is to follow general
convention of Unix tools to use arguments only for the most necessary
things and to document them in the introduction text by referring to them
by name.

Meta Vars
---------

Options and parameters accept a ``metavar`` argument that can change the
meta variable in the help page.  The default version is the parameter name
in uppercase with underscores and sometimes annotated differently if
optional.  This can be customized at all levels::

    @click.command(options_metavar='<options>')
    @click.option('--count', default=1, help='number of greetings',
                  metavar='<int>')
    @click.argument('name', metavar='<name>')
    def hello(count, name):
        """This script prints hello <name> <int> times."""
        for x in range(count):
            print('Hello %s!' % name)

Example::

    Usage: hello.py <options> <name>

    This script prints hello <name> <int> times.

    Options:
      --count=<int>  number of greetings
      --help         Show this message and exit.
                

Command Short Help
------------------

For commands a short help is generated.  By default it's the first part
(until the first dot) of the help message of the command unless it's too
long.  This can also be overridden::

    @click.group()
    def cli():
        """A simple command line tool."""

    @cli.command('init', short_help='init the repo')
    def init():
        """Initializes the repository."""

    @cli.command('delete', short_help='delete the repo')
    def delete():
        """Deletes the repository."""

And what it looks like::

    Usage: repo.py [OPTIONS] COMMAND [ARGS]...

    A simple command line tool.

    Commands:
      delete  delete the repo
      init    init the repo

    Options:
      --help  Show this message and exit.
