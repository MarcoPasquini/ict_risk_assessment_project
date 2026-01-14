#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void init(){
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
    setvbuf(stderr, 0, 2, 0);
}

int main(){
    init();
    return 0;
}

void marker(){
    int exploit_successful_code = 11;
    exit(exploit_successful_code);
}