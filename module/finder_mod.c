#define PY_SSIZE_T_CLEAN
#include "finder.h"
#include <Python.h>

static PyObject *py_contains_word(PyObject *self, PyObject *args)
{
    const char *filename;
    const char *word;

    if (!PyArg_ParseTuple(args, "ss", &filename, &word))
    {
        return NULL;
    }

    int result = search_in_dict(filename, word);

    if (result == -1)
    {
        PyErr_SetFromErrnoWithFilename(PyExc_IOError, filename);
        return NULL;
    }

    if (result)
    {
        Py_RETURN_TRUE;
    }
    else
    {
        Py_RETURN_FALSE;
    }
}

static PyMethodDef FileSearchMethods[] = {
    {"contains_word", py_contains_word, METH_VARARGS, "Search word in a sorted file path."}, {NULL, NULL, 0, NULL}};

static struct PyModuleDef file_search_module = {PyModuleDef_HEAD_INIT, "file_search", NULL, -1, FileSearchMethods};

PyMODINIT_FUNC PyInit_file_search(void)
{
    return PyModule_Create(&file_search_module);
}
