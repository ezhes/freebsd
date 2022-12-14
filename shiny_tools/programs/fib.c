#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int fib(int n) {
    if (n == 0)
        return 0;
    if (n == 1)
        return 1;
    return fib(n-1) + fib(n - 2);
}

int main(int argc, char **argv) {
    int n;
    if (argc != 2) {
        printf("Wrong number of arguments.\n");
        return 0;
    }
    n = atoi(argv[1]);

    int exe_times = 50; // adjusting how many times for the for loop here
    double total_time = 0; 
    for (int i = 0; i < exe_times; i++) {
        clock_t start, end;
        double execution_time;
        start = clock();
        printf("Fib %d = %d\n", n, fib(n));
        end = clock();
        double duration = ((double)end - start)/CLOCKS_PER_SEC;
        printf("Time taken to execute in seconds: %f\n", duration);
        total_time += duration;
    }
    double ave_time = total_time / exe_times;
    printf("Ave execution duration is %f\n", ave_time);
    return 0;
}