from setuptools import setup

setup(
    name='epp-lang',
    version='1.0.0',
    py_modules=['epp_interpreter', 'epp_ui'],
    entry_points={
        'console_scripts': [
            'Epp=epp_interpreter:main',
        ],
    },
)
