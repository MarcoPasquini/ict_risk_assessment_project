#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MAX_SONGS 16

char* playlist[MAX_SONGS];
int sizes[MAX_SONGS];
int n_songs = 0;

void init();
void menu();
void add_song();
void view_song();
void edit_song();
void delete_song();
int take_user_choise();
int get_valid_song();

int main(){
    init();
    while(1){
        menu();
        int choise = take_user_choise();
        switch(choise){
            case 1:
                add_song();
                break;
            case 2:
                view_song();
                break;
            case 3:
                edit_song();
                break;
            case 4:
                delete_song();
                break;
            default:
                printf("Bye.");
                exit(0);
        }
    }
}

void init(){
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
    setvbuf(stderr, 0, 2, 0);
}

void menu(){
    printf("1) Add song\n");
    printf("2) View song\n");
    printf("3) Edit song\n");
    printf("4) Delete song\n");
    printf("5) Quit\n");
    printf("> ");
}

void add_song(){
    printf("Index: ");
    int idx = take_user_choise();
    if(idx<0 || idx>=MAX_SONGS){
        printf("Invalid index.\n");
        return;
    }
    printf("Size: ");
    uint size = take_user_choise();
    playlist[idx] = malloc(size);
    sizes[idx] = size;
    printf("Song added.\n");
    return;
}

void view_song(){
    printf("Index: ");
    int idx = get_valid_song();
    if (idx == -1){
        return;
    }
    printf("Your song:\n");
    write(1, playlist[idx], sizes[idx]);
    return;
}

void edit_song(){
    printf("Index: ");
    int idx = get_valid_song();
    if (idx == -1){
        return;
    }
    printf("Content: ");
    read(0, playlist[idx], sizes[idx]);
    printf("Song written.\n");
    return;
}

void delete_song(){
    printf("Index: ");
    int idx = get_valid_song();
    if (idx == -1){
        return;
    }
    free(playlist[idx]);
    printf("Song deleted.\n");
    return;
}

int take_user_choise(){
    int choise = 0;
    scanf("%d%*c", &choise);
    return choise;
}

int get_valid_song(){
    int idx = take_user_choise();
    if(idx<0 || idx>=MAX_SONGS || playlist[idx] == 0){
        printf("Invalid song.\n");
        return -1;
    }
    return idx;
}

void marker(){
    int exploit_successful_code = 11;
    exit(exploit_successful_code);
}

//UAF vulnerability
//#libc can have or not safe linking