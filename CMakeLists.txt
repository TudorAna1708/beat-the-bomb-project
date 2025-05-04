cmake_minimum_required(VERSION 3.12)
project(bomb_game LANGUAGES C)

#  Asta este noua linie:
include_directories("C:/Users/anatu/AppData/Local/Programs/Python/Python312/include")

link_directories("C:/Users/anatu/AppData/Local/Programs/Python/Python312/libs")

add_library(bomb_game MODULE bomb_game/bomb_game.c)

set_target_properties(bomb_game PROPERTIES
    PREFIX ""
    SUFFIX ".pyd"
)

# Optional - doar dacă ai folosit install()
install(TARGETS bomb_game DESTINATION .)
