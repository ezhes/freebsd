
#include <stdio.h>
#include <stdlib.h> // For exit()
#include <time.h>

/*
* For testing file system access overhead. 
*/
  
int file_operation() {
    // Open the file for reading
    FILE *file = fopen("filename.txt", "r");

    // Make sure the file was opened successfully
    if (file == NULL) {
        printf("Failed to open file\n");
        return 1;
    }

    // Read the contents of the file one character at a time
    char c;
    while ((c = fgetc(file)) != EOF) {
        printf("%c", c);
    }
    // Write some text to the file
    fprintf(file, "Hello, world!\n");
    fprintf(file, "This is a sample program.\n");

    // Close the file
    fclose(file);

    return 0;
}

int main() {
    int exe_times = 100; // adjusting how many times for the for loop here
    double total_time = 0; 
    for (int i = 0; i < exe_times; i++) {
        clock_t start, end;
        double execution_time;
        start = clock();
        file_operation();
        end = clock();
        double duration = ((double)end - start)/CLOCKS_PER_SEC;
        printf("Time taken to execute in seconds: %f\n", duration);
        total_time += duration;
    }
    double ave_time = total_time / exe_times;
    printf("Ave execution duration is %f\n", ave_time);
    return 0;
}