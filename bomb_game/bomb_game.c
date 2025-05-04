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

// Constante
#define MAX_GAME_TIME 60.0
#define CORRECT_ANSWER_POINTS 10
#define TIME_FOR_CORRECT_ANSWER 5.0
#define TIME_PENALTY_FOR_WRONG 10.0

// Stare de joc globală
static GameState *game = NULL;

// Funcții interne
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

// Funcții expuse către Python

static PyObject* py_init_game(PyObject* self, PyObject* args) {
    int total_questions;
    if (!PyArg_ParseTuple(args, "i", &total_questions))
        return NULL;

    init_game_internal(total_questions);
    Py_RETURN_NONE;
}

static PyObject* py_answer_question(PyObject* self, PyObject* args) {
    int is_correct;
    if (!PyArg_ParseTuple(args, "i", &is_correct))
        return NULL;

    answer_question_internal(is_correct);
    Py_RETURN_NONE;
}

static PyObject* py_update_timer(PyObject* self, PyObject* args) {
    double delta_time;
    if (!PyArg_ParseTuple(args, "d", &delta_time))
        return NULL;

    int exploded = update_timer_internal(delta_time);
    return PyLong_FromLong(exploded);
}

static PyObject* py_get_fuse_percentage(PyObject* self, PyObject* args) {
    double percentage = get_fuse_percentage_internal();
    return PyFloat_FromDouble(percentage);
}

static PyObject* py_free_game(PyObject* self, PyObject* args) {
    free_game_internal();
    Py_RETURN_NONE;
}

// Tabel cu funcții
static PyMethodDef BombMethods[] = {
    {"init_game", py_init_game, METH_VARARGS, "Initialize the game"},
    {"answer_question", py_answer_question, METH_VARARGS, "Answer a question"},
    {"update_timer", py_update_timer, METH_VARARGS, "Update the bomb timer"},
    {"get_fuse_percentage", py_get_fuse_percentage, METH_NOARGS, "Get remaining fuse %"},
    {"free_game", py_free_game, METH_NOARGS, "Free game memory"},
    {NULL, NULL, 0, NULL}
};

// Definirea modulului
static struct PyModuleDef bombmodule = {
    PyModuleDef_HEAD_INIT,
    "bomb_game",      // numele modulului
    NULL,             // docstring (poate fi NULL)
    -1,               // size of per-interpreter state
    BombMethods
};

// Funcția PyInit obligatorie
PyMODINIT_FUNC PyInit_bomb_game(void) {
    return PyModule_Create(&bombmodule);
}
