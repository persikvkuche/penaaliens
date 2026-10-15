#ifndef FINDER_H
#define FINDER_H

#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#define IN_DICT 1
#define NOT_INT_DICT 0

int search_in_dict(const char *filename, const char *word);
#endif
