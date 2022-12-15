
#include <stdio.h>
#include <stdlib.h> // For exit()
#include <time.h>

/*
* For testing file system access overhead. 
*/
  
int file_operation()
{
    FILE *fptr;
  
    char filename[100], c;

    // Open file
    fptr = fopen("filename.txt", "r");
    if (fptr == NULL)
    {
        printf("Cannot open file \n");
        exit(0);
    }
  
    // Read contents from file
    c = fgetc(fptr);
    while (c != EOF)
    {
        printf ("%c", c);
        c = fgetc(fptr);
    }
  
    fclose(fptr);

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