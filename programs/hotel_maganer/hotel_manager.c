#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define CODE_LEN 10
#define GUEST_LEN 32
#define DATE_LEN 11
#define PAGE_SIZE 20

struct booking{
    char code[CODE_LEN];
    char guest_name[GUEST_LEN];
    char date[DATE_LEN];
};

struct booking* booking_db;
int n_bookings = 0;

void init(){
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
    setvbuf(stderr, 0, 2, 0);
}

void menu(){
    printf("1) Add bookings\n");
    printf("2) List bookings\n");
    printf("3) Quit\n");
    printf("> ");
}

void add_to_db(struct booking* booking_list, int size){
    booking_db = realloc(booking_db, (size+n_bookings)*sizeof(struct booking));
    for(int i=0;i<size;i++){
        memcpy((booking_db + (i+n_bookings)), &booking_list[i], sizeof(struct booking));
    }
    printf("Bookings sent to db.\n");
    n_bookings+=size;
    return;
}

void add_bookings(){
    int take_next_booking = 1;
    int i = 0;
    int j = 0;
    char user_next_choise = 0;
    struct booking booking_list[PAGE_SIZE];
    do{
        printf("Booking n.%d\n", i+1);
        printf("Booking code: ");
        read(0, booking_list[i].code, CODE_LEN);
        printf("Guest name: ");
        read(0, booking_list[i].guest_name, GUEST_LEN);
        printf("Date: ");
        read(0, booking_list[i].date, DATE_LEN);
        if (i < 19) {
            booking_list[i].date[DATE_LEN-1] = '\0';
            printf("> Do you want to add another booking? (y/n): ");
            j = scanf(" %c%*c",&user_next_choise);
            if ((j != 1) || ((user_next_choise != 'y' && (user_next_choise != 'Y')))){
                i++;
                break;
            }
        }
        j = i + 1;
        take_next_booking = i < PAGE_SIZE;
        i = j;
    } while (take_next_booking);
    add_to_db(booking_list, i);
}

void list_bookings(){
    if(!n_bookings){
        puts("No bookings found.");
        return;
    }
    int page = 0;
    char user_next_choise;
    while(1){
        int i=0;
        int j=0;
        struct booking booking_list[PAGE_SIZE];
        for(int i=0;i<PAGE_SIZE;i++){
            memcpy(&booking_list[i], (booking_db + i+(page*PAGE_SIZE)), sizeof(struct booking));
        }
        do {
            if (booking_list[j].code[0] == '\0') {
                puts("> No more bookings to display.");
                return;
            }
            printf("> Booking number: %s\n", booking_list[j].code);
            printf("  Guest name: %s\n", booking_list[j].guest_name);
            printf("  Date: %s\n", booking_list[j].date);
            i = j;
            j = j + 1;
        } while (i < PAGE_SIZE);
        printf("\n> Do you want to see the next page? (y/n): ");
        i = scanf(" %c%*c",&user_next_choise);
        if (i != 1 || ((user_next_choise != 'y') && (user_next_choise != 'Y'))) {
            return;
        }
        page++;
    }
}


int take_user_choise(){
    int choise = 0;
    scanf("%d%*c", &choise);
    return choise;
}

int main(){
    init();
    while(1){
        menu();
        int choise = take_user_choise();
        switch(choise){
            case 1:
                add_bookings();
                break;
            case 2:
                list_bookings();
                break;
            default:
                puts("Bye.");
                exit(0);
        }
    }
}

void marker(){
    int exploit_successful_code = 11;
    exit(exploit_successful_code);
}

//Buffer overflow, you can add 21 bookings in a list