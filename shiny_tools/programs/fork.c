#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>

/*
* For testing fork
*/

int main() {
    double total_time = 0; 
    clock_t start = clock();
    // Create a new process
    pid_t pid = fork();

    if (pid == 0) {
        // This is the child process
        printf("Child process: PID %d\n", getpid());

        // Execute a new program
        execl("/bin/ls", "ls", "-l", NULL);
    } else if (pid > 0) {
        // This is the parent process
        printf("Parent process: PID %d\n", getpid());

        // Wait for the child process to finish
        int status;
        wait(&status);

        printf("Child process finished with status %d\n", status);
    } else {
        // There was an error creating the process
        printf("Failed to create new process\n");
    }

    clock_t end = clock();
    double duration = ((double)end - start)/CLOCKS_PER_SEC;
    printf("Execution duration is %f\n", duration);

    return 0;
}