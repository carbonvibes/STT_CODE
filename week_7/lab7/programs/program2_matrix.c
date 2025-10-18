/*
 * Program 2: Matrix Operations Processor
 * Description: Performs various matrix operations including addition,
 * multiplication, transpose, and diagonal sum with validation.
 * Lines of Code: ~250
 */

#include <stdio.h>
#include <stdlib.h>

#define MAX_SIZE 10

// Global matrices
int matrix_a[MAX_SIZE][MAX_SIZE];
int matrix_b[MAX_SIZE][MAX_SIZE];
int matrix_result[MAX_SIZE][MAX_SIZE];

// Function to initialize matrix
void initialize_matrix(int mat[MAX_SIZE][MAX_SIZE], int rows, int cols) {
    int i = 0;
    int j = 0;
    
    i = 0;
    while (i < rows) {
        j = 0;
        while (j < cols) {
            mat[i][j] = 0;
            j = j + 1;
        }
        i = i + 1;
    }
}

// Function to input matrix
void input_matrix(int mat[MAX_SIZE][MAX_SIZE], int rows, int cols, char name) {
    int i = 0;
    int j = 0;
    
    printf("\nEnter elements for Matrix %c (%dx%d):\n", name, rows, cols);
    
    i = 0;
    while (i < rows) {
        j = 0;
        while (j < cols) {
            printf("Element [%d][%d]: ", i, j);
            scanf("%d", &mat[i][j]);
            j = j + 1;
        }
        i = i + 1;
    }
}

// Function to display matrix
void display_matrix(int mat[MAX_SIZE][MAX_SIZE], int rows, int cols, char name) {
    int i = 0;
    int j = 0;
    
    printf("\nMatrix %c:\n", name);
    i = 0;
    while (i < rows) {
        j = 0;
        while (j < cols) {
            printf("%4d ", mat[i][j]);
            j = j + 1;
        }
        printf("\n");
        i = i + 1;
    }
}

// Function to add two matrices
void add_matrices(int a[MAX_SIZE][MAX_SIZE], int b[MAX_SIZE][MAX_SIZE], 
                  int result[MAX_SIZE][MAX_SIZE], int rows, int cols) {
    int i = 0;
    int j = 0;
    
    i = 0;
    while (i < rows) {
        j = 0;
        while (j < cols) {
            result[i][j] = a[i][j] + b[i][j];
            j = j + 1;
        }
        i = i + 1;
    }
}

// Function to subtract two matrices
void subtract_matrices(int a[MAX_SIZE][MAX_SIZE], int b[MAX_SIZE][MAX_SIZE], 
                       int result[MAX_SIZE][MAX_SIZE], int rows, int cols) {
    int i = 0;
    int j = 0;
    
    i = 0;
    while (i < rows) {
        j = 0;
        while (j < cols) {
            result[i][j] = a[i][j] - b[i][j];
            j = j + 1;
        }
        i = i + 1;
    }
}

// Function to multiply two matrices
int multiply_matrices(int a[MAX_SIZE][MAX_SIZE], int b[MAX_SIZE][MAX_SIZE], 
                      int result[MAX_SIZE][MAX_SIZE], 
                      int rows_a, int cols_a, int cols_b) {
    int i = 0;
    int j = 0;
    int k = 0;
    int sum = 0;
    
    // Initialize result matrix
    i = 0;
    while (i < rows_a) {
        j = 0;
        while (j < cols_b) {
            result[i][j] = 0;
            j = j + 1;
        }
        i = i + 1;
    }
    
    // Perform multiplication
    i = 0;
    while (i < rows_a) {
        j = 0;
        while (j < cols_b) {
            sum = 0;
            k = 0;
            while (k < cols_a) {
                sum = sum + a[i][k] * b[k][j];
                k = k + 1;
            }
            result[i][j] = sum;
            j = j + 1;
        }
        i = i + 1;
    }
    
    return 1;
}

// Function to transpose matrix
void transpose_matrix(int mat[MAX_SIZE][MAX_SIZE], int result[MAX_SIZE][MAX_SIZE], 
                      int rows, int cols) {
    int i = 0;
    int j = 0;
    
    i = 0;
    while (i < rows) {
        j = 0;
        while (j < cols) {
            result[j][i] = mat[i][j];
            j = j + 1;
        }
        i = i + 1;
    }
}

// Function to calculate diagonal sum
int diagonal_sum(int mat[MAX_SIZE][MAX_SIZE], int size) {
    int sum = 0;
    int i = 0;
    
    i = 0;
    while (i < size) {
        sum = sum + mat[i][i];
        i = i + 1;
    }
    
    return sum;
}

// Function to find maximum element
int find_max_element(int mat[MAX_SIZE][MAX_SIZE], int rows, int cols) {
    int max = 0;
    int i = 0;
    int j = 0;
    
    max = mat[0][0];
    i = 0;
    while (i < rows) {
        j = 0;
        while (j < cols) {
            if (mat[i][j] > max) {
                max = mat[i][j];
            }
            j = j + 1;
        }
        i = i + 1;
    }
    
    return max;
}

// Function to check if matrix is symmetric
int is_symmetric(int mat[MAX_SIZE][MAX_SIZE], int size) {
    int i = 0;
    int j = 0;
    int symmetric = 1;
    
    i = 0;
    while (i < size && symmetric == 1) {
        j = 0;
        while (j < size && symmetric == 1) {
            if (mat[i][j] != mat[j][i]) {
                symmetric = 0;
            }
            j = j + 1;
        }
        i = i + 1;
    }
    
    return symmetric;
}

