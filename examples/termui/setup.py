from setuptools import setup

setup(
    name='click-example-termui',
    version='1.0',
    py_modules=['termui'],
    include_package_data=True,
    install_requires=[
        'Click',
        # Colorama is only required for windows.
        'colorama',
    ],
    entry_points='''
        [console_scripts]
        termui=termui:cli
    ''',
)
