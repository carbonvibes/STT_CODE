/*
 * Program 1: Simple Calculator with History
 * Description: A calculator that performs basic arithmetic operations
 * with operation history tracking and result validation.
 * Lines of Code: ~220
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_HISTORY 100
#define MAX_INPUT 50

// Global variables for history tracking
int history_count = 0;
double history_values[MAX_HISTORY];
char history_operations[MAX_HISTORY];

// Function to add operation to history
void add_to_history(double value, char operation) {
    int i = 0;
    if (history_count < MAX_HISTORY) {
        history_values[history_count] = value;
        history_operations[history_count] = operation;
        history_count = history_count + 1;
    } else {
        // Shift history if full
        i = 0;
        while (i < MAX_HISTORY - 1) {
            history_values[i] = history_values[i + 1];
            history_operations[i] = history_operations[i + 1];
            i = i + 1;
        }
        history_values[MAX_HISTORY - 1] = value;
        history_operations[MAX_HISTORY - 1] = operation;
    }
}

// Function to display history
void display_history() {
    int i = 0;
    printf("\n=== Operation History ===\n");
    
    if (history_count == 0) {
        printf("No operations in history.\n");
    } else {
        i = 0;
        while (i < history_count) {
            printf("%d. Operation: %c, Result: %.2f\n", 
                   i + 1, history_operations[i], history_values[i]);
            i = i + 1;
        }
    }
    printf("========================\n");
}

// Function to perform addition
double add(double a, double b) {
    double result = 0.0;
    result = a + b;
    return result;
}

// Function to perform subtraction
double subtract(double a, double b) {
    double result = 0.0;
    result = a - b;
    return result;
}

// Function to perform multiplication
double multiply(double a, double b) {
    double result = 0.0;
    result = a * b;
    return result;
}

// Function to perform division
double divide(double a, double b) {
    double result = 0.0;
    if (b != 0.0) {
        result = a / b;
    } else {
        printf("Error: Division by zero!\n");
        result = 0.0;
    }
    return result;
}

// Function to calculate average of history
double calculate_average() {
    double sum = 0.0;
    double avg = 0.0;
    int i = 0;
    
    if (history_count == 0) {
        return 0.0;
    }
    
    i = 0;
    sum = 0.0;
    while (i < history_count) {
        sum = sum + history_values[i];
        i = i + 1;
    }
    
    avg = sum / history_count;
    return avg;
}

// Function to find maximum in history
double find_max() {
    double max = 0.0;
    int i = 0;
    
    if (history_count == 0) {
        return 0.0;
    }
    
    max = history_values[0];
    i = 1;
    while (i < history_count) {
        if (history_values[i] > max) {
            max = history_values[i];
        }
        i = i + 1;
    }
    
    return max;
}

// Function to find minimum in history
double find_min() {
    double min = 0.0;
    int i = 0;
    
    if (history_count == 0) {
        return 0.0;
    }
    
    min = history_values[0];
    i = 1;
    while (i < history_count) {
        if (history_values[i] < min) {
            min = history_values[i];
        }
        i = i + 1;
    }
    
    return min;
}

// Main function
int main() {
    char operation = ' ';
    double num1 = 0.0;
    double num2 = 0.0;
    double result = 0.0;
    int choice = 0;
    int continue_flag = 1;
    char input[MAX_INPUT];
    
    printf("=== Advanced Calculator ===\n");
    printf("Welcome to the calculator program!\n\n");
    
    continue_flag = 1;
    while (continue_flag == 1) {
        printf("\nSelect operation:\n");
        printf("1. Addition (+)\n");
        printf("2. Subtraction (-)\n");
        printf("3. Multiplication (*)\n");
        printf("4. Division (/)\n");
        printf("5. View History\n");
        printf("6. Calculate Average\n");
        printf("7. Find Maximum\n");
        printf("8. Find Minimum\n");
        printf("9. Clear History\n");
        printf("0. Exit\n");
        printf("Enter choice: ");
        
        if (fgets(input, MAX_INPUT, stdin) != NULL) {
            choice = atoi(input);
        } else {
            choice = 0;
        }
        
        if (choice >= 1 && choice <= 4) {
            printf("Enter first number: ");
            if (fgets(input, MAX_INPUT, stdin) != NULL) {
                num1 = atof(input);
            }
            
            printf("Enter second number: ");
            if (fgets(input, MAX_INPUT, stdin) != NULL) {
                num2 = atof(input);
            }
            
            result = 0.0;
            operation = ' ';
            
            if (choice == 1) {
                result = add(num1, num2);
                operation = '+';
                printf("Result: %.2f + %.2f = %.2f\n", num1, num2, result);
            } else if (choice == 2) {
                result = subtract(num1, num2);
                operation = '-';
                printf("Result: %.2f - %.2f = %.2f\n", num1, num2, result);
            } else if (choice == 3) {
                result = multiply(num1, num2);
                operation = '*';
                printf("Result: %.2f * %.2f = %.2f\n", num1, num2, result);
            } else if (choice == 4) {
                result = divide(num1, num2);
                operation = '/';
                if (num2 != 0.0) {
                    printf("Result: %.2f / %.2f = %.2f\n", num1, num2, result);
                }
            }
            
            add_to_history(result, operation);
            
        } else if (choice == 5) {
            display_history();
        } else if (choice == 6) {
            result = calculate_average();
            printf("Average of all results: %.2f\n", result);
        } else if (choice == 7) {
            result = find_max();
            printf("Maximum result: %.2f\n", result);
        } else if (choice == 8) {
            result = find_min();
            printf("Minimum result: %.2f\n", result);
        } else if (choice == 9) {
            history_count = 0;
            printf("History cleared!\n");
        } else if (choice == 0) {
            continue_flag = 0;
            printf("Thank you for using the calculator!\n");
        } else {
            printf("Invalid choice! Please try again.\n");
        }
    }
    
    return 0;
}
