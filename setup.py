from setuptools import setup, Extension

setup(
    name="bomb_game",
    version="1.0",
    description="Native C extension for Beat the Bomb game",
    ext_modules=[
        Extension(
            "bomb_game",
            sources=["bomb_game.c"],
            extra_compile_args=["-O2"],  # Optional optimization
        )
    ],
)