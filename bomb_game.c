#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>

typedef struct {
    int score;
    int questions_answered;
    int total_questions;
    double time_remaining;
    int bomb_exploded;
} GameState;

// Constants
#define MAX_GAME_TIME 20.0
#define CORRECT_ANSWER_POINTS 10
#define TIME_FOR_CORRECT_ANSWER 5.0
#define TIME_PENALTY_FOR_WRONG 10.0

// Global game state
static GameState *game = NULL;

// Internal functions
static GameState* init_game_internal(int total_questions) {
    game = (GameState*)malloc(sizeof(GameState));
    if (!game) return NULL;

    game->score = 0;
    game->questions_answered = 0;
    game->total_questions = total_questions;
    game->time_remaining = MAX_GAME_TIME;
    game->bomb_exploded = 0;

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

static int update_timer_internal(double delta_time) {
    if (!game) return 0;

    game->time_remaining -= delta_time;

    if (game->time_remaining <= 0) {
        game->bomb_exploded = 1;
        return 1;
    }
    return 0;
}

static double get_fuse_percentage_internal() {
    if (!game) return 0.0;
    return (game->time_remaining / MAX_GAME_TIME) * 100.0;
}

static void free_game_internal() {
    if (game) {
        free(game);
        game = NULL;
    }
}

// Python-exposed functions
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
    double delta_time;
    if (!PyArg_ParseTuple(args, "d", &delta_time)) {
        PyErr_SetString(PyExc_TypeError, "Expected a float argument");
        return NULL;
    }

    int exploded = update_timer_internal(delta_time);
    return PyLong_FromLong(exploded);
}

static PyObject* py_get_fuse_percentage(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {  // No arguments expected
        return NULL;
    }
    double percentage = get_fuse_percentage_internal();
    return PyFloat_FromDouble(percentage);
}

static PyObject* py_free_game(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {  // No arguments expected
        return NULL;
    }
    free_game_internal();
    Py_RETURN_NONE;
}

// Method definitions
static PyMethodDef BombMethods[] = {
    {"init_game", py_init_game, METH_VARARGS, "Initialize the game with total questions count"},
    {"answer_question", py_answer_question, METH_VARARGS, "Answer a question (1=correct, 0=wrong)"},
    {"update_timer", py_update_timer, METH_VARARGS, "Update the bomb timer (delta_time in seconds)"},
    {"get_fuse_percentage", py_get_fuse_percentage, METH_VARARGS, "Get remaining fuse percentage"},
    {"free_game", py_free_game, METH_VARARGS, "Free game memory"},
    {NULL, NULL, 0, NULL}  // Sentinel
};

// Module definition
static struct PyModuleDef bombmodule = {
    PyModuleDef_HEAD_INIT,
    "bomb_game",     // Module name
    "A bomb defusal game module",  // Module documentation
    -1,              // Size of per-interpreter state
    BombMethods      // Method table
};

// Module initialization function
PyMODINIT_FUNC PyInit_bomb_game(void) {
    PyObject *module;
    module = PyModule_Create(&bombmodule);
    if (module == NULL) {
        return NULL;
    }
    
    // Add version constant
    PyModule_AddStringConstant(module, "__version__", "1.0");
    
    return module;
}