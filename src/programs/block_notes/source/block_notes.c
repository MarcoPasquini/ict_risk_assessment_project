#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MAX_NOTES 10

struct note{
    char title[32];
    char content[128];
};

void init();
void menu();
int take_user_choise();
void write_note(struct note* note);
void read_note(struct note* note);
int take_user_choise();
void marker();

int main(){
    init();
    struct note notes[10];
    int n_notes = 0;
    for(int i=0; i<MAX_NOTES; i++){
        notes[i].title[0] = '\0';
        notes[i].content[0] = '\0';
    }
    while(1){
        menu();
        int choise = take_user_choise();
        int idx = 0;
        switch(choise){
            case 1:
                printf("Index: ");
                idx = take_user_choise();
                if(idx>=0 && idx<MAX_NOTES)
                    write_note(&notes[idx]);
                break;
            case 2:
                printf("Index: ");
                idx = take_user_choise();
                if(idx>=0 && idx<MAX_NOTES)
                    read_note(&notes[idx]);
                break;
            default:
                printf("Bye.");
                exit(0);
        }
    }
    return 0;
}

void init(){
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
    setvbuf(stderr, 0, 2, 0);
}

void menu(){
    printf("1) Write note.\n");
    printf("2) Read note.\n");
    printf("3) Exit.\n");
    printf("> ");
}

void write_note(struct note* note){
    printf("Title: ");
    ssize_t bytes_read = read(0, note->title, sizeof(note->title)-1);
    note->title[bytes_read] = '\0';
    printf("Content: ");
    bytes_read = read(0, note->content, sizeof(note->content)-1);
    note->content[bytes_read] = '\0';
    printf("Note has been written.\n");
}

void read_note(struct note* note){
    if(!strlen(note->content)){
        printf("Invalid note.\n");
        return;
    }
    printf("Title:\n");
    printf(note->title);
    printf("\nContent:\n");
    printf(note->content);
    printf("\n");
}

int take_user_choise(){
    int choise = 0;
    scanf("%d%*c", &choise);
    return choise;
}

void marker(){
    int exploit_successful_code = 11;
    exit(exploit_successful_code);
}

//Missing sanitization, format string vulnerability