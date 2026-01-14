#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MAX_USERS 10
#define FIELD_LEN 64

struct user{
    char username[FIELD_LEN];
    char password[FIELD_LEN];
};

struct user registered_users[MAX_USERS];
int n_registered_users = 1;
struct user current_user;
int is_logged = 0;

char* document_stub = "PUBLIC DOCUMENTS.";

void init();
void menu();
int register_user();
int login_user();
int login_user();
int try_login(char* username, char* password);
int add_new_user(char* username, char* password);
void read_documents();
void read_username();
void read_password();
int take_user_choise();
int is_field_empty(char* username);
int is_user_registered(char* username);
void marker();

int main(){
    init();

    while(1){
        menu();
        int choise = take_user_choise();
        switch(choise){
            case 1:
                if(register_user())
                    printf("User registered.\n");
                break;
            case 2:
                if(login_user())
                    printf("User logged in.\n");
                else
                    printf("Invalid credentials.\n");
                break;
            case 3:
                if(is_logged)
                    read_documents();
                else
                    printf("You need to be logged in.\n");
                break;
            case 4:
                if(is_logged && !strcmp("admin", current_user.username))
                    marker();
                else
                    printf("You can't do that.\n");
                break;
            default:
                printf("Bye.\n");
                exit(0);
        }
    }

    return 0;
}

//ERRORE LOGICO NON VIENE RISOLTO DA PROTEZIONI

void init(){
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
    setvbuf(stderr, 0, 2, 0);
    strcpy(registered_users[0].username, "admin\0");
    strcpy(registered_users[0].password, "*****\0");
}

void menu(){
    printf("1) Register\n");
    printf("2) Login\n");
    printf("3) Read documents\n");
    printf("4) Marker\n");
    printf("5) Exit\n");
    printf("> ");
}

int register_user(){
    if(n_registered_users >= MAX_USERS){
        printf("Too many accounts.\n");
        return 0;
    }
    printf("Username: ");
    read_username();
    if(is_field_empty(current_user.username) || is_user_registered(current_user.username)){
        printf("Invalid username.\n");
        return 0;
    }
    printf("Password: ");
    read_password();
    if(is_field_empty(current_user.password)){
        printf("Password can't be empty.\n");
        return 0;
    }
    return add_new_user(current_user.username, current_user.password);
}

int login_user(){
    printf("Username: ");
    read_username();
    if(is_field_empty(current_user.username) || !is_user_registered(current_user.username)){
        printf("Invalid username.\n");
        return 0;
    }
    printf("Password: ");
    read_password();
    if(is_field_empty(current_user.password)){
        printf("Password can't be empty.\n");
        return 0;
    }
    if(try_login(current_user.username, current_user.password)){
        is_logged = 1;
        return 1;
    }
    return 0;
}

int try_login(char* username, char* password){
    for(int i=0; i<n_registered_users; i++){
        if(!strcmp(registered_users[i].username, username)){
            if(!strcmp(registered_users[i].password, password))
                return 1;
            return 0;
        }
    }
    return 0;
}

int add_new_user(char* username, char* password){
    strcpy(registered_users[n_registered_users].username, username);
    strcpy(registered_users[n_registered_users].password, password);
    n_registered_users++;
    return 1;
}

void read_documents(){
    printf("%s\n", document_stub);
}

void read_username(){
    ssize_t bytes_read = read(0, current_user.username, sizeof(current_user.username) - 1);
    if(current_user.username[bytes_read - 1] == '\n'){
        current_user.username[bytes_read - 1] = '\0';
    }else{
        current_user.username[bytes_read] = '\0';
    }
}

void read_password(){
    ssize_t bytes_read = read(0, current_user.password, sizeof(current_user.password) - 1);
    if(current_user.password[bytes_read - 1] == '\n'){
        current_user.password[bytes_read - 1] = '\0';
    }else{
        current_user.password[bytes_read] = '\0';
    }
}

int take_user_choise(){
    int choise = 0;
    scanf("%d*c", &choise);
    return choise;
}

int is_field_empty(char* username){
    return username[0] == '\0';
}

int is_user_registered(char* username){
    for(int i=0; i<n_registered_users; i++){
        if(!strcmp(username, registered_users[i].username)){
            return 1;
        }
    }
    return 0;
}

void marker(){
    int exploit_successful_code = 11;
    exit(exploit_successful_code);
}