#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <time.h>

typedef struct {
    int score;
    int questions_answered;
    int total_questions;
    double time_remaining;
    double last_update_time;
    int bomb_exploded;
    int is_paused;
} GameState;

// Constants
#define MAX_GAME_TIME 20.0
#define CORRECT_ANSWER_POINTS 10
#define TIME_FOR_CORRECT_ANSWER 5.0
#define TIME_PENALTY_FOR_WRONG 3.0

// Global game state
static GameState *game = NULL;

// Function declarations
static void free_game_internal(void);
static GameState* init_game_internal(int total_questions);
static void answer_question_internal(int is_correct);
static int update_timer_internal(double current_time);
static double get_fuse_percentage_internal(void);
static void set_paused_internal(int pause_state);
static int is_paused_internal(void);

static GameState* init_game_internal(int total_questions) {
    // Free existing game state if it exists
    if (game != NULL) {
        free_game_internal();
    }

    game = (GameState*)malloc(sizeof(GameState));
    if (!game) return NULL;

    game->score = 0;
    game->questions_answered = 0;
    game->total_questions = total_questions;
    game->time_remaining = MAX_GAME_TIME;
    game->last_update_time = 0.0;
    game->bomb_exploded = 0;
    game->is_paused = 0;

    return game;
}

static void answer_question_internal(int is_correct) {
    if (!game) return;

    game->questions_answered++;

    if (is_correct) {
        game->score += CORRECT_ANSWER_POINTS;
        game->time_remaining += TIME_FOR_CORRECT_ANSWER;
        if (game->time_remaining > MAX_GAME_TIME)
            game->time_remaining = MAX_GAME_TIME;
    } else {
        game->time_remaining -= TIME_PENALTY_FOR_WRONG;
    }
}

static int update_timer_internal(double current_time) {
    if (!game) return 0;

    // Only update if not paused
    if (!game->is_paused) {
        if (game->last_update_time > 0) {
            double delta_time = current_time - game->last_update_time;
            game->time_remaining -= delta_time;
        }
        game->last_update_time = current_time;
    }

    if (game->time_remaining <= 0) {
        game->bomb_exploded = 1;
        return 1;
    }
    return 0;
}

static double get_fuse_percentage_internal(void) {
    if (!game) return 0.0;
    double percentage = (game->time_remaining / MAX_GAME_TIME) * 100.0;
    return (percentage < 0) ? 0 : percentage;
}

static void set_paused_internal(int pause_state) {
    if (!game) return;
    game->is_paused = pause_state;
}

static int is_paused_internal(void) {
    if (!game) return 0;
    return game->is_paused;
}

static void free_game_internal(void) {
    if (game) {
        free(game);
        game = NULL;
    }
}

// Python interface functions
static PyObject* py_init_game(PyObject* self, PyObject* args) {
    int total_questions;
    if (!PyArg_ParseTuple(args, "i", &total_questions)) {
        PyErr_SetString(PyExc_TypeError, "Expected an integer argument");
        return NULL;
    }

    if (!init_game_internal(total_questions)) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to initialize game");
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyObject* py_answer_question(PyObject* self, PyObject* args) {
    int is_correct;
    if (!PyArg_ParseTuple(args, "i", &is_correct)) {
        PyErr_SetString(PyExc_TypeError, "Expected an integer argument");
        return NULL;
    }

    answer_question_internal(is_correct);
    Py_RETURN_NONE;
}

static PyObject* py_update_timer(PyObject* self, PyObject* args) {
    double current_time;
    if (!PyArg_ParseTuple(args, "d", &current_time)) {
        PyErr_SetString(PyExc_TypeError, "Expected a float argument");
        return NULL;
    }

    int exploded = update_timer_internal(current_time);
    return PyLong_FromLong(exploded);
}

static PyObject* py_get_fuse_percentage(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    double percentage = get_fuse_percentage_internal();
    return PyFloat_FromDouble(percentage);
}

static PyObject* py_set_paused(PyObject* self, PyObject* args) {
    int pause_state;
    if (!PyArg_ParseTuple(args, "i", &pause_state)) {
        PyErr_SetString(PyExc_TypeError, "Expected an integer argument");
        return NULL;
    }

    set_paused_internal(pause_state);
    Py_RETURN_NONE;
}

static PyObject* py_is_paused(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    int paused = is_paused_internal();
    return PyBool_FromLong(paused);
}

static PyObject* py_free_game(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    free_game_internal();
    Py_RETURN_NONE;
}

// Method definitions
static PyMethodDef BombMethods[] = {
    {"init_game", py_init_game, METH_VARARGS, "Initialize the game with total questions count"},
    {"answer_question", py_answer_question, METH_VARARGS, "Answer a question (1=correct, 0=wrong)"},
    {"update_timer", py_update_timer, METH_VARARGS, "Update the bomb timer (current_time in seconds)"},
    {"get_fuse_percentage", py_get_fuse_percentage, METH_VARARGS, "Get remaining fuse percentage"},
    {"set_paused", py_set_paused, METH_VARARGS, "Set pause state (1=pause, 0=unpause)"},
    {"is_paused", py_is_paused, METH_VARARGS, "Check if game is paused"},
    {"free_game", py_free_game, METH_VARARGS, "Free game memory"},
    {NULL, NULL, 0, NULL}  // Sentinel
};

static struct PyModuleDef bombmodule = {
    PyModuleDef_HEAD_INIT,
    "bomb_game",
    "A bomb defusal game module",
    -1,
    BombMethods
};

PyMODINIT_FUNC PyInit_bomb_game(void) {
    return PyModule_Create(&bombmodule);
}