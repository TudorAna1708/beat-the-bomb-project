from skbuild import setup
from setuptools import find_packages

setup(
    name="bomb_game",
    version="1.0",
    description="Native C extension for Beat the Bomb game",
    packages=find_packages(),
    cmake_install_dir="bomb_game",  # spune unde să copieze .pyd-ul
)
