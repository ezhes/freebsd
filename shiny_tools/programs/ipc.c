#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

/*
* For testing inter-process communication. 
*/
int ipc() {
    // Create a pipe
    int fd[2];
    int result = pipe(fd);

    if (result < 0) {
        // Handle error
    }

    // Write to the pipe
    const char* data = "Hello, world!";
    ssize_t count = write(fd[1], data, strlen(data));

    if (count < 0) {
        // Handle error
    }

    // Read from the pipe
    char buffer[1024];
    count = read(fd[0], buffer, sizeof(buffer));

    if (count < 0) {
        // Handle error
    }

    // Print the data that was read from the pipe
    printf("Received: %.*s\n", (int)count, buffer);

    return 0;
}

int main() {
    int exe_times = 100; // adjusting how many times for the for loop here
    double total_time = 0; 
    for (int i = 0; i < exe_times; i++) {
        clock_t start, end;
        double execution_time;
        start = clock();
        ipc();
        end = clock();
        double duration = ((double)end - start)/CLOCKS_PER_SEC;
        printf("Time taken to execute in seconds: %f\n", duration);
        total_time += duration;
    }
    double ave_time = total_time / exe_times;
    printf("Ave execution duration is %f\n", ave_time);
    return 0;
}