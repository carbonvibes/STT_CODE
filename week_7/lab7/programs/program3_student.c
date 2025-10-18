/*
 * Program 3: Student Grade Management System
 * Description: Manages student grades with statistics calculation,
 * grade assignment, sorting, and reporting features.
 * Lines of Code: ~280
 */

#include <stdio.h>
#include <string.h>

#define MAX_STUDENTS 50
#define MAX_NAME 50
#define MAX_SUBJECTS 5

// Student structure
struct Student {
    int id;
    char name[MAX_NAME];
    int marks[MAX_SUBJECTS];
    float average;
    char grade;
};

// Global variables
struct Student students[MAX_STUDENTS];
int student_count = 0;
int num_subjects = 3;

// Function to calculate average
float calculate_average(int marks[], int count) {
    int sum = 0;
    int i = 0;
    float avg = 0.0;
    
    sum = 0;
    i = 0;
    while (i < count) {
        sum = sum + marks[i];
        i = i + 1;
    }
    
    avg = (float)sum / count;
    return avg;
}

// Function to assign grade based on average
char assign_grade(float average) {
    char grade = 'F';
    
    if (average >= 90.0) {
        grade = 'A';
    } else if (average >= 80.0) {
        grade = 'B';
    } else if (average >= 70.0) {
        grade = 'C';
    } else if (average >= 60.0) {
        grade = 'D';
    } else {
        grade = 'F';
    }
    
    return grade;
}

// Function to add student
void add_student() {
    int i = 0;
    int id = 0;
    char name[MAX_NAME];
    int marks[MAX_SUBJECTS];
    float avg = 0.0;
    char grade = 'F';
    
    if (student_count >= MAX_STUDENTS) {
        printf("Maximum student limit reached!\n");
        return;
    }
    
    printf("\nEnter student ID: ");
    scanf("%d", &id);
    getchar();
    
    printf("Enter student name: ");
    fgets(name, MAX_NAME, stdin);
    name[strcspn(name, "\n")] = 0;
    
    printf("Enter marks for %d subjects:\n", num_subjects);
    i = 0;
    while (i < num_subjects) {
        printf("Subject %d: ", i + 1);
        scanf("%d", &marks[i]);
        i = i + 1;
    }
    
    // Calculate average and grade
    avg = calculate_average(marks, num_subjects);
    grade = assign_grade(avg);
    
    // Store student data
    students[student_count].id = id;
    strcpy(students[student_count].name, name);
    i = 0;
    while (i < num_subjects) {
        students[student_count].marks[i] = marks[i];
        i = i + 1;
    }
    students[student_count].average = avg;
    students[student_count].grade = grade;
    
    student_count = student_count + 1;
    printf("Student added successfully!\n");
}

// Function to display all students
void display_students() {
    int i = 0;
    int j = 0;
    
    if (student_count == 0) {
        printf("\nNo students in the system.\n");
        return;
    }
    
    printf("\n=== Student Records ===\n");
    i = 0;
    while (i < student_count) {
        printf("\nStudent %d:\n", i + 1);
        printf("ID: %d\n", students[i].id);
        printf("Name: %s\n", students[i].name);
        printf("Marks: ");
        
        j = 0;
        while (j < num_subjects) {
            printf("%d ", students[i].marks[j]);
            j = j + 1;
        }
        
        printf("\nAverage: %.2f\n", students[i].average);
        printf("Grade: %c\n", students[i].grade);
        i = i + 1;
    }
}

// Function to search student by ID
void search_student() {
    int search_id = 0;
    int i = 0;
    int found = 0;
    int j = 0;
    
    printf("\nEnter student ID to search: ");
    scanf("%d", &search_id);
    
    found = 0;
    i = 0;
    while (i < student_count && found == 0) {
        if (students[i].id == search_id) {
            found = 1;
            printf("\nStudent Found:\n");
            printf("ID: %d\n", students[i].id);
            printf("Name: %s\n", students[i].name);
            printf("Marks: ");
            
            j = 0;
            while (j < num_subjects) {
                printf("%d ", students[i].marks[j]);
                j = j + 1;
            }
            
            printf("\nAverage: %.2f\n", students[i].average);
            printf("Grade: %c\n", students[i].grade);
        }
        i = i + 1;
    }
    
    if (found == 0) {
        printf("Student not found!\n");
    }
}

