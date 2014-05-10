import os
import sys
import click
import shutil
import tempfile
import contextlib

from ._compat import iteritems, PY2


if PY2:
    from cStringIO import StringIO
else:
    import io


class EchoingStdin(object):

    def __init__(self, input, output):
        self._input = input
        self._output = output

    def __getattr__(self, x):
        return getattr(self._input, x)

    def _echo(self, rv):
        self._output.write(rv)
        return rv

    def read(self, n=-1):
        return self._echo(self._input.read(n))

    def readline(self, n=-1):
        return self._echo(self._input.readline(n))

    def readlines(self):
        return [self._echo(x) for x in self._input.readlines()]

    def __iter__(self):
        return iter(self._echo(x) for x in self._input)


class Result(object):
    """Holds the captured result of an invoked CLI script."""

    def __init__(self, output, exit_code, exception):
        #: The output as unicode string.
        self.output = output
        #: The exit code as integer.
        self.exit_code = exit_code
        #: The exception that happend if one did.
        self.exception = exception

    def __repr__(self):
        return '<Result %s>' % (
            self.exception and repr(self.exception) or 'okay',
        )


class CliRunner(object):
    """The CLI runner provides functionality to invoke a Click command line
    script for unittesting purposes in a isolated environment.  This only
    works in single-threaded systems without any concurrency as it changes
    global interpreter state.
    """

    def __init__(self, charset=None, env=None):
        if charset is None:
            charset = 'utf-8'
        self.charset = charset
        self.env = env or {}

    def get_default_prog_name(self, cli):
        """Given a command object it will return the default program name
        for it.  The default is the `name` attribute or ``"root"`` if not
        set.
        """
        return cli.name or 'root'

    def make_env(self, overrides=None):
        """Returns the environment overrides for invoking a script."""
        rv = dict(self.env)
        if overrides:
            rv.update(overrides)
        return rv

    @contextlib.contextmanager
    def isolation(self, input=None, env=None):
        """A context manager that set up the isolation for invoking of a
        command line tool.  This sets up stdin with the given input data,
        and `os.environ` with the overrides from the given dictionary.
        This also rebinds some internals in Click to be mocked (like the
        prompt functionality).

        This is automatically done in the :meth:`invoke` method.

        :param input: the input stream to put into sys.stdin.
        :param env: the environment overrides as dictionary.
        """
        if hasattr(input, 'read'):
            input = input.read()
        if input is not None and not isinstance(input, bytes):
            input = input.encode(self.charset)

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        env = self.make_env(env)

        if PY2:
            input = StringIO(input or '')
            output = StringIO()
            sys.stdin = EchoingStdin(input, output)
            sys.stdin.encoding = self.charset
            sys.stdout = sys.stderr = output
        else:
            real_input = io.BytesIO(input)
            output = io.BytesIO()
            input = io.TextIOWrapper(real_input, encoding=self.charset)
            sys.stdin = EchoingStdin(real_input, output)
            sys.stdout = sys.stderr = io.TextIOWrapper(output,
                                                       encoding=self.charset)

        def visible_input(prompt=None):
            sys.stdout.write(prompt or '')
            val = input.readline().rstrip('\r\n')
            sys.stdout.write(val + '\n')
            sys.stdout.flush()
            return val

        def hidden_input(prompt=None):
            sys.stdout.write((prompt or '') + '\n')
            sys.stdout.flush()
            return input.readline().rstrip('\r\n')

        old_visible_prompt_func = click.termui.visible_prompt_func
        old_hidden_prompt_func = click.termui.hidden_prompt_func
        click.termui.visible_prompt_func = visible_input
        click.termui.hidden_prompt_func = hidden_input

        old_env = {}
        try:
            for key, value in iteritems(env):
                old_env[key] = os.environ.get(value)
                if value is None:
                    try:
                        del os.environ[key]
                    except Exception:
                        pass
                else:
                    os.environ[key] = value
            yield output
        finally:
            for key, value in iteritems(old_env):
                if value is None:
                    try:
                        del os.environ[key]
                    except Exception:
                        pass
                else:
                    os.environ[key] = value
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            click.termui.visible_prompt_func = old_visible_prompt_func
            click.termui.hidden_prompt_func = old_hidden_prompt_func

    def invoke(self, cli, args, input=None, env=None, **extra):
        """Invokes a command in an isolated environment.  The arguments are
        forwarded directly to the command line script, the `extra` keyword
        arguments are passed to the :meth:`~click.Command.main` function of
        the command.

        This returns a :class:`Result` object.

        :param cli: the command to invoke
        :param args: the arguments to invoke
        :param input: the input data for `sys.stdin`.
        :param env: the environment overrides.
        :param extra: the keyword arguments to pass to :meth:`main`.
        """
        with self.isolation(input=input, env=env) as out:
            exception = None
            exit_code = 0

            try:
                cli.main(args=args, prog_name=self.get_default_prog_name(cli),
                         **extra)
            except SystemExit as e:
                if e.code != 0:
                    exception = e
                exit_code = e.code
            except Exception as e:
                exception = e
                exit_code = -1
            output = out.getvalue().decode(self.charset).replace('\r\n', '\n')

        return Result(output=output,
                      exit_code=exit_code,
                      exception=exception)

    @contextlib.contextmanager
    def isolated_filesystem(self):
        """A context manager that creates a temporary folder and changes
        the current working directory to it for isolated filesystem tests.
        """
        cwd = os.getcwd()
        t = tempfile.mkdtemp()
        os.chdir(t)
        try:
            yield
        finally:
            os.chdir(cwd)
            try:
                shutil.rmtree(t)
            except (OSError, IOError):
                pass
