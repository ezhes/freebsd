#include <stdio.h>
#include <time.h>
int main(int argc, char **argv) {
    int n;
    clock_t start = clock();
    scanf("%d", &n);
    printf("Read: %d\n", n);
    clock_t end = clock();
    double elapsed = ((double)end - start)/CLOCKS_PER_SEC;
    printf("Time elapsed: %f\n", elapsed);
    return 0;

}