// Function to calculate class statistics
void calculate_statistics() {
    float sum = 0.0;
    float class_avg = 0.0;
    float highest = 0.0;
    float lowest = 0.0;
    int i = 0;
    int pass_count = 0;
    int fail_count = 0;
    
    if (student_count == 0) {
        printf("\nNo students in the system.\n");
        return;
    }
    
    sum = 0.0;
    highest = students[0].average;
    lowest = students[0].average;
    pass_count = 0;
    fail_count = 0;
    
    i = 0;
    while (i < student_count) {
        sum = sum + students[i].average;
        
        if (students[i].average > highest) {
            highest = students[i].average;
        }
        
        if (students[i].average < lowest) {
            lowest = students[i].average;
        }
        
        if (students[i].average >= 60.0) {
            pass_count = pass_count + 1;
        } else {
            fail_count = fail_count + 1;
        }
        
        i = i + 1;
    }
    
    class_avg = sum / student_count;
    
    printf("\n=== Class Statistics ===\n");
    printf("Total Students: %d\n", student_count);
    printf("Class Average: %.2f\n", class_avg);
    printf("Highest Average: %.2f\n", highest);
    printf("Lowest Average: %.2f\n", lowest);
    printf("Pass Count: %d\n", pass_count);
    printf("Fail Count: %d\n", fail_count);
}

// Function to sort students by average
void sort_students() {
    int i = 0;
    int j = 0;
    struct Student temp;
    int swapped = 0;
    
    if (student_count == 0) {
        printf("\nNo students to sort.\n");
        return;
    }
    
    // Bubble sort
    i = 0;
    while (i < student_count - 1) {
        swapped = 0;
        j = 0;
        while (j < student_count - i - 1) {
            if (students[j].average < students[j + 1].average) {
                temp = students[j];
                students[j] = students[j + 1];
                students[j + 1] = temp;
                swapped = 1;
            }
            j = j + 1;
        }
        
        if (swapped == 0) {
            break;
        }
        
        i = i + 1;
    }
    
    printf("Students sorted by average (descending order).\n");
}

// Function to display top performers
void display_top_performers() {
    int i = 0;
    int count = 0;
    int display_count = 5;
    
    if (student_count == 0) {
        printf("\nNo students in the system.\n");
        return;
    }
    
    // First sort students
    sort_students();
    
    printf("\n=== Top Performers ===\n");
    
    count = student_count;
    if (count > display_count) {
        count = display_count;
    }
    
    i = 0;
    while (i < count) {
        printf("%d. %s (ID: %d) - Average: %.2f, Grade: %c\n",
               i + 1, students[i].name, students[i].id,
               students[i].average, students[i].grade);
        i = i + 1;
    }
}

// Function to update student marks
void update_student() {
    int search_id = 0;
    int i = 0;
    int j = 0;
    int found = 0;
    int marks[MAX_SUBJECTS];
    float avg = 0.0;
    char grade = 'F';
    
    printf("\nEnter student ID to update: ");
    scanf("%d", &search_id);
    
    found = 0;
    i = 0;
    while (i < student_count && found == 0) {
        if (students[i].id == search_id) {
            found = 1;
            printf("Current marks: ");
            j = 0;
            while (j < num_subjects) {
                printf("%d ", students[i].marks[j]);
                j = j + 1;
            }
            printf("\n");
            
            printf("Enter new marks for %d subjects:\n", num_subjects);
            j = 0;
            while (j < num_subjects) {
                printf("Subject %d: ", j + 1);
                scanf("%d", &marks[j]);
                students[i].marks[j] = marks[j];
                j = j + 1;
            }
            
            avg = calculate_average(students[i].marks, num_subjects);
            grade = assign_grade(avg);
            students[i].average = avg;
            students[i].grade = grade;
            
            printf("Student marks updated successfully!\n");
        }
        i = i + 1;
    }
    
    if (found == 0) {
        printf("Student not found!\n");
    }
}

// Main function
int main() {
    int choice = 0;
    int continue_flag = 1;
    
    printf("=== Student Grade Management System ===\n");
    printf("Welcome to the Grade Management System!\n");
    
    continue_flag = 1;
    while (continue_flag == 1) {
        printf("\n=== Main Menu ===\n");
        printf("1. Add Student\n");
        printf("2. Display All Students\n");
        printf("3. Search Student by ID\n");
        printf("4. Calculate Class Statistics\n");
        printf("5. Sort Students by Average\n");
        printf("6. Display Top Performers\n");
        printf("7. Update Student Marks\n");
        printf("0. Exit\n");
        printf("Enter choice: ");
        scanf("%d", &choice);
        
        if (choice == 1) {
            add_student();
        } else if (choice == 2) {
            display_students();
        } else if (choice == 3) {
            search_student();
        } else if (choice == 4) {
            calculate_statistics();
        } else if (choice == 5) {
            sort_students();
            printf("Display sorted list? (1=Yes, 0=No): ");
            scanf("%d", &choice);
            if (choice == 1) {
                display_students();
            }
        } else if (choice == 6) {
            display_top_performers();
        } else if (choice == 7) {
            update_student();
        } else if (choice == 0) {
            continue_flag = 0;
            printf("Exiting system. Thank you!\n");
        } else {
            printf("Invalid choice! Please try again.\n");
        }
    }
    
    return 0;
}