// Main function
int main() {
    int choice = 0;
    int rows_a = 0;
    int cols_a = 0;
    int rows_b = 0;
    int cols_b = 0;
    int continue_flag = 1;
    int result_value = 0;
    
    printf("=== Matrix Operations Processor ===\n");
    printf("Welcome to the matrix calculator!\n");
    
    continue_flag = 1;
    while (continue_flag == 1) {
        printf("\n=== Menu ===\n");
        printf("1. Matrix Addition\n");
        printf("2. Matrix Subtraction\n");
        printf("3. Matrix Multiplication\n");
        printf("4. Matrix Transpose\n");
        printf("5. Diagonal Sum\n");
        printf("6. Find Maximum Element\n");
        printf("7. Check Symmetric Matrix\n");
        printf("0. Exit\n");
        printf("Enter choice: ");
        scanf("%d", &choice);
        
        if (choice >= 1 && choice <= 3) {
            printf("Enter dimensions for Matrix A (rows cols): ");
            scanf("%d %d", &rows_a, &cols_a);
            
            if (rows_a <= 0 || rows_a > MAX_SIZE || cols_a <= 0 || cols_a > MAX_SIZE) {
                printf("Invalid dimensions!\n");
            } else {
                printf("Enter dimensions for Matrix B (rows cols): ");
                scanf("%d %d", &rows_b, &cols_b);
                
                if (rows_b <= 0 || rows_b > MAX_SIZE || cols_b <= 0 || cols_b > MAX_SIZE) {
                    printf("Invalid dimensions!\n");
                } else {
                    if (choice == 1 || choice == 2) {
                        if (rows_a != rows_b || cols_a != cols_b) {
                            printf("Matrices must have same dimensions for addition/subtraction!\n");
                        } else {
                            input_matrix(matrix_a, rows_a, cols_a, 'A');
                            input_matrix(matrix_b, rows_b, cols_b, 'B');
                            
                            if (choice == 1) {
                                add_matrices(matrix_a, matrix_b, matrix_result, rows_a, cols_a);
                                printf("\nResult of Addition:\n");
                            } else {
                                subtract_matrices(matrix_a, matrix_b, matrix_result, rows_a, cols_a);
                                printf("\nResult of Subtraction:\n");
                            }
                            
                            display_matrix(matrix_result, rows_a, cols_a, 'R');
                        }
                    } else if (choice == 3) {
                        if (cols_a != rows_b) {
                            printf("Invalid dimensions for multiplication!\n");
                            printf("Columns of A must equal rows of B.\n");
                        } else {
                            input_matrix(matrix_a, rows_a, cols_a, 'A');
                            input_matrix(matrix_b, rows_b, cols_b, 'B');
                            
                            result_value = multiply_matrices(matrix_a, matrix_b, matrix_result, 
                                                           rows_a, cols_a, cols_b);
                            
                            if (result_value == 1) {
                                printf("\nResult of Multiplication:\n");
                                display_matrix(matrix_result, rows_a, cols_b, 'R');
                            }
                        }
                    }
                }
            }
        } else if (choice == 4) {
            printf("Enter dimensions for Matrix (rows cols): ");
            scanf("%d %d", &rows_a, &cols_a);
            
            if (rows_a <= 0 || rows_a > MAX_SIZE || cols_a <= 0 || cols_a > MAX_SIZE) {
                printf("Invalid dimensions!\n");
            } else {
                input_matrix(matrix_a, rows_a, cols_a, 'A');
                transpose_matrix(matrix_a, matrix_result, rows_a, cols_a);
                printf("\nTranspose of Matrix:\n");
                display_matrix(matrix_result, cols_a, rows_a, 'T');
            }
        } else if (choice == 5) {
            printf("Enter size of square matrix: ");
            scanf("%d", &rows_a);
            
            if (rows_a <= 0 || rows_a > MAX_SIZE) {
                printf("Invalid size!\n");
            } else {
                cols_a = rows_a;
                input_matrix(matrix_a, rows_a, cols_a, 'A');
                result_value = diagonal_sum(matrix_a, rows_a);
                printf("\nDiagonal sum: %d\n", result_value);
            }
        } else if (choice == 6) {
            printf("Enter dimensions for Matrix (rows cols): ");
            scanf("%d %d", &rows_a, &cols_a);
            
            if (rows_a <= 0 || rows_a > MAX_SIZE || cols_a <= 0 || cols_a > MAX_SIZE) {
                printf("Invalid dimensions!\n");
            } else {
                input_matrix(matrix_a, rows_a, cols_a, 'A');
                result_value = find_max_element(matrix_a, rows_a, cols_a);
                printf("\nMaximum element: %d\n", result_value);
            }
        } else if (choice == 7) {
            printf("Enter size of square matrix: ");
            scanf("%d", &rows_a);
            
            if (rows_a <= 0 || rows_a > MAX_SIZE) {
                printf("Invalid size!\n");
            } else {
                cols_a = rows_a;
                input_matrix(matrix_a, rows_a, cols_a, 'A');
                result_value = is_symmetric(matrix_a, rows_a);
                
                if (result_value == 1) {
                    printf("\nMatrix is symmetric.\n");
                } else {
                    printf("\nMatrix is not symmetric.\n");
                }
            }
        } else if (choice == 0) {
            continue_flag = 0;
            printf("Exiting program. Thank you!\n");
        } else {
            printf("Invalid choice! Please try again.\n");
        }
    }
    
    return 0;
}
