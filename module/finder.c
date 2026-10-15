#define _GNU_SOURCE
#include "finder.h"

static int cmp(const char *word, const char *line_st, const char *file_end)
{
    const char *t = word;
    const char *f = line_st;

    while (*t && f < file_end)
    {
        if (*f == '\n')
            return 1;

        if (*t != *f)
            return (unsigned char)*t - (unsigned char)*f;
        t++;
        f++;
    }

    if (f == file_end || *f == '\n')
    {
        if (*t == '\0')
            return 0;
        return 1;
    }

    return -1;
}

static int bin_search(const char *data, size_t size, const char *target)
{
    const char *left = data;
    const char *right = data + size;
    const char *orig_right = right;

    while (left < right)
    {
        const char *mid = left + (right - left) / 2;
        const char *line_start = mid;

        if (line_start > data)
        {
            while (line_start > data && *(line_start - 1) != '\n')
                line_start--;
        }

        int cmp_res = cmp(target, line_start, orig_right);

        if (cmp_res == 0)
            return 1;
        else if (cmp_res < 0)
            right = line_start;
        else
        {
            const char *next_newline = memchr(line_start, '\n', right - line_start);
            if (next_newline)
                left = next_newline + 1;
            else
                break;
        }

        if (right <= left)
            break;
    }

    return 0;
}

int search_in_dict(const char *filename, const char *word)
{
    int fd = open(filename, O_RDONLY);
    if (fd == -1)
        return -1;

    struct stat sb;
    if (fstat(fd, &sb) == -1)
    {
        int old_errno = errno;
        close(fd);
        errno = old_errno;
        return -1;
    }

    if (!S_ISREG(sb.st_mode))
    {
        close(fd);
        errno = EISDIR;
        return -1;
    }

    if (sb.st_size == 0)
    {
        close(fd);
        return 0;
    }

    void *data = mmap(NULL, sb.st_size, PROT_READ, MAP_PRIVATE, fd, 0);

    close(fd);

    if (data == MAP_FAILED)
        return -1;

    int res = bin_search((const char *)data, sb.st_size, word);

    munmap(data, sb.st_size);

    return res;
}
