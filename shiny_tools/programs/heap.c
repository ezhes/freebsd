#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int heap_operation() {
    // Allocate an array on the heap
    int* array = malloc(10 * sizeof(int));

    if (array == NULL) {
        // Handle error
    }

    // Initialize the array with some values
    for (int i = 0; i < 10; i++) {
        array[i] = i * i;
    }

    // Print the values of the array
    for (int i = 0; i < 10; i++) {
        printf("%d ", array[i]);
    }
    printf("\n");

    // Free the memory allocated for the array
    free(array);

    return 0;
}

int main() {
    int exe_times = 100; // adjusting how many times for the for loop here
    double total_time = 0; 
    for (int i = 0; i < exe_times; i++) {
        clock_t start, end;
        double execution_time;
        start = clock();
        heap_operation();
        end = clock();
        double duration = ((double)end - start)/CLOCKS_PER_SEC;
        printf("Time taken to execute in seconds: %f\n", duration);
        total_time += duration;
    }
    double ave_time = total_time / exe_times;
    printf("Ave execution duration is %f\n", ave_time);
    return 0;
}