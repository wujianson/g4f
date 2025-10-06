/* minishell.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>

#define MAX_LINE 1024

void cmd_pwd() {
    char cwd[PATH_MAX];
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        puts(cwd);
    } else {
        perror("pwd");
    }
}

void cmd_cd(char *path) {
    if (chdir(path) != 0) {
        perror("cd");
    }
}

void cmd_ls(char *path) {
    DIR *d = opendir(path);
    if (!d) {
        perror("ls");
        return;
    }
    struct dirent *entry;
    while ((entry = readdir(d)) != NULL) {
        printf("%s\n", entry->d_name);
    }
    closedir(d);
}

int main() {
    char line[MAX_LINE];
    while (1) {
        char cwd[PATH_MAX];
        getcwd(cwd, sizeof(cwd));
        printf("%s$ ", cwd);
        if (!fgets(line, sizeof(line), stdin)) break;
        line[strcspn(line, "\n")] = 0;   // 去掉换行
        if (strlen(line) == 0) continue;

        char *args[4];
        int argc = 0;
        char *token = strtok(line, " ");
        while (token && argc < 3) {
            args[argc++] = token;
            token = strtok(NULL, " ");
        }
        args[argc] = NULL;

        if (strcmp(args[0], "exit") == 0) break;
        else if (strcmp(args[0], "pwd") == 0) cmd_pwd();
        else if (strcmp(args[0], "cd") == 0) {
            if (argc > 1) cmd_cd(args[1]);
            else cmd_cd("~");
        }
        else if (strcmp(args[0], "ls") == 0) {
            if (argc > 1) cmd_ls(args[1]);
            else cmd_ls(".");
        }
        else {
            fprintf(stderr, "%s: command not found\n", args[0]);
        }
    }
    return 0;
}
