Advanced Patterns
=================

In addition to common functionality that is implemented in the library
itself, there are countless of patterns that can be implemented by extending
click.  This page should give some inspiration of what can be
accomplished.

Command Aliases
---------------

Many tools support aliases for commands.  For instance you can configure
``git`` to accept ``git ci`` as alias for ``git commit``.  Other tools
also support auto discovery for aliases by automatically shortening them.

Click does not support this out of the box but it's very easy to customize
the :class:`Group` or any other :class:`MultiCommand` to provide this
functionality.

As explained in :ref:`custom-multi-commands` a multi command can provide
two methods: :meth:`~MultiCommand.list_commands` and
:meth:`~MultiCommand.get_command`.  In this particular case you only need
to override the latter as you generally don't want to enumerate the
aliases on the help page to avoid confusion.

This following example implements a subclass of :class:`Group` that
accepts a prefix for a command.  So if there is a command called
``push`` it would accept ``pus`` as alias if it's unique::

    class AliasedGroup(click.Group):

        def get_command(self, ctx, cmd_name):
            rv = click.Group.get_command(self, ctx, cmd_name)
            if rv is not None:
                return rv
            matches = [x for x in self.list_commands()
                       if x.startswith(cmd_name)]
            if not matches:
                return None
            elif len(matches) == 1:
                return click.Group.get_command(self, ctx, matches[0])
            ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))

And it can be used like this then::

    @click.command(cls=AliasedGroup)
    def cli():
        pass

    @cli.command()
    def push():
        pass

    @cli.command()
    def pop():
        pass
