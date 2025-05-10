from setuptools import setup, Extension

module = Extension(
    'bomb_game',
    sources=['bomb_game.c'],
    define_macros=[('PY_SSIZE_T_CLEAN', None)],
)

setup(
    name='bomb_game',
    version='1.0',
    description='Bomb game module',
    ext_modules=[module]
)